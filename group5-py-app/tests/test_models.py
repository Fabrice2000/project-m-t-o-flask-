"""Tests simplifiés pour les modèles de données"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from app.models import (
    User, UserProfile, Activity, Vote, 
    WeatherForecast, ActivityInstance,
    WeatherConditions, ActivityType, WeatherSensitivity, UserRole
)

class TestUser:
    """Tests pour le modèle User"""
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        user = User()
        user.name = "Test User"
        user.email = "test@example.com"
        user.role = UserRole.USER
        user.is_active = True  # Définir explicitement
        
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True

    def test_user_with_admin_role(self):
        """Test de création d'un utilisateur admin"""
        admin = User(
            name="Admin User",
            email="admin@example.com",
            role=UserRole.ADMIN
        )
        
        assert admin.role == UserRole.ADMIN

class TestUserProfile:
    """Tests pour le modèle UserProfile"""
    
    def test_user_profile_creation(self):
        """Test de création d'un profil utilisateur"""
        profile = UserProfile(
            user_id=1,
            outdoor_preference=0.7,
            temperature_min=10.0,
            temperature_max=25.0
        )
        
        assert profile.user_id == 1
        assert profile.outdoor_preference == 0.7
        assert profile.temperature_min == 10.0
        assert profile.temperature_max == 25.0

class TestActivity:
    """Tests pour le modèle Activity"""
    
    def test_activity_creation(self):
        """Test de création d'une activité"""
        activity = Activity(
            title="Randonnée",
            description="Activité de plein air",
            category="Sport",
            activity_type=ActivityType.OUTDOOR,
            weather_sensitivity=WeatherSensitivity.HIGH
        )
        
        assert activity.title == "Randonnée"
        assert activity.category == "Sport"
        assert activity.activity_type == ActivityType.OUTDOOR
        assert activity.weather_sensitivity == WeatherSensitivity.HIGH

    def test_indoor_activity(self):
        """Test de création d'une activité intérieure"""
        activity = Activity(
            title="Cinéma",
            description="Regarder un film",
            category="Culture",
            activity_type=ActivityType.INDOOR,
            weather_sensitivity=WeatherSensitivity.NONE
        )
        
        assert activity.activity_type == ActivityType.INDOOR
        assert activity.weather_sensitivity == WeatherSensitivity.NONE

class TestVote:
    """Tests pour le modèle Vote"""
    
    def test_vote_creation(self):
        """Test de création d'un vote"""
        vote = Vote(
            user_id=1,
            activity_ranking=[1, 2, 3]
        )
        
        assert vote.user_id == 1
        assert vote.activity_ranking == [1, 2, 3]

class TestWeatherConditions:
    """Tests pour la classe WeatherConditions"""
    
    def test_weather_conditions_creation(self):
        """Test de création de conditions météorologiques"""
        weather = WeatherConditions(
            temperature=20.5,
            humidity=65.0,
            precipitation=0.0,
            wind_speed=5.2,
            description="Ensoleillé",
            feels_like=22.0
        )
        
        assert weather.temperature == 20.5
        assert weather.humidity == 65.0
        assert weather.precipitation == 0.0
        assert weather.wind_speed == 5.2
        assert weather.description == "Ensoleillé"
        assert weather.feels_like == 22.0
        assert weather.air_quality_index is None

    def test_weather_conditions_with_aqi(self):
        """Test avec indice de qualité de l'air"""
        weather = WeatherConditions(
            temperature=18.0,
            humidity=70.0,
            precipitation=2.5,
            wind_speed=10.0,
            description="Pluvieux",
            feels_like=16.0,
            air_quality_index=85
        )
        
        assert weather.air_quality_index == 85

class TestWeatherForecast:
    """Tests pour le modèle WeatherForecast"""
    
    def test_weather_forecast_creation(self):
        """Test de création d'une prévision météo"""
        forecast = WeatherForecast()
        forecast.city = "Paris"
        forecast.country = "FR"
        forecast.forecast_date = datetime(2025, 11, 9)
        forecast.temperature = 15.0
        forecast.humidity = 80.0
        forecast.precipitation = 0.6
        
        assert forecast.city == "Paris"
        assert forecast.country == "FR"
        assert forecast.temperature == 15.0
        assert forecast.humidity == 80.0
        assert forecast.precipitation == 0.6

class TestActivityInstance:
    """Tests pour le modèle ActivityInstance"""
    
    def test_activity_instance_creation(self):
        """Test de création d'une instance d'activité"""
        instance = ActivityInstance()
        instance.activity_id = 1
        instance.start_datetime = datetime(2025, 11, 10, 14, 0)
        instance.end_datetime = datetime(2025, 11, 10, 16, 0)
        instance.location_name = "Parc de la Villette"
        
        assert instance.activity_id == 1
        assert instance.location_name == "Parc de la Villette"
        assert instance.start_datetime.hour == 14

class TestEnums:
    """Tests pour les énumérations"""
    
    def test_activity_type_enum(self):
        """Test de l'énumération ActivityType"""
        assert ActivityType.INDOOR.value == "indoor"
        assert ActivityType.OUTDOOR.value == "outdoor"
        assert ActivityType.MIXED.value == "mixed"
    
    def test_weather_sensitivity_enum(self):
        """Test de l'énumération WeatherSensitivity"""
        assert WeatherSensitivity.NONE.value == "none"
        assert WeatherSensitivity.LOW.value == "low"
        assert WeatherSensitivity.MEDIUM.value == "medium"
        assert WeatherSensitivity.HIGH.value == "high"
    
    def test_user_role_enum(self):
        """Test de l'énumération UserRole"""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MODERATOR.value == "moderator"