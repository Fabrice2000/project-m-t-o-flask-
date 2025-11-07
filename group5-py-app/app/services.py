from abc import ABC, abstractmethod
import requests
import os
from datetime import datetime

class WeatherServiceInterface(ABC):
    @abstractmethod
    def get_forecast(self, city: str, date: datetime) -> dict:
        pass

class OpenWeatherService(WeatherServiceInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_forecast(self, city: str, date: datetime) -> dict:
        params = {"q": city, "appid": self.api_key, "units": "metric"}
        resp = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
