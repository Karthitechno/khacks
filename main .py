import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
import heapq
import numpy as np
import folium
from groq import Groq
import logging

# Replace these with your actual API keys
WEATHER_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Configure logging
logging.basicConfig(filename='marine_optimization.log', level=logging.INFO)

@dataclass
class WeatherData:
    location: str
    temperature: float
    feels_like: float
    description: str
    wind_speed: float
    wind_direction: float
    humidity: int
    pressure: float
    visibility: float
    timestamp: datetime

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

    def fetch_weather_data(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Fetch and parse marine weather data"""
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Improved location handling
            location = data.get('name', 'Open Water')
            if not location or location == '':
                location = f"Coordinates: {lat}°N, {lon}°E"
            
            return WeatherData(
                location=location,
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                description=data['weather'][0]['description'],
                wind_speed=data['wind'].get('speed', 0),
                wind_direction=data['wind'].get('deg', 0),
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                visibility=data.get('visibility', 0) / 1000,  # Convert to km
                timestamp=datetime.fromtimestamp(data['dt'])
            )
        except requests.RequestException as e:
            logging.error(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            logging.error(f"Error parsing weather data: {e}")
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
                    wind_direction=entry['wind'].get('deg', 0),
                    humidity=entry['main']['humidity'],
                    pressure=entry['main']['pressure'],
                    visibility=entry.get('visibility', 0) / 1000,
                    timestamp=datetime.fromtimestamp(entry['dt'])
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
        """Generate comprehensive weather analysis using Groq LLM"""
        try:
            beaufort_info = self.calculate_beaufort_scale(weather_data.wind_speed)
            
            prompt = f"""
            Generate a detailed marine weather analysis with the following sections:
            
            f"🌊 *Current Conditions at {weather_data.location}:*\n"
        f"- Temperature: {weather_data.temperature}°C\n"
        f"- Weather: {weather_data.description}\n"
        f"- Wind: {beaufort_info['wind_knots']} knots, {beaufort_info['condition']}\n"
        f"- Sea State: {beaufort_info['sea_state']}\n"
        f"- Visibility: {weather_data.visibility} km\n\n"
        f"🚨 *Navigation Safety:*\n"
        f"- Risk Level: {'Low' if beaufort_info['force'] < 4 else 'Moderate/High'}\n"
        f"- Hazards: Heat, humidity, potential weather changes\n\n"
        f"📋 *Recommendations:*\n"
        f"- Monitor weather updates regularly.\n"
        f"- Ensure safety equipment is functional.\n"
        f"- Manage crew comfort in high heat.\n\n"
        f"⚠ *Key Precautions:*\n"
        f"- Stay hydrated and avoid heat exposure.\n"
        f"- Maintain vigilance for weather changes.\n"
            
            
            """

            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            logging.error(f"Error generating weather summary: {e}")
            return f"Error generating weather summary: {str(e)}"

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
        """Visualize the optimized route on a map using Leaflet and OpenSeaMap"""
        if not route:
            print("No route to visualize.")
            return

        # Create a map centered at the start point
        map_center = route[0]
        m = folium.Map(location=map_center, zoom_start=10)

        # Add OpenSeaMap tiles
        folium.TileLayer(
            tiles='https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
            attr='OpenSeaMap',
            name='OpenSeaMap',
            overlay=True,
            control=True
        ).add_to(m)

        # Add the route to the map
        folium.PolyLine(route, color="blue", weight=2.5, opacity=1).add_to(m)

        # Add markers for start and end points
        folium.Marker(route[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(route[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)

        # Save the map to an HTML file
        m.save("optimized_route.html")
        print("Optimized route saved to 'optimized_route.html'. Open this file in your browser to view the map.")

def main():
    analyzer = MarineWeatherAnalyzer()
    ship = Ship(ship_type="Cargo", max_speed=20, fuel_consumption=0.1, safety_rating=0.9)
    
    # Input coordinates
    start_lat = float(input("Enter start latitude (-90 to 90): "))
    start_lon = float(input("Enter start longitude (-180 to 180): "))
    end_lat = float(input("Enter end latitude (-90 to 90): "))
    end_lon = float(input("Enter end longitude (-180 to 180): "))

    start = (start_lat, start_lon)
    end = (end_lat, end_lon)

    weather_data = analyzer.fetch_weather_data(start_lat, start_lon)
    if weather_data:
        print("🌊 Generating Marine Weather Analysis...")
        print(analyzer.generate_weather_summary(weather_data))

        optimized_route = analyzer.optimize_route(start, end, ship, weather_data)
        print("Optimized Route:", optimized_route)

        # Visualize the optimized route
        analyzer.visualize_route(optimized_route)

if _name_ == "_main_":
    main()
