from abc import ABC, abstractmethod
import requests
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
import json
import time

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Structure standardisée des données météorologiques"""
    temperature: float
    feels_like: float
    humidity: float
    precipitation: float  # en mm
    wind_speed: float     # en km/h
    wind_direction: int   # en degrés
    pressure: float       # en hPa
    visibility: float     # en km
    description: str
    timestamp: datetime
    source: str

@dataclass
class AirQualityData:
    """Structure des données de qualité de l'air"""
    aqi: int              # Index qualité de l'air (0-500)
    pm25: Optional[float] # PM2.5 en μg/m³
    pm10: Optional[float] # PM10 en μg/m³
    o3: Optional[float]   # Ozone en μg/m³
    no2: Optional[float]  # NO2 en μg/m³
    so2: Optional[float]  # SO2 en μg/m³
    co: Optional[float]   # CO en mg/m³
    timestamp: datetime
    source: str

class WeatherServiceException(Exception):
    """Exception levée en cas d'erreur dans les services météo"""
    def __init__(self, message: str, service_name: str, status_code: Optional[int] = None):
        self.message = message
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(f"[{service_name}] {message}")

class AirQualityServiceException(Exception):
    """Exception levée en cas d'erreur dans les services de qualité de l'air"""
    def __init__(self, message: str, service_name: str, status_code: Optional[int] = None):
        self.message = message
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(f"[{service_name}] {message}")

class WeatherServiceInterface(ABC):
    """Interface pour les services météorologiques"""
    
    @abstractmethod
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> WeatherData:
        """Récupère la météo actuelle pour une ville"""
        pass

    @abstractmethod
    def get_forecast(self, city: str, days: int = 5, country_code: Optional[str] = None) -> List[WeatherData]:
        """Récupère les prévisions météorologiques pour plusieurs jours"""
        pass

    @abstractmethod
    def get_weather_for_date(self, city: str, target_date: datetime, country_code: Optional[str] = None) -> WeatherData:
        """Récupère la météo pour une date spécifique"""
        pass

class AirQualityServiceInterface(ABC):
    """Interface pour les services de qualité de l'air"""
    
    @abstractmethod
    def get_current_air_quality(self, city: str, country_code: Optional[str] = None) -> AirQualityData:
        """Récupère la qualité de l'air actuelle"""
        pass

    @abstractmethod
    def get_air_quality_forecast(self, city: str, days: int = 3, country_code: Optional[str] = None) -> List[AirQualityData]:
        """Récupère les prévisions de qualité de l'air"""
        pass

