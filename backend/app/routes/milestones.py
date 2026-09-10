from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.milestone import Milestone


router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"]
)


class MilestoneCreate(BaseModel):
    project_id: int
    name: str
    planned_date: date
    actual_date: date | None = None
    status: str


class MilestoneResponse(MilestoneCreate):
    id: int

    class Config:
        from_attributes = True


@router.get("/project/{project_id}", response_model=list[MilestoneResponse])
def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_db)
):
    milestones = (
        db.query(Milestone)
        .filter(Milestone.project_id == project_id)
        .all()
    )

    return milestones


@router.post(
    "/",
    response_model=MilestoneResponse,
    status_code=201
)
def create_milestone(
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db)
):
    milestone = Milestone(
        **milestone_data.model_dump()
    )

    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    milestone = (
        db.query(Milestone)
        .filter(Milestone.id == milestone_id)
        .first()
    )

    if milestone is None:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    return milestone