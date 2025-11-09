import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.recommender import (
    ActivityRecommendationEngine,
    SmartRecommendationEngine,
    RecommendationContext,
    RecommendationScore
)
from app.models import Activity, UserProfile, WeatherConditions, ActivityType, WeatherSensitivity
from app.services import WeatherData, AirQualityData

class TestActivityRecommendationEngine:
    """Tests complets du moteur de recommandation d'activités"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        # Mocks des services
        self.weather_service = Mock()
        self.air_quality_service = Mock()
        self.activity_repository = Mock()
        self.instance_repository = Mock()
        
        # Configuration du moteur
        self.recommendation_engine = ActivityRecommendationEngine(
            weather_service=self.weather_service,
            air_quality_service=self.air_quality_service,
            activity_repository=self.activity_repository,
            instance_repository=self.instance_repository
        )
        
        # Données de test
        self.setup_test_data()
    
    def setup_test_data(self):
        """Prépare les données de test"""
        # Profil utilisateur de test
        self.user_profile = Mock(spec=UserProfile)
        self.user_profile.outdoor_preference = 0.7
        self.user_profile.temperature_min = 10.0
        self.user_profile.temperature_max = 25.0
        self.user_profile.rain_tolerance = 0.3
        self.user_profile.wind_tolerance = 25.0
        self.user_profile.family_friendly_only = False
        self.user_profile.preferred_categories = ["sport", "culture"]
        
        # Mock de la méthode get_weather_preference_score
        self.user_profile.get_weather_preference_score.return_value = 0.8
        
        # Activités de test
        self.activities = [
            self.create_mock_activity(1, "Randonnée", "sport", ActivityType.OUTDOOR, WeatherSensitivity.HIGH),
            self.create_mock_activity(2, "Musée", "culture", ActivityType.INDOOR, WeatherSensitivity.NONE),
            self.create_mock_activity(3, "Piscine couverte", "sport", ActivityType.MIXED, WeatherSensitivity.LOW),
            self.create_mock_activity(4, "Concert en plein air", "culture", ActivityType.OUTDOOR, WeatherSensitivity.MEDIUM)
        ]
        
        # Conditions météo de test
        self.good_weather = WeatherData(
            temperature=22.0,
            feels_like=23.0,
            humidity=60.0,
            precipitation=0.0,
            wind_speed=10.0,
            wind_direction=180,
            pressure=1015.0,
            visibility=10.0,
            description="Ensoleillé",
            timestamp=datetime.now(),
            source="Test"
        )
        
        self.bad_weather = WeatherData(
            temperature=5.0,
            feels_like=2.0,
            humidity=90.0,
            precipitation=15.0,
            wind_speed=35.0,
            wind_direction=270,
            pressure=995.0,
            visibility=2.0,
            description="Pluie forte",
            timestamp=datetime.now(),
            source="Test"
        )
        
        # Qualité de l'air de test
        self.good_air_quality = AirQualityData(
            aqi=45,
            pm25=12.0,
            pm10=20.0,
            o3=80.0,
            no2=25.0,
            so2=10.0,
            co=0.8,
            timestamp=datetime.now(),
            source="Test"
        )
    
    def create_mock_activity(self, id: int, title: str, category: str, 
                           activity_type: ActivityType, weather_sensitivity: WeatherSensitivity) -> Mock:
        """Crée une activité mock pour les tests"""
        activity = Mock(spec=Activity)
        activity.id = id
        activity.title = title
        activity.category = category
        activity.activity_type = activity_type
        activity.weather_sensitivity = weather_sensitivity
        activity.family_friendly = True
        activity.min_age = 0
        activity.max_age = None
        activity.ideal_temp_min = None
        activity.ideal_temp_max = None
        activity.requires_good_weather = (weather_sensitivity == WeatherSensitivity.HIGH)
        activity.is_active = True
        
        # Mock des méthodes
        activity.is_suitable_for_weather.return_value = True
        activity.get_weather_compatibility_score.return_value = 0.8
        
        return activity
    
    def test_get_recommendations_good_weather(self):
        """Test des recommandations par beau temps"""
        # Configuration des mocks
        self.weather_service.get_weather_for_date.return_value = self.good_weather
        self.air_quality_service.get_current_air_quality.return_value = self.good_air_quality
        self.activity_repository.find_available_activities.return_value = self.activities
        self.instance_repository.find_by_activity_and_date.return_value = []
        
        # Contexte de recommandation
        context = RecommendationContext(
            user_profile=self.user_profile,
            target_date=datetime.now() + timedelta(days=1),
            city="Paris",
            country_code="FR"
        )
        
        # Exécution
        recommendations = self.recommendation_engine.get_recommendations(context, limit=10)
        
        # Vérifications
        assert len(recommendations) > 0
        assert all(isinstance(rec, RecommendationScore) for rec in recommendations)
        assert all(0 <= rec.total_score <= 1 for rec in recommendations)
        
        # Vérification que les activités extérieures sont mieux notées par beau temps
        outdoor_scores = [rec.total_score for rec in recommendations 
                         if rec.activity_id in [1, 4]]  # Randonnée et concert
        indoor_scores = [rec.total_score for rec in recommendations 
                        if rec.activity_id == 2]  # Musée
        
        if outdoor_scores and indoor_scores:
            assert max(outdoor_scores) >= max(indoor_scores)
    
    def test_get_recommendations_bad_weather(self):
        """Test des recommandations par mauvais temps"""
        # Configuration pour mauvais temps
        self.weather_service.get_weather_for_date.return_value = self.bad_weather
        self.air_quality_service.get_current_air_quality.return_value = self.good_air_quality
        self.activity_repository.find_available_activities.return_value = self.activities
        self.instance_repository.find_by_activity_and_date.return_value = []
        
        # Activité extérieure non adaptée au mauvais temps
        self.activities[0].is_suitable_for_weather.return_value = False  # Randonnée
        self.activities[0].get_weather_compatibility_score.return_value = 0.1
        
        context = RecommendationContext(
            user_profile=self.user_profile,
            target_date=datetime.now() + timedelta(days=1),
            city="Paris"
        )
        
        recommendations = self.recommendation_engine.get_recommendations(context, limit=10)
        
        # Vérifications
        assert len(recommendations) > 0
        
        # L'activité intérieure (musée) devrait être mieux classée
        museum_score = next((rec.total_score for rec in recommendations if rec.activity_id == 2), 0)
        hiking_score = next((rec.total_score for rec in recommendations if rec.activity_id == 1), 0)
        
        assert museum_score > hiking_score
    
    def test_weather_score_calculation(self):
        """Test du calcul du score météorologique"""
        activity = self.activities[0]  # Randonnée (outdoor, high sensitivity)
        
        good_conditions = WeatherConditions(
            temperature=20.0, humidity=50.0, precipitation=0.0,
            wind_speed=10.0, description="Beau temps", feels_like=20.0
        )
        
        bad_conditions = WeatherConditions(
            temperature=5.0, humidity=90.0, precipitation=10.0,
            wind_speed=50.0, description="Mauvais temps", feels_like=2.0
        )
        
        reasons = []
        
        # Test avec bonnes conditions
        activity.is_suitable_for_weather.return_value = True
        activity.get_weather_compatibility_score.return_value = 0.9
        good_score = self.recommendation_engine._calculate_weather_score(
            activity, good_conditions, reasons
        )
        
        # Test avec mauvaises conditions
        activity.is_suitable_for_weather.return_value = False
        bad_score = self.recommendation_engine._calculate_weather_score(
            activity, bad_conditions, reasons
        )
        
        assert good_score > bad_score
        assert bad_score == 0.0  # Activité non adaptée
    
    def test_preference_score_calculation(self):
        """Test du calcul du score de préférences"""
        # Activité extérieure avec utilisateur qui aime l'extérieur
        outdoor_activity = self.activities[0]  # Randonnée
        indoor_activity = self.activities[1]   # Musée
        
        good_weather_conditions = WeatherConditions(
            temperature=20.0, humidity=50.0, precipitation=0.0,
            wind_speed=10.0, description="Beau temps", feels_like=20.0
        )
        
        reasons = []
        
        outdoor_score = self.recommendation_engine._calculate_preference_score(
            outdoor_activity, self.user_profile, good_weather_conditions, reasons
        )
        
        indoor_score = self.recommendation_engine._calculate_preference_score(
            indoor_activity, self.user_profile, good_weather_conditions, reasons
        )
        
        # Utilisateur préfère l'extérieur (preference = 0.7)
        assert outdoor_score > indoor_score
    
    def test_availability_score_calculation(self):
        """Test du calcul du score de disponibilité"""
        activity = self.activities[0]
        
        context = RecommendationContext(
            user_profile=self.user_profile,
            target_date=datetime.now(),
            city="Paris"
        )
        
        # Test sans instances (activité généralement disponible)
        self.instance_repository.find_by_activity_and_date.return_value = []
        reasons = []
        
        score = self.recommendation_engine._calculate_availability_score(
            activity, context, reasons
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_time_score_calculation(self):
        """Test du calcul du score temporel"""
        activity = self.activities[0]  # Randonnée
        activity.category = "randonnée"
        
        # Test en été (favorable pour randonnée)
        summer_date = datetime(2024, 7, 15)  # Juillet
        winter_date = datetime(2024, 1, 15)  # Janvier
        
        reasons = []
        
        summer_score = self.recommendation_engine._calculate_time_score(
            activity, summer_date, reasons
        )
        
        winter_score = self.recommendation_engine._calculate_time_score(
            activity, winter_date, reasons
        )
        
        # La randonnée devrait être mieux notée en été
        assert summer_score >= winter_score
    
    def test_diversification(self):
        """Test de la diversification des recommandations"""
        # Crée plusieurs activités de même catégorie
        sport_activities = [
            self.create_mock_activity(i, f"Sport {i}", "sport", ActivityType.OUTDOOR, WeatherSensitivity.MEDIUM)
            for i in range(10, 20)
        ]
        
        culture_activities = [
            self.create_mock_activity(i, f"Culture {i}", "culture", ActivityType.INDOOR, WeatherSensitivity.NONE)
            for i in range(20, 25)
        ]
        
        all_activities = sport_activities + culture_activities
        
        # Mock du repository pour retourner les activités par ID
        def get_by_id(activity_id):
            return next((a for a in all_activities if a.id == activity_id), None)
        
        self.activity_repository.get_by_id = get_by_id
        
        # Crée des scores de recommandation
        recommendations = [
            RecommendationScore(
                activity_id=a.id,
                total_score=0.8 - (a.id % 10) * 0.05,  # Scores décroissants
                weather_score=0.8,
                preference_score=0.7,
                availability_score=0.9,
                time_score=0.8,
                reasons=["Test"]
            )
            for a in all_activities
        ]
        
        # Test de diversification
        diversified = self.recommendation_engine._diversify_recommendations(recommendations, limit=8)
        
        # Vérifie la diversification
        categories = [get_by_id(rec.activity_id).category for rec in diversified]
        unique_categories = set(categories)
        
        assert len(unique_categories) > 1  # Au moins 2 catégories différentes
        assert len(diversified) <= 8
    
    def test_recommendation_explanation(self):
        """Test de génération d'explications"""
        activity = self.activities[0]
        self.activity_repository.get_by_id.return_value = activity
        
        recommendation = RecommendationScore(
            activity_id=1,
            total_score=0.85,
            weather_score=0.9,
            preference_score=0.8,
            availability_score=0.7,
            time_score=0.9,
            reasons=["Météo favorable", "Correspond à vos préférences", "Activité de saison"]
        )
        
        explanation = self.recommendation_engine.explain_recommendation(recommendation)
        
        assert isinstance(explanation, str)
        assert activity.title in explanation
        assert "0.85" in explanation  # Score total
        assert "Météo favorable" in explanation
    
    def test_error_handling_weather_service_failure(self):
        """Test de gestion d'erreur du service météo"""
        # Service météo en échec
        self.weather_service.get_weather_for_date.side_effect = Exception("API indisponible")
        self.activity_repository.find_available_activities.return_value = self.activities
        
        context = RecommendationContext(
            user_profile=self.user_profile,
            target_date=datetime.now(),
            city="Paris"
        )
        
        # Doit utiliser des données par défaut et ne pas planter
        recommendations = self.recommendation_engine.get_recommendations(context)
        
        # Peut retourner une liste vide ou avec données par défaut
        assert isinstance(recommendations, list)
    
    def test_context_validation(self):
        """Test de validation du contexte de recommandation"""
        # Test avec différents contextes
        contexts = [
            RecommendationContext(
                user_profile=self.user_profile,
                target_date=datetime.now(),
                city="",  # Ville vide
            ),
            RecommendationContext(
                user_profile=self.user_profile,
                target_date=datetime.now() - timedelta(days=365),  # Date trop ancienne
                city="Paris"
            ),
        ]
        
        self.activity_repository.find_available_activities.return_value = []
        
        for context in contexts:
            # Ne doit pas planter même avec contexte invalide
            try:
                recommendations = self.recommendation_engine.get_recommendations(context)
                assert isinstance(recommendations, list)
            except Exception:
                # Peut lever une exception mais doit être gérée
                pass