class OpenWeatherMapService(WeatherServiceInterface):
    """Service météorologique utilisant l'API OpenWeatherMap"""
    
    def __init__(self, api_key: str, cache_duration: int = 600):
        """
        Initialise le service OpenWeatherMap
        
        Args:
            api_key: Clé API OpenWeatherMap
            cache_duration: Durée de cache en secondes (défaut: 10 minutes)
        """
        if not api_key:
            raise ValueError("La clé API OpenWeatherMap est requise")
        
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache_duration = cache_duration
        self._cache = {}  # Cache simple en mémoire
        
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Effectue une requête à l'API avec gestion d'erreurs"""
        params.update({
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr"
        })
        
        url = f"{self.base_url}/{endpoint}"
        cache_key = f"{url}_{hash(str(sorted(params.items())))}"
        
        # Vérification du cache
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                logger.debug(f"Données récupérées du cache pour {endpoint}")
                return cached_data
        
        try:
            logger.info(f"Requête API OpenWeatherMap: {endpoint}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Vérification des erreurs de l'API
            if "cod" in data and str(data["cod"]) != "200":
                raise WeatherServiceException(
                    data.get("message", "Erreur inconnue de l'API"), 
                    "OpenWeatherMap",
                    data.get("cod")
                )
            
            # Mise en cache
            self._cache[cache_key] = (data, time.time())
            return data
            
        except requests.exceptions.RequestException as e:
            raise WeatherServiceException(
                f"Erreur de communication avec l'API: {str(e)}", 
                "OpenWeatherMap"
            )
        except json.JSONDecodeError as e:
            raise WeatherServiceException(
                f"Erreur de décodage JSON: {str(e)}", 
                "OpenWeatherMap"
            )

    def _parse_weather_data(self, weather_json: Dict, source_timestamp: Optional[datetime] = None) -> WeatherData:
        """Parse les données météo depuis la réponse JSON"""
        main = weather_json["main"]
        wind = weather_json.get("wind", {})
        weather = weather_json["weather"][0] if weather_json.get("weather") else {}
        
        # Conversion du timestamp Unix vers datetime
        timestamp = source_timestamp or datetime.fromtimestamp(weather_json.get("dt", time.time()))
        
        return WeatherData(
            temperature=main["temp"],
            feels_like=main.get("feels_like", main["temp"]),
            humidity=main["humidity"],
            precipitation=weather_json.get("rain", {}).get("1h", 0) + weather_json.get("snow", {}).get("1h", 0),
            wind_speed=wind.get("speed", 0) * 3.6,  # conversion m/s vers km/h
            wind_direction=wind.get("deg", 0),
            pressure=main.get("pressure", 1013),
            visibility=weather_json.get("visibility", 10000) / 1000,  # conversion m vers km
            description=weather.get("description", ""),
            timestamp=timestamp,
            source="OpenWeatherMap"
        )

    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> WeatherData:
        """Récupère la météo actuelle"""
        query = f"{city},{country_code}" if country_code else city
        params = {"q": query}
        
        data = self._make_request("weather", params)
        return self._parse_weather_data(data)

    def get_forecast(self, city: str, days: int = 5, country_code: Optional[str] = None) -> List[WeatherData]:
        """Récupère les prévisions météorologiques"""
        if days > 5:
            logger.warning("OpenWeatherMap API gratuite limitée à 5 jours, réduction automatique")
            days = 5
        
        query = f"{city},{country_code}" if country_code else city
        params = {"q": query}
        
        data = self._make_request("forecast", params)
        
        forecasts = []
        for item in data["list"][:days * 8]:  # 8 prévisions par jour (toutes les 3h)
            forecasts.append(self._parse_weather_data(item))
        
        return forecasts

    def get_weather_for_date(self, city: str, target_date: datetime, country_code: Optional[str] = None) -> WeatherData:
        """Récupère la météo pour une date spécifique"""
        # Pour les dates futures, utilise les prévisions
        if target_date.date() >= datetime.now().date():
            forecasts = self.get_forecast(city, days=5, country_code=country_code)
            
            # Trouve la prévision la plus proche de la date cible
            target_day = target_date.date()
            for forecast in forecasts:
                if forecast.timestamp.date() == target_day:
                    return forecast
            
            # Si pas de correspondance exacte, prend la plus proche
            if forecasts:
                return min(forecasts, key=lambda f: abs((f.timestamp.date() - target_day).days))
        
        # Pour les dates passées, retourne la météo actuelle (limitation API gratuite)
        logger.warning("Données historiques non disponibles avec l'API gratuite OpenWeatherMap")
        return self.get_current_weather(city, country_code)

class WeatherAPIService(WeatherServiceInterface):
    """Service météorologique alternatif utilisant WeatherAPI.com"""
    
    def __init__(self, api_key: str, cache_duration: int = 600):
        if not api_key:
            raise ValueError("La clé API WeatherAPI est requise")
        
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
        self.cache_duration = cache_duration
        self._cache = {}

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Effectue une requête à l'API WeatherAPI"""
        params.update({"key": self.api_key})
        
        url = f"{self.base_url}/{endpoint}"
        cache_key = f"{url}_{hash(str(sorted(params.items())))}"
        
        # Vérification du cache
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise WeatherServiceException(
                    data["error"].get("message", "Erreur inconnue"),
                    "WeatherAPI",
                    data["error"].get("code")
                )
            
            self._cache[cache_key] = (data, time.time())
            return data
            
        except requests.exceptions.RequestException as e:
            raise WeatherServiceException(f"Erreur de communication: {str(e)}", "WeatherAPI")

    def _parse_weather_data(self, weather_json: Dict, timestamp: Optional[datetime] = None) -> WeatherData:
        """Parse les données météo depuis WeatherAPI"""
        current = weather_json.get("current", weather_json)
        condition = current.get("condition", {})
        
        return WeatherData(
            temperature=current["temp_c"],
            feels_like=current.get("feelslike_c", current["temp_c"]),
            humidity=current["humidity"],
            precipitation=current.get("precip_mm", 0),
            wind_speed=current["wind_kph"],
            wind_direction=current.get("wind_degree", 0),
            pressure=current.get("pressure_mb", 1013),
            visibility=current.get("vis_km", 10),
            description=condition.get("text", ""),
            timestamp=timestamp or datetime.now(),
            source="WeatherAPI"
        )

    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> WeatherData:
        query = f"{city},{country_code}" if country_code else city
        data = self._make_request("current.json", {"q": query})
        return self._parse_weather_data(data)

    def get_forecast(self, city: str, days: int = 5, country_code: Optional[str] = None) -> List[WeatherData]:
        if days > 10:
            days = 10  # Limite de l'API gratuite
        
        query = f"{city},{country_code}" if country_code else city
        data = self._make_request("forecast.json", {"q": query, "days": days})
        
        forecasts = []
        for day in data["forecast"]["forecastday"]:
            for hour in day["hour"]:
                timestamp = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
                forecasts.append(self._parse_weather_data({"current": hour}, timestamp))
        
        return forecasts

    def get_weather_for_date(self, city: str, target_date: datetime, country_code: Optional[str] = None) -> WeatherData:
        # WeatherAPI permet les données historiques avec un abonnement payant
        query = f"{city},{country_code}" if country_code else city
        date_str = target_date.strftime("%Y-%m-%d")
        
        try:
            data = self._make_request("history.json", {"q": query, "dt": date_str})
            day_data = data["forecast"]["forecastday"][0]
            return self._parse_weather_data({"current": day_data["day"]}, target_date)
        except WeatherServiceException:
            # Fallback vers les prévisions si l'historique n'est pas disponible
            return self.get_forecast(city, days=1, country_code=country_code)[0]

