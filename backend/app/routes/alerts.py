from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.alert import Alert
from ..models.project import Project
from ..services.alert_service import generate_project_alerts


router = APIRouter(
    prefix="/alerts",
    tags=["Early Warning Alerts"]
)


@router.post("/generate/{project_id}")
def generate_alerts(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    alerts = generate_project_alerts(
        project,
        db
    )

    return {
        "project_id": project.id,
        "project_name": project.name,
        "alerts_generated": len(alerts),
        "alerts": [
            {
                "id": alert.id,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "is_resolved": alert.is_resolved,
            }
            for alert in alerts
        ],
    }


@router.get("/project/{project_id}")
def get_project_alerts(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    alerts = (
        db.query(Alert)
        .filter(Alert.project_id == project_id)
        .order_by(Alert.created_at.desc())
        .all()
    )

    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_alerts": len(alerts),
        "alerts": [
            {
                "id": alert.id,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at,
            }
            for alert in alerts
        ],
    }