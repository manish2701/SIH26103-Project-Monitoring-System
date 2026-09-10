from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_FILE = BASE_DIR / "data" / "projects.csv"


def load_project_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)

    df["start_date"] = pd.to_datetime(df["start_date"])
    df["expected_completion_date"] = pd.to_datetime(
        df["expected_completion_date"]
    )

    return df


def clean_project_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates(subset=["project_id"])

    numeric_columns = [
        "budget",
        "current_cost",
        "planned_progress",
        "actual_progress",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=[
            "project_id",
            "budget",
            "current_cost",
            "planned_progress",
            "actual_progress",
        ]
    )

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["cost_variance"] = df["current_cost"] - (
        df["budget"] * df["actual_progress"] / 100
    )

    df["cost_variance_percentage"] = (
        df["cost_variance"] / df["budget"]
    ) * 100

    df["progress_variance"] = (
        df["planned_progress"] - df["actual_progress"]
    )

    df["is_delayed"] = (
        df["actual_progress"] < df["planned_progress"]
    ).astype(int)

    df["budget_utilization"] = (
        df["current_cost"] / df["budget"]
    ) * 100

    return df


def process_project_data() -> pd.DataFrame:
    df = load_project_data()
    df = clean_project_data(df)
    df = engineer_features(df)

    return df


if __name__ == "__main__":
    processed_df = process_project_data()

    print("Project data processed successfully.")
    print(f"Total projects: {len(processed_df)}")
    print("\nGenerated features:")
    print(
        [
            "cost_variance",
            "cost_variance_percentage",
            "progress_variance",
            "is_delayed",
            "budget_utilization",
        ]
    )

    print("\nSample processed data:")
    print(
        processed_df[
            [
                "project_name",
                "cost_variance_percentage",
                "progress_variance",
                "budget_utilization",
                "is_delayed",
            ]
        ].head()
    )