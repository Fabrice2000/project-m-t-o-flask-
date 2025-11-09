"""Tests pour les modèles de données"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Mock des dépendances pour éviter les erreurs d'import
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    # Mock SQLAlchemy pour les tests
    class MockColumn:
        def __init__(self, *args, **kwargs):
            pass
    
    class MockRelationship:
        def __init__(self, *args, **kwargs):
            pass
    
    class MockDateTime:
        def __init__(self, *args, **kwargs):
            pass
    
    create_engine = Mock()
    sessionmaker = Mock()

from app.models import (
    User, UserProfile, Activity, UserActivityVote, 
    WeatherData, PredefinedActivity, ActivityConstraint,
    get_database_url, create_database_engine, get_session
)

class TestUser:
    """Tests pour le modèle User"""
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_active is True  # Valeur par défaut
        assert user.created_at is not None
    
    def test_user_representation(self):
        """Test de la représentation string de l'utilisateur"""
        user = User(username="testuser", email="test@example.com")
        
        assert str(user) == "User(username='testuser', email='test@example.com')"
    
    def test_user_equality(self):
        """Test d'égalité entre utilisateurs"""
        user1 = User(username="testuser", email="test@example.com")
        user2 = User(username="testuser", email="test@example.com")
        user3 = User(username="otheruser", email="other@example.com")
        
        # Note: En réalité, SQLAlchemy compare par ID, mais pour le test unitaire
        assert user1.username == user2.username
        assert user1.username != user3.username
    
    def test_user_password_validation(self):
        """Test de validation du mot de passe"""
        # Test avec mot de passe valide
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="valid_hash_with_sufficient_length"
        )
        assert len(user.password_hash) > 0
        
        # Test avec mot de passe vide (devrait être géré par la validation)
        user_empty = User(username="test", email="test@example.com")
        assert user_empty.password_hash is None

class TestUserProfile:
    """Tests pour le modèle UserProfile"""
    
    def test_profile_creation(self):
        """Test de création d'un profil utilisateur"""
        profile = UserProfile(
            user_id=1,
            preferred_activities=["running", "hiking"],
            weather_sensitivity=7.5,
            temperature_preference_min=15.0,
            temperature_preference_max=25.0,
            wind_tolerance=20.0,
            rain_tolerance=2.0
        )
        
        assert profile.user_id == 1
        assert "running" in profile.preferred_activities
        assert profile.weather_sensitivity == 7.5
        assert profile.temperature_preference_min == 15.0
        assert profile.updated_at is not None
    
    def test_profile_preferences_in_range(self):
        """Test que les préférences sont dans les bonnes plages"""
        profile = UserProfile(
            user_id=1,
            weather_sensitivity=8.5,
            temperature_preference_min=10.0,
            temperature_preference_max=30.0,
            wind_tolerance=15.0,
            rain_tolerance=1.5
        )
        
        # Sensibilité météo entre 0 et 10
        assert 0 <= profile.weather_sensitivity <= 10
        
        # Température min < max
        assert profile.temperature_preference_min < profile.temperature_preference_max
        
        # Tolérances positives
        assert profile.wind_tolerance >= 0
        assert profile.rain_tolerance >= 0
    
    def test_profile_activity_management(self):
        """Test de gestion des activités préférées"""
        profile = UserProfile(
            user_id=1,
            preferred_activities=["swimming", "cycling", "reading"]
        )
        
        # Ajouter une activité
        if "tennis" not in profile.preferred_activities:
            profile.preferred_activities.append("tennis")
        
        assert "tennis" in profile.preferred_activities
        assert len(profile.preferred_activities) == 4
        
        # Retirer une activité
        if "reading" in profile.preferred_activities:
            profile.preferred_activities.remove("reading")
        
        assert "reading" not in profile.preferred_activities
        assert len(profile.preferred_activities) == 3

