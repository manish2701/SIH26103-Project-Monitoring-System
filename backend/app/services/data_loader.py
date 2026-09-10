from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.project import Project
from .data_processor import process_project_data


def load_projects_into_database():
    df = process_project_data()

    db: Session = SessionLocal()

    try:
        # Avoid inserting duplicate projects
        existing_ids = {
            project.id
            for project in db.query(Project.id).all()
        }

        projects_added = 0

        for _, row in df.iterrows():
            project_id = int(row["project_id"])

            if project_id in existing_ids:
                continue

            project = Project(
                id=project_id,
                name=str(row["project_name"]),
                department=str(row["department"]),
                location=str(row["location"]),
                project_type=str(row["project_type"]),
                start_date=row["start_date"].date(),
                expected_completion_date=row[
                    "expected_completion_date"
                ].date(),
                budget=float(row["budget"]),
                current_cost=float(row["current_cost"]),
                planned_progress=float(row["planned_progress"]),
                actual_progress=float(row["actual_progress"]),
                status=str(row["status"]),
            )

            db.add(project)
            projects_added += 1

        db.commit()

        print("Project data loaded successfully.")
        print(f"Projects added: {projects_added}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_projects_into_database()