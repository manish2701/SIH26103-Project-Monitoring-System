import os
import json
import urllib.error
import urllib.request

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

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
    url = f"{API_URL}{endpoint}"

    for attempt in range(2):
        try:
            with urllib.request.urlopen(
                url,
                timeout=60
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except Exception as e:
            if attempt == 1:
                st.error(f"API request failed: {url}")
                st.error(f"Error: {e}")
                return None

    return None


def api_post(endpoint):
    url = f"{API_URL}{endpoint}"

    for attempt in range(2):
        try:
            request = urllib.request.Request(
                url,
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except Exception as e:
            if attempt == 1:
                st.error(f"API request failed: {url}")
                st.error(f"Error: {e}")
                return None

    return None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f14;
        --surface: #111821;
        --surface-2: #17212d;
        --text: #f5f7fa;
        --muted: #9aa7b5;
        --border: #283443;
        --accent: #4da3ff;
        --high: #ef4444;
        --medium: #f59e0b;
        --low: #22c55e;
        --shadow: 0 10px 30px rgba(0,0,0,.24);
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 0%, rgba(77,163,255,.08), transparent 28%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(11,15,20,.92);
    }

    [data-testid="stSidebar"] {
        background: #0d131a;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    .main {
        padding-top: 1rem;
    }

    .dashboard-header {
        background: linear-gradient(135deg, #121b26 0%, #0f151d 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }

    .dashboard-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: var(--text);
        line-height: 1.15;
        letter-spacing: -0.025em;
        margin-bottom: .35rem;
    }

    .dashboard-subtitle {
        color: var(--muted);
        font-size: .96rem;
        margin: 0;
    }

    .live-badge {
        display: inline-block;
        margin-top: .75rem;
        padding: .28rem .65rem;
        border-radius: 999px;
        background: rgba(34,197,94,.12);
        border: 1px solid rgba(34,197,94,.28);
        color: #86efac;
        font-size: .76rem;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text);
        margin-top: 1.35rem;
        margin-bottom: .75rem;
    }

    .section-caption {
        color: var(--muted);
        font-size: .86rem;
        margin-top: -.35rem;
        margin-bottom: .75rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, var(--surface-2), var(--surface));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: .85rem 1rem;
        min-height: 108px;
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 800;
    }

    .attention-card {
        background: linear-gradient(145deg, #181e27, #111821);
        border: 1px solid var(--border);
        border-left: 4px solid var(--high);
        border-radius: 13px;
        padding: .8rem .95rem;
        margin-bottom: .65rem;
        box-shadow: 0 6px 18px rgba(0,0,0,.18);
    }

    .attention-card.medium {
        border-left-color: var(--medium);
    }

    .attention-name {
        color: var(--text);
        font-weight: 750;
        font-size: .92rem;
        margin-bottom: .2rem;
    }

    .attention-meta {
        color: var(--muted);
        font-size: .78rem;
    }

    .attention-score {
        color: #fca5a5;
        font-size: 1.15rem;
        font-weight: 850;
        text-align: right;
    }

    .risk-high,
    .risk-medium,
    .risk-low {
        padding: .38rem .78rem;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        font-size: .82rem;
    }

    .risk-high {
        background: rgba(239,68,68,.14);
        border: 1px solid rgba(239,68,68,.35);
        color: #fca5a5;
    }

    .risk-medium {
        background: rgba(245,158,11,.14);
        border: 1px solid rgba(245,158,11,.35);
        color: #fcd34d;
    }

    .risk-low {
        background: rgba(34,197,94,.14);
        border: 1px solid rgba(34,197,94,.35);
        color: #86efac;
    }

    .alert-card {
        padding: 1rem 1.05rem;
        border-radius: 13px;
        margin-bottom: .7rem;
        border: 1px solid var(--border);
        background: linear-gradient(145deg, var(--surface-2), var(--surface));
        color: var(--text);
        box-shadow: var(--shadow);
    }

    .alert-high {
        border-left: 4px solid var(--high);
    }

    .alert-medium {
        border-left: 4px solid var(--medium);
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background: var(--surface);
        color: var(--text);
        border-color: var(--border);
        border-radius: 9px;
    }

    input,
    textarea {
        color: var(--text) !important;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid var(--border);
        font-weight: 700;
        min-height: 2.5rem;
    }

    .stButton > button:hover {
        border-color: var(--accent);
        color: #ffffff;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }

    hr {
        border-color: var(--border) !important;
    }

    .stMarkdown p,
    .stCaption,
    .stText,
    label {
        color: var(--text);
    }

    @media print {
        @page {
            size: A4 landscape;
            margin: 10mm;
        }

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {
            background: #ffffff !important;
            color: #111827 !important;
        }

        [data-testid="stSidebar"],
        [data-testid="stHeader"],
        button,
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"] {
            display: none !important;
        }

        .dashboard-header,
        [data-testid="stMetric"],
        .attention-card,
        .alert-card {
            background: #ffffff !important;
            color: #111827 !important;
            box-shadow: none !important;
            border-color: #d1d5db !important;
        }

        .dashboard-title,
        .section-title,
        .attention-name,
        .stMarkdown p,
        .stCaption,
        label,
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"] {
            color: #111827 !important;
        }

        .dashboard-subtitle,
        .section-caption,
        .attention-meta {
            color: #4b5563 !important;
        }

        .risk-high {
            color: #991b1b !important;
            background: #fee2e2 !important;
        }

        .risk-medium {
            color: #92400e !important;
            background: #fef3c7 !important;
        }

        .risk-low {
            color: #166534 !important;
            background: #dcfce7 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="dashboard-header">
        <div class="dashboard-title">📊 AI-Powered Project Monitoring</div>
        <div class="dashboard-subtitle">
            SIH26103 • Project Monitoring & Early Warning Platform
        </div>
        <div class="live-badge">● AI MONITORING ACTIVE</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD ALL PROJECTS
# =========================================================

projects = api_get("/projects/")

if projects is None:
    st.error(
        "❌ Cannot connect to the FastAPI backend. "
        "Make sure Uvicorn is running on port 8000."
    )
    st.stop()

if not projects:
    st.warning(
        "No projects found in the database."
    )
    st.stop()


projects_df = pd.DataFrame(projects)


# =========================================================
# GENERATE AI PREDICTIONS FOR ALL PROJECTS
# =========================================================

prediction_records = []

for project in projects:

    prediction = api_get(
        f"/predictions/project/{project['id']}"
    )

    if prediction is not None:

        prediction_records.append(
            {
                "project_id": project["id"],
                "project_name": project["name"],
                "location": project["location"],
                "department": project["department"],
                "project_type": project["project_type"],
                "budget": project["budget"],
                "current_cost": project["current_cost"],
                "planned_progress": project[
                    "planned_progress"
                ],
                "actual_progress": project[
                    "actual_progress"
                ],
                "status": project["status"],
                "risk_score": prediction[
                    "risk_score"
                ],
                "risk_level": prediction[
                    "risk_level"
                ],
                "cost_overrun": prediction[
                    "cost_overrun_percentage"
                ],
                "predicted_delay": prediction[
                    "predicted_delay_days"
                ],
                "predicted_final_cost": prediction[
                    "predicted_final_cost"
                ],
            }
        )


risk_df = pd.DataFrame(
    prediction_records
)


if risk_df.empty:
    st.error(
        "Unable to generate project risk predictions."
    )
    st.stop()


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🏛️ Executive Project Overview'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    'Portfolio health, AI-generated risk signals and projects requiring attention.'
    '</div>',
    unsafe_allow_html=True,
)

total_projects = len(risk_df)

high_risk_count = len(
    risk_df[
        risk_df["risk_level"] == "HIGH"
    ]
)

medium_risk_count = len(
    risk_df[
        risk_df["risk_level"] == "MEDIUM"
    ]
)

low_risk_count = len(
    risk_df[
        risk_df["risk_level"] == "LOW"
    ]
)


# =========================================================
# EXECUTIVE KPI CARDS
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:

    st.metric(
        "Total Projects",
        total_projects
    )

with k2:

    st.metric(
        "🔴 High Risk",
        high_risk_count
    )

with k3:

    st.metric(
        "🟡 Medium Risk",
        medium_risk_count
    )

with k4:

    st.metric(
        "🟢 Low Risk",
        low_risk_count
    )


# =========================================================
# IMMEDIATE ATTENTION
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Immediate Attention Required</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    'Highest-risk projects based on the current AI risk assessment.'
    '</div>',
    unsafe_allow_html=True,
)