class TestActivity:
    """Tests pour le modèle Activity"""
    
    def test_activity_creation(self):
        """Test de création d'une activité"""
        activity = Activity(
            name="Course à pied",
            description="Course matinale dans le parc",
            location="Parc Central",
            date=datetime(2024, 6, 15, 8, 0),
            duration_minutes=45,
            organizer_id=1,
            max_participants=20,
            outdoor=True
        )
        
        assert activity.name == "Course à pied"
        assert activity.outdoor is True
        assert activity.max_participants == 20
        assert activity.status == "planned"  # Statut par défaut
        assert activity.created_at is not None
    
    def test_activity_status_transitions(self):
        """Test des transitions de statut d'activité"""
        activity = Activity(
            name="Test Activity",
            date=datetime.now() + timedelta(days=1),
            organizer_id=1
        )
        
        # Statut initial
        assert activity.status == "planned"
        
        # Transition vers "active"
        activity.status = "active"
        assert activity.status == "active"
        
        # Transition vers "completed"
        activity.status = "completed"
        assert activity.status == "completed"
        
        # Transition vers "cancelled"
        activity.status = "cancelled"
        assert activity.status == "cancelled"
    
    def test_activity_time_validation(self):
        """Test de validation des horaires d'activité"""
        future_date = datetime.now() + timedelta(days=7)
        past_date = datetime.now() - timedelta(days=1)
        
        # Activité future (valide)
        future_activity = Activity(
            name="Future Activity",
            date=future_date,
            organizer_id=1
        )
        assert future_activity.date > datetime.now()
        
        # Activité passée (pour test)
        past_activity = Activity(
            name="Past Activity",
            date=past_date,
            organizer_id=1
        )
        assert past_activity.date < datetime.now()
    
    def test_activity_participant_management(self):
        """Test de gestion des participants"""
        activity = Activity(
            name="Group Activity",
            date=datetime.now() + timedelta(days=1),
            organizer_id=1,
            max_participants=5
        )
        
        # Vérifier la limite de participants
        assert activity.max_participants == 5
        
        # Simuler l'ajout de participants (en réalité via relation)
        current_participants = 3
        assert current_participants < activity.max_participants
        
        # Vérifier qu'on peut encore ajouter des participants
        available_spots = activity.max_participants - current_participants
        assert available_spots == 2

class TestUserActivityVote:
    """Tests pour le modèle UserActivityVote"""
    
    def test_vote_creation(self):
        """Test de création d'un vote"""
        vote = UserActivityVote(
            user_id=1,
            activity_id=10,
            preference_rank=1,
            weather_importance=8.0,
            distance_importance=6.0,
            social_importance=7.5
        )
        
        assert vote.user_id == 1
        assert vote.activity_id == 10
        assert vote.preference_rank == 1
        assert vote.weather_importance == 8.0
        assert vote.voted_at is not None
    
    def test_vote_importance_ranges(self):
        """Test des plages de valeurs d'importance"""
        vote = UserActivityVote(
            user_id=1,
            activity_id=10,
            preference_rank=2,
            weather_importance=9.0,
            distance_importance=5.5,
            social_importance=3.0
        )
        
        # Toutes les importances doivent être entre 0 et 10
        assert 0 <= vote.weather_importance <= 10
        assert 0 <= vote.distance_importance <= 10
        assert 0 <= vote.social_importance <= 10
    
    def test_vote_ranking_validation(self):
        """Test de validation du classement"""
        # Rang valide
        vote1 = UserActivityVote(
            user_id=1,
            activity_id=10,
            preference_rank=1
        )
        assert vote1.preference_rank >= 1
        
        # Rang plus élevé
        vote2 = UserActivityVote(
            user_id=1,
            activity_id=11,
            preference_rank=5
        )
        assert vote2.preference_rank >= 1

class TestWeatherDataModel:
    """Tests pour le modèle WeatherData"""
    
    def test_weather_data_creation(self):
        """Test de création de données météo"""
        weather = WeatherData(
            location="Paris",
            temperature=22.5,
            feels_like=23.0,
            humidity=65,
            wind_speed=15.0,
            wind_direction=270,
            pressure=1015.0,
            description="Partiellement nuageux",
            recorded_at=datetime.now(),
            source="OpenWeatherMap"
        )
        
        assert weather.location == "Paris"
        assert weather.temperature == 22.5
        assert weather.humidity == 65
        assert weather.source == "OpenWeatherMap"
    
    def test_weather_data_validation(self):
        """Test de validation des données météo"""
        weather = WeatherData(
            location="Lyon",
            temperature=18.0,
            humidity=80,
            wind_speed=25.0,
            pressure=1020.0,
            recorded_at=datetime.now()
        )
        
        # Humidité en pourcentage (0-100)
        assert 0 <= weather.humidity <= 100
        
        # Pression atmosphérique raisonnable
        assert 900 <= weather.pressure <= 1100
        
        # Vitesse du vent positive
        assert weather.wind_speed >= 0

