from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

PROJECT_DATA_FILE = BASE_DIR / "data" / "projects.csv"
OUTPUT_FILE = BASE_DIR / "ml" / "ml_dataset.csv"


def build_ml_dataset():
    # ---------------------------------------------------------
    # 1. Load project data
    # ---------------------------------------------------------

    df = pd.read_csv(PROJECT_DATA_FILE)

    # ---------------------------------------------------------
    # 2. Convert dates
    # ---------------------------------------------------------

    df["start_date"] = pd.to_datetime(df["start_date"])
    df["expected_completion_date"] = pd.to_datetime(
        df["expected_completion_date"]
    )

    # ---------------------------------------------------------
    # 3. Basic feature engineering
    # ---------------------------------------------------------

    df["project_duration_days"] = (
        df["expected_completion_date"] - df["start_date"]
    ).dt.days

    df["cost_variance"] = (
        df["current_cost"]
        - (df["budget"] * df["actual_progress"] / 100)
    )

    df["cost_variance_percentage"] = (
        df["cost_variance"] / df["budget"]
    ) * 100

    df["progress_variance"] = (
        df["planned_progress"] - df["actual_progress"]
    )

    df["budget_utilization"] = (
        df["current_cost"] / df["budget"]
    ) * 100

    df["is_delayed"] = (
        df["actual_progress"] < df["planned_progress"]
    ).astype(int)

    # ---------------------------------------------------------
    # 4. Create ML target variables
    # ---------------------------------------------------------

    # Estimated final cost based on current spending rate.
    progress_ratio = (
        df["actual_progress"].clip(lower=1) / 100
    )

    df["predicted_final_cost_target"] = (
        df["current_cost"] / progress_ratio
    )

    df["cost_overrun_target"] = (
        (
            df["predicted_final_cost_target"]
            - df["budget"]
        )
        / df["budget"]
    ) * 100

    # Estimated delay target.
    # Larger progress gaps produce larger estimated delays.
    df["delay_days_target"] = (
        df["progress_variance"].clip(lower=0)
        * 3
    ).round().astype(int)

    # ---------------------------------------------------------
    # 5. Create risk target
    # ---------------------------------------------------------

    risk_score = (
        df["progress_variance"].clip(lower=0) * 3
        + df["cost_variance_percentage"].clip(lower=0) * 2
        + df["budget_utilization"].clip(lower=0) * 0.5
    )

    df["risk_score_target"] = risk_score.clip(
        lower=0,
        upper=100
    )

    df["risk_level_target"] = pd.cut(
        df["risk_score_target"],
        bins=[-1, 30, 60, 100],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    # ---------------------------------------------------------
    # 6. Save ML dataset
    # ---------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("ML dataset created successfully.")
    print(f"Total records: {len(df)}")
    print(f"Output file: {OUTPUT_FILE}")

    print("\nML features:")

    features = [
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

    for feature in features:
        print(f"- {feature}")

    print("\nTarget variables:")

    targets = [
        "predicted_final_cost_target",
        "cost_overrun_target",
        "delay_days_target",
        "risk_score_target",
        "risk_level_target",
    ]

    for target in targets:
        print(f"- {target}")

    print("\nSample data:")
    print(
        df[
            [
                "project_name",
                "cost_overrun_target",
                "delay_days_target",
                "risk_score_target",
                "risk_level_target",
            ]
        ].head()
    )


if __name__ == "__main__":
    build_ml_dataset()