attention_df = (
    risk_df
    .sort_values("risk_score", ascending=False)
    .head(6)
)

attention_cols = st.columns(3)

for index, (_, row) in enumerate(attention_df.iterrows()):
    with attention_cols[index % 3]:
        risk_class = (
            "medium"
            if row["risk_level"] == "MEDIUM"
            else ""
        )

        st.markdown(
            f"""
            <div class="attention-card {risk_class}">
                <div class="attention-name">{row["project_name"]}</div>
                <div class="attention-meta">
                    {row["location"]} • {row["department"]}
                </div>
                <div style="display:flex;justify-content:space-between;align-items:end;margin-top:.45rem;">
                    <span class="attention-meta">
                        Cost +{row["cost_overrun"]:.1f}% • Delay {row["predicted_delay"]}d
                    </span>
                    <span class="attention-score">{row["risk_score"]:.1f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# EXECUTIVE CHARTS
# =========================================================

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    risk_distribution = pd.DataFrame(
        {
            "Risk Level": [
                "HIGH",
                "MEDIUM",
                "LOW"
            ],
            "Projects": [
                high_risk_count,
                medium_risk_count,
                low_risk_count
            ]
        }
    )

    fig_risk = px.pie(
        risk_distribution,
        names="Risk Level",
        values="Projects",
        hole=0.45,
        title="Project Risk Distribution"
    )

    fig_risk.update_layout(
        height=380
    )

    fig_risk.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f3f4f6",
    )

    fig_risk.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f7fa",
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(font=dict(color="#d7dee8")),
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )


with chart_col2:

    attention_df = risk_df.sort_values(
        "risk_score",
        ascending=False
    ).head(10)

    fig_attention = px.bar(
        attention_df.sort_values(
            "risk_score",
            ascending=True
        ),
        x="risk_score",
        y="project_name",
        orientation="h",
        text="risk_score",
        title="Top Projects Requiring Attention"
    )

    fig_attention.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_attention.update_xaxes(
        range=[0, 100],
        title="Risk Score"
    )

    fig_attention.update_yaxes(
        title=""
    )

    fig_attention.update_layout(
        height=380
    )

    fig_attention.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f3f4f6",
    )

    fig_attention.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f7fa",
        margin=dict(l=10, r=35, t=55, b=10),
    )

    st.plotly_chart(
        fig_attention,
        use_container_width=True
    )


# =========================================================
# PORTFOLIO RISK SUMMARY
# =========================================================

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    avg_risk = risk_df["risk_score"].mean()
    st.metric("Portfolio Avg. Risk", f"{avg_risk:.1f}/100")

with summary_col2:
    projects_with_delay = int((risk_df["predicted_delay"] > 0).sum())
    st.metric("Projects With Delay Risk", projects_with_delay)

with summary_col3:
    projects_with_overrun = int((risk_df["cost_overrun"] > 0).sum())
    st.metric("Projects With Cost Overrun", projects_with_overrun)


# =========================================================
# PROJECT RISK TABLE
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📋 Project Risk Register'
    '</div>',
    unsafe_allow_html=True,
)

search_text = st.text_input(
    "🔎 Search project, location or department",
    placeholder="Example: Ahmedabad, Metro, Urban Development..."
)


filter_col1, filter_col2 = st.columns(2)


with filter_col1:

    selected_risk = st.multiselect(
        "Risk Level",
        ["HIGH", "MEDIUM", "LOW"],
        default=[
            "HIGH",
            "MEDIUM",
            "LOW"
        ]
    )


with filter_col2:

    sort_option = st.selectbox(
        "Sort Projects By",
        [
            "Risk Score",
            "Cost Overrun",
            "Predicted Delay"
        ]
    )


filtered_df = risk_df.copy()


if selected_risk:

    filtered_df = filtered_df[
        filtered_df["risk_level"].isin(
            selected_risk
        )
    ]


if search_text:

    search_lower = (
        search_text.lower()
    )

    filtered_df = filtered_df[
        filtered_df[
            [
                "project_name",
                "location",
                "department"
            ]
        ]
        .astype(str)
        .apply(
            lambda row:
            row.str.lower()
            .str.contains(search_lower)
            .any(),
            axis=1
        )
    ]


if sort_option == "Risk Score":

    filtered_df = filtered_df.sort_values(
        "risk_score",
        ascending=False
    )

elif sort_option == "Cost Overrun":

    filtered_df = filtered_df.sort_values(
        "cost_overrun",
        ascending=False
    )

else:

    filtered_df = filtered_df.sort_values(
        "predicted_delay",
        ascending=False
    )


display_df = filtered_df[
    [
        "project_id",
        "project_name",
        "location",
        "risk_level",
        "risk_score",
        "cost_overrun",
        "predicted_delay",
        "actual_progress",
        "status"
    ]
].copy()


display_df.columns = [
    "ID",
    "Project",
    "Location",
    "Risk",
    "Risk Score",
    "Cost Overrun %",
    "Delay (Days)",
    "Actual Progress %",
    "Status"
]


display_df["Risk Score"] = (
    display_df["Risk Score"].round(1)
)

display_df["Cost Overrun %"] = (
    display_df["Cost Overrun %"].round(1)
)

display_df["Actual Progress %"] = (
    display_df["Actual Progress %"].round(1)
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# SELECT PROJECT
# =========================================================

st.sidebar.markdown(
    """
    <div style="font-size:1.25rem;font-weight:800;margin-bottom:.15rem;">
        🔎 Project Monitor
    </div>
    <div style="color:#9aa7b5;font-size:.82rem;margin-bottom:.9rem;">
        Portfolio intelligence console
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption(
    f"{total_projects} projects available"
)

project_options = {
    f"{project['id']} — {project['name']}":
    project["id"]
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
# SELECTED PROJECT DETAILS
# =========================================================

project = api_get(
    f"/projects/{selected_project_id}"
)

if project is None:

    st.error(
        "Unable to retrieve project details."
    )

    st.stop()


# =========================================================
# BASIC PROJECT METRICS
# =========================================================

budget = float(
    project["budget"]
)

current_cost = float(
    project["current_cost"]
)

planned_progress = float(
    project["planned_progress"]
)

actual_progress = float(
    project["actual_progress"]
)

progress_gap = (
    planned_progress
    - actual_progress
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

    st.error(
        "AI prediction service unavailable."
    )

    st.stop()


risk_score = float(
    prediction["risk_score"]
)

risk_level = prediction[
    "risk_level"
]

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
# PROJECT DETAIL HEADER
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '🔍 Selected Project Details'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    'Detailed monitoring, forecasts, explainability and early-warning signals for the selected project.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"## {project['name']}"
)

info1, info2, info3 = st.columns(3)

with info1:

    st.write(
        f"**Department:** "
        f"{project['department']}"
    )

with info2:

    st.write(
        f"**Location:** "
        f"{project['location']}"
    )

with info3:

    st.write(
        f"**Project Type:** "
        f"{project['project_type']}"
    )


# =========================================================
# PROJECT KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📈 Project Overview'
    '</div>',
    unsafe_allow_html=True,
)

p1, p2, p3, p4, p5 = st.columns(5)

with p1:

    st.metric(
        "Budget",
        f"₹{budget / 1e7:.1f} Cr"
    )

with p2:

    st.metric(
        "Current Cost",
        f"₹{current_cost / 1e7:.1f} Cr"
    )

with p3:

    st.metric(
        "Actual Progress",
        f"{actual_progress:.1f}%"
    )

with p4:

    st.metric(
        "Planned Progress",
        f"{planned_progress:.1f}%"
    )

with p5:

    st.metric(
        "Budget Used",
        f"{budget_utilization:.1f}%"
    )


# =========================================================
# AI RISK ASSESSMENT
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🤖 AI Risk Assessment'
    '</div>',
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
            '<div class="risk-high">'
            '🔴 HIGH RISK'
            '</div>',
            unsafe_allow_html=True
        )

    elif risk_level == "MEDIUM":

        st.markdown(
            '<div class="risk-medium">'
            '🟡 MEDIUM RISK'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="risk-low">'
            '🟢 LOW RISK'
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# PROGRESS + COST VISUALIZATION
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📊 Progress & Cost Analysis'
    '</div>',
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

    fig_progress.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f3f4f6",
    )

    fig_progress.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f7fa",
        margin=dict(l=10, r=20, t=55, b=10),
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

    fig_cost.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f3f4f6",
    )

    fig_cost.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f7fa",
        margin=dict(l=10, r=20, t=55, b=10),
    )

    st.plotly_chart(
        fig_cost,
        use_container_width=True
    )