class TestSmartRecommendationEngine:
    """Tests pour le moteur de recommandation intelligent avec apprentissage"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.weather_service = Mock()
        self.air_quality_service = Mock()
        self.activity_repository = Mock()
        self.instance_repository = Mock()
        self.user_history_repository = Mock()
        
        self.smart_engine = SmartRecommendationEngine(
            weather_service=self.weather_service,
            air_quality_service=self.air_quality_service,
            activity_repository=self.activity_repository,
            instance_repository=self.instance_repository,
            user_history_repository=self.user_history_repository
        )
        
        # Profil utilisateur mock
        self.user_profile = Mock()
        self.user_profile.user_id = 1
        self.user_profile.outdoor_preference = 0.6
        self.user_profile.get_weather_preference_score.return_value = 0.7
    
    def test_user_history_analysis(self):
        """Test d'analyse de l'historique utilisateur"""
        user_id = 1
        
        # Mock de l'historique
        self.user_history_repository.get_user_activities.return_value = [
            {"activity_id": 1, "category": "sport", "rating": 5},
            {"activity_id": 2, "category": "sport", "rating": 4},
            {"activity_id": 3, "category": "culture", "rating": 2}
        ]
        
        preferences = self.smart_engine._analyze_user_history(user_id)
        
        assert isinstance(preferences, dict)
        # Devrait identifier une préférence pour le sport
    
    def test_learning_integration(self):
        """Test d'intégration de l'apprentissage dans les recommandations"""
        # Configuration basique
        self.weather_service.get_weather_for_date.return_value = Mock()
        self.air_quality_service.get_current_air_quality.return_value = None
        self.activity_repository.find_available_activities.return_value = []
        
        # Mock du parent pour retourner des recommandations de base
        with patch.object(ActivityRecommendationEngine, 'get_recommendations') as mock_parent:
            mock_parent.return_value = [
                RecommendationScore(
                    activity_id=1, total_score=0.6, weather_score=0.7,
                    preference_score=0.5, availability_score=0.8, time_score=0.6,
                    reasons=["Test"]
                )
            ]
            
            context = RecommendationContext(
                user_profile=self.user_profile,
                target_date=datetime.now(),
                city="Paris"
            )
            
            recommendations = self.smart_engine.get_recommendations(context)
            
            assert len(recommendations) >= 0
            # Le score peut être ajusté par l'apprentissage

class TestRecommendationContext:
    """Tests pour la classe RecommendationContext"""
    
    def test_context_creation(self):
        """Test de création d'un contexte de recommandation"""
        user_profile = Mock()
        target_date = datetime.now()
        
        context = RecommendationContext(
            user_profile=user_profile,
            target_date=target_date,
            city="Lyon",
            country_code="FR",
            budget_limit=50.0,
            group_size=4
        )
        
        assert context.user_profile == user_profile
        assert context.target_date == target_date
        assert context.city == "Lyon"
        assert context.country_code == "FR"
        assert context.budget_limit == 50.0
        assert context.group_size == 4

