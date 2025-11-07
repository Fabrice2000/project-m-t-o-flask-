from fastapi import APIRouter
import requests
import os

router = APIRouter(prefix="/weather", tags=["weather"])

API_KEY = os.getenv("OPENWEATHER_API_KEY")

@router.get("/")
def get_weather(city: str):
    if not API_KEY:
        return {"error": "OPENWEATHER_API_KEY non défini"}
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=fr"
    r = requests.get(url)
    return r.json()
