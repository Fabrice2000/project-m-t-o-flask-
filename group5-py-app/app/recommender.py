from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import math
import logging

from .models import Activity, UserProfile, ActivityInstance, WeatherConditions
from .services import WeatherServiceInterface, AirQualityServiceInterface, WeatherData, AirQualityData

logger = logging.getLogger(__name__)

@dataclass
class RecommendationScore:
    """Score détaillé d'une recommandation"""
    activity_id: int
    total_score: float
    weather_score: float
    preference_score: float
    availability_score: float
    time_score: float
    reasons: List[str]  # Explications du score

@dataclass
class RecommendationContext:
    """Contexte pour les recommandations"""
    user_profile: UserProfile
    target_date: datetime
    city: str
    country_code: Optional[str] = None
    max_distance_km: Optional[float] = None
    budget_limit: Optional[float] = None
    activity_categories: Optional[List[str]] = None
    group_size: int = 1

class ActivityRecommendationEngine:
    """
    Moteur de recommandation d'activités basé sur plusieurs facteurs :
    - Conditions météorologiques
    - Préférences utilisateur
    - Disponibilité des activités
    - Contexte temporel
    """
    
    def __init__(self, 
                 weather_service: WeatherServiceInterface,
                 air_quality_service: AirQualityServiceInterface,
                 activity_repository,
                 instance_repository):
        """
        Initialise le moteur de recommandation
        
        Args:
            weather_service: Service météorologique
            air_quality_service: Service de qualité de l'air
            activity_repository: Repository des activités
            instance_repository: Repository des instances d'activités
        """
        self.weather_service = weather_service
        self.air_quality_service = air_quality_service
        self.activity_repository = activity_repository
        self.instance_repository = instance_repository
        
        # Poids des différents facteurs dans le calcul du score
        self.weights = {
            "weather": 0.35,      # Importance de la météo
            "preference": 0.25,   # Préférences utilisateur
            "availability": 0.20, # Disponibilité de l'activité
            "time": 0.15,         # Pertinence temporelle
            "bonus": 0.05         # Bonus divers (nouveauté, popularité, etc.)
        }

    def get_recommendations(self, 
                          context: RecommendationContext, 
                          limit: int = 20) -> List[RecommendationScore]:
        """
        Génère des recommandations d'activités selon le contexte
        
        Args:
            context: Contexte de la recommandation
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste de scores de recommandation triés par pertinence
        """
        logger.info(f"Génération de recommandations pour {context.user_profile.user.name}")
        
        try:
            # Récupération des données météorologiques
            weather_data = self._get_weather_data(context)
            air_quality_data = self._get_air_quality_data(context)
            
            # Récupération des activités candidates
            candidate_activities = self._get_candidate_activities(context)
            
            if not candidate_activities:
                logger.warning("Aucune activité candidate trouvée")
                return []
            
            # Calcul des scores pour chaque activité
            recommendations = []
            for activity in candidate_activities:
                score = self._calculate_activity_score(
                    activity, weather_data, air_quality_data, context
                )
                if score.total_score > 0.1:  # Seuil minimum de pertinence
                    recommendations.append(score)
            
            # Tri par score décroissant
            recommendations.sort(key=lambda x: x.total_score, reverse=True)
            
            # Application de la diversification (éviter trop d'activités similaires)
            recommendations = self._diversify_recommendations(recommendations, limit)
            
            logger.info(f"Généré {len(recommendations)} recommandations")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de recommandations: {str(e)}")
            return []

    def _get_weather_data(self, context: RecommendationContext) -> WeatherData:
        """Récupère les données météorologiques pour le contexte"""
        try:
            return self.weather_service.get_weather_for_date(
                context.city, 
                context.target_date, 
                context.country_code
            )
        except Exception as e:
            logger.warning(f"Impossible de récupérer la météo: {str(e)}")
            # Données météo par défaut en cas d'échec
            return WeatherData(
                temperature=20.0, feels_like=20.0, humidity=50.0,
                precipitation=0.0, wind_speed=10.0, wind_direction=0,
                pressure=1013.0, visibility=10.0, description="Données indisponibles",
                timestamp=context.target_date, source="Défaut"
            )

    def _get_air_quality_data(self, context: RecommendationContext) -> Optional[AirQualityData]:
        """Récupère les données de qualité de l'air"""
        try:
            return self.air_quality_service.get_current_air_quality(
                context.city, context.country_code
            )
        except Exception as e:
            logger.warning(f"Impossible de récupérer la qualité de l'air: {str(e)}")
            return None

    def _get_candidate_activities(self, context: RecommendationContext) -> List[Activity]:
        """Récupère les activités candidates selon les filtres du contexte"""
        filters = {}
        
        # Filtrage par catégorie si spécifié
        if context.activity_categories:
            filters["category__in"] = context.activity_categories
        
        # Filtrage par âge approprié
        if hasattr(context.user_profile, 'age') and context.user_profile.age:
            filters["min_age__lte"] = context.user_profile.age
            if context.user_profile.age < 18:
                filters["family_friendly"] = True
        
        # Filtrage pour les familles si nécessaire
        if context.user_profile.family_friendly_only:
            filters["family_friendly"] = True
        
        # Récupération depuis le repository
        return self.activity_repository.find_available_activities(
            date=context.target_date,
            filters=filters
        )

    def _calculate_activity_score(self, 
                                activity: Activity, 
                                weather: WeatherData, 
                                air_quality: Optional[AirQualityData],
                                context: RecommendationContext) -> RecommendationScore:
        """Calcule le score de recommandation pour une activité"""
        
        reasons = []
        
        # Score météorologique
        weather_conditions = WeatherConditions(
            temperature=weather.temperature,
            humidity=weather.humidity,
            precipitation=weather.precipitation,
            wind_speed=weather.wind_speed,
            description=weather.description,
            feels_like=weather.feels_like,
            air_quality_index=air_quality.aqi if air_quality else None
        )
        
        weather_score = self._calculate_weather_score(activity, weather_conditions, reasons)
        
        # Score de préférences utilisateur
        preference_score = self._calculate_preference_score(
            activity, context.user_profile, weather_conditions, reasons
        )
        
        # Score de disponibilité
        availability_score = self._calculate_availability_score(
            activity, context, reasons
        )
        
        # Score temporel (moment de la journée, saison, etc.)
        time_score = self._calculate_time_score(activity, context.target_date, reasons)
        
        # Calcul du score total pondéré
        total_score = (
            weather_score * self.weights["weather"] +
            preference_score * self.weights["preference"] +
            availability_score * self.weights["availability"] +
            time_score * self.weights["time"]
        )
        
        # Application de bonus/malus
        total_score = self._apply_bonus_penalties(total_score, activity, context, reasons)
        
        return RecommendationScore(
            activity_id=activity.id,
            total_score=max(0.0, min(1.0, total_score)),  # Clamp entre 0 et 1
            weather_score=weather_score,
            preference_score=preference_score,
            availability_score=availability_score,
            time_score=time_score,
            reasons=reasons
        )

    def _calculate_weather_score(self, 
                               activity: Activity, 
                               weather: WeatherConditions, 
                               reasons: List[str]) -> float:
        """Calcule le score basé sur l'adéquation météorologique"""
        if not activity.is_suitable_for_weather(weather):
            reasons.append("Conditions météo inadaptées")
            return 0.0
        
        base_score = activity.get_weather_compatibility_score(weather)
        
        # Ajustements selon la sensibilité météo de l'activité
        if activity.weather_sensitivity.value == "none":
            reasons.append("Non affecté par la météo")
            return 1.0
        elif activity.weather_sensitivity.value == "low":
            base_score = max(base_score, 0.7)  # Score minimum élevé
            reasons.append("Peu sensible à la météo")
        elif activity.weather_sensitivity.value == "high":
            # Plus strict sur les conditions
            if weather.precipitation > 2.0:
                base_score *= 0.3
                reasons.append("Sensible à la pluie")
            if weather.wind_speed > 30.0:
                base_score *= 0.5
                reasons.append("Sensible au vent")
        
        # Bonus pour conditions idéales
        if (activity.ideal_temp_min and activity.ideal_temp_max and
            activity.ideal_temp_min <= weather.temperature <= activity.ideal_temp_max):
            base_score *= 1.2
            reasons.append("Température idéale")
        
        return min(base_score, 1.0)

    def _calculate_preference_score(self, 
                                  activity: Activity, 
                                  profile: UserProfile, 
                                  weather: WeatherConditions,
                                  reasons: List[str]) -> float:
        """Calcule le score basé sur les préférences utilisateur"""
        score = 0.5  # Score de base neutre
        
        # Préférence intérieur/extérieur
        user_weather_score = profile.get_weather_preference_score(weather)
        
        if activity.activity_type.value == "outdoor":
            score = profile.outdoor_preference * user_weather_score
            if profile.outdoor_preference > 0.7:
                reasons.append("Préfère les activités extérieures")
        elif activity.activity_type.value == "indoor":
            score = (1.0 - profile.outdoor_preference) * (2.0 - user_weather_score)
            if profile.outdoor_preference < 0.3:
                reasons.append("Préfère les activités intérieures")
        else:  # mixed
            score = 0.7  # Score neutre élevé pour les activités mixtes
            reasons.append("Activité adaptable")
        
        # Préférences de catégories
        if (hasattr(profile, 'preferred_categories') and 
            profile.preferred_categories and
            activity.category in profile.preferred_categories):
            score *= 1.3
            reasons.append(f"Catégorie préférée: {activity.category}")
        
        # Contraintes familiales
        if profile.family_friendly_only and not activity.family_friendly:
            score *= 0.1
            reasons.append("Non adapté aux familles")
        elif activity.family_friendly and profile.family_friendly_only:
            score *= 1.2
            reasons.append("Adapté aux familles")
        
        return min(score, 1.0)

    def _calculate_availability_score(self, 
                                    activity: Activity, 
                                    context: RecommendationContext,
                                    reasons: List[str]) -> float:
        """Calcule le score basé sur la disponibilité de l'activité"""
        # Vérifie s'il y a des instances programmées pour cette date
        instances = self.instance_repository.find_by_activity_and_date(
            activity.id, context.target_date
        )
        
        if not instances:
            # Pas d'instance programmée, vérifie si l'activité est généralement disponible
            if activity.is_active:
                reasons.append("Activité disponible en général")
                return 0.7  # Score moyen pour les activités sans horaires fixes
            else:
                reasons.append("Activité inactive")
                return 0.0
        
        # Calcule la disponibilité moyenne des instances
        total_availability = 0.0
        available_instances = 0
        
        for instance in instances:
            if instance.is_cancelled:
                continue
            
            if not instance.max_participants:
                # Pas de limite de participants
                total_availability += 1.0
                available_instances += 1
            else:
                availability = instance.availability_percentage / 100.0
                total_availability += availability
                available_instances += 1
        
        if available_instances == 0:
            reasons.append("Aucune instance disponible")
            return 0.0
        
        avg_availability = total_availability / available_instances
        
        if avg_availability > 0.8:
            reasons.append("Très disponible")
        elif avg_availability > 0.5:
            reasons.append("Disponibilité modérée")
        elif avg_availability > 0.2:
            reasons.append("Disponibilité limitée")
        else:
            reasons.append("Presque complet")
        
        return avg_availability

    def _calculate_time_score(self, 
                            activity: Activity, 
                            target_date: datetime,
                            reasons: List[str]) -> float:
        """Calcule le score basé sur la pertinence temporelle"""
        score = 1.0
        
        # Analyse saisonnière
        month = target_date.month
        
        # Activités estivales
        if activity.category.lower() in ["plage", "piscine", "festival", "randonnée"]:
            if 6 <= month <= 8:  # Été
                score *= 1.2
                reasons.append("Activité de saison")
            elif month in [12, 1, 2]:  # Hiver
                score *= 0.6
                reasons.append("Hors saison")
        
        # Activités hivernales
        elif activity.category.lower() in ["ski", "patinoire", "musée", "cinéma"]:
            if month in [12, 1, 2]:  # Hiver
                score *= 1.2
                reasons.append("Activité de saison")
            elif 6 <= month <= 8:  # Été
                score *= 0.8
        
        # Analyse du jour de la semaine
        day_of_week = target_date.weekday()  # 0 = lundi, 6 = dimanche
        
        if day_of_week >= 5:  # Weekend
            if activity.category.lower() in ["loisirs", "famille", "sport"]:
                score *= 1.1
                reasons.append("Parfait pour le weekend")
        else:  # Semaine
            if activity.category.lower() in ["culture", "éducation", "formation"]:
                score *= 1.1
                reasons.append("Activité de semaine")
        
        # Distance temporelle (favorise les activités prochaines mais pas trop)
        days_ahead = (target_date.date() - datetime.now().date()).days
        if 1 <= days_ahead <= 7:
            score *= 1.1
            reasons.append("Planification optimale")
        elif days_ahead > 30:
            score *= 0.9
            reasons.append("Planification lointaine")
        
        return min(score, 1.0)

    def _apply_bonus_penalties(self, 
                             base_score: float, 
                             activity: Activity, 
                             context: RecommendationContext,
                             reasons: List[str]) -> float:
        """Applique des bonus et pénalités additionnels"""
        score = base_score
        
        # Bonus pour les nouvelles activités
        if hasattr(activity, 'created_at'):
            days_since_creation = (datetime.now() - activity.created_at).days
            if days_since_creation <= 30:
                score *= 1.05
                reasons.append("Nouvelle activité")
        
        # Pénalité pour les activités peu populaires (si données disponibles)
        # Ceci nécessiterait un système de rating/popularité
        
        # Contrainte budgétaire
        if context.budget_limit and hasattr(activity, 'typical_price'):
            if activity.typical_price > context.budget_limit:
                score *= 0.3
                reasons.append("Dépasse le budget")
        
        # Bonus pour diversité (calculé ailleurs dans diversify_recommendations)
        
        return score

    def _diversify_recommendations(self, 
                                 recommendations: List[RecommendationScore], 
                                 limit: int) -> List[RecommendationScore]:
        """
        Diversifie les recommandations pour éviter trop d'activités similaires
        
        Utilise un algorithme de sélection qui balance score et diversité
        """
        if len(recommendations) <= limit:
            return recommendations
        
        # Groupe les activités par catégorie
        by_category = {}
        for rec in recommendations:
            activity = self.activity_repository.get_by_id(rec.activity_id)
            category = activity.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        # Sélection diversifiée
        selected = []
        remaining = limit
        
        # Première passe : prend les meilleures de chaque catégorie
        while remaining > 0 and by_category:
            for category in list(by_category.keys()):
                if remaining <= 0:
                    break
                
                if by_category[category]:
                    selected.append(by_category[category].pop(0))
                    remaining -= 1
                else:
                    del by_category[category]
        
        # Deuxième passe : complète avec les meilleures restantes
        all_remaining = []
        for category_recs in by_category.values():
            all_remaining.extend(category_recs)
        
        all_remaining.sort(key=lambda x: x.total_score, reverse=True)
        selected.extend(all_remaining[:remaining])
        
        # Re-trie par score total
        selected.sort(key=lambda x: x.total_score, reverse=True)
        
        return selected[:limit]

    def explain_recommendation(self, recommendation: RecommendationScore) -> str:
        """Génère une explication textuelle de la recommandation"""
        activity = self.activity_repository.get_by_id(recommendation.activity_id)
        
        explanation = f"**{activity.title}**\n"
        explanation += f"Score total: {recommendation.total_score:.2f}/1.0\n\n"
        
        explanation += "**Facteurs positifs:**\n"
        for reason in recommendation.reasons:
            if not any(neg in reason.lower() for neg in ["inadapt", "non", "dépasse", "hors"]):
                explanation += f"• {reason}\n"
        
        negative_reasons = [r for r in recommendation.reasons 
                          if any(neg in r.lower() for neg in ["inadapt", "non", "dépasse", "hors"])]
        
        if negative_reasons:
            explanation += "\n**Points d'attention:**\n"
            for reason in negative_reasons:
                explanation += f"• {reason}\n"
        
        return explanation

