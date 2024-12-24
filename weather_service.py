import requests
from config import WEATHER_API_KEY, WEATHER_API_URL

BASE_URL = WEATHER_API_URL

def get_location_key(city):
    location_url = f"{BASE_URL}locations/v1/cities/search"
    params = {'apikey': WEATHER_API_KEY, 'q': city}
    response = requests.get(location_url, params=params)
    response.raise_for_status()
    location_data = response.json()
    if not location_data:
        raise ValueError("Город не найден.")
    return location_data[0]['Key']

def get_weather_forecast(location_key, days):
    weather_url = f"{BASE_URL}forecasts/v1/daily/{days}day/{location_key}"
    params = {'apikey': WEATHER_API_KEY, 'metric': 'true'}
    response = requests.get(weather_url, params=params)
    response.raise_for_status()
    return response.json()

def get_weather_forecasts(route_points, days):
    forecasts = {}
    for point in route_points:
        location_key = get_location_key(point)
        forecast_data = get_weather_forecast(location_key, days)
        forecasts[point] = forecast_data
    return forecasts