class CompositeWeatherService(WeatherServiceInterface):
    """Service météo composite utilisant plusieurs sources avec fallback"""
    
    def __init__(self, primary_service: WeatherServiceInterface, 
                 fallback_services: List[WeatherServiceInterface]):
        self.primary_service = primary_service
        self.fallback_services = fallback_services
        self.service_failures = {}  # Suivi des échecs par service
    
    def _try_service(self, service: WeatherServiceInterface, method_name: str, *args, **kwargs):
        """Tente d'exécuter une méthode sur un service avec gestion d'erreurs"""
        service_name = service.__class__.__name__
        
        try:
            method = getattr(service, method_name)
            result = method(*args, **kwargs)
            
            # Réinitialise le compteur d'échecs en cas de succès
            if service_name in self.service_failures:
                del self.service_failures[service_name]
            
            logger.info(f"Succès avec le service {service_name}")
            return result
            
        except (WeatherServiceException, Exception) as e:
            # Incrémente le compteur d'échecs
            self.service_failures[service_name] = self.service_failures.get(service_name, 0) + 1
            logger.warning(f"Échec du service {service_name}: {str(e)}")
            raise

    def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """Exécute une méthode avec fallback automatique"""
        services = [self.primary_service] + self.fallback_services
        last_exception = None
        
        for service in services:
            try:
                return self._try_service(service, method_name, *args, **kwargs)
            except Exception as e:
                last_exception = e
                continue
        
        # Tous les services ont échoué
        raise WeatherServiceException(
            f"Tous les services météo ont échoué. Dernière erreur: {str(last_exception)}",
            "CompositeWeatherService"
        )

    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> WeatherData:
        return self._execute_with_fallback("get_current_weather", city, country_code)

    def get_forecast(self, city: str, days: int = 5, country_code: Optional[str] = None) -> List[WeatherData]:
        return self._execute_with_fallback("get_forecast", city, days, country_code)

    def get_weather_for_date(self, city: str, target_date: datetime, country_code: Optional[str] = None) -> WeatherData:
        return self._execute_with_fallback("get_weather_for_date", city, target_date, country_code)

