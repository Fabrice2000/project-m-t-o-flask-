from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
import os

from app.services import (
    create_weather_service, 
    create_air_quality_service,
    WeatherServiceException,
    AirQualityServiceException
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["weather"])

# Configuration par défaut des services (devrait venir d'un fichier de config)
DEFAULT_WEATHER_CONFIG = {
    "type": "composite",
    "primary": {
        "type": "openweathermap",
        # Autorise le fallback vers WEATHER_API_KEY si OPENWEATHER_API_KEY n'est pas défini
        "api_key": os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY"),
        "cache_duration": 600
    },
    "fallbacks": [
        {
            "type": "weatherapi",
            "api_key": os.getenv("WEATHER_API_KEY"),
            "cache_duration": 600
        }
    ]
}

DEFAULT_AIR_QUALITY_CONFIG = {
    "type": "openaq",
    "cache_duration": 1800
}

def get_weather_service():
    """Fournit le service météorologique configuré"""
    try:
        return create_weather_service(DEFAULT_WEATHER_CONFIG)
    except Exception as e:
        logger.error(f"Erreur de configuration du service météo: {str(e)}")
        # Fallback vers OpenWeatherMap simple
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service météorologique non configuré"
            )
        return create_weather_service({
            "type": "openweathermap", 
            "api_key": api_key,
            "cache_duration": 600
        })

def get_air_quality_service():
    """Fournit le service de qualité de l'air configuré"""
    try:
        return create_air_quality_service(DEFAULT_AIR_QUALITY_CONFIG)
    except Exception as e:
        logger.warning(f"Service qualité de l'air indisponible: {str(e)}")
        return None

@router.get("/current", summary="Météo actuelle")
def get_current_weather(
    city: str = Query(..., min_length=1, max_length=100, description="Nom de la ville"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="Code pays (FR, BE, etc.)"),
    include_air_quality: bool = Query(True, description="Inclure les données de qualité de l'air")
):
    """
    Récupère les conditions météorologiques actuelles pour une ville donnée.
    
    - **city**: Nom de la ville (requis)
    - **country_code**: Code pays ISO à 2 lettres (optionnel, améliore la précision)
    - **include_air_quality**: Inclure les données de qualité de l'air si disponibles
    
    Retourne les conditions actuelles avec température, humidité, précipitations,
    vent, pression, visibilité et qualité de l'air.
    """
    try:
        weather_service = get_weather_service()
        weather_data = weather_service.get_current_weather(city, country_code)
        
        response = {
            "city": city,
            "country_code": country_code,
            "timestamp": weather_data.timestamp.isoformat(),
            "weather": {
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "humidity": weather_data.humidity,
                "precipitation": weather_data.precipitation,
                "wind": {
                    "speed": weather_data.wind_speed,
                    "direction": weather_data.wind_direction
                },
                "pressure": weather_data.pressure,
                "visibility": weather_data.visibility,
                "description": weather_data.description
            },
            "source": weather_data.source
        }
        
        # Ajout des données de qualité de l'air si demandées
        if include_air_quality:
            try:
                air_quality_service = get_air_quality_service()
                if air_quality_service:
                    air_data = air_quality_service.get_current_air_quality(city, country_code)
                    response["air_quality"] = {
                        "aqi": air_data.aqi,
                        "pm25": air_data.pm25,
                        "pm10": air_data.pm10,
                        "o3": air_data.o3,
                        "no2": air_data.no2,
                        "so2": air_data.so2,
                        "co": air_data.co,
                        "timestamp": air_data.timestamp.isoformat(),
                        "source": air_data.source
                    }
            except AirQualityServiceException as e:
                logger.warning(f"Données qualité de l'air indisponibles: {str(e)}")
                response["air_quality"] = {"error": "Données indisponibles"}
        
        logger.info(f"Météo actuelle récupérée pour {city} ({country_code or 'sans pays'})")
        return response
        
    except WeatherServiceException as e:
        logger.error(f"Erreur service météo pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service météorologique indisponible: {e.message}"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des données météorologiques"
        )

