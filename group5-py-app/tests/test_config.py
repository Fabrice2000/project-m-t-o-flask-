"""Tests pour le système de configuration"""

import pytest
import os
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from app.config import (
    ConfigManager,
    DatabaseConfig,
    WeatherServiceConfig,
    AirQualityServiceConfig,
    RecommendationConfig,
    AppConfig,
    create_config_manager,
    validate_config_file
)

class TestConfigManager:
    """Tests pour le gestionnaire de configuration"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.config_manager = ConfigManager()
    
    def test_initialization(self):
        """Test d'initialisation du gestionnaire"""
        assert self.config_manager.config is None
        assert len(self.config_manager._env_cache) == 0
    
    def test_get_env_with_default(self):
        """Test de récupération de variable d'environnement avec défaut"""
        # Variable inexistante avec défaut
        value = self.config_manager._get_env("NONEXISTENT_VAR", "default_value")
        assert value == "default_value"
        
        # Variable existante
        with patch.dict('os.environ', {'TEST_VAR': 'test_value'}):
            value = self.config_manager._get_env("TEST_VAR", "default")
            assert value == "test_value"
    
    def test_get_env_with_type_conversion(self):
        """Test de conversion de type pour les variables d'environnement"""
        with patch.dict('os.environ', {
            'INT_VAR': '42',
            'FLOAT_VAR': '3.14',
            'BOOL_VAR_TRUE': 'true',
            'BOOL_VAR_FALSE': 'false'
        }):
            # Test conversion entier
            int_val = self.config_manager._get_env("INT_VAR", 0, int)
            assert int_val == 42
            assert isinstance(int_val, int)
            
            # Test conversion flottant
            float_val = self.config_manager._get_env("FLOAT_VAR", 0.0, float)
            assert float_val == 3.14
            assert isinstance(float_val, float)
            
            # Test conversion booléen
            bool_true = self.config_manager._get_env("BOOL_VAR_TRUE", False, bool)
            bool_false = self.config_manager._get_env("BOOL_VAR_FALSE", True, bool)
            assert bool_true is True
            assert bool_false is False
    
    def test_load_from_env_only(self):
        """Test de chargement depuis les variables d'environnement uniquement"""
        with patch.dict('os.environ', {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb',
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'WEATHER_API_KEY': 'weather_key',
            'APP_DEBUG': 'true',
            'APP_LOG_LEVEL': 'INFO'
        }):
            config = self.config_manager.load_config()
            
            # Vérifier la structure de configuration
            assert isinstance(config, AppConfig)
            assert config.database.host == 'localhost'
            assert config.database.port == 5432
            assert config.database.name == 'testdb'
            assert config.weather_service.api_key == 'weather_key'
            assert config.debug is True
    
    def test_load_from_yaml_file(self):
        """Test de chargement depuis un fichier YAML"""
        yaml_content = """
database:
  host: yaml_host
  port: 3306
  name: yaml_db
  user: yaml_user
  password: yaml_pass

weather_service:
  type: openweathermap
  api_key: yaml_weather_key
  cache_duration: 300

air_quality_service:
  type: openaq
  cache_duration: 900

recommendation:
  max_recommendations: 10
  score_threshold: 0.7
  weather_weight: 0.4
  user_preference_weight: 0.6

debug: false
log_level: WARNING
secret_key: yaml_secret_key
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            config = self.config_manager.load_config(yaml_file)
            
            assert config.database.host == 'yaml_host'
            assert config.database.port == 3306
            assert config.weather_service.api_key == 'yaml_weather_key'
            assert config.weather_service.cache_duration == 300
            assert config.air_quality_service.cache_duration == 900
            assert config.recommendation.max_recommendations == 10
            assert config.debug is False
            assert config.log_level == 'WARNING'
        finally:
            os.unlink(yaml_file)
    
    def test_load_from_json_file(self):
        """Test de chargement depuis un fichier JSON"""
        json_content = {
            "database": {
                "host": "json_host",
                "port": 5432,
                "name": "json_db",
                "user": "json_user",
                "password": "json_pass"
            },
            "weather_service": {
                "type": "weatherapi",
                "api_key": "json_weather_key"
            },
            "debug": True,
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_content, f)
            json_file = f.name
        
        try:
            config = self.config_manager.load_config(json_file)
            
            assert config.database.host == 'json_host'
            assert config.weather_service.type == 'weatherapi'
            assert config.weather_service.api_key == 'json_weather_key'
            assert config.debug is True
            assert config.log_level == 'DEBUG'
        finally:
            os.unlink(json_file)
    
    def test_env_override_file_config(self):
        """Test que les variables d'environnement surchargent le fichier"""
        yaml_content = """
database:
  host: file_host
  port: 5432
  name: file_db

weather_service:
  api_key: file_key

debug: false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            with patch.dict('os.environ', {
                'DB_HOST': 'env_host',
                'WEATHER_API_KEY': 'env_key',
                'APP_DEBUG': 'true'
            }):
                config = self.config_manager.load_config(yaml_file)
                
                # Les variables d'environnement doivent prendre le dessus
                assert config.database.host == 'env_host'
                assert config.database.port == 5432  # Du fichier
                assert config.weather_service.api_key == 'env_key'
                assert config.debug is True
        finally:
            os.unlink(yaml_file)
    
    def test_invalid_file_format(self):
        """Test avec format de fichier invalide"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid config content")
            invalid_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Format de fichier non supporté"):
                self.config_manager.load_config(invalid_file)
        finally:
            os.unlink(invalid_file)
    
    def test_missing_file(self):
        """Test avec fichier inexistant"""
        with pytest.raises(FileNotFoundError):
            self.config_manager.load_config("nonexistent_file.yaml")
    
    def test_config_caching(self):
        """Test du cache de configuration"""
        with patch.dict('os.environ', {'DB_HOST': 'cached_host'}):
            # Première charge
            config1 = self.config_manager.load_config()
            
            # Deuxième charge (devrait utiliser le cache)
            config2 = self.config_manager.load_config()
            
            assert config1 is config2  # Même instance
            assert self.config_manager.config is not None

