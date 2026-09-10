import json
import urllib.error
import urllib.request

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="SIH26103 | Project Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# API HELPERS
# =========================================================

def api_get(endpoint):
    try:
        with urllib.request.urlopen(
            f"{API_URL}{endpoint}",
            timeout=10
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError:
        return None

    except Exception:
        return None


def api_post(endpoint):
    try:
        request = urllib.request.Request(
            f"{API_URL}{endpoint}",
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError:
        return None

    except Exception:
        return None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .risk-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }

    .risk-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }

    .risk-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }

    .alert-card {
        padding: 1rem;
        border-radius: 0.7rem;
        margin-bottom: 0.7rem;
        border: 1px solid #e5e7eb;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="dashboard-title">📊 AI-Powered Project Monitoring</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'SIH26103 • Project Monitoring & Early Warning Platform'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# LOAD PROJECTS
# =========================================================

projects = api_get("/projects/")

if projects is None:
    st.error(
        "❌ Cannot connect to the FastAPI backend. "
        "Make sure Uvicorn is running on port 8000."
    )
    st.stop()

if not projects:
    st.warning("No projects found in the database.")
    st.stop()


projects_df = pd.DataFrame(projects)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔎 Project Monitor")

st.sidebar.caption(
    f"{len(projects)} projects available"
)

project_options = {
    f"{project['id']} — {project['name']}": project["id"]
    for project in projects
}

selected_project_label = st.sidebar.selectbox(
    "Select Project",
    list(project_options.keys())
)

selected_project_id = project_options[
    selected_project_label
]

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Refresh Dashboard",
    use_container_width=True
):
    st.rerun()


# =========================================================
# PROJECT SELECTION
# =========================================================

project = api_get(
    f"/projects/{selected_project_id}"
)

if project is None:
    st.error("Unable to retrieve project details.")
    st.stop()


# =========================================================
# CALCULATE BASIC METRICS
# =========================================================

budget = float(project["budget"])
current_cost = float(project["current_cost"])

planned_progress = float(
    project["planned_progress"]
)

actual_progress = float(
    project["actual_progress"]
)

progress_gap = (
    planned_progress - actual_progress
)

budget_utilization = (
    current_cost / budget
) * 100


# =========================================================
# AI PREDICTION
# =========================================================

prediction = api_get(
    f"/predictions/project/{selected_project_id}"
)

if prediction is None:
    st.error("AI prediction service unavailable.")
    st.stop()


risk_score = float(
    prediction["risk_score"]
)

risk_level = prediction["risk_level"]

predicted_cost = float(
    prediction["predicted_final_cost"]
)

cost_overrun = float(
    prediction["cost_overrun_percentage"]
)

delay_days = int(
    prediction["predicted_delay_days"]
)


# =========================================================
# PROJECT HEADER
# =========================================================

st.markdown(
    f"## {project['name']}"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.write(
        f"**Department:** {project['department']}"
    )

with col2:
    st.write(
        f"**Location:** {project['location']}"
    )

with col3:
    st.write(
        f"**Project Type:** {project['project_type']}"
    )


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">📈 Project Overview</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "Budget",
        f"₹{budget / 1e7:.1f} Cr"
    )

with k2:
    st.metric(
        "Current Cost",
        f"₹{current_cost / 1e7:.1f} Cr"
    )

with k3:
    st.metric(
        "Actual Progress",
        f"{actual_progress:.1f}%"
    )

with k4:
    st.metric(
        "Planned Progress",
        f"{planned_progress:.1f}%"
    )

with k5:
    st.metric(
        "Budget Used",
        f"{budget_utilization:.1f}%"
    )


# =========================================================
# AI RISK SUMMARY
# =========================================================

st.markdown(
    '<div class="section-title">🤖 AI Risk Assessment</div>',
    unsafe_allow_html=True,
)

r1, r2, r3, r4 = st.columns(4)

with r1:
    st.metric(
        "Risk Score",
        f"{risk_score:.1f}/100"
    )

with r2:
    st.metric(
        "Cost Overrun",
        f"{cost_overrun:.1f}%"
    )

with r3:
    st.metric(
        "Predicted Delay",
        f"{delay_days} days"
    )

with r4:
    if risk_level == "HIGH":
        st.markdown(
            '<div class="risk-high">🔴 HIGH RISK</div>',
            unsafe_allow_html=True
        )

    elif risk_level == "MEDIUM":
        st.markdown(
            '<div class="risk-medium">🟡 MEDIUM RISK</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            '<div class="risk-low">🟢 LOW RISK</div>',
            unsafe_allow_html=True
        )


# =========================================================
# PROGRESS + COST VISUALIZATION
# =========================================================

st.markdown(
    '<div class="section-title">📊 Progress & Cost Analysis</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    progress_chart = pd.DataFrame(
        {
            "Metric": [
                "Planned Progress",
                "Actual Progress"
            ],
            "Progress": [
                planned_progress,
                actual_progress
            ]
        }
    )

    fig_progress = px.bar(
        progress_chart,
        x="Metric",
        y="Progress",
        range_y=[0, 100],
        text="Progress",
        title="Planned vs Actual Progress"
    )

    fig_progress.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_progress.update_layout(
        showlegend=False,
        height=350
    )

    st.plotly_chart(
        fig_progress,
        use_container_width=True
    )