# =========================================================
# SHAP EXPLAINABILITY
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🧠 Explainable AI — Why is this project risky?'
    '</div>',
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

        shap_df = pd.DataFrame(
            factors
        )

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

        fig_shap.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f3f4f6",
        )

        fig_shap.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f5f7fa",
            margin=dict(l=10, r=35, t=55, b=10),
        )

        st.plotly_chart(
            fig_shap,
            use_container_width=True
        )

        st.caption(
            "Positive SHAP impact indicates that "
            "the feature increases predicted risk; "
            "negative impact indicates that it "
            "reduces predicted risk."
        )

        if factors:
            top_factor = factors[0]
            direction_text = (
                "increases"
                if top_factor["impact"] > 0
                else "reduces"
            )
            st.info(
                f"Primary AI driver: **{top_factor['feature']}** "
                f"currently {direction_text} predicted risk "
                f"(SHAP impact {top_factor['impact']:.2f})."
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
    '<div class="section-title">'
    '📌 Project Milestones'
    '</div>',
    unsafe_allow_html=True,
)

milestones = api_get(
    f"/milestones/project/{selected_project_id}"
)

if milestones is not None and len(milestones) > 0:

    milestone_df = pd.DataFrame(
        milestones
    )

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
    '<div class="section-title">'
    '📈 Historical Progress'
    '</div>',
    unsafe_allow_html=True,
)

progress_history = api_get(
    f"/progress/project/{selected_project_id}"
)

if (
    progress_history is not None
    and len(progress_history) > 0
):

    progress_df = pd.DataFrame(
        progress_history
    )

    progress_df["update_date"] = (
        pd.to_datetime(
            progress_df["update_date"]
        )
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

    fig_history.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f3f4f6",
    )

    fig_history.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f7fa",
        margin=dict(l=10, r=20, t=55, b=10),
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
    '<div class="section-title">'
    '🚨 Early Warning Alerts'
    '</div>',
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

            severity = alert[
                "severity"
            ]

            if severity == "HIGH":

                icon = "🔴"

            elif severity == "MEDIUM":

                icon = "🟡"

            else:

                icon = "🟢"

            alert_class = (
                "alert-high"
                if severity == "HIGH"
                else "alert-medium"
            )

            st.markdown(
                f"""
                <div class="alert-card {alert_class}">
                    <strong>
                        {icon} {alert['title']}
                    </strong>
                    <br>
                    <span style="color:#aeb8c4;">
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
# ALERT GENERATION
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
        "AI predictions and explanations are "
        "generated from the current project data."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "SIH26103 • AI-Powered Project Monitoring "
    "& Early Warning Platform"
)