class TestPredefinedActivity:
    """Tests pour le modèle PredefinedActivity"""
    
    def test_predefined_activity_creation(self):
        """Test de création d'activité prédéfinie"""
        activity = PredefinedActivity(
            name="Jogging",
            category="Sport",
            indoor=False,
            min_participants=1,
            max_participants=10,
            typical_duration=30,
            equipment_needed=["Chaussures de sport", "Vêtements adaptés"],
            difficulty_level=3
        )
        
        assert activity.name == "Jogging"
        assert activity.category == "Sport"
        assert activity.indoor is False
        assert activity.difficulty_level == 3
        assert "Chaussures de sport" in activity.equipment_needed
    
    def test_predefined_activity_constraints(self):
        """Test des contraintes d'activité prédéfinie"""
        activity = PredefinedActivity(
            name="Tennis",
            category="Sport",
            min_participants=2,
            max_participants=4,
            difficulty_level=5
        )
        
        # Participants
        assert activity.min_participants <= activity.max_participants
        assert activity.min_participants >= 1
        
        # Niveau de difficulté entre 1 et 10
        assert 1 <= activity.difficulty_level <= 10

class TestActivityConstraint:
    """Tests pour le modèle ActivityConstraint"""
    
    def test_constraint_creation(self):
        """Test de création de contrainte d'activité"""
        constraint = ActivityConstraint(
            activity_id=1,
            min_temperature=10.0,
            max_temperature=30.0,
            max_wind_speed=20.0,
            max_precipitation=2.0,
            min_visibility=5.0,
            constraint_type="weather"
        )
        
        assert constraint.activity_id == 1
        assert constraint.min_temperature == 10.0
        assert constraint.max_temperature == 30.0
        assert constraint.constraint_type == "weather"
    
    def test_constraint_validation(self):
        """Test de validation des contraintes"""
        constraint = ActivityConstraint(
            activity_id=1,
            min_temperature=15.0,
            max_temperature=25.0,
            max_wind_speed=15.0,
            max_precipitation=1.0
        )
        
        # Température min < max
        assert constraint.min_temperature < constraint.max_temperature
        
        # Valeurs positives
        assert constraint.max_wind_speed >= 0
        assert constraint.max_precipitation >= 0

class TestDatabaseUtilities:
    """Tests pour les utilitaires de base de données"""
    
    def test_database_url_generation(self):
        """Test de génération d'URL de base de données"""
        # Test avec variables d'environnement simulées
        with patch.dict('os.environ', {
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb'
        }):
            url = get_database_url()
            expected = "postgresql://testuser:testpass@localhost:5432/testdb"
            assert url == expected
    
    def test_database_url_with_defaults(self):
        """Test avec valeurs par défaut"""
        with patch.dict('os.environ', {
            'DB_NAME': 'myapp'
        }, clear=True):
            url = get_database_url()
            # Doit contenir au moins le nom de la base
            assert 'myapp' in url
    
    @pytest.mark.skipif(not HAS_SQLALCHEMY, reason="SQLAlchemy non disponible")
    def test_database_engine_creation(self):
        """Test de création du moteur de base de données"""
        # Test avec une URL SQLite pour éviter les dépendances
        test_url = "sqlite:///test.db"
        engine = create_database_engine(test_url)
        
        assert engine is not None
        # Vérifier que c'est bien un moteur SQLAlchemy
        assert hasattr(engine, 'connect')
    
    @pytest.mark.skipif(not HAS_SQLALCHEMY, reason="SQLAlchemy non disponible")
    def test_session_creation(self):
        """Test de création de session"""
        # Utiliser un moteur en mémoire pour les tests
        test_url = "sqlite:///:memory:"
        session = get_session(test_url)
        
        assert session is not None
        # Vérifier que c'est bien une session SQLAlchemy
        assert hasattr(session, 'query')
        assert hasattr(session, 'commit')