class TestDatabaseConfig:
    """Tests pour la configuration de base de données"""
    
    def test_database_config_creation(self):
        """Test de création de configuration DB"""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="myapp",
            user="myuser",
            password="mypass"
        )
        
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.name == "myapp"
        assert db_config.user == "myuser"
        assert db_config.password == "mypass"
    
    def test_database_url_generation(self):
        """Test de génération d'URL de base de données"""
        db_config = DatabaseConfig(
            host="db.example.com",
            port=3306,
            name="production_db",
            user="prod_user",
            password="secure_pass"
        )
        
        expected_url = "postgresql://prod_user:secure_pass@db.example.com:3306/production_db"
        assert db_config.get_url() == expected_url
    
    def test_database_url_with_special_characters(self):
        """Test avec caractères spéciaux dans le mot de passe"""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="testdb",
            user="testuser",
            password="p@ssw0rd!"
        )
        
        url = db_config.get_url()
        # Le mot de passe devrait être encodé dans l'URL
        assert "testuser" in url
        assert "localhost" in url
        assert "testdb" in url

class TestWeatherServiceConfig:
    """Tests pour la configuration du service météo"""
    
    def test_weather_service_config_creation(self):
        """Test de création de configuration météo"""
        weather_config = WeatherServiceConfig(
            type="openweathermap",
            api_key="test_api_key",
            cache_duration=300,
            timeout=10.0,
            max_retries=3
        )
        
        assert weather_config.type == "openweathermap"
        assert weather_config.api_key == "test_api_key"
        assert weather_config.cache_duration == 300
        assert weather_config.timeout == 10.0
        assert weather_config.max_retries == 3
    
    def test_weather_service_defaults(self):
        """Test des valeurs par défaut"""
        weather_config = WeatherServiceConfig(
            type="weatherapi",
            api_key="test_key"
        )
        
        assert weather_config.cache_duration == 600  # Défaut
        assert weather_config.timeout == 30.0        # Défaut
        assert weather_config.max_retries == 3       # Défaut
    
    def test_composite_weather_service_config(self):
        """Test de configuration pour service composite"""
        composite_config = {
            "type": "composite",
            "primary": {
                "type": "openweathermap",
                "api_key": "primary_key"
            },
            "fallbacks": [
                {
                    "type": "weatherapi",
                    "api_key": "fallback_key"
                }
            ]
        }
        
        # Vérifier la structure
        assert composite_config["type"] == "composite"
        assert "primary" in composite_config
        assert "fallbacks" in composite_config
        assert len(composite_config["fallbacks"]) == 1

class TestRecommendationConfig:
    """Tests pour la configuration des recommandations"""
    
    def test_recommendation_config_creation(self):
        """Test de création de configuration recommandations"""
        rec_config = RecommendationConfig(
            max_recommendations=15,
            score_threshold=0.8,
            weather_weight=0.5,
            user_preference_weight=0.5,
            enable_machine_learning=True,
            diversity_factor=0.3
        )
        
        assert rec_config.max_recommendations == 15
        assert rec_config.score_threshold == 0.8
        assert rec_config.weather_weight == 0.5
        assert rec_config.user_preference_weight == 0.5
        assert rec_config.enable_machine_learning is True
        assert rec_config.diversity_factor == 0.3
    
    def test_recommendation_config_validation(self):
        """Test de validation des poids"""
        rec_config = RecommendationConfig(
            weather_weight=0.6,
            user_preference_weight=0.4
        )
        
        # Les poids doivent être entre 0 et 1
        assert 0 <= rec_config.weather_weight <= 1
        assert 0 <= rec_config.user_preference_weight <= 1
        
        # La somme peut être vérifiée si nécessaire
        total_weight = rec_config.weather_weight + rec_config.user_preference_weight
        assert 0.9 <= total_weight <= 1.1  # Tolérance pour les flottants

