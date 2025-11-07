from typing import List
from datetime import datetime

class Recommender:
    def __init__(self, weather_service, aq_service, activity_repo):
        self.weather_service = weather_service
        self.aq_service = aq_service
        self.activity_repo = activity_repo

    def score_activity(self, activity, forecast: dict, profile: dict) -> float:
        """
        Score simple:
         - if forecast indicates rain and activity is OUTDOOR => penalize
         - profile.outdoor_pref increases score for OUTDOOR activities
         - good AQ increases outdoor score
        Returns score (higher = better)
        """
        base = 0.5
        io = activity.indoor_outdoor.value
        rain = forecast.get("precipitation", 0)
        temp = forecast.get("temp", 15)
        aqi = forecast.get("aqi", 50)

        if io == "outdoor":
            base += profile.get("outdoor_pref", 0.5)
            base -= rain * 1.0
            if aqi > 100:
                base -= 0.5
        elif io == "indoor":
            base += (1 - profile.get("outdoor_pref", 0.5))

        if temp < 5 or temp > 32:
            base -= 0.3

        return base

    def recommend(self, city: str, date: datetime, user_profile: dict, limit=10):
        forecast = self.weather_service.get_forecast(city, date)
        aq = self.aq_service.get_aq(city, date)
        activities = self.activity_repo.list_for_date(date)
        scored = []
        for a in activities:
            combined = {**forecast, **aq}
            s = self.score_activity(a, combined, user_profile)
            scored.append((s, a))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [a.to_dict() for _, a in scored[:limit]]