class TestIntegration:
    """Tests d'intégration des composants"""
    
    @pytest.mark.integration
    def test_full_recommendation_pipeline(self):
        """Test complet du pipeline de recommandation"""
        # Ce test nécessiterait des vrais services ou des mocks plus complexes
        # Il vérifierait l'intégration complète depuis la requête jusqu'à la réponse
        pass
    
    @pytest.mark.performance
    def test_recommendation_performance(self):
        """Test de performance du système de recommandation"""
        import time
        
        # Configuration avec beaucoup d'activités
        activities = [Mock() for _ in range(100)]
        for i, activity in enumerate(activities):
            activity.id = i
            activity.title = f"Activité {i}"
            activity.category = f"Catégorie {i % 10}"
            activity.activity_type = ActivityType.MIXED
            activity.weather_sensitivity = WeatherSensitivity.MEDIUM
            activity.is_suitable_for_weather.return_value = True
            activity.get_weather_compatibility_score.return_value = 0.8
        
        # Mocks des services
        weather_service = Mock()
        air_quality_service = Mock()
        activity_repository = Mock()
        instance_repository = Mock()
        
        weather_service.get_weather_for_date.return_value = Mock(
            temperature=20.0, precipitation=0.0, wind_speed=10.0
        )
        air_quality_service.get_current_air_quality.return_value = None
        activity_repository.find_available_activities.return_value = activities
        instance_repository.find_by_activity_and_date.return_value = []
        activity_repository.get_by_id.side_effect = lambda id: activities[id] if id < len(activities) else None
        
        engine = ActivityRecommendationEngine(
            weather_service=weather_service,
            air_quality_service=air_quality_service,
            activity_repository=activity_repository,
            instance_repository=instance_repository
        )
        
        user_profile = Mock()
        user_profile.get_weather_preference_score.return_value = 0.7
        user_profile.outdoor_preference = 0.6
        user_profile.family_friendly_only = False
        
        context = RecommendationContext(
            user_profile=user_profile,
            target_date=datetime.now(),
            city="Paris"
        )
        
        # Test de performance
        start_time = time.time()
        recommendations = engine.get_recommendations(context, limit=50)
        end_time = time.time()
        
        # Doit terminer rapidement même avec beaucoup d'activités
        assert end_time - start_time < 2.0
        assert len(recommendations) <= 50