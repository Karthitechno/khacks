import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
import heapq
import numpy as np
import folium
from groq import Groq
import logging
import arrow  # Make sure to install arrow if you haven't already

# Replace these with your actual API keys
WEATHER_API_KEY = "xxxxxxxxxxx"  # This can be removed if not used
GROQ_API_KEY = "xxxxxxxxxxxxxxx"

# Configure logging
logging.basicConfig(filename='marine_optimization.log', level=logging.INFO)

@dataclass
class WeatherData:
    location: str
    temperature: float
    feels_like: float
    description: str
    wind_speed: float
    humidity: int
    pressure: float
    visibility: float

@dataclass
class Ship:
    ship_type: str
    max_speed: float
    fuel_consumption: float
    safety_rating: float

class MarineWeatherAnalyzer:
    def _init_(self):
        """Initialize the analyzer with API clients"""
        self.weather_api_key = WEATHER_API_KEY
        self.groq_client = Groq(api_key=GROQ_API_KEY)

    def fetch_weather_data(self, lat: float, lng: float) -> Optional[WeatherData]:
        """Fetch and parse marine weather data based on location using Storm Glass API"""
        start = arrow.now().floor('day')
        end = arrow.now().ceil('day')

        response = requests.get(
            'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': lat,
                'lng': lng,
                'params': ','.join(['waveHeight', 'airTemperature', 'visibility', 'windSpeed', 'windDirection']),
                'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
                'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
            },
            headers={
                'Authorization': 'ec6e10b0-e0a3-11ef-b651-0242ac130003-ec6e111e-e0a3-11ef-b651-0242ac130003'  # Replace with your actual API key
            }
        )

        if response.status_code == 200:
            json_data = response.json()
            # Extract relevant data from the response
            if json_data and 'hours' in json_data:
                latest_data = json_data['hours'][0]  # Get the first hour of data
                return WeatherData(
                    location=f"Coordinates: {lat}, {lng}",
                    temperature=latest_data.get('airTemperature', {}).get('noaa', None),
                    feels_like=None,  # You can calculate this if needed
                    description="Weather data from Storm Glass API",
                    wind_speed=latest_data.get('windSpeed', {}).get('noaa', None),
                    humidity=latest_data.get('humidity', {}).get('noaa', None),
                    pressure=None,  # Add if available
                    visibility=latest_data.get('visibility', {}).get('noaa', None)
                )
            else:
                logging.error("No weather data found.")
                return None
        else:
            logging.error(f"Error fetching weather data: {response.status_code} - {response.text}")
            return None

    def fetch_weather_forecast(self, lat: float, lon: float) -> List[WeatherData]:
        """Fetch weather forecast data for the next 5 days"""
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/forecast?"
                f"lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            forecast = []
            for entry in data['list']:
                forecast.append(WeatherData(
                    location=data['city']['name'],
                    temperature=entry['main']['temp'],
                    feels_like=entry['main']['feels_like'],
                    description=entry['weather'][0]['description'],
                    wind_speed=entry['wind'].get('speed', 0),
                    humidity=entry['main']['humidity'],
                    pressure=entry['main']['pressure'],
                    visibility=entry.get('visibility', 0) / 1000,
                ))
            return forecast
        except requests.RequestException as e:
            logging.error(f"Error fetching weather forecast: {e}")
            return []

    def calculate_beaufort_scale(self, wind_speed: float) -> Dict[str, any]:
        """Calculate Beaufort scale force and description"""
        try:
            wind_knots = wind_speed * 1.944  # Convert m/s to knots
            
            beaufort_scale = [
                (0, 1, "Calm", "Sea like a mirror"),
                (1, 3, "Light air", "Ripples with appearance of scales"),
                (4, 6, "Light breeze", "Small wavelets"),
                (7, 10, "Gentle breeze", "Large wavelets"),
                (11, 16, "Moderate breeze", "Small waves with breaking crests"),
                (17, 21, "Fresh breeze", "Moderate waves with whitecaps"),
                (22, 27, "Strong breeze", "Larger waves with extensive whitecaps"),
                (28, 33, "Near gale", "Sea heaps up, foam begins to streak"),
                (34, 40, "Gale", "Moderately high waves with breaking crests"),
                (41, 47, "Strong gale", "High waves with dense foam"),
                (48, 55, "Storm", "Very high waves with overhanging crests"),
                (56, 63, "Violent storm", "Exceptionally high waves"),
                (64, float('inf'), "Hurricane", "Air filled with foam and spray")
            ]
            
            for force, (min_speed, max_speed, condition, sea_state) in enumerate(beaufort_scale):
                if min_speed <= wind_knots <= max_speed:
                    return {
                        "force": force,
                        "condition": condition,
                        "sea_state": sea_state,
                        "wind_knots": round(wind_knots, 1)
                    }
            
            return {
                "force": 12,
                "condition": "Hurricane",
                "sea_state": "Air filled with foam and spray",
                "wind_knots": round(wind_knots, 1)
            }
        except Exception as e:
            logging.error(f"Error calculating Beaufort scale: {e}")
            return {
                "force": 0,
                "condition": "Unknown",
                "sea_state": "Unable to determine",
                "wind_knots": 0.0
            }

    def generate_weather_summary(self, weather_data: WeatherData) -> str:
        """Generate a summary of the weather data"""
        return (
            f"Current Weather in {weather_data.location}:\n"
            f"Temperature: {weather_data.temperature}°C\n"
            f"Wind Speed: {weather_data.wind_speed} m/s\n"
            f"Humidity: {weather_data.humidity}%\n"
            f"Visibility: {weather_data.visibility} km\n"
        )

    def generate_llm_response(self, user_query: str) -> str:
        """Generate a concise response using the LLM for non-weather queries"""
        prompt = f"User asked: {user_query}\nProvide a short and conversational response."
        completion = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150  # Limit the response length
        )
        return completion.choices[0].message.content

    def handle_fallback(self, user_query: str) -> str:
        """Handle queries that the chatbot cannot process."""
        return self.generate_llm_response(f"I'm not sure how to answer this: {user_query}. Can you rephrase or provide more details?")

    def optimize_route(self, start: tuple, end: tuple, ship: Ship, weather_data: WeatherData) -> List[tuple]:
        """Optimize the route based on weather conditions and ship characteristics"""
        def heuristic(a, b):
            return np.sqrt((a[0] - b[0])*2 + (a[1] - b[1])*2)

        def cost_function(current, neighbor, weather_data, ship):
            # Calculate cost based on distance, weather, and ship characteristics
            distance = heuristic(current, neighbor)
            wind_speed = weather_data.wind_speed
            wave_height = wind_speed * 0.1  # Simplified wave height estimation
            fuel_cost = distance * ship.fuel_consumption
            safety_cost = (wind_speed / 20) + (wave_height / 2)  # Higher cost for worse conditions
            time_cost = distance / ship.max_speed
            return fuel_cost + safety_cost + time_cost

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + cost_function(current, neighbor, weather_data, ship)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def get_neighbors(self, point: tuple) -> List[tuple]:
        """Get neighboring points for route optimization"""
        neighbors = []
        for dx, dy in [(-0.1, 0), (0.1, 0), (0, -0.1), (0, 0.1)]:
            neighbors.append((point[0] + dx, point[1] + dy))
        return neighbors

    def visualize_route(self, route: List[tuple]):
        """Visualize the optimized route on a map"""
        if not route:
            print("No route to visualize.")
            return

        # Create a map centered at the start point
        map_center = route[0]
        m = folium.Map(location=map_center, zoom_start=10)

        # Add the route to the map
        folium.PolyLine(route, color="blue", weight=2.5, opacity=1).add_to(m)

        # Add markers for start and end points
        folium.Marker(route[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(route[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)

        # Save the map as an HTML file
        m.save("route_map.html")
        print("Map saved as route_map.html. Open this file in your browser to view the route.")

def main():
    analyzer = MarineWeatherAnalyzer()
    
    marine_keywords = ["sea", "marine", "ocean", "vessel", "ship", "weather", "navigation", "sailing", "fishing"]

    while True:
        user_input = input("Ask me anything about marine topics (type 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Check if the user input contains any marine-related keywords
        if any(keyword in user_input.lower() for keyword in marine_keywords):
            if "weather" in user_input.lower():
                # Extract latitude and longitude from user input
                lat = float(input("Please enter the latitude: "))
                lng = float(input("Please enter the longitude: "))
                weather_data = analyzer.fetch_weather_data(lat, lng)
                if weather_data:
                    summary = analyzer.generate_weather_summary(weather_data)
                    print(summary)
                else:
                    print("Could not fetch weather data.")
            else:
                response = analyzer.generate_llm_response(user_input)
                print(response)
        else:
            # Use the fallback function for unrecognized queries
            fallback_response = analyzer.handle_fallback(user_input)
            print(fallback_response)

if __name__ == "_main_":
    main()