with chart_col2:

    cost_chart = pd.DataFrame(
        {
            "Metric": [
                "Approved Budget",
                "Current Cost",
                "Predicted Final Cost"
            ],
            "Cost": [
                budget,
                current_cost,
                predicted_cost
            ]
        }
    )

    fig_cost = px.bar(
        cost_chart,
        x="Metric",
        y="Cost",
        text="Cost",
        title="Cost Forecast"
    )

    fig_cost.update_traces(
        texttemplate="₹%{text:.2s}",
        textposition="outside"
    )

    fig_cost.update_layout(
        showlegend=False,
        height=350
    )

    st.plotly_chart(
        fig_cost,
        use_container_width=True
    )


# =========================================================
# SHAP EXPLAINABILITY
# =========================================================

st.markdown(
    '<div class="section-title">🧠 Explainable AI — Why is this project risky?</div>',
    unsafe_allow_html=True,
)

explanation = api_get(
    f"/explainability/project/{selected_project_id}"
)

if explanation is not None:

    factors = explanation.get(
        "risk_explanation",
        []
    )

    if factors:

        shap_df = pd.DataFrame(factors)

        shap_df["impact_abs"] = (
            shap_df["impact"].abs()
        )

        shap_df = shap_df.sort_values(
            "impact_abs",
            ascending=True
        )

        fig_shap = px.bar(
            shap_df,
            x="impact",
            y="feature",
            orientation="h",
            text="impact",
            title="Top Risk Drivers"
        )

        fig_shap.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig_shap.update_layout(
            height=400
        )

        st.plotly_chart(
            fig_shap,
            use_container_width=True
        )

        st.caption(
            "Positive SHAP impact indicates that the feature "
            "increases predicted risk; negative impact indicates "
            "that it reduces predicted risk."
        )

    else:
        st.info(
            "No SHAP explanations available."
        )

else:
    st.warning(
        "Explainability service unavailable."
    )


# =========================================================
# MILESTONES
# =========================================================

st.markdown(
    '<div class="section-title">📌 Project Milestones</div>',
    unsafe_allow_html=True,
)

milestones = api_get(
    f"/milestones/project/{selected_project_id}"
)

if milestones is not None and len(milestones) > 0:

    milestone_df = pd.DataFrame(milestones)

    milestone_df = milestone_df[
        [
            "name",
            "planned_date",
            "actual_date",
            "status"
        ]
    ]

    milestone_df.columns = [
        "Milestone",
        "Planned Date",
        "Actual Date",
        "Status"
    ]

    st.dataframe(
        milestone_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "No milestone data available."
    )


# =========================================================
# PROGRESS HISTORY
# =========================================================

st.markdown(
    '<div class="section-title">📈 Historical Progress</div>',
    unsafe_allow_html=True,
)

progress_history = api_get(
    f"/progress/project/{selected_project_id}"
)

if progress_history is not None and len(progress_history) > 0:

    progress_df = pd.DataFrame(
        progress_history
    )

    progress_df["update_date"] = pd.to_datetime(
        progress_df["update_date"]
    )

    progress_df = progress_df.sort_values(
        "update_date"
    )

    fig_history = px.line(
        progress_df,
        x="update_date",
        y="progress",
        markers=True,
        title="Project Progress Trend"
    )

    fig_history.update_yaxes(
        range=[0, 100],
        title="Progress (%)"
    )

    fig_history.update_xaxes(
        title="Date"
    )

    fig_history.update_layout(
        height=350
    )

    st.plotly_chart(
        fig_history,
        use_container_width=True
    )

else:
    st.info(
        "No progress history available."
    )


# =========================================================
# EARLY WARNING ALERTS
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Early Warning Alerts</div>',
    unsafe_allow_html=True,
)

alerts = api_get(
    f"/alerts/project/{selected_project_id}"
)

if alerts is not None:

    alert_list = alerts.get(
        "alerts",
        []
    )

    if alert_list:

        for alert in alert_list:

            severity = alert["severity"]

            if severity == "HIGH":
                icon = "🔴"

            elif severity == "MEDIUM":
                icon = "🟡"

            else:
                icon = "🟢"

            st.markdown(
                f"""
                <div class="alert-card">
                    <strong>
                        {icon} {alert['title']}
                    </strong>
                    <br>
                    <span>
                        {alert['message']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.success(
            "✅ No active alerts for this project."
        )

else:
    st.warning(
        "Unable to retrieve alerts."
    )


# =========================================================
# GENERATE / REFRESH ALERTS
# =========================================================

st.divider()

button_col1, button_col2 = st.columns(2)

with button_col1:

    if st.button(
        "🚨 Generate Latest AI Alerts",
        use_container_width=True
    ):

        result = api_post(
            f"/alerts/generate/{selected_project_id}"
        )

        if result is not None:

            st.success(
                f"{result['alerts_generated']} "
                "new alerts generated."
            )

            st.rerun()

        else:

            st.error(
                "Could not generate alerts."
            )


with button_col2:

    st.info(
        "AI predictions and explanations are generated "
        "from the current project data."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "SIH26103 • AI-Powered Project Monitoring & Early Warning Platform"
)