from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app import models, database
from app.services import OpenWeatherService
from app.recommender import Recommender

router = APIRouter(prefix="/activities", tags=["activities"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

from pydantic import BaseModel

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    indoor_outdoor: str = "mix"
    min_age: Optional[int] = 0

class ActivityCreate(ActivityBase):
    pass

class ActivityRead(ActivityBase):
    id: int

    class Config:
        orm_mode = True

@router.get("/", response_model=List[ActivityRead])
def list_activities(db: Session = Depends(get_db)):
    """
    Récupère la liste complète des activités disponibles.
    """
    activities = db.query(models.Activity).all()
    return activities


@router.post("/", response_model=ActivityRead)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle activité (réservée à l'administrateur).
    """
    new_activity = models.Activity(
        title=activity.title,
        description=activity.description,
        category=activity.category,
        indoor_outdoor=activity.indoor_outdoor,
        min_age=activity.min_age,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


@router.get("/by-date", response_model=List[ActivityRead])
def get_activities_by_date(
    date: str = Query(..., description="Date au format YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    Récupère les activités prévues à une date donnée (ActivityInstance).
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilise YYYY-MM-DD")

    activities = (
        db.query(models.Activity)
        .join(models.ActivityInstance)
        .filter(models.ActivityInstance.start_dt <= date_obj, models.ActivityInstance.end_dt >= date_obj)
        .all()
    )
    return activities


@router.get("/recommendations")
def recommend_activities(
    city: str,
    date: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Recommande des activités selon la météo et le profil utilisateur.
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilise YYYY-MM-DD")

    api_key = "ta_cle_api_openweather"
    weather_service = OpenWeatherService(api_key)
    aq_service = None
    activity_repo = ActivityRepository(db)

    recommender = Recommender(weather_service, aq_service, activity_repo)

    profile = {
        "outdoor_pref": 0.7,
        "children_friendly": True,
    }

    recs = recommender.recommend(city, date_obj, profile)
    return {"city": city, "date": date, "recommendations": recs}

class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_date(self, date: datetime):
        """
        Liste toutes les activités actives à une date donnée.
        """
        return (
            self.db.query(models.Activity)
            .join(models.ActivityInstance)
            .filter(models.ActivityInstance.start_dt <= date, models.ActivityInstance.end_dt >= date)
            .all()
        )

    def list_all(self):
        return self.db.query(models.Activity).all()