@router.get("/forecast", summary="Prévisions météorologiques")
def get_weather_forecast(
    city: str = Query(..., min_length=1, max_length=100, description="Nom de la ville"),
    days: int = Query(5, ge=1, le=10, description="Nombre de jours de prévisions"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="Code pays")
):
    """
    Récupère les prévisions météorologiques pour plusieurs jours.
    
    - **city**: Nom de la ville
    - **days**: Nombre de jours de prévisions (1-10, défaut 5)
    - **country_code**: Code pays ISO à 2 lettres
    
    Retourne les prévisions détaillées pour chaque jour avec toutes les
    informations météorologiques.
    """
    try:
        weather_service = get_weather_service()
        forecast_data = weather_service.get_forecast(city, days, country_code)
        
        # Groupement des prévisions par jour
        daily_forecasts = {}
        for forecast in forecast_data:
            date_key = forecast.timestamp.date().isoformat()
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = []
            
            daily_forecasts[date_key].append({
                "timestamp": forecast.timestamp.isoformat(),
                "temperature": forecast.temperature,
                "feels_like": forecast.feels_like,
                "humidity": forecast.humidity,
                "precipitation": forecast.precipitation,
                "wind_speed": forecast.wind_speed,
                "wind_direction": forecast.wind_direction,
                "pressure": forecast.pressure,
                "visibility": forecast.visibility,
                "description": forecast.description
            })
        
        # Calcul des résumés quotidiens
        daily_summaries = {}
        for date, hourly_data in daily_forecasts.items():
            temperatures = [h["temperature"] for h in hourly_data]
            precipitations = [h["precipitation"] for h in hourly_data]
            
            daily_summaries[date] = {
                "date": date,
                "temperature_min": min(temperatures),
                "temperature_max": max(temperatures),
                "temperature_avg": sum(temperatures) / len(temperatures),
                "total_precipitation": sum(precipitations),
                "max_precipitation": max(precipitations) if precipitations else 0,
                "hourly_forecasts": hourly_data
            }
        
        response = {
            "city": city,
            "country_code": country_code,
            "forecast_days": days,
            "generated_at": datetime.now().isoformat(),
            "source": forecast_data[0].source if forecast_data else "unknown",
            "daily_forecasts": daily_summaries
        }
        
        logger.info(f"Prévisions {days} jours récupérées pour {city}")
        return response
        
    except WeatherServiceException as e:
        logger.error(f"Erreur prévisions pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service de prévisions indisponible: {e.message}"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue prévisions {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des prévisions"
        )

@router.get("/for-date", summary="Météo pour une date spécifique")
def get_weather_for_date(
    city: str = Query(..., min_length=1, max_length=100, description="Nom de la ville"),
    date: str = Query(..., description="Date au format YYYY-MM-DD"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="Code pays")
):
    """
    Récupère la météo pour une date spécifique.
    
    - **city**: Nom de la ville
    - **date**: Date au format YYYY-MM-DD
    - **country_code**: Code pays ISO à 2 lettres
    
    Pour les dates futures, utilise les prévisions.
    Pour les dates passées, utilise les données historiques si disponibles.
    """
    try:
        # Validation et parsing de la date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        
        # Vérification que la date n'est pas trop ancienne ou trop future
        now = datetime.now()
        if target_date < now - timedelta(days=365):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date trop ancienne (maximum 1 an dans le passé)"
            )
        elif target_date > now + timedelta(days=30):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date trop future (maximum 30 jours dans le futur)"
            )
        
        weather_service = get_weather_service()
        weather_data = weather_service.get_weather_for_date(city, target_date, country_code)
        
        # Détermination du type de données
        data_type = "current"
        if target_date.date() > now.date():
            data_type = "forecast"
        elif target_date.date() < now.date():
            data_type = "historical"
        
        response = {
            "city": city,
            "country_code": country_code,
            "requested_date": date,
            "data_type": data_type,
            "weather": {
                "timestamp": weather_data.timestamp.isoformat(),
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "humidity": weather_data.humidity,
                "precipitation": weather_data.precipitation,
                "wind": {
                    "speed": weather_data.wind_speed,
                    "direction": weather_data.wind_direction
                },
                "pressure": weather_data.pressure,
                "visibility": weather_data.visibility,
                "description": weather_data.description
            },
            "source": weather_data.source
        }
        
        # Ajout d'informations contextuelles
        if data_type == "forecast":
            response["note"] = "Données prévisionnelles"
        elif data_type == "historical":
            response["note"] = "Données historiques (disponibilité limitée selon le service)"
        
        logger.info(f"Météo pour {date} récupérée pour {city} (type: {data_type})")
        return response
        
    except WeatherServiceException as e:
        logger.error(f"Erreur météo date {date} pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Données météorologiques indisponibles: {e.message}"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue météo date {date} pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des données météorologiques"
        )

