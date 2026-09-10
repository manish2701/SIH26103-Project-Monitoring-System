from pathlib import Path

import joblib
import pandas as pd
import shap
from sqlalchemy.orm import Session

from ..models.project import Project
from .prediction_service import prepare_project_features


BASE_DIR = Path(__file__).resolve().parents[3]

RISK_MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "risk_model.pkl"
)


def load_risk_model():
    return joblib.load(RISK_MODEL_FILE)


def explain_project_risk(
    project: Project,
    top_n: int = 5
):
    # ---------------------------------------------------------
    # 1. Load trained risk model
    # ---------------------------------------------------------

    risk_model = load_risk_model()

    # ---------------------------------------------------------
    # 2. Prepare project features
    # ---------------------------------------------------------

    features = prepare_project_features(project)

    # ---------------------------------------------------------
    # 3. Generate SHAP values
    # ---------------------------------------------------------

    explainer = shap.TreeExplainer(risk_model)

    shap_values = explainer.shap_values(features)

    # RandomForestRegressor returns a 2D array:
    # shape = (number_of_rows, number_of_features)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = shap_values[0]

    # ---------------------------------------------------------
    # 4. Build explanation table
    # ---------------------------------------------------------

    explanation = pd.DataFrame(
        {
            "feature": features.columns,
            "value": features.iloc[0].values,
            "impact": shap_values,
        }
    )

    explanation["absolute_impact"] = (
        explanation["impact"].abs()
    )

    explanation = explanation.sort_values(
        "absolute_impact",
        ascending=False
    ).head(top_n)

    # ---------------------------------------------------------
    # 5. Create human-readable explanations
    # ---------------------------------------------------------

    factors = []

    for _, row in explanation.iterrows():

        feature = row["feature"]
        value = float(row["value"])
        impact = float(row["impact"])

        if impact > 0:
            direction = "increases"
        else:
            direction = "reduces"

        factors.append(
            {
                "feature": feature,
                "value": round(value, 2),
                "impact": round(impact, 4),
                "direction": direction,
            }
        )

    # ---------------------------------------------------------
    # 6. Return explanation
    # ---------------------------------------------------------

    return {
        "project_id": project.id,
        "project_name": project.name,
        "risk_explanation": factors,
    }