class OpenAQAirQualityService(AirQualityServiceInterface):
    """Service de qualité de l'air utilisant l'API OpenAQ"""
    
    def __init__(self, cache_duration: int = 1800):  # Cache de 30 minutes
        self.base_url = "https://api.openaq.org/v3"
        self.cache_duration = cache_duration
        self._cache = {}

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Effectue une requête à l'API OpenAQ"""
        url = f"{self.base_url}/{endpoint}"
        cache_key = f"{url}_{hash(str(sorted(params.items())))}"
        
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._cache[cache_key] = (data, time.time())
            return data
            
        except requests.exceptions.RequestException as e:
            raise AirQualityServiceException(f"Erreur de communication: {str(e)}", "OpenAQ")

    def get_current_air_quality(self, city: str, country_code: Optional[str] = None) -> AirQualityData:
        """Récupère la qualité de l'air actuelle pour une ville"""
        params = {
            "city": city,
            "limit": 100,
            "sort": "desc",
            "order_by": "datetime"
        }
        
        if country_code:
            params["countries"] = country_code  # v3 utilise "countries" au pluriel
        
        data = self._make_request("measurements", params)
        
        if not data.get("results"):
            raise AirQualityServiceException(
                f"Aucune donnée de qualité de l'air trouvée pour {city}",
                "OpenAQ"
            )
        
        # Agrège les mesures récentes par polluant
        measurements = {}
        latest_time = None
        
        for result in data["results"]:
            parameter = result["parameter"]
            value = result["value"]
            timestamp = datetime.fromisoformat(result["date"]["utc"].replace("Z", "+00:00"))
            
            if parameter not in measurements or timestamp > measurements[parameter]["timestamp"]:
                measurements[parameter] = {"value": value, "timestamp": timestamp}
                if not latest_time or timestamp > latest_time:
                    latest_time = timestamp
        
        # Calcul d'un AQI simplifié basé sur PM2.5
        pm25 = measurements.get("pm25", {}).get("value")
        aqi = self._calculate_simple_aqi(pm25) if pm25 else 50  # valeur par défaut
        
        return AirQualityData(
            aqi=aqi,
            pm25=measurements.get("pm25", {}).get("value"),
            pm10=measurements.get("pm10", {}).get("value"),
            o3=measurements.get("o3", {}).get("value"),
            no2=measurements.get("no2", {}).get("value"),
            so2=measurements.get("so2", {}).get("value"),
            co=measurements.get("co", {}).get("value"),
            timestamp=latest_time or datetime.now(),
            source="OpenAQ"
        )

    def _calculate_simple_aqi(self, pm25: float) -> int:
        """Calcule un AQI simplifié basé sur les valeurs PM2.5"""
        if pm25 <= 12:
            return int(pm25 * 50 / 12)
        elif pm25 <= 35.4:
            return int(50 + (pm25 - 12) * 50 / (35.4 - 12))
        elif pm25 <= 55.4:
            return int(100 + (pm25 - 35.4) * 50 / (55.4 - 35.4))
        elif pm25 <= 150.4:
            return int(150 + (pm25 - 55.4) * 100 / (150.4 - 55.4))
        elif pm25 <= 250.4:
            return int(200 + (pm25 - 150.4) * 100 / (250.4 - 150.4))
        else:
            return min(int(300 + (pm25 - 250.4) * 200 / (500.4 - 250.4)), 500)

    def get_air_quality_forecast(self, city: str, days: int = 3, country_code: Optional[str] = None) -> List[AirQualityData]:
        """OpenAQ ne fournit pas de prévisions, retourne les données actuelles"""
        current = self.get_current_air_quality(city, country_code)
        return [current]  # Limitation de l'API gratuite

def create_weather_service(config: Dict) -> WeatherServiceInterface:
    """Factory pour créer un service météo selon la configuration"""
    service_type = config.get("type", "openweathermap").lower()
    
    if service_type == "openweathermap":
        # Accept both OPENWEATHER_API_KEY and a generic WEATHER_API_KEY as fallback
        api_key = config.get("api_key") or os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
        if not api_key:
            raise ValueError("Clé API OpenWeatherMap requise")
        return OpenWeatherMapService(api_key, config.get("cache_duration", 600))
    
    elif service_type == "weatherapi":
        # WeatherAPI should accept its dedicated env var, but allow OPENWEATHER_API_KEY
        api_key = config.get("api_key") or os.getenv("WEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise ValueError("Clé API WeatherAPI requise")
        return WeatherAPIService(api_key, config.get("cache_duration", 600))
    
    elif service_type == "composite":
        primary_config = config.get("primary", {"type": "openweathermap"})
        fallback_configs = config.get("fallbacks", [])
        
        primary = create_weather_service(primary_config)
        fallbacks = [create_weather_service(fb_config) for fb_config in fallback_configs]
        
        return CompositeWeatherService(primary, fallbacks)
    
    else:
        raise ValueError(f"Type de service météo non supporté: {service_type}")

def create_air_quality_service(config: Dict) -> AirQualityServiceInterface:
    """Factory pour créer un service de qualité de l'air"""
    service_type = config.get("type", "openaq").lower()
    
    if service_type == "openaq":
        return OpenAQAirQualityService(config.get("cache_duration", 1800))
    
    else:
        raise ValueError(f"Type de service qualité de l'air non supporté: {service_type}")