@router.get("/air-quality", summary="Qualité de l'air actuelle")
def get_air_quality(
    city: str = Query(..., min_length=1, max_length=100, description="Nom de la ville"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="Code pays")
):
    """
    Récupère les données de qualité de l'air pour une ville.
    
    - **city**: Nom de la ville
    - **country_code**: Code pays ISO à 2 lettres
    
    Retourne l'indice de qualité de l'air (AQI) et les concentrations
    des principaux polluants (PM2.5, PM10, O3, NO2, SO2, CO).
    """
    try:
        air_quality_service = get_air_quality_service()
        
        if not air_quality_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service de qualité de l'air non disponible"
            )
        
        air_data = air_quality_service.get_current_air_quality(city, country_code)
        
        # Classification de l'AQI
        aqi_level = "Inconnu"
        aqi_color = "#808080"
        aqi_advice = "Données insuffisantes"
        
        if air_data.aqi is not None:
            if air_data.aqi <= 50:
                aqi_level = "Bon"
                aqi_color = "#00e400"
                aqi_advice = "Qualité de l'air satisfaisante"
            elif air_data.aqi <= 100:
                aqi_level = "Modéré"
                aqi_color = "#ffff00"
                aqi_advice = "Acceptable pour la plupart des personnes"
            elif air_data.aqi <= 150:
                aqi_level = "Mauvais pour groupes sensibles"
                aqi_color = "#ff7e00"
                aqi_advice = "Les personnes sensibles peuvent ressentir des effets"
            elif air_data.aqi <= 200:
                aqi_level = "Mauvais"
                aqi_color = "#ff0000"
                aqi_advice = "Tout le monde peut commencer à ressentir des effets"
            elif air_data.aqi <= 300:
                aqi_level = "Très mauvais"
                aqi_color = "#8f3f97"
                aqi_advice = "Avertissement sanitaire : conditions d'urgence"
            else:
                aqi_level = "Dangereux"
                aqi_color = "#7e0023"
                aqi_advice = "Alerte sanitaire : tout le monde est affecté"
        
        response = {
            "city": city,
            "country_code": country_code,
            "timestamp": air_data.timestamp.isoformat(),
            "air_quality": {
                "aqi": air_data.aqi,
                "level": aqi_level,
                "color": aqi_color,
                "advice": aqi_advice,
                "pollutants": {
                    "pm25": {
                        "value": air_data.pm25,
                        "unit": "μg/m³",
                        "description": "Particules fines (diamètre < 2.5 μm)"
                    },
                    "pm10": {
                        "value": air_data.pm10,
                        "unit": "μg/m³",
                        "description": "Particules (diamètre < 10 μm)"
                    },
                    "o3": {
                        "value": air_data.o3,
                        "unit": "μg/m³",
                        "description": "Ozone"
                    },
                    "no2": {
                        "value": air_data.no2,
                        "unit": "μg/m³",
                        "description": "Dioxyde d'azote"
                    },
                    "so2": {
                        "value": air_data.so2,
                        "unit": "μg/m³",
                        "description": "Dioxyde de soufre"
                    },
                    "co": {
                        "value": air_data.co,
                        "unit": "mg/m³",
                        "description": "Monoxyde de carbone"
                    }
                }
            },
            "source": air_data.source
        }
        
        logger.info(f"Qualité de l'air récupérée pour {city} (AQI: {air_data.aqi})")
        return response
        
    except AirQualityServiceException as e:
        logger.error(f"Erreur qualité de l'air pour {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service de qualité de l'air indisponible: {e.message}"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue qualité de l'air {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des données de qualité de l'air"
        )

