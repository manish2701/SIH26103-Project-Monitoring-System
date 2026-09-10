from sqlalchemy.orm import Session

from ..models.alert import Alert
from ..models.project import Project
from .prediction_service import predict_project


def create_alert_if_new(
    project: Project,
    db: Session,
    severity: str,
    title: str,
    message: str,
):
    """
    Create an alert only if the same unresolved alert
    does not already exist for this project.
    """

    existing_alert = (
        db.query(Alert)
        .filter(
            Alert.project_id == project.id,
            Alert.title == title,
            Alert.is_resolved == False,
        )
        .first()
    )

    if existing_alert:
        return None

    alert = Alert(
        project_id=project.id,
        severity=severity,
        title=title,
        message=message,
        is_resolved=False,
    )

    db.add(alert)

    return alert


def generate_project_alerts(
    project: Project,
    db: Session
):
    """
    Generate early warning alerts for a project
    based on AI predictions and current project conditions.

    Duplicate unresolved alerts are prevented.
    """

    prediction = predict_project(project)

    alerts_created = []

    risk_score = prediction["risk_score"]
    risk_level = prediction["risk_level"]
    cost_overrun = prediction["cost_overrun_percentage"]
    delay_days = prediction["predicted_delay_days"]

    progress_variance = (
        project.planned_progress
        - project.actual_progress
    )

    budget_utilization = (
        project.current_cost
        / project.budget
    ) * 100

    # =========================================================
    # 1. HIGH RISK ALERT
    # =========================================================

    if risk_score >= 60:

        alert = create_alert_if_new(
            project,
            db,
            "HIGH",
            "High Project Risk Detected",
            (
                f"AI risk score is {risk_score:.1f}/100. "
                f"The project is classified as {risk_level} risk "
                f"and requires immediate monitoring."
            ),
        )

        if alert:
            alerts_created.append(alert)

    # =========================================================
    # 2. COST OVERRUN ALERT
    # =========================================================

    if cost_overrun >= 5:

        alert = create_alert_if_new(
            project,
            db,
            "HIGH",
            "Potential Cost Overrun",
            (
                f"AI predicts a {cost_overrun:.1f}% cost overrun. "
                f"Estimated final cost is "
                f"₹{prediction['predicted_final_cost']:,.0f}."
            ),
        )

        if alert:
            alerts_created.append(alert)

    elif cost_overrun >= 2:

        alert = create_alert_if_new(
            project,
            db,
            "MEDIUM",
            "Cost Overrun Warning",
            (
                f"AI predicts a {cost_overrun:.1f}% cost overrun. "
                f"Budget utilization should be monitored."
            ),
        )

        if alert:
            alerts_created.append(alert)

    # =========================================================
    # 3. SCHEDULE DELAY ALERT
    # =========================================================

    if delay_days >= 30:

        alert = create_alert_if_new(
            project,
            db,
            "HIGH",
            "Significant Schedule Delay Risk",
            (
                f"AI predicts approximately "
                f"{delay_days} days of potential delay. "
                f"Progress is {progress_variance:.1f}% "
                f"behind the planned schedule."
            ),
        )

        if alert:
            alerts_created.append(alert)

    elif delay_days >= 10:

        alert = create_alert_if_new(
            project,
            db,
            "MEDIUM",
            "Schedule Delay Warning",
            (
                f"AI predicts approximately "
                f"{delay_days} days of potential delay. "
                f"Progress is currently "
                f"{progress_variance:.1f}% behind plan."
            ),
        )

        if alert:
            alerts_created.append(alert)

    # =========================================================
    # 4. BUDGET UTILIZATION ALERT
    # =========================================================

    if budget_utilization >= 90:

        alert = create_alert_if_new(
            project,
            db,
            "HIGH",
            "High Budget Utilization",
            (
                f"Current expenditure has reached "
                f"{budget_utilization:.1f}% of the approved budget."
            ),
        )

        if alert:
            alerts_created.append(alert)

    elif budget_utilization >= 80:

        alert = create_alert_if_new(
            project,
            db,
            "MEDIUM",
            "Budget Utilization Warning",
            (
                f"Current expenditure has reached "
                f"{budget_utilization:.1f}% of the approved budget."
            ),
        )

        if alert:
            alerts_created.append(alert)

    # =========================================================
    # 5. BEHIND-SCHEDULE ALERT
    # =========================================================

    if progress_variance >= 10:

        alert = create_alert_if_new(
            project,
            db,
            "HIGH",
            "Project Progress Behind Schedule",
            (
                f"Actual progress is "
                f"{progress_variance:.1f}% below planned progress."
            ),
        )

        if alert:
            alerts_created.append(alert)

    elif progress_variance >= 5:

        alert = create_alert_if_new(
            project,
            db,
            "MEDIUM",
            "Progress Below Plan",
            (
                f"Actual progress is "
                f"{progress_variance:.1f}% below planned progress."
            ),
        )

        if alert:
            alerts_created.append(alert)

    # =========================================================
    # SAVE ONLY NEW ALERTS
    # =========================================================

    if alerts_created:

        db.commit()

        for alert in alerts_created:
            db.refresh(alert)

    return alerts_created