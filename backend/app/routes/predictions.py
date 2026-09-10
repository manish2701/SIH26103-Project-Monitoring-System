from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.prediction_service import predict_project_by_id


router = APIRouter(
    prefix="/predictions",
    tags=["AI Predictions"]
)


@router.get("/project/{project_id}")
def get_project_prediction(
    project_id: int,
    db: Session = Depends(get_db)
):
    prediction = predict_project_by_id(
        project_id,
        db
    )

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return prediction