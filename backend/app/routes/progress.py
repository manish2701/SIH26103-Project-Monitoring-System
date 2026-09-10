from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.progress_update import ProgressUpdate


router = APIRouter(
    prefix="/progress",
    tags=["Progress"]
)


class ProgressCreate(BaseModel):
    project_id: int
    update_date: date
    progress: float
    cost: float
    remarks: str | None = None


class ProgressResponse(ProgressCreate):
    id: int

    class Config:
        from_attributes = True


@router.get(
    "/project/{project_id}",
    response_model=list[ProgressResponse]
)
def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db)
):
    progress_updates = (
        db.query(ProgressUpdate)
        .filter(ProgressUpdate.project_id == project_id)
        .order_by(ProgressUpdate.update_date)
        .all()
    )

    return progress_updates


@router.post(
    "/",
    response_model=ProgressResponse,
    status_code=201
)
def create_progress_update(
    progress_data: ProgressCreate,
    db: Session = Depends(get_db)
):
    progress_update = ProgressUpdate(
        **progress_data.model_dump()
    )

    db.add(progress_update)
    db.commit()
    db.refresh(progress_update)

    return progress_update


@router.get(
    "/{progress_id}",
    response_model=ProgressResponse
)
def get_progress_update(
    progress_id: int,
    db: Session = Depends(get_db)
):
    progress_update = (
        db.query(ProgressUpdate)
        .filter(ProgressUpdate.id == progress_id)
        .first()
    )

    if progress_update is None:
        raise HTTPException(
            status_code=404,
            detail="Progress update not found"
        )

    return progress_update