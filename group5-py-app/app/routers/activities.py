from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from app import models, database
from app.services import create_weather_service, create_air_quality_service, WeatherServiceException
from app.recommender import ActivityRecommendationEngine, RecommendationContext
from app.condorcet import CondorcetVotingSystem, VoteValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activities", tags=["activities"])

def get_db():
    """Générateur de session de base de données"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Modèles Pydantic pour la validation et sérialisation ===

from pydantic import BaseModel, Field, validator
from enum import Enum

class ActivityTypeEnum(str, Enum):
    indoor = "indoor"
    outdoor = "outdoor"
    mixed = "mixed"

class WeatherSensitivityEnum(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"

class ActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'activité")
    description: Optional[str] = Field(None, max_length=2000, description="Description détaillée")
    category: str = Field(..., min_length=1, max_length=100, description="Catégorie de l'activité")
    activity_type: ActivityTypeEnum = Field(ActivityTypeEnum.mixed, description="Type d'environnement")
    weather_sensitivity: WeatherSensitivityEnum = Field(WeatherSensitivityEnum.medium, description="Sensibilité météorologique")
    min_age: int = Field(0, ge=0, le=100, description="Âge minimum requis")
    max_age: Optional[int] = Field(None, ge=0, le=150, description="Âge maximum recommandé")
    family_friendly: bool = Field(True, description="Adapté aux familles")
    ideal_temp_min: Optional[float] = Field(None, ge=-50, le=50, description="Température idéale minimale (°C)")
    ideal_temp_max: Optional[float] = Field(None, ge=-50, le=60, description="Température idéale maximale (°C)")
    requires_good_weather: bool = Field(False, description="Nécessite un beau temps")

    @validator('ideal_temp_max')
    def validate_temperature_range(cls, v, values):
        if v is not None and 'ideal_temp_min' in values and values['ideal_temp_min'] is not None:
            if v <= values['ideal_temp_min']:
                raise ValueError('La température maximale doit être supérieure à la minimale')
        return v

class ActivityCreate(ActivityBase):
    """Modèle pour la création d'activité"""
    pass