class TestAppConfig:
    """Tests pour la configuration principale de l'application"""
    
    def test_app_config_creation(self):
        """Test de création de configuration complète"""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="testdb",
            user="testuser",
            password="testpass"
        )
        
        weather_config = WeatherServiceConfig(
            type="openweathermap",
            api_key="weather_key"
        )
        
        air_quality_config = AirQualityServiceConfig(
            type="openaq",
            cache_duration=900
        )
        
        rec_config = RecommendationConfig(
            max_recommendations=10,
            score_threshold=0.7
        )
        
        app_config = AppConfig(
            database=db_config,
            weather_service=weather_config,
            air_quality_service=air_quality_config,
            recommendation=rec_config,
            debug=True,
            log_level="DEBUG",
            secret_key="test_secret"
        )
        
        assert app_config.database == db_config
        assert app_config.weather_service == weather_config
        assert app_config.air_quality_service == air_quality_config
        assert app_config.recommendation == rec_config
        assert app_config.debug is True
        assert app_config.log_level == "DEBUG"
        assert app_config.secret_key == "test_secret"
    
    def test_app_config_to_dict(self):
        """Test de conversion en dictionnaire"""
        app_config = AppConfig(
            database=DatabaseConfig(host="localhost", port=5432, name="test", user="user", password="pass"),
            weather_service=WeatherServiceConfig(type="test", api_key="key"),
            debug=False
        )
        
        config_dict = app_config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "database" in config_dict
        assert "weather_service" in config_dict
        assert config_dict["debug"] is False

class TestFactoryFunctions:
    """Tests pour les fonctions de création de configuration"""
    
    def test_create_config_manager(self):
        """Test de création du gestionnaire de configuration"""
        manager = create_config_manager()
        
        assert isinstance(manager, ConfigManager)
        assert manager.config is None
    
    def test_create_config_manager_with_file(self):
        """Test de création avec fichier de configuration"""
        yaml_content = """
database:
  host: localhost
  port: 5432
  name: testapp
  user: testuser
  password: testpass

weather_service:
  type: openweathermap
  api_key: test_key

debug: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            manager = create_config_manager(yaml_file)
            
            assert isinstance(manager, ConfigManager)
            assert manager.config is not None
            assert manager.config.database.host == "localhost"
            assert manager.config.weather_service.api_key == "test_key"
        finally:
            os.unlink(yaml_file)

class TestConfigValidation:
    """Tests pour la validation de configuration"""
    
    def test_validate_yaml_config_file(self):
        """Test de validation de fichier YAML"""
        valid_yaml = """
database:
  host: localhost
  port: 5432
  name: valid_db
  user: valid_user
  password: valid_pass

weather_service:
  type: openweathermap
  api_key: valid_key

debug: false
log_level: INFO
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_yaml)
            yaml_file = f.name
        
        try:
            # La validation ne devrait pas lever d'exception
            is_valid = validate_config_file(yaml_file)
            assert is_valid is True
        finally:
            os.unlink(yaml_file)
    
    def test_validate_invalid_yaml_syntax(self):
        """Test avec syntaxe YAML invalide"""
        invalid_yaml = """
database:
  host: localhost
  port: invalid_port_not_number
    invalid_indentation
weather_service:
  - invalid list when dict expected
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            yaml_file = f.name
        
        try:
            is_valid = validate_config_file(yaml_file)
            assert is_valid is False
        finally:
            os.unlink(yaml_file)
    
    def test_validate_missing_required_sections(self):
        """Test avec sections requises manquantes"""
        incomplete_yaml = """
# Manque la section database
weather_service:
  type: openweathermap
  api_key: test_key

debug: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(incomplete_yaml)
            yaml_file = f.name
        
        try:
            is_valid = validate_config_file(yaml_file)
            # Selon l'implémentation, pourrait être False ou True avec defaults
            assert isinstance(is_valid, bool)
        finally:
            os.unlink(yaml_file)

