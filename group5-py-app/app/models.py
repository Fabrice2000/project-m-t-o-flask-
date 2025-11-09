from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import enum

Base = declarative_base()

class ActivityType(enum.Enum):
    """Type d'activité selon l'environnement nécessaire"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    MIXED = "mixed"  # peut se faire dedans ou dehors

class WeatherSensitivity(enum.Enum):
    """Niveau de sensibilité aux conditions météorologiques"""
    NONE = "none"        # pas affecté par la météo (musée, cinéma)
    LOW = "low"          # légèrement affecté (sport en salle avec terrasse)
    MEDIUM = "medium"    # moyennement affecté (parc couvert)
    HIGH = "high"        # très affecté (randonnée, plage)

class UserRole(enum.Enum):
    """Rôles des utilisateurs dans le système"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

@dataclass
class WeatherConditions:
    """Structure des données météorologiques"""
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    description: str
    feels_like: float
    air_quality_index: Optional[int] = None

class User(Base):
    """Modèle représentant un utilisateur de l'application"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relations
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    votes = relationship("Vote", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

class UserProfile(Base):
    """Profil utilisateur avec préférences pour les recommandations"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Préférences météorologiques
    outdoor_preference = Column(Float, default=0.5, nullable=False)  # 0=intérieur, 1=extérieur
    temperature_min = Column(Float, default=5.0)  # température minimale confortable
    temperature_max = Column(Float, default=30.0)  # température maximale confortable
    rain_tolerance = Column(Float, default=0.2)  # tolérance à la pluie (0-1)
    wind_tolerance = Column(Float, default=20.0)  # vitesse de vent max tolérée (km/h)
    
    # Préférences d'activités
    family_friendly_only = Column(Boolean, default=False)
    preferred_categories = Column(JSON, default=list)  # liste des catégories préférées
    mobility_restrictions = Column(JSON, default=dict)  # restrictions de mobilité
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="profile")
    
    def get_weather_preference_score(self, weather: WeatherConditions) -> float:
        """Calcule un score de préférence basé sur les conditions météo (0-1)"""
        score = 1.0
        
        # Pénalité pour température hors zone de confort
        if weather.temperature < self.temperature_min or weather.temperature > self.temperature_max:
            score *= 0.3
        
        # Pénalité pour la pluie selon la tolérance
        if weather.precipitation > 0:
            rain_penalty = min(weather.precipitation / 10.0, 1.0)  # normalise sur 10mm
            score *= (1.0 - rain_penalty * (1.0 - self.rain_tolerance))
        
        # Pénalité pour le vent
        if weather.wind_speed > self.wind_tolerance:
            wind_penalty = min((weather.wind_speed - self.wind_tolerance) / 30.0, 0.7)
            score *= (1.0 - wind_penalty)
        
        return max(score, 0.0)

class Activity(Base):
    """Modèle représentant une activité disponible"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    
    # Caractéristiques environnementales
    activity_type = Column(Enum(ActivityType), default=ActivityType.MIXED, nullable=False)
    weather_sensitivity = Column(Enum(WeatherSensitivity), default=WeatherSensitivity.MEDIUM)
    
    # Contraintes d'âge et accessibilité
    min_age = Column(Integer, default=0)
    max_age = Column(Integer)  # None = pas de limite
    family_friendly = Column(Boolean, default=True)
    accessibility_info = Column(JSON, default=dict)  # infos d'accessibilité
    
    # Conditions météo requises/recommandées
    ideal_temp_min = Column(Float)
    ideal_temp_max = Column(Float)
    requires_good_weather = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # Relations
    instances = relationship("ActivityInstance", back_populates="activity")
    created_by = relationship("User")
    
    def is_suitable_for_weather(self, weather: WeatherConditions) -> bool:
        """Vérifie si l'activité est adaptée aux conditions météo"""
        if self.activity_type == ActivityType.INDOOR:
            return True  # activités intérieures toujours OK
        
        # Vérifications pour activités extérieures ou mixtes
        if self.requires_good_weather and weather.precipitation > 1.0:
            return False
        
        if self.ideal_temp_min and weather.temperature < self.ideal_temp_min:
            return False
            
        if self.ideal_temp_max and weather.temperature > self.ideal_temp_max:
            return False
        
        # Conditions extrêmes générales
        if weather.precipitation > 10.0:  # pluie forte
            return self.activity_type == ActivityType.INDOOR
        
        if weather.wind_speed > 50.0:  # vent très fort
            return self.activity_type == ActivityType.INDOOR
        
        return True
    
    def get_weather_compatibility_score(self, weather: WeatherConditions) -> float:
        """Calcule un score de compatibilité avec la météo (0-1)"""
        if not self.is_suitable_for_weather(weather):
            return 0.0
        
        if self.activity_type == ActivityType.INDOOR:
            return 1.0  # toujours compatible
        
        score = 1.0
        
        # Bonus/malus selon le type de temps
        if self.activity_type == ActivityType.OUTDOOR:
            if weather.precipitation > 0:
                score *= max(0.2, 1.0 - weather.precipitation / 5.0)
            if weather.wind_speed > 20:
                score *= max(0.3, 1.0 - (weather.wind_speed - 20) / 30.0)
        
        return max(score, 0.1)