class SmartRecommendationEngine(ActivityRecommendationEngine):
    """
    Version avancée du moteur de recommandation avec apprentissage
    
    Prend en compte l'historique des choix utilisateur pour améliorer
    les recommandations futures
    """
    
    def __init__(self, *args, user_history_repository=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_history_repository = user_history_repository
        self.learning_weight = 0.1  # Poids de l'historique dans le score
    
    def get_recommendations(self, context: RecommendationContext, limit: int = 20) -> List[RecommendationScore]:
        """Version améliorée avec prise en compte de l'historique"""
        base_recommendations = super().get_recommendations(context, limit * 2)  # Récupère plus pour filtrer
        
        if not self.user_history_repository or not base_recommendations:
            return base_recommendations[:limit]
        
        # Améliore les scores basés sur l'historique utilisateur
        user_preferences = self._analyze_user_history(context.user_profile.user_id)
        
        for rec in base_recommendations:
            history_score = self._calculate_history_score(rec.activity_id, user_preferences)
            
            # Intègre le score historique
            rec.total_score = (
                rec.total_score * (1 - self.learning_weight) +
                history_score * self.learning_weight
            )
            
            if history_score > 0.7:
                rec.reasons.append("Correspond à vos goûts habituels")
            elif history_score < 0.3:
                rec.reasons.append("Style différent de vos préférences")
        
        # Re-trie et applique la diversification
        base_recommendations.sort(key=lambda x: x.total_score, reverse=True)
        return self._diversify_recommendations(base_recommendations, limit)
    
    def _analyze_user_history(self, user_id: int) -> Dict:
        """Analyse l'historique utilisateur pour extraire les préférences"""
        # Cette méthode devrait analyser les activités passées de l'utilisateur
        # pour identifier des patterns de préférences
        
        # Implémentation simplifiée - à étendre selon les besoins
        return {
            "preferred_categories": [],
            "preferred_times": [],
            "weather_preferences": {},
            "activity_types": {}
        }
    
    def _calculate_history_score(self, activity_id: int, user_preferences: Dict) -> float:
        """Calcule un score basé sur l'historique utilisateur"""
        # Implémentation simplifiée
        return 0.5  # Score neutre par défaut
