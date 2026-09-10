from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.project import Project
from ..schemas.project import ProjectCreate, ProjectResponse


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.get("/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    project = Project(**project_data.model_dump())

    db.add(project)
    db.commit()
    db.refresh(project)

    return project