class ActivityUpdate(BaseModel):
    """Modèle pour la mise à jour d'activité (champs optionnels)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    activity_type: Optional[ActivityTypeEnum] = None
    weather_sensitivity: Optional[WeatherSensitivityEnum] = None
    min_age: Optional[int] = Field(None, ge=0, le=100)
    max_age: Optional[int] = Field(None, ge=0, le=150)
    family_friendly: Optional[bool] = None
    ideal_temp_min: Optional[float] = Field(None, ge=-50, le=50)
    ideal_temp_max: Optional[float] = Field(None, ge=-50, le=60)
    requires_good_weather: Optional[bool] = None
    is_active: Optional[bool] = None

class ActivityRead(ActivityBase):
    """Modèle pour la lecture d'activité"""
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class ActivityInstanceBase(BaseModel):
    start_datetime: datetime = Field(..., description="Date/heure de début")
    end_datetime: datetime = Field(..., description="Date/heure de fin")
    location_name: Optional[str] = Field(None, max_length=200, description="Nom du lieu")
    address: Optional[str] = Field(None, max_length=500, description="Adresse complète")
    max_participants: Optional[int] = Field(None, ge=1, le=10000, description="Nombre max de participants")
    price: float = Field(0.0, ge=0, description="Prix en euros")
    booking_required: bool = Field(False, description="Réservation obligatoire")
    booking_url: Optional[str] = Field(None, max_length=500, description="URL de réservation")

    @validator('end_datetime')
    def validate_end_after_start(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('La date de fin doit être postérieure à la date de début')
        return v

class ActivityInstanceCreate(ActivityInstanceBase):
    activity_id: int = Field(..., description="ID de l'activité associée")

class ActivityInstanceRead(ActivityInstanceBase):
    id: int
    activity_id: int
    current_participants: int
    is_cancelled: bool
    is_full: bool
    availability_percentage: float

    class Config:
        orm_mode = True

class RecommendationRequest(BaseModel):
    """Modèle pour les demandes de recommandation"""
    city: str = Field(..., min_length=1, max_length=100, description="Nom de la ville")
    country_code: Optional[str] = Field(None, min_length=2, max_length=2, description="Code pays (FR, BE, etc.)")
    target_date: datetime = Field(..., description="Date cible pour les activités")
    user_id: Optional[int] = Field(None, description="ID utilisateur pour personnalisation")
    max_results: int = Field(20, ge=1, le=100, description="Nombre maximum de résultats")
    categories: Optional[List[str]] = Field(None, description="Catégories d'activités souhaitées")
    budget_limit: Optional[float] = Field(None, ge=0, description="Budget maximum en euros")
    group_size: int = Field(1, ge=1, le=50, description="Taille du groupe")

class RecommendationResponse(BaseModel):
    """Modèle pour les réponses de recommandation"""
    activity_id: int
    activity_title: str
    activity_category: str
    total_score: float
    weather_score: float
    preference_score: float
    availability_score: float
    reasons: List[str]
    weather_conditions: Dict[str, Any]

class VoteRequest(BaseModel):
    """Modèle pour les demandes de vote"""
    user_id: int = Field(..., description="ID de l'utilisateur votant")
    activity_ranking: List[int] = Field(..., min_items=2, description="Classement des activités par ordre de préférence")
    vote_context: Optional[Dict[str, Any]] = Field(None, description="Contexte du vote (météo, date, etc.)")

    @validator('activity_ranking')
    def validate_no_duplicates(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Le classement ne peut pas contenir de doublons')
        return v

class VoteResultResponse(BaseModel):
    """Modèle pour les résultats de vote"""
    winner: Optional[int]
    total_votes: int
    ranking: List[int]
    pairwise_comparisons: Dict[str, Dict[str, int]]
    has_condorcet_winner: bool
    smith_set: List[int]

# === Repository pour la gestion des données ===

class ActivityRepository:
    """Repository pour la gestion des activités"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_activity(self, activity_data: ActivityCreate, created_by_id: Optional[int] = None) -> models.Activity:
        """Crée une nouvelle activité"""
        db_activity = models.Activity(
            **activity_data.dict(),
            created_by_id=created_by_id
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

    def get_activity_by_id(self, activity_id: int) -> Optional[models.Activity]:
        """Récupère une activité par son ID"""
        return self.db.query(models.Activity).filter(
            models.Activity.id == activity_id,
            models.Activity.is_active == True
        ).first()

    def get_all_activities(self, skip: int = 0, limit: int = 100) -> List[models.Activity]:
        """Récupère toutes les activités actives"""
        return self.db.query(models.Activity).filter(
            models.Activity.is_active == True
        ).offset(skip).limit(limit).all()

    def update_activity(self, activity_id: int, update_data: ActivityUpdate) -> Optional[models.Activity]:
        """Met à jour une activité"""
        activity = self.get_activity_by_id(activity_id)
        if not activity:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(activity, field, value)
        
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def delete_activity(self, activity_id: int) -> bool:
        """Supprime (désactive) une activité"""
        activity = self.get_activity_by_id(activity_id)
        if not activity:
            return False
        
        activity.is_active = False
        self.db.commit()
        return True

    def find_available_activities(self, date: datetime, filters: Dict = None) -> List[models.Activity]:
        """Trouve les activités disponibles à une date donnée"""
        query = self.db.query(models.Activity).filter(
            models.Activity.is_active == True
        )
        
        if filters:
            if "category__in" in filters:
                query = query.filter(models.Activity.category.in_(filters["category__in"]))
            if "min_age__lte" in filters:
                query = query.filter(models.Activity.min_age <= filters["min_age__lte"])
            if "family_friendly" in filters:
                query = query.filter(models.Activity.family_friendly == filters["family_friendly"])
        
        return query.all()

    def get_activities_by_category(self, category: str) -> List[models.Activity]:
        """Récupère les activités d'une catégorie donnée"""
        return self.db.query(models.Activity).filter(
            models.Activity.category == category,
            models.Activity.is_active == True
        ).all()

# === Routes API ===

@router.get("/", response_model=List[ActivityRead], summary="Liste toutes les activités")
def list_activities(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum d'éléments à retourner"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des activités disponibles avec pagination et filtrage optionnel.
    
    - **skip**: Nombre d'activités à ignorer (pour la pagination)
    - **limit**: Nombre maximum d'activités à retourner
    - **category**: Filtrer par catégorie d'activité (optionnel)
    """
    try:
        repo = ActivityRepository(db)
        
        if category:
            activities = repo.get_activities_by_category(category)
        else:
            activities = repo.get_all_activities(skip=skip, limit=limit)
        
        logger.info(f"Récupération de {len(activities)} activités (skip={skip}, limit={limit})")
        return activities
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur base de données lors de la récupération des activités: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des activités"
        )

@router.get("/{activity_id}", response_model=ActivityRead, summary="Récupère une activité par ID")
def get_activity(
    activity_id: int = Path(..., ge=1, description="ID de l'activité"),
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une activité spécifique par son ID.
    """
    try:
        repo = ActivityRepository(db)
        activity = repo.get_activity_by_id(activity_id)
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activité {activity_id} non trouvée"
            )
        
        logger.info(f"Récupération de l'activité {activity_id}: {activity.title}")
        return activity
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur base de données: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'activité"
        )

@router.post("/", response_model=ActivityRead, status_code=status.HTTP_201_CREATED, summary="Crée une nouvelle activité")
def create_activity(
    activity: ActivityCreate = Body(..., description="Données de l'activité à créer"),
    created_by_id: Optional[int] = Query(None, description="ID de l'utilisateur créateur"),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle activité dans le système.
    
    Réservé aux administrateurs et modérateurs.
    """
    try:
        repo = ActivityRepository(db)
        new_activity = repo.create_activity(activity, created_by_id)
        
        logger.info(f"Nouvelle activité créée: {new_activity.id} - {new_activity.title}")
        return new_activity
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la création d'activité: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'activité"
        )

@router.put("/{activity_id}", response_model=ActivityRead, summary="Met à jour une activité")
def update_activity(
    activity_id: int = Path(..., ge=1, description="ID de l'activité à modifier"),
    activity_update: ActivityUpdate = Body(..., description="Champs à mettre à jour"),
    db: Session = Depends(get_db)
):
    """
    Met à jour une activité existante.
    
    Seuls les champs fournis seront modifiés.
    """
    try:
        repo = ActivityRepository(db)
        updated_activity = repo.update_activity(activity_id, activity_update)
        
        if not updated_activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activité {activity_id} non trouvée"
            )
        
        logger.info(f"Activité {activity_id} mise à jour: {updated_activity.title}")
        return updated_activity
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la mise à jour: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de l'activité"
        )

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprime une activité")
def delete_activity(
    activity_id: int = Path(..., ge=1, description="ID de l'activité à supprimer"),
    db: Session = Depends(get_db)
):
    """
    Supprime (désactive) une activité du système.
    
    L'activité n'est pas physiquement supprimée mais marquée comme inactive.
    """
    try:
        repo = ActivityRepository(db)
        success = repo.delete_activity(activity_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activité {activity_id} non trouvée"
            )
        
        logger.info(f"Activité {activity_id} supprimée")
        return
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la suppression: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'activité"
        )

@router.post("/recommendations", response_model=List[RecommendationResponse], summary="Recommandations d'activités")
def get_activity_recommendations(
    request: RecommendationRequest = Body(..., description="Paramètres de recommandation"),
    db: Session = Depends(get_db)
):
    """
    Génère des recommandations d'activités personnalisées basées sur :
    - Les conditions météorologiques
    - Le profil utilisateur
    - La disponibilité des activités
    - Le contexte temporel
    """
    try:
        # Configuration des services (devrait venir d'un système de configuration)
        weather_config = {"type": "openweathermap", "cache_duration": 600}
        air_quality_config = {"type": "openaq", "cache_duration": 1800}
        
        weather_service = create_weather_service(weather_config)
        air_quality_service = create_air_quality_service(air_quality_config)
        
        # Création des repositories
        activity_repo = ActivityRepository(db)
        instance_repo = None  # À implémenter si nécessaire
        
        # Configuration du moteur de recommandation
        recommendation_engine = ActivityRecommendationEngine(
            weather_service=weather_service,
            air_quality_service=air_quality_service,
            activity_repository=activity_repo,
            instance_repository=instance_repo
        )
        
        # Récupération du profil utilisateur
        user_profile = None
        if request.user_id:
            user_profile = db.query(models.UserProfile).filter(
                models.UserProfile.user_id == request.user_id
            ).first()
        
        # Profil par défaut si pas d'utilisateur
        if not user_profile:
            # Création d'un profil temporaire avec des valeurs par défaut
            user_profile = models.UserProfile(
                outdoor_preference=0.5,
                temperature_min=5.0,
                temperature_max=30.0,
                rain_tolerance=0.2,
                wind_tolerance=20.0,
                family_friendly_only=False
            )
        
        # Configuration du contexte de recommandation
        context = RecommendationContext(
            user_profile=user_profile,
            target_date=request.target_date,
            city=request.city,
            country_code=request.country_code,
            budget_limit=request.budget_limit,
            activity_categories=request.categories,
            group_size=request.group_size
        )
        
        # Génération des recommandations
        recommendations = recommendation_engine.get_recommendations(context, request.max_results)
        
        # Récupération des conditions météo pour le contexte
        try:
            weather_data = weather_service.get_weather_for_date(
                request.city, request.target_date, request.country_code
            )
            weather_conditions = {
                "temperature": weather_data.temperature,
                "description": weather_data.description,
                "precipitation": weather_data.precipitation,
                "wind_speed": weather_data.wind_speed
            }
        except WeatherServiceException:
            weather_conditions = {"error": "Données météo indisponibles"}
        
        # Construction de la réponse
        response = []
        for rec in recommendations:
            activity = activity_repo.get_activity_by_id(rec.activity_id)
            if activity:
                response.append(RecommendationResponse(
                    activity_id=rec.activity_id,
                    activity_title=activity.title,
                    activity_category=activity.category,
                    total_score=rec.total_score,
                    weather_score=rec.weather_score,
                    preference_score=rec.preference_score,
                    availability_score=rec.availability_score,
                    reasons=rec.reasons,
                    weather_conditions=weather_conditions
                ))
        
        logger.info(f"Généré {len(response)} recommandations pour {request.city} le {request.target_date}")
        return response
        
    except WeatherServiceException as e:
        logger.error(f"Erreur service météo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service météorologique indisponible: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération de recommandations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la génération des recommandations"
        )

@router.get("/by-date/{date}", response_model=List[ActivityRead], summary="Activités par date")
def get_activities_by_date(
    date: str = Path(..., description="Date au format YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Récupère les activités programmées pour une date donnée.
    
    Retourne les activités ayant des instances prévues à cette date.
    """
    try:
        # Validation et parsing de la date
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        
        # Recherche des activités avec instances à cette date
        activities = (
            db.query(models.Activity)
            .join(models.ActivityInstance)
            .filter(
                models.Activity.is_active == True,
                models.ActivityInstance.is_cancelled == False,
                models.ActivityInstance.start_datetime <= date_obj + timedelta(days=1),
                models.ActivityInstance.end_datetime >= date_obj
            )
            .distinct()
            .all()
        )
        
        logger.info(f"Trouvé {len(activities)} activités pour le {date}")
        return activities
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur base de données: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche d'activités"
        )

@router.post("/vote", response_model=VoteResultResponse, summary="Voter pour des activités")
def vote_for_activities(
    vote_request: VoteRequest = Body(..., description="Données du vote"),
    db: Session = Depends(get_db)
):
    """
    Enregistre un vote utilisateur selon la méthode Condorcet.
    
    Permet aux utilisateurs de classer leurs activités préférées.
    """
    try:
        # Validation des activités votées
        activity_ids = vote_request.activity_ranking
        existing_activities = db.query(models.Activity.id).filter(
            models.Activity.id.in_(activity_ids),
            models.Activity.is_active == True
        ).all()
        
        existing_ids = {a.id for a in existing_activities}
        invalid_ids = set(activity_ids) - existing_ids
        
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Activités non trouvées: {list(invalid_ids)}"
            )
        
        # Enregistrement du vote en base
        new_vote = models.Vote(
            user_id=vote_request.user_id,
            activity_ranking=activity_ids,
            vote_context=vote_request.vote_context or {}
        )
        
        db.add(new_vote)
        db.commit()
        
        # Calcul des résultats Condorcet pour toutes les activités votées
        all_votes = db.query(models.Vote).filter(
            models.Vote.activity_ranking.op('?&')(activity_ids)  # PostgreSQL JSON operator
        ).all()
        
        # Extraction des classements pour le calcul Condorcet
        rankings = [vote.activity_ranking for vote in all_votes]
        
        # Calcul du résultat avec le système Condorcet
        voting_system = CondorcetVotingSystem(tie_breaking_method="margin")
        
        try:
            result = voting_system.conduct_election(rankings, activity_ids)
            
            # Construction de la réponse
            response = VoteResultResponse(
                winner=result.winner,
                total_votes=result.vote_count,
                ranking=result.ranking,
                pairwise_comparisons={
                    str(a): {str(b): result.pairwise_matrix[a][b] for b in result.pairwise_matrix[a]}
                    for a in result.pairwise_matrix
                },
                has_condorcet_winner=result.winner is not None,
                smith_set=result.smith_set
            )
            
            logger.info(f"Vote enregistré pour l'utilisateur {vote_request.user_id}. Gagnant: {result.winner}")
            return response
            
        except VoteValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur de validation du vote: {str(e)}"
            )
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de l'enregistrement du vote: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement du vote"
        )

@router.get("/categories", response_model=List[str], summary="Liste des catégories")
def get_activity_categories(db: Session = Depends(get_db)):
    """
    Récupère la liste de toutes les catégories d'activités disponibles.
    """
    try:
        categories = db.query(models.Activity.category).filter(
            models.Activity.is_active == True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        category_list.sort()
        
        logger.info(f"Trouvé {len(category_list)} catégories d'activités")
        return category_list
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des catégories"
        )