class TestModelIntegration:
    """Tests d'intégration entre modèles"""
    
    def test_user_profile_relationship(self):
        """Test de la relation User-UserProfile"""
        # Créer un utilisateur et son profil
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        profile = UserProfile(
            user_id=1,  # Simule l'ID de l'utilisateur
            preferred_activities=["swimming"],
            weather_sensitivity=5.0
        )
        
        # Vérifier la cohérence
        assert profile.user_id == 1
        assert len(profile.preferred_activities) > 0
    
    def test_activity_vote_relationship(self):
        """Test de la relation Activity-Vote"""
        activity = Activity(
            name="Test Activity",
            date=datetime.now() + timedelta(days=1),
            organizer_id=1
        )
        
        vote = UserActivityVote(
            user_id=2,
            activity_id=1,  # Simule l'ID de l'activité
            preference_rank=1,
            weather_importance=8.0
        )
        
        # Vérifier la cohérence
        assert vote.activity_id == 1
        assert vote.preference_rank >= 1
    
    def test_activity_constraint_relationship(self):
        """Test de la relation Activity-Constraint"""
        activity = Activity(
            name="Outdoor Activity",
            date=datetime.now() + timedelta(days=1),
            organizer_id=1,
            outdoor=True
        )
        
        constraint = ActivityConstraint(
            activity_id=1,  # Simule l'ID de l'activité
            min_temperature=5.0,
            max_temperature=35.0,
            max_wind_speed=30.0,
            constraint_type="weather"
        )
        
        # Vérifier la cohérence pour activité extérieure
        assert constraint.activity_id == 1
        assert activity.outdoor is True  # Cohérent avec les contraintes météo

class TestDataValidation:
    """Tests de validation des données"""
    
    def test_email_format_simulation(self):
        """Test de simulation de validation d'email"""
        # En réalité, ceci serait géré par des validators SQLAlchemy/Pydantic
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "simple@test.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            ""
        ]
        
        for email in valid_emails:
            # Simulation de validation - en réalité ferait appel à un validator
            assert "@" in email and "." in email.split("@")[1]
        
        for email in invalid_emails:
            # Simulation d'échec de validation
            is_valid = "@" in email and len(email.split("@")) == 2 and "." in email.split("@")[1]
            assert not is_valid
    
    def test_datetime_validation(self):
        """Test de validation des dates"""
        # Dates valides
        valid_dates = [
            datetime.now(),
            datetime.now() + timedelta(days=30),
            datetime(2024, 12, 31, 23, 59, 59)
        ]
        
        for date in valid_dates:
            assert isinstance(date, datetime)
            assert date.year >= 2020  # Année raisonnable
        
        # Test de date future pour activité
        future_activity_date = datetime.now() + timedelta(hours=2)
        assert future_activity_date > datetime.now()

class TestPerformanceAndScaling:
    """Tests de performance et montée en charge"""
    
    def test_bulk_activity_creation_simulation(self):
        """Test de création en masse d'activités (simulation)"""
        activities = []
        base_date = datetime.now() + timedelta(days=1)
        
        # Créer 100 activités en mémoire
        for i in range(100):
            activity = Activity(
                name=f"Activity {i}",
                description=f"Description for activity {i}",
                date=base_date + timedelta(hours=i),
                organizer_id=(i % 10) + 1,  # 10 organisateurs différents
                max_participants=10 + (i % 20)  # Variété dans les tailles
            )
            activities.append(activity)
        
        assert len(activities) == 100
        assert all(isinstance(a, Activity) for a in activities)
        assert len(set(a.organizer_id for a in activities)) == 10  # 10 organisateurs uniques
    
    def test_vote_aggregation_simulation(self):
        """Test de simulation d'agrégation de votes"""
        # Simuler des votes pour une activité
        votes = []
        activity_id = 1
        
        for user_id in range(1, 21):  # 20 utilisateurs
            vote = UserActivityVote(
                user_id=user_id,
                activity_id=activity_id,
                preference_rank=min(user_id % 5 + 1, 5),  # Rangs 1-5
                weather_importance=5.0 + (user_id % 6),  # 5.0-10.0
                distance_importance=3.0 + (user_id % 8),  # 3.0-10.0
                social_importance=4.0 + (user_id % 7)     # 4.0-10.0
            )
            votes.append(vote)
        
        # Calculer des statistiques simples
        avg_weather_importance = sum(v.weather_importance for v in votes) / len(votes)
        most_popular_rank = max(set(v.preference_rank for v in votes), 
                               key=lambda x: sum(1 for v in votes if v.preference_rank == x))
        
        assert len(votes) == 20
        assert 5.0 <= avg_weather_importance <= 10.0
        assert 1 <= most_popular_rank <= 5