class ActivityInstance(Base):
    """Instance programmée d'une activité à une date/heure précise"""
    __tablename__ = "activity_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    # Programmation
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False)
    
    # Localisation
    location_name = Column(String(200))
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Informations pratiques
    max_participants = Column(Integer)
    current_participants = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    booking_required = Column(Boolean, default=False)
    booking_url = Column(String(500))
    
    # Statut
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(Text)
    
    # Relations
    activity = relationship("Activity", back_populates="instances")
    
    @property
    def is_full(self) -> bool:
        """Vérifie si l'activité est complète"""
        if not self.max_participants:
            return False
        return self.current_participants >= self.max_participants
    
    @property
    def availability_percentage(self) -> float:
        """Retourne le pourcentage de places disponibles"""
        if not self.max_participants:
            return 100.0
        return max(0.0, (self.max_participants - self.current_participants) / self.max_participants * 100)

class Vote(Base):
    """Vote d'un utilisateur pour le classement des activités (méthode Condorcet)"""
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Le classement est stocké comme une liste d'IDs d'activités
    # Index 0 = préféré, index croissant = moins préféré
    activity_ranking = Column(JSON, nullable=False)  # [activity_id1, activity_id2, ...]
    
    # Contexte du vote
    vote_context = Column(JSON, default=dict)  # conditions météo, date, etc.
    created_at = Column(DateTime, default=func.now())
    
    # Relations
    user = relationship("User", back_populates="votes")
    
    def get_preference_between(self, activity_a_id: int, activity_b_id: int) -> Optional[int]:
        """
        Retourne l'ID de l'activité préférée entre A et B, ou None si pas dans le vote
        """
        try:
            pos_a = self.activity_ranking.index(activity_a_id)
            pos_b = self.activity_ranking.index(activity_b_id)
            return activity_a_id if pos_a < pos_b else activity_b_id
        except ValueError:
            # Une ou les deux activités ne sont pas dans le classement
            return None

class WeatherForecast(Base):
    """Cache des prévisions météorologiques pour éviter les appels API répétés"""
    __tablename__ = "weather_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(10))
    forecast_date = Column(DateTime, nullable=False, index=True)
    
    # Données météo
    temperature = Column(Float, nullable=False)
    feels_like = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float, default=0.0)
    wind_speed = Column(Float)
    wind_direction = Column(Integer)  # degrés
    pressure = Column(Float)
    visibility = Column(Float)
    description = Column(String(200))
    
    # Qualité de l'air
    air_quality_index = Column(Integer)
    
    # Métadonnées
    data_source = Column(String(50))  # OpenWeatherMap, WeatherAPI, etc.
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_weather_conditions(self) -> WeatherConditions:
        """Convertit vers la structure WeatherConditions"""
        return WeatherConditions(
            temperature=self.temperature,
            humidity=self.humidity or 0.0,
            precipitation=self.precipitation,
            wind_speed=self.wind_speed or 0.0,
            description=self.description or "",
            feels_like=self.feels_like or self.temperature,
            air_quality_index=self.air_quality_index
        )