@router.get("/dashboard", summary="Tableau de bord météorologique")
def get_weather_dashboard(
    city: str = Query(..., min_length=1, max_length=100, description="Nom de la ville"),
    country_code: Optional[str] = Query(None, min_length=2, max_length=2, description="Code pays"),
    forecast_days: int = Query(7, ge=1, le=10, description="Nombre de jours de prévisions")
):
    """
    Tableau de bord météorologique complet combinant :
    - Conditions actuelles
    - Prévisions sur plusieurs jours
    - Qualité de l'air
    - Recommandations d'activités
    
    Endpoint principal pour les interfaces utilisateur nécessitant
    une vue d'ensemble complète.
    """
    try:
        # Récupération des services
        weather_service = get_weather_service()
        air_quality_service = get_air_quality_service()
        
        # Conditions actuelles
        current_weather = weather_service.get_current_weather(city, country_code)
        
        # Prévisions
        forecast_data = weather_service.get_forecast(city, forecast_days, country_code)
        
        # Groupement des prévisions par jour
        daily_forecasts = {}
        for forecast in forecast_data:
            date_key = forecast.timestamp.date().isoformat()
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = []
            daily_forecasts[date_key].append(forecast)
        
        # Résumés quotidiens
        daily_summaries = []
        for date, hourly_data in sorted(daily_forecasts.items()):
            temperatures = [h.temperature for h in hourly_data]
            precipitations = [h.precipitation for h in hourly_data]
            
            daily_summaries.append({
                "date": date,
                "temperature_min": min(temperatures),
                "temperature_max": max(temperatures),
                "total_precipitation": sum(precipitations),
                "avg_wind_speed": sum(h.wind_speed for h in hourly_data) / len(hourly_data),
                "description": hourly_data[len(hourly_data)//2].description  # Description du milieu de journée
            })
        
        # Qualité de l'air
        air_quality_data = None
        if air_quality_service:
            try:
                air_data = air_quality_service.get_current_air_quality(city, country_code)
                air_quality_data = {
                    "aqi": air_data.aqi,
                    "pm25": air_data.pm25,
                    "timestamp": air_data.timestamp.isoformat()
                }
            except AirQualityServiceException:
                air_quality_data = {"error": "Données indisponibles"}
        
        # Alertes météorologiques
        alerts = []
        
        # Vérifications pour les alertes
        if current_weather.temperature < -10:
            alerts.append({"type": "cold", "message": "Températures très froides"})
        elif current_weather.temperature > 35:
            alerts.append({"type": "heat", "message": "Températures très élevées"})
        
        if current_weather.precipitation > 10:
            alerts.append({"type": "rain", "message": "Fortes précipitations"})
        
        if current_weather.wind_speed > 50:
            alerts.append({"type": "wind", "message": "Vents forts"})
        
        if air_quality_data and isinstance(air_quality_data.get("aqi"), int) and air_quality_data["aqi"] > 150:
            alerts.append({"type": "air_quality", "message": "Qualité de l'air dégradée"})
        
        # Recommandations d'activités basées sur la météo actuelle
        activity_recommendations = []
        
        if current_weather.precipitation < 1 and current_weather.temperature > 15:
            activity_recommendations.append("Activités extérieures recommandées")
        elif current_weather.precipitation > 5:
            activity_recommendations.append("Privilégier les activités intérieures")
        
        if current_weather.wind_speed > 30:
            activity_recommendations.append("Éviter les activités exposées au vent")
        
        response = {
            "city": city,
            "country_code": country_code,
            "generated_at": datetime.now().isoformat(),
            "current_weather": {
                "timestamp": current_weather.timestamp.isoformat(),
                "temperature": current_weather.temperature,
                "feels_like": current_weather.feels_like,
                "humidity": current_weather.humidity,
                "precipitation": current_weather.precipitation,
                "wind_speed": current_weather.wind_speed,
                "pressure": current_weather.pressure,
                "description": current_weather.description
            },
            "forecast_summary": daily_summaries,
            "air_quality": air_quality_data,
            "alerts": alerts,
            "activity_recommendations": activity_recommendations,
            "data_sources": {
                "weather": current_weather.source,
                "air_quality": air_quality_data.get("source") if air_quality_data and "source" in air_quality_data else None
            }
        }
        
        logger.info(f"Tableau de bord généré pour {city} avec {len(daily_summaries)} jours de prévisions")
        return response
        
    except WeatherServiceException as e:
        logger.error(f"Erreur service météo dashboard {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service météorologique indisponible: {e.message}"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue dashboard {city}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération du tableau de bord"
        )

# Endpoint de compatibilité avec l'ancienne API
@router.get("/", summary="[Déprécié] Météo simple")
def get_weather_legacy(
    city: str = Query(..., description="Nom de la ville")
):
    """
    Endpoint de compatibilité avec l'ancienne API.
    
    **Déprécié** : Utilisez `/weather/current` à la place.
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "OPENWEATHER_API_KEY non définie"}
        
        # Appel direct à l'API pour compatibilité
        import requests
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "fr"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erreur API: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Erreur endpoint legacy pour {city}: {str(e)}")
        return {"error": f"Erreur: {str(e)}"}
