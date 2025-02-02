# Marine Route Optimizer

## Overview
The Marine Route Optimizer is a Python application designed to optimize maritime routes based on weather conditions, vessel specifications, and geographical waypoints. It utilizes Ant Colony Optimization (ACO) algorithms to find the most efficient path for vessels while considering real-time weather data.

## Features
- Fetches real-time weather data using the OpenWeatherMap API.
- Optimizes maritime routes using Ant Colony Optimization.
- Sends SMS notifications for emergency weather conditions using Twilio.
- Visualizes routes on a map using Folium.

## Requirements
- Python 3.x
- Required Python packages:
  - `requests`
  - `geopy`
  - `numpy`
  - `folium`
  - `twilio`
  - `streamlit`
  - `groq`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/marine-route-optimizer.git
   cd marine-route-optimizer
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Twilio account:
   - Sign up for a Twilio account and obtain your Account SID, Auth Token, and a Twilio phone number.
   - Update the Twilio credentials in the `app.py` file.

4. Set up your OpenWeatherMap API key:
   - Sign up for an OpenWeatherMap account and obtain your API key.
   - Update the API key in the `app.py` file.

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Enter the start and end locations, fuel capacity, and vessel weight, then click "Optimize Route".

4. Monitor the weather conditions and receive SMS notifications for any emergencies.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [OpenWeatherMap](https://openweathermap.org/) for weather data.
- [Twilio](https://www.twilio.com/) for SMS notifications.
- [Streamlit](https://streamlit.io/) for building the web application.


