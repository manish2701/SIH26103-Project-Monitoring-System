from fastapi import FastAPI

from .routes.projects import router as projects_router
from .routes.milestones import router as milestones_router
from .routes.progress import router as progress_router
from .routes.predictions import router as predictions_router
from .routes.explainability import router as explainability_router
from .routes.alerts import router as alerts_router


app = FastAPI(
    title="SIH26103 Project Monitoring API",
    description="AI-Powered Project Monitoring & Early Warning Platform",
    version="1.0.0",
)


app.include_router(projects_router)
app.include_router(milestones_router)
app.include_router(progress_router)
app.include_router(predictions_router)
app.include_router(explainability_router)
app.include_router(alerts_router)


@app.get("/")
def root():
    return {
        "message": "SIH26103 Project Monitoring API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }