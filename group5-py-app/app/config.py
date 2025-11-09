"""
Module de configuration pour l'application météo-activités

Gère le chargement et la validation de la configuration depuis différents formats :
- Variables d'environnement
- Fichiers YAML
- Fichiers TOML
- Configuration par défaut

La configuration suit une hiérarchie :
1. Variables d'environnement (priorité maximale)
2. Fichier de configuration spécifié
3. Fichier config.yaml dans le répertoire courant
4. Fichier config.toml dans le répertoire courant
5. Configuration par défaut (priorité minimale)
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import json

# Import conditionnel des parseurs de configuration
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("PyYAML non disponible, support YAML désactivé")

try:
    import tomllib  # Python 3.11+
    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli as tomllib  # Fallback pour versions antérieures
        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False
        logging.warning("tomllib/tomli non disponible, support TOML désactivé")

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Exception levée en cas d'erreur de configuration"""
    pass

@dataclass
class DatabaseConfig:
    """Configuration de la base de données"""
    url: str = "sqlite:///meteo_activities.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class WeatherServiceConfig:
    """Configuration d'un service météorologique"""
    type: str = "openweathermap"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 10
    cache_duration: int = 600  # secondes
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class WeatherConfig:
    """Configuration des services météorologiques"""
    primary: WeatherServiceConfig = field(default_factory=WeatherServiceConfig)
    fallbacks: List[WeatherServiceConfig] = field(default_factory=list)
    composite_enabled: bool = True

@dataclass
class AirQualityConfig:
    """Configuration du service de qualité de l'air"""
    type: str = "openaq"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 15
    cache_duration: int = 1800  # secondes
    enabled: bool = True

@dataclass
class RecommendationConfig:
    """Configuration du système de recommandation"""
    max_results: int = 20
    cache_duration: int = 300  # secondes
    learning_enabled: bool = False
    learning_weight: float = 0.1
    diversification_enabled: bool = True
    
    # Poids des facteurs de recommandation
    weather_weight: float = 0.35
    preference_weight: float = 0.25
    availability_weight: float = 0.20
    time_weight: float = 0.15
    bonus_weight: float = 0.05

@dataclass
class VotingConfig:
    """Configuration du système de vote Condorcet"""
    tie_breaking_method: str = "margin"  # margin, copeland, borda
    min_votes_for_result: int = 3
    stability_analysis_enabled: bool = True
    cache_results: bool = True
    cache_duration: int = 1800

@dataclass
class LoggingConfig:
    """Configuration du système de logs"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    console_enabled: bool = True

@dataclass
class SecurityConfig:
    """Configuration de sécurité"""
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rate_limit_per_minute: int = 60
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

@dataclass
class APIConfig:
    """Configuration de l'API FastAPI"""
    title: str = "Météo Activités API"
    description: str = "API pour recommandations d'activités basées sur la météo"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False

