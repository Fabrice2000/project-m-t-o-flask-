Application de Recommandation d'Activités Météo

Une application qui recommande des activités selon la météo et les préférences des utilisateurs.

Fonctionnalités

Recommandations personnalisées selon la météo
Intégration de plusieurs services météo
Système de vote Condorcet pour les groupes
API REST avec documentation automatique
Profils utilisateur personnalisables
Installation

Prérequis

Python 3.8+
PostgreSQL (optionnel)
Clé API météo (optionnel pour la démo)
Démarrage rapide

git clone <repository-url>
cd group5-py-app
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app/main.py
Configuration

Créez un fichier .env :

# Base de données (optionnel)
DB_HOST=localhost
DB_NAME=meteo_app
DB_USER=user
DB_PASSWORD=password

# Service météo (optionnel)
WEATHER_API_KEY=your_api_key

# Application
APP_DEBUG=true
SECRET_KEY=your_secret_key
Utilisation

Démarrer l'application

python app/main.py
L'API est accessible sur http://localhost:8000

Documentation

Interface Swagger : http://localhost:8000/docs
Documentation alternative : http://localhost:8000/redoc
Exemples d'API

# Météo actuelle
curl "http://localhost:8000/demo/weather?ville=Paris"

# Recommandations d'activités
curl "http://localhost:8000/demo/activities"
Tests

pytest                    # Tous les tests
pytest --cov=app         # Avec couverture
pytest tests/test_*.py   # Tests spécifiques
Fonctionnalités principales

Vote Condorcet

Système de vote par préférence pour choisir les activités en groupe.

Recommandations intelligentes

Météo (40%) : température, vent, précipitations
Préférences utilisateur (60%) : activités favorites, historique
Services météo

OpenWeatherMap (principal)
WeatherAPI (secours)
OpenAQ (qualité de l'air)
Contribution

Fork le projet
Créer une branche (git checkout -b feature/nouvelle-fonctionnalite)
Commiter (git commit -m 'Ajout nouvelle fonctionnalité')
Push (git push origin feature/nouvelle-fonctionnalite)
Créer une Pull Request
Licence

MIT License - voir le fichier LICENSE

Développé par l'équipe Groupe 5

Kouadjeu Ngatchou Fabrice

Benitez Noah

Yazid EL-BAK

Irina LETSARA
