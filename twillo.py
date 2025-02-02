import requests
from geopy.geocoders import Nominatim
from datetime import datetime
import numpy as np
import logging
import random
import time
from functools import lru_cache
import threading
from math import radians, sin, cos, sqrt, atan2
from twilio.rest import Client

# Replace these with your actual API keys
WEATHER_API_KEY = "xxxxxxx"
TWILIO_ACCOUNT_SID = "xxxxxxxxx"
TWILIO_AUTH_TOKEN ="xxxxxxxxxxx"
TWILIO_PHONE_NUMBER = "xxxxxxxxxx"
RECIPIENT_PHONE_NUMBER = "xxxxxxxxxx"

# Configure logging
logging.basicConfig(filename='marine_optimization.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class MarineWeatherAnalyzer:
    def _init_(self):
        """Initialize the analyzer with API clients and caching"""
        self.weather_api_key = WEATHER_API_KEY
        self.geolocator = Nominatim(
            user_agent="marine_optimization_v1.0",
            timeout=5
        )

    @lru_cache(maxsize=100)
    def get_coordinates(self, location: str):
        """Get coordinates with caching for faster repeated lookups"""
        location = location.lower().strip()
        loc = self.geolocator.geocode(location)
        if loc:
            return (loc.latitude, loc.longitude)
        return None

    def fetch_weather_data(self, lat: float, lon: float):
        """Fetch and parse marine weather data"""
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
        )
        response = requests.get(url)
        data = response.json()
        return data

    def ant_colony_optimization(self, graph, start, end, ship, weather_data):
        """Implement Ant Colony Optimization"""
        # Simplified route optimization logic
        return [start, end], 0

    def send_sms_notification(self, message):
        """Send SMS notification using Twilio"""
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=RECIPIENT_PHONE_NUMBER
            )
            print(f"SMS notification sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send SMS: {e}")
            print(f"Failed to send SMS: {e}")

    def check_weather_conditions(self, weather_data):
        """Check weather conditions and return alert message if conditions are dangerous"""
        try:
            wind_speed = weather_data.get('wind', {}).get('speed', 0)
            temperature = weather_data.get('main', {}).get('temp', 0)
            visibility = weather_data.get('visibility', 10000) / 1000  # Convert to km
            
            alerts = []
            
            # Wind speed alert (> 20 knots / 10.3 m/s)
            if wind_speed > 10.3:
                alerts.append(f"HIGH WIND ALERT: Wind speed is {wind_speed} m/s ({wind_speed * 1.944:.1f} knots)")
            
            # Poor visibility alert (< 2 km)
            if visibility < 2:
                alerts.append(f"LOW VISIBILITY ALERT: Visibility is {visibility} km")
            
            # Extreme temperature alert
            if temperature > 35:
                alerts.append(f"HIGH TEMPERATURE ALERT: Temperature is {temperature}°C")
            elif temperature < 0:
                alerts.append(f"LOW TEMPERATURE ALERT: Temperature is {temperature}°C")
            
            if alerts:
                return "\n".join(alerts)
            return None

        except Exception as e:
            logging.error(f"Error checking weather conditions: {e}")
            return None

    def monitor_weather(self, start_coords):
        """Continuously monitor weather and send alerts"""
        print("\nStarting weather monitoring...")
        print("The system will send SMS alerts when:")
        print("- Wind speed exceeds 1 knots (1 m/s)")
        print("- Visibility drops below 2 km")
        print("- Temperature goes above 35°C or below 0°C")
        
        while True:
            try:
                weather_data = self.fetch_weather_data(start_coords[0], start_coords[1])
                if weather_data:
                    alert_message = self.check_weather_conditions(weather_data)
                    
                    if alert_message:
                        print(f"\nALERT CONDITIONS DETECTED!")
                        print(alert_message)
                        self.send_sms_notification(alert_message)
                        print("SMS alert sent!")
                    
                    # Print current conditions
                    print("\nCurrent Weather Conditions:")
                    print(f"Temperature: {weather_data.get('main', {}).get('temp', 'N/A')}°C")
                    print(f"Wind Speed: {weather_data.get('wind', {}).get('speed', 'N/A')} m/s")
                    print(f"Visibility: {weather_data.get('visibility', 'N/A')/1000} km")
                    
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Error in weather monitoring: {e}")
                print(f"Error in weather monitoring: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def simulate_dangerous_weather(self):
        """Simulate dangerous weather conditions for demonstration"""
        return {
            'wind': {'speed': 25.7},  # Very high wind speed
            'visibility': 1500,       # Poor visibility (1.5 km)
            'main': {'temp': 38},     # High temperature
            'weather': [{'description': 'dangerous storm conditions'}]
        }

    def demo_weather_alert(self):
        """Demonstration function to trigger weather alerts"""
        print("\n=== WEATHER ALERT DEMONSTRATION ===")
        print("Simulating dangerous weather conditions...")
        
        # Use simulated weather data
        weather_data = self.simulate_dangerous_weather()
        
        # Check conditions and send alert
        alert_message = self.check_weather_conditions(weather_data)
        if alert_message:
            print("\nDangerous conditions detected!")
            print(alert_message)
            print("\nSending SMS notification...")
            self.send_sms_notification(alert_message)
            print("\nSMS alert sent! Check your phone.")
            print(f"Message sent to: {RECIPIENT_PHONE_NUMBER}")
        
        return weather_data

def main():
    try:
        print("Marine Route Optimizer")
        print("---------------------")
        
        analyzer = MarineWeatherAnalyzer()
        
        # Add demo option
        print("\nSelect operation:")
        print("1. Run normal weather monitoring")
        print("2. Run demonstration (trigger alert)")
        choice = input("Enter your choice (1/2): ")
        
        if choice == "2":
            # Run demonstration
            weather_data = analyzer.demo_weather_alert()
            print("\nCurrent (Simulated) Weather Conditions:")
            print(f"Temperature: {weather_data.get('main', {}).get('temp', 'N/A')}°C")
            print(f"Wind Speed: {weather_data.get('wind', {}).get('speed', 'N/A')} m/s")
            print(f"Visibility: {weather_data.get('visibility', 'N/A')/1000} km")
            return
            
        # Normal operation
        start_location = input("Enter start location: ")
        end_location = input("Enter end location: ")
        fuel_capacity = float(input("Enter fuel capacity (liters/tons): "))
        vessel_weight = float(input("Enter vessel weight (tons): "))
        
        print("\nFetching coordinates...")
        start_coords = analyzer.get_coordinates(start_location)
        end_coords = analyzer.get_coordinates(end_location)

        if not start_coords or not end_coords:
            print("Error: Could not find coordinates for the specified locations.")
            return

        # Start weather monitoring in a separate thread
        weather_thread = threading.Thread(
            target=analyzer.monitor_weather,
            args=(start_coords,),
            daemon=True
        )
        weather_thread.start()

        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"\nAn error occurred: {e}")

if __name__ == "_main_":
    main()
