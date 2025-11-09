"""
Point d'entrée principal de l'application FastAPI
Application de recommandation d'activités basée sur la météo
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO if os.getenv('APP_DEBUG', 'false').lower() == 'true' else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Météo Activités",
    description="Application intelligente de recommandation d'activités selon la météo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Une erreur interne s'est produite",
            "detail": str(exc) if os.getenv('APP_DEBUG', 'false').lower() == 'true' else "Erreur serveur"
        }
    )

# Tentative d'import et d'initialisation des modules
try:
    # Import conditionnel pour éviter les erreurs si les dépendances manquent
    from app import models, database
    from app.routers import activities, weather
    
    # Initialisation de la base de données (optionnel en mode démo)
    try:
        models.Base.metadata.create_all(bind=database.engine)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.warning(f"Impossible d'initialiser la base de données: {e}")
        logger.info("L'application fonctionnera en mode démo sans base de données")
    
    # Ajout des routes
    app.include_router(weather.router, prefix="/weather", tags=["Météo"])
    app.include_router(activities.router, prefix="/activities", tags=["Activités"])
    
    logger.info("Routes ajoutées avec succès")
    
except ImportError as e:
    logger.warning(f"Certains modules ne sont pas disponibles: {e}")
    logger.info("L'application fonctionnera avec les fonctionnalités de base")

@app.get("/", tags=["Accueil"])
async def racine():
    """
    Point d'entrée de l'API - Informations générales
    """
    return {
        "message": "Bienvenue sur l'API Météo Activités !",
        "description": "Application intelligente de recommandation d'activités selon la météo",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "météo": "/weather/",
            "activités": "/activities/",
            "santé": "/health"
        }
    }

@app.get("/health", tags=["Système"])
async def verifier_sante():
    """
    Vérification de l'état de santé de l'application
    """
    status = {
        "status": "healthy",
        "timestamp": "2024-11-09T10:00:00Z",
        "services": {}
    }
    
    # Vérification base de données
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        status["services"]["database"] = "connected"
    except Exception:
        status["services"]["database"] = "disconnected"
        status["status"] = "degraded"
    
    # Vérification service météo
    weather_key = os.getenv('WEATHER_API_KEY')
    if weather_key and weather_key != 'demo_key_for_testing':
        status["services"]["weather_api"] = "configured"
    else:
        status["services"]["weather_api"] = "demo_mode"
    
    return status

# Endpoint de démonstration sans dépendances
@app.get("/demo/weather", tags=["Démo"])
async def demo_meteo(ville: str = "Paris"):
    """
    Démonstration de données météo (mode simulation)
    """
    return {
        "ville": ville,
        "température": 18.5,
        "description": "Partiellement nuageux",
        "humidité": 65,
        "vent": 12.0,
        "pression": 1015.2,
        "source": "Données de démonstration",
        "recommandations": [
            "Course à pied matinale",
            "Visite de musée",
            "Café en terrasse"
        ]
    }

@app.get("/demo/activities", tags=["Démo"])  
async def demo_activites():
    """
    Démonstration d'activités recommandées (mode simulation)
    """
    return {
        "activités_recommandées": [
            {
                "id": 1,
                "nom": "Course matinale au parc",
                "description": "Jogging dans le Bois de Boulogne",
                "météo_requise": "Temps sec, température > 10°C",
                "participants_max": 20,
                "score_recommandation": 8.5
            },
            {
                "id": 2,
                "nom": "Visite du Louvre",
                "description": "Découverte des collections permanentes",
                "météo_requise": "Intérieur, toute météo",
                "participants_max": 50,
                "score_recommandation": 7.8
            },
            {
                "id": 3,
                "nom": "Pique-nique en famille",
                "description": "Déjeuner en plein air aux Tuileries",
                "météo_requise": "Ensoleillé, vent < 15 km/h",
                "participants_max": 8,
                "score_recommandation": 9.2
            }
        ],
        "critères_recommandation": {
            "météo": "40%",
            "préférences_utilisateur": "60%"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configuration du serveur
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('APP_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Démarrage du serveur sur {host}:{port}")
    logger.info(f"Mode debug: {debug}")
    logger.info(f"Documentation disponible sur: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
