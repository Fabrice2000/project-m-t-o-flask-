"""Tests simplifiés pour le système de configuration"""

import pytest
import os
from unittest.mock import patch

from app.config import (
    ConfigLoader,
    DatabaseConfig,
    WeatherServiceConfig,
    AirQualityConfig,
    RecommendationConfig,
    AppConfig,
    get_config
)

class TestConfigLoaderSimple:
    """Tests simplifiés pour le chargeur de configuration"""
    
    def test_config_loader_initialization(self):
        """Test d'initialisation du chargeur"""
        loader = ConfigLoader()
        assert loader.config_file is None
        assert loader.env_prefix == "METEO_"
    
    def test_load_default_config(self):
        """Test de chargement de la configuration par défaut"""
        loader = ConfigLoader()
        config = loader.load()
        
        assert isinstance(config, AppConfig)
        assert config.environment == "development"
        assert config.api.port == 8000
    
    def test_get_config_function(self):
        """Test de la fonction get_config"""
        config = get_config()
        assert isinstance(config, AppConfig)
        
    def test_database_config(self):
        """Test de la configuration de base de données"""
        db_config = DatabaseConfig()
        assert "sqlite" in db_config.url
        assert db_config.echo is False
    
    def test_weather_service_config(self):
        """Test de la configuration du service météo"""
        weather_config = WeatherServiceConfig()
        assert weather_config.type == "openweathermap"
        assert weather_config.timeout == 10
    
    def test_air_quality_config(self):
        """Test de la configuration de qualité de l'air"""
        air_config = AirQualityConfig()
        assert air_config.type == "openaq"
        assert air_config.enabled is True
    
    def test_recommendation_config(self):
        """Test de la configuration des recommandations"""
        rec_config = RecommendationConfig()
        assert rec_config.max_results == 20
        assert rec_config.weather_weight == 0.35
    
    @patch.dict('os.environ', {'METEO_DATABASE_URL': 'postgresql://test'})
    def test_environment_override(self):
        """Test de surcharge par variables d'environnement"""
        loader = ConfigLoader()
        config = loader.load()
        assert config.database.url == 'postgresql://test'

class TestAppConfig:
    """Tests pour la configuration principale"""
    
    def test_app_config_creation(self):
        """Test de création d'une configuration d'application"""
        config = AppConfig()
        
        assert config.environment == "development"
        assert config.timezone == "Europe/Paris"
        assert config.locale == "fr_FR"
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.recommendation, RecommendationConfig)
    
    def test_config_validation(self):
        """Test de validation de la configuration"""
        config = AppConfig()
        # La validation se fait automatiquement dans __post_init__
        # Si pas d'exception, la validation a réussi
        assert config is not None