@dataclass
class AppConfig:
    """Configuration principale de l'application"""
    # Configuration des composants
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    air_quality: AirQualityConfig = field(default_factory=AirQualityConfig)
    recommendation: RecommendationConfig = field(default_factory=RecommendationConfig)
    voting: VotingConfig = field(default_factory=VotingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    # Métadonnées
    environment: str = "development"
    timezone: str = "Europe/Paris"
    locale: str = "fr_FR"
    
    def __post_init__(self):
        """Validation post-initialisation"""
        self._validate_config()
    
    def _validate_config(self):
        """Valide la cohérence de la configuration"""
        # Validation des clés API requises
        if self.weather.primary.type == "openweathermap" and not self.weather.primary.api_key:
            logger.warning("Clé API OpenWeatherMap manquante")
        
        if self.weather.primary.type == "weatherapi" and not self.weather.primary.api_key:
            logger.warning("Clé API WeatherAPI manquante")
        
        # Validation des poids de recommandation
        total_weight = (
            self.recommendation.weather_weight +
            self.recommendation.preference_weight +
            self.recommendation.availability_weight +
            self.recommendation.time_weight +
            self.recommendation.bonus_weight
        )
        
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Somme des poids de recommandation != 1.0 (actuel: {total_weight})")
        
        # Validation du niveau de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level.upper() not in valid_log_levels:
            raise ConfigurationError(f"Niveau de log invalide: {self.logging.level}")
        
        # Validation de la méthode de départage des votes
        valid_tie_methods = ["margin", "copeland", "borda"]
        if self.voting.tie_breaking_method not in valid_tie_methods:
            raise ConfigurationError(f"Méthode de départage invalide: {self.voting.tie_breaking_method}")

class ConfigLoader:
    """Chargeur de configuration avec support multi-format"""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialise le chargeur de configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration (optionnel)
        """
        self.config_file = Path(config_file) if config_file else None
        self.env_prefix = "METEO_"
    
    def load(self) -> AppConfig:
        """
        Charge la configuration selon la hiérarchie définie
        
        Returns:
            Configuration de l'application
        """
        logger.info("Début du chargement de la configuration")
        
        # 1. Configuration par défaut
        config_dict = self._get_default_config()
        
        # 2. Fichier de configuration spécifié ou auto-détecté
        file_config = self._load_config_file()
        if file_config:
            config_dict = self._merge_configs(config_dict, file_config)
        
        # 3. Variables d'environnement (priorité maximale)
        env_config = self._load_env_config()
        config_dict = self._merge_configs(config_dict, env_config)
        
        # 4. Création de l'objet de configuration
        try:
            config = self._dict_to_config(config_dict)
            logger.info("Configuration chargée avec succès")
            return config
        except Exception as e:
            raise ConfigurationError(f"Erreur lors de la création de la configuration: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut"""
        return {
            "database": {
                "url": "sqlite:///meteo_activities.db",
                "echo": False
            },
            "weather": {
                "primary": {
                    "type": "openweathermap",
                    "cache_duration": 600
                },
                "fallbacks": [],
                "composite_enabled": True
            },
            "air_quality": {
                "type": "openaq",
                "cache_duration": 1800,
                "enabled": True
            },
            "recommendation": {
                "max_results": 20,
                "cache_duration": 300,
                "weather_weight": 0.35,
                "preference_weight": 0.25,
                "availability_weight": 0.20,
                "time_weight": 0.15,
                "bonus_weight": 0.05
            },
            "voting": {
                "tie_breaking_method": "margin",
                "min_votes_for_result": 3
            },
            "logging": {
                "level": "INFO",
                "console_enabled": True
            },
            "security": {
                "secret_key": "dev-secret-key-change-in-production",
                "rate_limit_per_minute": 60
            },
            "api": {
                "title": "Météo Activités API",
                "version": "1.0.0",
                "debug": False,
                "port": 8000
            },
            "environment": "development"
        }
    
    def _load_config_file(self) -> Optional[Dict[str, Any]]:
        """Charge la configuration depuis un fichier"""
        config_file = self.config_file
        
        # Auto-détection si pas de fichier spécifié
        if not config_file:
            for filename in ["config.yaml", "config.yml", "config.toml"]:
                candidate = Path(filename)
                if candidate.exists():
                    config_file = candidate
                    break
        
        if not config_file or not config_file.exists():
            logger.info("Aucun fichier de configuration trouvé")
            return None
        
        logger.info(f"Chargement du fichier de configuration: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    return self._load_yaml(f)
                elif config_file.suffix.lower() == '.toml':
                    return self._load_toml(f)
                else:
                    raise ConfigurationError(f"Format de fichier non supporté: {config_file.suffix}")
        
        except Exception as e:
            raise ConfigurationError(f"Erreur lors du chargement de {config_file}: {str(e)}")
    
    def _load_yaml(self, file_handle) -> Dict[str, Any]:
        """Charge un fichier YAML"""
        if not YAML_AVAILABLE:
            raise ConfigurationError("PyYAML requis pour les fichiers YAML")
        return yaml.safe_load(file_handle) or {}
    
    def _load_toml(self, file_handle) -> Dict[str, Any]:
        """Charge un fichier TOML"""
        if not TOML_AVAILABLE:
            raise ConfigurationError("tomllib/tomli requis pour les fichiers TOML")
        
        content = file_handle.read()
        if isinstance(content, str):
            content = content.encode('utf-8')
        return tomllib.loads(content.decode('utf-8'))
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis les variables d'environnement"""
        env_config = {}
        
        # Mapping des variables d'environnement vers la configuration
        env_mappings = {
            # Base de données
            f"{self.env_prefix}DATABASE_URL": ("database", "url"),
            f"{self.env_prefix}DATABASE_ECHO": ("database", "echo"),
            
            # Services météo
            f"{self.env_prefix}WEATHER_API_KEY": ("weather", "primary", "api_key"),
            f"{self.env_prefix}OPENWEATHER_API_KEY": ("weather", "primary", "api_key"),
            f"{self.env_prefix}WEATHER_API_TYPE": ("weather", "primary", "type"),
            
            # Qualité de l'air
            f"{self.env_prefix}AIR_QUALITY_ENABLED": ("air_quality", "enabled"),
            
            # API
            f"{self.env_prefix}API_DEBUG": ("api", "debug"),
            f"{self.env_prefix}API_PORT": ("api", "port"),
            f"{self.env_prefix}API_HOST": ("api", "host"),
            
            # Sécurité
            f"{self.env_prefix}SECRET_KEY": ("security", "secret_key"),
            
            # Logs
            f"{self.env_prefix}LOG_LEVEL": ("logging", "level"),
            f"{self.env_prefix}LOG_FILE": ("logging", "file_path"),
            
            # Environnement
            f"{self.env_prefix}ENVIRONMENT": ("environment",),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Conversion de type selon le contexte
                converted_value = self._convert_env_value(value, config_path)
                self._set_nested_value(env_config, config_path, converted_value)
        
        # Variables spéciales avec logique complexe
        self._handle_special_env_vars(env_config)
        
        if env_config:
            logger.info(f"Configuration chargée depuis {len(env_config)} variables d'environnement")
        
        return env_config
    
    def _convert_env_value(self, value: str, config_path: tuple) -> Any:
        """Convertit une valeur d'environnement vers le type approprié"""
        # Détection du type basée sur le chemin de configuration
        if any(keyword in config_path for keyword in ["port", "timeout", "size", "count", "minutes"]):
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Impossible de convertir '{value}' en entier pour {'.'.join(config_path)}")
                return value
        
        if any(keyword in config_path for keyword in ["weight", "delay", "expire"]):
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Impossible de convertir '{value}' en float pour {'.'.join(config_path)}")
                return value
        
        if any(keyword in config_path for keyword in ["enabled", "debug", "echo", "reload"]):
            return value.lower() in ("true", "1", "yes", "on")
        
        return value
    
    def _set_nested_value(self, config_dict: Dict[str, Any], path: tuple, value: Any):
        """Définit une valeur dans un dictionnaire imbriqué"""
        current = config_dict
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _handle_special_env_vars(self, env_config: Dict[str, Any]):
        """Gère les variables d'environnement avec logique spéciale"""
        # Fallback services météo depuis variables d'environnement
        weatherapi_key = os.getenv("WEATHER_API_KEY")
        if weatherapi_key:
            if "weather" not in env_config:
                env_config["weather"] = {}
            if "fallbacks" not in env_config["weather"]:
                env_config["weather"]["fallbacks"] = []
            
            env_config["weather"]["fallbacks"].append({
                "type": "weatherapi",
                "api_key": weatherapi_key
            })
        
        # CORS origins depuis variable d'environnement
        cors_origins = os.getenv(f"{self.env_prefix}CORS_ORIGINS")
        if cors_origins:
            origins_list = [origin.strip() for origin in cors_origins.split(",")]
            self._set_nested_value(env_config, ("security", "cors_origins"), origins_list)
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Fusionne deux configurations de manière récursive"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convertit un dictionnaire en objet AppConfig"""
        # Création des sous-configurations
        database_config = DatabaseConfig(**config_dict.get("database", {}))
        
        # Configuration météo avec gestion des fallbacks
        weather_data = config_dict.get("weather", {})
        primary_config = WeatherServiceConfig(**weather_data.get("primary", {}))
        
        fallback_configs = []
        for fallback_data in weather_data.get("fallbacks", []):
            fallback_configs.append(WeatherServiceConfig(**fallback_data))
        
        weather_config = WeatherConfig(
            primary=primary_config,
            fallbacks=fallback_configs,
            composite_enabled=weather_data.get("composite_enabled", True)
        )
        
        # Autres configurations
        air_quality_config = AirQualityConfig(**config_dict.get("air_quality", {}))
        recommendation_config = RecommendationConfig(**config_dict.get("recommendation", {}))
        voting_config = VotingConfig(**config_dict.get("voting", {}))
        logging_config = LoggingConfig(**config_dict.get("logging", {}))
        security_config = SecurityConfig(**config_dict.get("security", {}))
        api_config = APIConfig(**config_dict.get("api", {}))
        
        # Configuration principale
        return AppConfig(
            database=database_config,
            weather=weather_config,
            air_quality=air_quality_config,
            recommendation=recommendation_config,
            voting=voting_config,
            logging=logging_config,
            security=security_config,
            api=api_config,
            environment=config_dict.get("environment", "development"),
            timezone=config_dict.get("timezone", "Europe/Paris"),
            locale=config_dict.get("locale", "fr_FR")
        )

# Instance globale de configuration
_config: Optional[AppConfig] = None

def get_config(config_file: Optional[Union[str, Path]] = None, force_reload: bool = False) -> AppConfig:
    """
    Obtient l'instance de configuration globale
    
    Args:
        config_file: Fichier de configuration à charger (optionnel)
        force_reload: Force le rechargement de la configuration
        
    Returns:
        Configuration de l'application
    """
    global _config
    
    if _config is None or force_reload:
        loader = ConfigLoader(config_file)
        _config = loader.load()
    
    return _config

def setup_logging(logging_config: LoggingConfig):
    """
    Configure le système de logging selon la configuration
    
    Args:
        logging_config: Configuration du logging
    """
    import logging.handlers
    
    # Configuration du niveau de log
    level = getattr(logging, logging_config.level.upper())
    
    # Configuration du formateur
    formatter = logging.Formatter(logging_config.format)
    
    # Logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Suppression des handlers existants
    root_logger.handlers.clear()
    
    # Handler console
    if logging_config.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)
    
    # Handler fichier avec rotation
    if logging_config.file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            logging_config.file_path,
            maxBytes=logging_config.max_file_size,
            backupCount=logging_config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    logger.info(f"Logging configuré - Niveau: {logging_config.level}")

def create_sample_config_files():
    """Crée des exemples de fichiers de configuration"""
    
    # Configuration YAML d'exemple
    yaml_content = """
# Configuration de l'application Météo Activités

database:
  url: "sqlite:///meteo_activities.db"
  echo: false
  pool_size: 5

weather:
  primary:
    type: "openweathermap"
    api_key: "your-openweather-api-key"
    cache_duration: 600
  fallbacks:
    - type: "weatherapi"
      api_key: "your-weatherapi-key"
      cache_duration: 600
  composite_enabled: true

air_quality:
  type: "openaq"
  cache_duration: 1800
  enabled: true

recommendation:
  max_results: 20
  cache_duration: 300
  learning_enabled: false
  weather_weight: 0.35
  preference_weight: 0.25
  availability_weight: 0.20
  time_weight: 0.15
  bonus_weight: 0.05

voting:
  tie_breaking_method: "margin"
  min_votes_for_result: 3
  stability_analysis_enabled: true

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "logs/meteo_app.log"
  console_enabled: true

security:
  secret_key: "your-secret-key-here"
  rate_limit_per_minute: 60
  cors_enabled: true
  cors_origins: ["*"]

api:
  title: "Météo Activités API"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 8000

environment: "development"
timezone: "Europe/Paris"
locale: "fr_FR"
"""
    
    # Configuration TOML d'exemple
    toml_content = """
# Configuration de l'application Météo Activités

environment = "development"
timezone = "Europe/Paris"
locale = "fr_FR"

[database]
url = "sqlite:///meteo_activities.db"
echo = false
pool_size = 5

[weather.primary]
type = "openweathermap"
api_key = "your-openweather-api-key"
cache_duration = 600

[[weather.fallbacks]]
type = "weatherapi"
api_key = "your-weatherapi-key"
cache_duration = 600

[weather]
composite_enabled = true

[air_quality]
type = "openaq"
cache_duration = 1800
enabled = true

[recommendation]
max_results = 20
cache_duration = 300
learning_enabled = false
weather_weight = 0.35
preference_weight = 0.25
availability_weight = 0.20
time_weight = 0.15
bonus_weight = 0.05

[voting]
tie_breaking_method = "margin"
min_votes_for_result = 3
stability_analysis_enabled = true

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file_path = "logs/meteo_app.log"
console_enabled = true

[security]
secret_key = "your-secret-key-here"
rate_limit_per_minute = 60
cors_enabled = true
cors_origins = ["*"]

[api]
title = "Météo Activités API"
version = "1.0.0"
debug = false
host = "0.0.0.0"
port = 8000
"""
    
    # Écriture des fichiers d'exemple
    try:
        if YAML_AVAILABLE:
            with open("config.example.yaml", "w", encoding="utf-8") as f:
                f.write(yaml_content)
            logger.info("Fichier config.example.yaml créé")
        
        if TOML_AVAILABLE:
            with open("config.example.toml", "w", encoding="utf-8") as f:
                f.write(toml_content)
            logger.info("Fichier config.example.toml créé")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des fichiers d'exemple: {str(e)}")

if __name__ == "__main__":
    # Création des fichiers d'exemple si le script est exécuté directement
    print("Création des fichiers de configuration d'exemple...")
    create_sample_config_files()
    
    # Test de chargement de configuration
    print("Test de chargement de configuration...")
    try:
        config = get_config()
        print(f"Configuration chargée - Environnement: {config.environment}")
        print(f"Service météo principal: {config.weather.primary.type}")
        print(f"Port API: {config.api.port}")
    except Exception as e:
        print(f"Erreur: {str(e)}")