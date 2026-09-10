from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.project import Project
from ..services.explainability_service import explain_project_risk


router = APIRouter(
    prefix="/explainability",
    tags=["Explainable AI"]
)


@router.get("/project/{project_id}")
def get_project_explanation(
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

    return explain_project_risk(project)