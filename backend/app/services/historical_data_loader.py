from datetime import timedelta

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.project import Project
from ..models.milestone import Milestone
from ..models.progress_update import ProgressUpdate


MILESTONE_NAMES = [
    "Project Planning",
    "Foundation / Initial Work",
    "Main Construction",
    "Project Completion",
]


def load_historical_data():
    db: Session = SessionLocal()

    try:
        projects = db.query(Project).order_by(Project.id).all()

        milestones_added = 0
        progress_added = 0

        for project in projects:

            # ---------------------------------------------------------
            # MILESTONES
            # ---------------------------------------------------------

            existing_milestones = (
                db.query(Milestone)
                .filter(Milestone.project_id == project.id)
                .count()
            )

            if existing_milestones == 0:

                total_days = (
                    project.expected_completion_date
                    - project.start_date
                ).days

                milestone_fractions = [0.15, 0.40, 0.70, 1.00]

                for index, fraction in enumerate(milestone_fractions):

                    planned_date = (
                        project.start_date
                        + timedelta(days=int(total_days * fraction))
                    )

                    # Determine milestone status using current progress
                    required_progress = fraction * 100

                    if project.actual_progress >= required_progress:
                        actual_date = planned_date
                        status = "Completed"

                    elif project.actual_progress >= required_progress - 15:
                        actual_date = None
                        status = "In Progress"

                    else:
                        actual_date = None
                        status = "Pending"

                    milestone = Milestone(
                        project_id=project.id,
                        name=MILESTONE_NAMES[index],
                        planned_date=planned_date,
                        actual_date=actual_date,
                        status=status,
                    )

                    db.add(milestone)
                    milestones_added += 1

            # ---------------------------------------------------------
            # PROGRESS HISTORY
            # ---------------------------------------------------------

            existing_progress = (
                db.query(ProgressUpdate)
                .filter(
                    ProgressUpdate.project_id == project.id
                )
                .count()
            )

            if existing_progress == 0:

                total_days = (
                    project.expected_completion_date
                    - project.start_date
                ).days

                # Six historical checkpoints
                fractions = [
                    0.15,
                    0.30,
                    0.45,
                    0.60,
                    0.75,
                    0.90,
                ]

                for index, fraction in enumerate(fractions):

                    update_date = (
                        project.start_date
                        + timedelta(days=int(total_days * fraction))
                    )

                    # Build a realistic progress curve ending
                    # at the project's current actual progress.
                    progress_fraction = (index + 1) / len(fractions)

                    progress = (
                        project.actual_progress
                        * progress_fraction
                    )

                    # Prevent unrealistic values
                    progress = max(1.0, min(progress, 100.0))

                    # Estimate historical cost from current cost.
                    cost_fraction = (
                        0.20 + (0.80 * progress / 100)
                    )

                    cost = project.current_cost * cost_fraction

                    # Keep historical cost below current cost
                    cost = min(cost, project.current_cost)

                    if progress < project.planned_progress:
                        remarks = "Progress below planned schedule"
                    else:
                        remarks = "Progress proceeding as planned"

                    progress_update = ProgressUpdate(
                        project_id=project.id,
                        update_date=update_date,
                        progress=round(progress, 2),
                        cost=round(cost, 2),
                        remarks=remarks,
                    )

                    db.add(progress_update)
                    progress_added += 1

        db.commit()

        print("Historical project data loaded successfully.")
        print(f"Projects processed: {len(projects)}")
        print(f"Milestones added: {milestones_added}")
        print(f"Progress updates added: {progress_added}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_historical_data()