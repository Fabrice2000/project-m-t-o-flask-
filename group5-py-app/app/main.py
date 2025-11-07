from fastapi import FastAPI
from app import models, database
from app.routers import activities, weather

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Météo Activités API")

app.include_router(weather.router)
app.include_router(activities.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Météo Activités !"}
