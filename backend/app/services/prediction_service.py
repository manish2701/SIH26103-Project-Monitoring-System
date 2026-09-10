from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from ..models.project import Project


BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_DIR = BASE_DIR / "ml" / "models"

COST_MODEL_FILE = MODEL_DIR / "cost_overrun_model.pkl"
DELAY_MODEL_FILE = MODEL_DIR / "delay_model.pkl"
RISK_MODEL_FILE = MODEL_DIR / "risk_model.pkl"


FEATURES = [
    "budget",
    "current_cost",
    "planned_progress",
    "actual_progress",
    "project_duration_days",
    "cost_variance",
    "cost_variance_percentage",
    "progress_variance",
    "budget_utilization",
    "is_delayed",
]


def load_models():
    cost_model = joblib.load(COST_MODEL_FILE)
    delay_model = joblib.load(DELAY_MODEL_FILE)
    risk_model = joblib.load(RISK_MODEL_FILE)

    return cost_model, delay_model, risk_model


def prepare_project_features(project: Project) -> pd.DataFrame:
    # ---------------------------------------------------------
    # Calculate project duration
    # ---------------------------------------------------------

    project_duration_days = (
        project.expected_completion_date
        - project.start_date
    ).days

    # ---------------------------------------------------------
    # Calculate cost variance
    # ---------------------------------------------------------

    expected_cost_at_progress = (
        project.budget
        * project.actual_progress
        / 100
    )

    cost_variance = (
        project.current_cost
        - expected_cost_at_progress
    )

    cost_variance_percentage = (
        cost_variance / project.budget
    ) * 100

    # ---------------------------------------------------------
    # Calculate progress variance
    # ---------------------------------------------------------

    progress_variance = (
        project.planned_progress
        - project.actual_progress
    )

    # ---------------------------------------------------------
    # Calculate budget utilization
    # ---------------------------------------------------------

    budget_utilization = (
        project.current_cost
        / project.budget
    ) * 100

    # ---------------------------------------------------------
    # Determine delay indicator
    # ---------------------------------------------------------

    is_delayed = int(
        project.actual_progress
        < project.planned_progress
    )

    # ---------------------------------------------------------
    # Build model input
    # ---------------------------------------------------------

    data = {
        "budget": project.budget,
        "current_cost": project.current_cost,
        "planned_progress": project.planned_progress,
        "actual_progress": project.actual_progress,
        "project_duration_days": project_duration_days,
        "cost_variance": cost_variance,
        "cost_variance_percentage": cost_variance_percentage,
        "progress_variance": progress_variance,
        "budget_utilization": budget_utilization,
        "is_delayed": is_delayed,
    }

    return pd.DataFrame([data])[FEATURES]


def get_risk_level(risk_score: float) -> str:
    if risk_score >= 60:
        return "HIGH"

    if risk_score >= 30:
        return "MEDIUM"

    return "LOW"


def predict_project(project: Project):
    # ---------------------------------------------------------
    # Load trained models
    # ---------------------------------------------------------

    cost_model, delay_model, risk_model = load_models()

    # ---------------------------------------------------------
    # Prepare project features
    # ---------------------------------------------------------

    features = prepare_project_features(project)

    # ---------------------------------------------------------
    # Generate predictions
    # ---------------------------------------------------------

    predicted_cost_overrun = float(
        cost_model.predict(features)[0]
    )

    predicted_delay_days = int(
        round(delay_model.predict(features)[0])
    )

    risk_score = float(
        risk_model.predict(features)[0]
    )

    # Keep values within sensible ranges
    predicted_delay_days = max(
        0,
        predicted_delay_days
    )

    risk_score = max(
        0,
        min(risk_score, 100)
    )

    # ---------------------------------------------------------
    # Calculate predicted final cost
    # ---------------------------------------------------------

    predicted_final_cost = (
        project.budget
        * (1 + predicted_cost_overrun / 100)
    )

    # ---------------------------------------------------------
    # Determine risk level
    # ---------------------------------------------------------

    risk_level = get_risk_level(risk_score)

    return {
        "project_id": project.id,
        "project_name": project.name,
        "predicted_final_cost": round(
            predicted_final_cost,
            2
        ),
        "cost_overrun_percentage": round(
            predicted_cost_overrun,
            2
        ),
        "predicted_delay_days": predicted_delay_days,
        "risk_score": round(
            risk_score,
            2
        ),
        "risk_level": risk_level,
    }


def predict_project_by_id(
    project_id: int,
    db: Session
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        return None

    return predict_project(project)