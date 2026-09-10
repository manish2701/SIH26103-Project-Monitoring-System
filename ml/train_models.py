from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = BASE_DIR / "ml" / "ml_dataset.csv"
MODEL_DIR = BASE_DIR / "ml" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


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


def train_models():
    # ---------------------------------------------------------
    # 1. Load ML dataset
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_FILE)

    print(f"Dataset loaded: {len(df)} projects")

    X = df[FEATURES]

    # ---------------------------------------------------------
    # 2. Cost overrun model
    # ---------------------------------------------------------

    y_cost = df["cost_overrun_target"]

    cost_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=8
    )

    cost_model.fit(X, y_cost)

    # ---------------------------------------------------------
    # 3. Delay prediction model
    # ---------------------------------------------------------

    y_delay = df["delay_days_target"]

    delay_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=8
    )

    delay_model.fit(X, y_delay)

    # ---------------------------------------------------------
    # 4. Risk score model
    # ---------------------------------------------------------

    y_risk = df["risk_score_target"]

    risk_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=8
    )

    risk_model.fit(X, y_risk)

    # ---------------------------------------------------------
    # 5. Save trained models
    # ---------------------------------------------------------

    joblib.dump(
        cost_model,
        MODEL_DIR / "cost_overrun_model.pkl"
    )

    joblib.dump(
        delay_model,
        MODEL_DIR / "delay_model.pkl"
    )

    joblib.dump(
        risk_model,
        MODEL_DIR / "risk_model.pkl"
    )

    print("\nModels trained successfully.")

    print("\nSaved models:")

    print(
        f"- {MODEL_DIR / 'cost_overrun_model.pkl'}"
    )

    print(
        f"- {MODEL_DIR / 'delay_model.pkl'}"
    )

    print(
        f"- {MODEL_DIR / 'risk_model.pkl'}"
    )

    # ---------------------------------------------------------
    # 6. Display feature importance
    # ---------------------------------------------------------

    print("\nRisk model feature importance:")

    importance = pd.Series(
        risk_model.feature_importances_,
        index=FEATURES
    ).sort_values(ascending=False)

    print(importance)


if __name__ == "__main__":
    train_models()