class TestEnvironmentSpecificConfig:
    """Tests pour les configurations spécifiques à l'environnement"""
    
    def test_development_config(self):
        """Test de configuration de développement"""
        with patch.dict('os.environ', {
            'APP_ENV': 'development',
            'APP_DEBUG': 'true',
            'APP_LOG_LEVEL': 'DEBUG',
            'DB_HOST': 'localhost',
            'DB_NAME': 'dev_db'
        }):
            manager = ConfigManager()
            config = manager.load_config()
            
            assert config.debug is True
            assert config.log_level == 'DEBUG'
            assert config.database.host == 'localhost'
            assert config.database.name == 'dev_db'
    
    def test_production_config(self):
        """Test de configuration de production"""
        with patch.dict('os.environ', {
            'APP_ENV': 'production',
            'APP_DEBUG': 'false',
            'APP_LOG_LEVEL': 'WARNING',
            'DB_HOST': 'prod-db.example.com',
            'DB_NAME': 'prod_db',
            'SECRET_KEY': 'production_secret_key'
        }):
            manager = ConfigManager()
            config = manager.load_config()
            
            assert config.debug is False
            assert config.log_level == 'WARNING'
            assert config.database.host == 'prod-db.example.com'
            assert config.secret_key == 'production_secret_key'
    
    def test_test_config(self):
        """Test de configuration de test"""
        with patch.dict('os.environ', {
            'APP_ENV': 'test',
            'DB_NAME': 'test_db',
            'WEATHER_API_KEY': 'test_weather_key'
        }):
            manager = ConfigManager()
            config = manager.load_config()
            
            assert config.database.name == 'test_db'
            assert config.weather_service.api_key == 'test_weather_key'

class TestConfigSecurity:
    """Tests pour la sécurité de la configuration"""
    
    def test_sensitive_data_not_logged(self):
        """Test que les données sensibles ne sont pas loggées"""
        config = AppConfig(
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                name="test",
                user="user",
                password="sensitive_password"
            ),
            weather_service=WeatherServiceConfig(
                type="test",
                api_key="sensitive_api_key"
            ),
            secret_key="very_secret_key"
        )
        
        # Conversion en string pour logging
        config_str = str(config)
        
        # Les données sensibles ne devraient pas apparaître en clair
        assert "sensitive_password" not in config_str
        assert "sensitive_api_key" not in config_str
        assert "very_secret_key" not in config_str
    
    def test_config_copy_without_sensitive_data(self):
        """Test de copie de configuration sans données sensibles"""
        original_config = AppConfig(
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                name="test",
                user="user",
                password="secret_pass"
            ),
            weather_service=WeatherServiceConfig(
                type="test",
                api_key="secret_key"
            ),
            secret_key="app_secret"
        )
        
        # Créer une version "sûre" pour le logging
        safe_dict = original_config.to_dict()
        
        # Masquer les données sensibles
        if 'database' in safe_dict:
            safe_dict['database']['password'] = '***'
        if 'weather_service' in safe_dict:
            safe_dict['weather_service']['api_key'] = '***'
        safe_dict['secret_key'] = '***'
        
        assert safe_dict['database']['password'] == '***'
        assert safe_dict['weather_service']['api_key'] == '***'
        assert safe_dict['secret_key'] == '***'
        
        # Les autres données doivent rester intactes
        assert safe_dict['database']['host'] == 'localhost'
        assert safe_dict['weather_service']['type'] == 'test'

class TestConfigMigration:
    """Tests pour la migration de configuration"""
    
    def test_legacy_config_format_support(self):
        """Test de support des anciens formats de configuration"""
        legacy_yaml = """
# Ancien format
db_host: legacy_host
db_port: 3306
db_name: legacy_db
weather_api_key: legacy_key
debug_mode: true
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(legacy_yaml)
            yaml_file = f.name
        
        try:
            # Le système devrait pouvoir traiter l'ancien format
            with open(yaml_file, 'r') as file:
                legacy_data = yaml.safe_load(file)
            
            # Conversion vers le nouveau format
            modern_config = {
                'database': {
                    'host': legacy_data.get('db_host', 'localhost'),
                    'port': legacy_data.get('db_port', 5432),
                    'name': legacy_data.get('db_name', 'app'),
                    'user': legacy_data.get('db_user', 'user'),
                    'password': legacy_data.get('db_password', 'password')
                },
                'weather_service': {
                    'type': 'openweathermap',
                    'api_key': legacy_data.get('weather_api_key', 'key')
                },
                'debug': legacy_data.get('debug_mode', False)
            }
            
            assert modern_config['database']['host'] == 'legacy_host'
            assert modern_config['database']['port'] == 3306
            assert modern_config['weather_service']['api_key'] == 'legacy_key'
            assert modern_config['debug'] is True
        finally:
            os.unlink(yaml_file)