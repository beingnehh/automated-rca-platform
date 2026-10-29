
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from devices import DEVICES
from alarm_generator import generate_scenario
from rca_engine import run_rca
from database import (
    init_db,
    save_device_inventory,
    save_incident,
    fetch_all_alarms,
    fetch_all_incidents,
    fetch_incident_details,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Automated RCA | Network Operations",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PREMIUM DARK THEME
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg-main: #0b1120;
        --bg-card: #141f32;
        --border-color: #2b3b52;
        --accent: #38bdf8;
        --text-main: #f8fafc;
        --text-muted: #cbd5e1;
    }

    /* Main application */
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #0b1120 !important;
        color: #f8fafc !important;
    }

    [data-testid="stHeader"] {
        background: #0b1120 !important;
        border-bottom: 1px solid #1e293b;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1650px;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* General typography */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    p, li, label {
        color: #e2e8f0;
    }

    [data-testid="stCaptionContainer"] {
        color: #cbd5e1 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #101a2b !important;
        border-right: 1px solid #26364d;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #dbe5f1 !important;
    }

    /* Dashboard hero banner */
    .hero {
        background:
            radial-gradient(
                circle at 90% 15%,
                rgba(56, 189, 248, 0.16),
                transparent 32%
            ),
            linear-gradient(120deg, #172554, #111c2e 72%);
        border: 1px solid #334b6a;
        border-radius: 18px;
        padding: 30px 32px;
        margin: 8px 0 26px 0;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.20);
    }

    .hero-label {
        display: inline-block;
        color: #7dd3fc !important;
        background: rgba(56, 189, 248, 0.10);
        border: 1px solid rgba(56, 189, 248, 0.30);
        border-radius: 20px;
        padding: 5px 11px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin-bottom: 16px;
    }

    .hero h1 {
        color: #ffffff !important;
        font-size: clamp(26px, 3vw, 36px) !important;
        font-weight: 800 !important;
        letter-spacing: -0.7px;
        margin: 0 0 10px 0;
    }

    .hero p {
        color: #d5e2f1 !important;
        font-size: 15px !important;
        line-height: 1.7;
        margin: 0;
    }

    /* Section titles */
    .section-title {
        color: #f8fafc !important;
        font-size: 21px;
        font-weight: 750;
        margin: 8px 0 14px 0;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #18263b, #111c2e);
        border: 1px solid #30445e;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.15);
        transition: border-color 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: #38bdf8;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 14px !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 30px !important;
        font-weight: 750 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #7dd3fc !important;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 9px;
        min-height: 43px;
        font-weight: 650;
        border: 1px solid #38516f;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #38bdf8;
        color: #7dd3fc;
    }

    /* Inputs */
    [data-testid="stWidgetLabel"] p {
        color: #e2e8f0 !important;
    }

    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] div {
        color: #111827;
    }

    [data-testid="stTextInput"] input {
        color: #111827 !important;
        background: #ffffff !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #7dd3fc !important;
    }

    /* Data tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #2b3b52;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Dividers */
    hr {
        border-color: #26364d !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Download buttons */
    [data-testid="stDownloadButton"] button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

init_db()
save_device_inventory(DEVICES)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def to_dataframe(data):
    """Convert returned database data into a DataFrame."""

    if data is None:
        return pd.DataFrame()

    if isinstance(data, pd.DataFrame):
        return data.copy()

    try:
        return pd.DataFrame(data)
    except (TypeError, ValueError):
        return pd.DataFrame()


def find_column(df, possible_names):
    """Find a matching column without case sensitivity."""

    if df.empty:
        return None

    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    return None


def display_dataframe(df, empty_message):
    """Display a table or an empty-state message."""

    if df.empty:
        st.info(empty_message)
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


def make_csv_download(df, filename, button_label):
    """Add a CSV export button when data is available."""

    if not df.empty:
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=button_label,
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            key=f"download_{filename}",
        )


def load_alarms():
    try:
        return to_dataframe(fetch_all_alarms())
    except Exception as error:
        st.warning(f"Could not load alarm records: {error}")
        return pd.DataFrame()


def load_incidents():
    try:
        return to_dataframe(fetch_all_incidents())
    except Exception as error:
        st.warning(f"Could not load incidents: {error}")
        return pd.DataFrame()


def search_dataframe(df, query):
    """Search string columns without treating input as a regex."""

    if df.empty or not query.strip():
        return df.copy()

    result = df.copy()

    searchable_columns = [
        column
        for column in result.columns
        if (
            result[column].dtype == "object"
            or pd.api.types.is_string_dtype(result[column])
        )
    ]

    if not searchable_columns:
        return result

    matches = result[searchable_columns].fillna("").astype(str).apply(
        lambda column: column.str.contains(
            query,
            case=False,
            regex=False,
        )
    ).any(axis=1)

    return result[matches]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 🌐 Automated RCA")
st.sidebar.caption("NETWORK OPERATIONS CENTER")

st.sidebar.divider()

st.sidebar.subheader("Scenario Simulator")

scenario_choice = st.sidebar.selectbox(
    "Choose a network scenario",
    options=[
        "router_failure",
        "switch_failure",
        "recovery",
    ],
    format_func=lambda value: {
        "router_failure": "Router Failure",
        "switch_failure": "Switch Failure",
        "recovery": "Network Recovery",
    }.get(value, value),
)
from rca_engine import run_rca
from alarm_generator import generate_scenario
from database import save_incident

# Inside your sidebar button logic:
if st.sidebar.button("🚨 Run Simulation", use_container_width=True):
    try:
        # Generate raw scenario alarms
        raw_alarms = generate_scenario(scenario_choice)
        
        # Try calling FastAPI backend (if running locally)
        response = requests.post("http://127.0.0.1:8000/api/v1/alarms/ingest", json=raw_alarms, timeout=2)
        if response.status_code == 200:
            st.sidebar.success("Simulation processed via FastAPI Backend!")
        else:
            raise Exception("API returned non-200 status")
            
    except Exception:
        # Fallback for Cloud Deployment: Run backend RCA engine directly in Python!
        raw_alarms = generate_scenario(scenario_choice)
        incidents = run_rca(raw_alarms)
        for inc in incidents:
            save_incident(inc)
        st.sidebar.success("Simulation processed directly by RCA Engine!")
        
    st.rerun()



# ============================================================
# DASHBOARD HEADER
# ============================================================



# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    """
<div style="background:linear-gradient(120deg,#172554,#102a43);
            border:1px solid #334b6a;
            border-radius:18px;
            padding:30px;
            margin-bottom:24px;">

<div style="color:#7dd3fc;
            font-size:11px;
            font-weight:700;
            letter-spacing:1.5px;
            margin-bottom:14px;">
NETWORK OPERATIONS CENTER
</div>

<h1 style="color:white;font-size:34px;font-weight:800;margin:0 0 12px 0;">
Automated Root Cause Analysis
</h1>

<p style="color:#d5e2f1;font-size:16px;margin:0;line-height:1.7;">
Intelligent alarm correlation, root cause detection,
and incident triage — all in one place.
</p>

</div>
    """,
    unsafe_allow_html=True,
)




# ============================================================
# LOAD DATA
# ============================================================

alarms_df = load_alarms()
incidents_df = load_incidents()
devices_df = to_dataframe(DEVICES)


# ============================================================
# KEY PERFORMANCE INDICATORS
# ============================================================

root_cause_column = find_column(
    incidents_df,
    ["root_cause", "root_cause_device", "cause", "root_device"],
)

if root_cause_column is not None:
    root_cause_count = int(
        incidents_df[root_cause_column]
        .dropna()
        .astype(str)
        .nunique()
    )
else:
    root_cause_count = 0


status_column = find_column(
    incidents_df,
    ["status", "incident_status", "state"],
)

if status_column is not None:
    status_values = (
        incidents_df[status_column]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    active_count = int(
        status_values.str.contains(
            "open|active|ongoing|investigating",
            regex=True,
        ).sum()
    )
else:
    active_count = len(incidents_df)


st.markdown(
    '<div class="section-title">System Overview</div>',
    unsafe_allow_html=True,
)

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "Total Alarms",
    f"{len(alarms_df):,}",
    help="Alarm records currently returned by the database.",
)

metric2.metric(
    "Total Incidents",
    f"{len(incidents_df):,}",
    help="Incident records currently returned by the database.",
)

metric3.metric(
    "Root Causes Identified",
    f"{root_cause_count:,}",
    help="Unique root-cause values available in the incident records.",
)

metric4.metric(
    "Active Incidents",
    f"{active_count:,}",
    help="Incidents whose status is identified as active or open.",
)

st.divider()


# ============================================================
# DASHBOARD TABS
# ============================================================

tab_incidents, tab_alarms, tab_topology, tab_analytics = st.tabs(
    [
        "🚨 Incident Triage",
        "📡 Raw Alarm Stream",
        "🗺️ Network Topology",
        "📊 Analytics",
    ]
)


# ============================================================
# TAB 1: INCIDENT TRIAGE
# ============================================================

with tab_incidents:
    st.markdown(
        '<div class="section-title">Incident Management</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Review detected incidents, search records, and export results."
    )

    if incidents_df.empty:
        st.info(
            "No incidents are available yet. "
            "Choose a scenario in the sidebar and run RCA Analysis."
        )
    else:
        col_search, col_status = st.columns([2, 1])

        with col_search:
            incident_search = st.text_input(
                "Search incidents",
                placeholder="Search device, cause, status or description...",
                key="incident_search",
            )

        with col_status:
            incident_status_column = find_column(
                incidents_df,
                ["status", "incident_status", "state"],
            )

            if incident_status_column is not None:
                available_statuses = (
                    incidents_df[incident_status_column]
                    .fillna("Unknown")
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected_statuses = st.multiselect(
                    "Filter by status",
                    options=available_statuses,
                    default=available_statuses,
                    key="incident_status_filter",
                )
            else:
                selected_statuses = []

        filtered_incidents = search_dataframe(
            incidents_df,
            incident_search,
        )

        if incident_status_column is not None:
            filtered_incidents = filtered_incidents[
                filtered_incidents[incident_status_column]
                .fillna("Unknown")
                .astype(str)
                .isin(selected_statuses)
            ]

        st.caption(
            f"Showing {len(filtered_incidents)} of "
            f"{len(incidents_df)} incidents"
        )

        display_dataframe(
            filtered_incidents,
            "No incidents match the selected filters.",
        )

        make_csv_download(
            filtered_incidents,
            "rca_incidents.csv",
            "⬇ Export Incidents",
        )

        id_column = find_column(
            incidents_df,
            ["id", "incident_id"],
        )

        if id_column is not None:
            st.divider()
            st.subheader("Incident Details")

            incident_ids = incidents_df[id_column].dropna().tolist()

            if incident_ids:
                selected_incident = st.selectbox(
                    "Select an incident",
                    options=incident_ids,
                    key="incident_details_select",
                )

                if st.button(
                    "View Incident Details",
                    key="view_incident_details",
                ):
                    try:
                        details = fetch_incident_details(
                            selected_incident
                        )

                        details_df = to_dataframe(details)

                        if not details_df.empty:
                            display_dataframe(
                                details_df,
                                "No additional details available.",
                            )
                        elif isinstance(details, dict):
                            st.json(details)
                        elif details is not None:
                            st.write(details)
                        else:
                            st.info(
                                "No additional details were returned."
                            )

                    except Exception as error:
                        st.warning(
                            "Could not load incident details. "
                            "Check fetch_incident_details() in database.py."
                        )
                        st.exception(error)


# ============================================================
# TAB 2: RAW ALARM STREAM
# ============================================================

with tab_alarms:
    st.markdown(
        '<div class="section-title">Raw Network Alarm Records</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Raw alarms remain available for investigation, even when "
        "multiple alarms are associated with a single incident."
    )

    if alarms_df.empty:
        st.info(
            "No alarm records are available. "
            "Run a scenario to generate alarm data."
        )
    else:
        col_search, col_severity = st.columns([2, 1])

        with col_search:
            alarm_search = st.text_input(
                "Search alarm records",
                placeholder="Search device, message or alarm type...",
                key="alarm_search",
            )

        with col_severity:
            severity_column = find_column(
                alarms_df,
                ["severity", "level", "priority"],
            )

            if severity_column is not None:
                severities = (
                    alarms_df[severity_column]
                    .fillna("Unknown")
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected_severities = st.multiselect(
                    "Filter by severity",
                    options=severities,
                    default=severities,
                    key="alarm_severity_filter",
                )
            else:
                selected_severities = []

        filtered_alarms = search_dataframe(
            alarms_df,
            alarm_search,
        )

        if severity_column is not None:
            filtered_alarms = filtered_alarms[
                filtered_alarms[severity_column]
                .fillna("Unknown")
                .astype(str)
                .isin(selected_severities)
            ]

        st.caption(
            f"Showing {len(filtered_alarms)} of {len(alarms_df)} alarm records"
        )

        display_dataframe(
            filtered_alarms,
            "No alarm records match the selected filters.",
        )

        make_csv_download(
            filtered_alarms,
            "network_alarms.csv",
            "⬇ Export Alarm Records",
        )


# ============================================================
# TAB 3: NETWORK TOPOLOGY
# ============================================================

with tab_topology:
    st.markdown(
        '<div class="section-title">Network Device Inventory</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Review the devices configured in your network inventory."
    )

    if devices_df.empty:
        st.info(
            "No device inventory could be displayed. "
            "Check the DEVICES structure in devices.py."
        )
    else:
        device_type_column = find_column(
            devices_df,
            ["type", "device_type", "category", "role"],
        )

        device_metric1, device_metric2 = st.columns(2)

        device_metric1.metric(
            "Configured Devices",
            len(devices_df),
        )

        if device_type_column is not None:
            device_metric2.metric(
                "Device Types",
                devices_df[device_type_column].nunique(),
            )
        else:
            device_metric2.metric(
                "Inventory Fields",
                len(devices_df.columns),
            )

        display_dataframe(
            devices_df,
            "No configured devices were found.",
        )

        make_csv_download(
            devices_df,
            "network_device_inventory.csv",
            "⬇ Export Device Inventory",
        )

        if device_type_column is not None:
            type_counts = (
                devices_df[device_type_column]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .reset_index()
            )

            type_counts.columns = ["Device Type", "Count"]

            fig_types = px.bar(
                type_counts,
                x="Device Type",
                y="Count",
                color="Device Type",
                title="Devices by Type",
                template="plotly_dark",
            )

            fig_types.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                title_font_color="#f8fafc",
                margin=dict(l=10, r=10, t=55, b=10),
            )

            st.plotly_chart(
                fig_types,
                use_container_width=True,
            )


# ============================================================
# TAB 4: ANALYTICS
# ============================================================

with tab_analytics:
    st.markdown(
        '<div class="section-title">Network Analytics</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Explore alarm severity, incident status and alarm activity."
    )

    if alarms_df.empty and incidents_df.empty:
        st.info(
            "Analytics will appear after alarm records or incidents "
            "have been saved to the database."
        )
    else:
        chart_left, chart_right = st.columns(2)

        # Alarm severity distribution
        with chart_left:
            st.subheader("Alarm Severity")

            severity_column = find_column(
                alarms_df,
                ["severity", "level", "priority"],
            )

            if severity_column is not None and not alarms_df.empty:
                severity_counts = (
                    alarms_df[severity_column]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )

                severity_counts.columns = ["Severity", "Count"]

                severity_fig = px.pie(
                    severity_counts,
                    names="Severity",
                    values="Count",
                    hole=0.58,
                    title="Alarms by Severity",
                    template="plotly_dark",
                )

                severity_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e2e8f0",
                    title_font_color="#f8fafc",
                    margin=dict(l=10, r=10, t=55, b=10),
                )

                st.plotly_chart(
                    severity_fig,
                    use_container_width=True,
                )
            else:
                st.info(
                    "A severity, level or priority column is needed "
                    "for this chart."
                )

        # Incident status distribution
        with chart_right:
            st.subheader("Incident Status")

            incident_status_column = find_column(
                incidents_df,
                ["status", "incident_status", "state"],
            )

            if (
                incident_status_column is not None
                and not incidents_df.empty
            ):
                status_counts = (
                    incidents_df[incident_status_column]
                    .fillna("Unknown")
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )

                status_counts.columns = ["Status", "Count"]

                status_fig = px.bar(
                    status_counts,
                    x="Status",
                    y="Count",
                    color="Status",
                    title="Incidents by Status",
                    template="plotly_dark",
                )

                status_fig.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e2e8f0",
                    title_font_color="#f8fafc",
                    margin=dict(l=10, r=10, t=55, b=10),
                )

                st.plotly_chart(
                    status_fig,
                    use_container_width=True,
                )
            else:
                st.info(
                    "A status or incident_status column is needed "
                    "for this chart."
                )

        # Alarm timeline
        st.divider()
        st.subheader("Alarm Activity Timeline")

        timestamp_column = find_column(
            alarms_df,
            [
                "timestamp",
                "time",
                "created_at",
                "event_time",
                "alarm_time",
            ],
        )

        if timestamp_column is not None and not alarms_df.empty:
            timeline_df = alarms_df.copy()

            timeline_df[timestamp_column] = pd.to_datetime(
                timeline_df[timestamp_column],
                errors="coerce",
            )

            timeline_df = timeline_df.dropna(
                subset=[timestamp_column]
            )

            if not timeline_df.empty:
                timeline_df["Time"] = timeline_df[
                    timestamp_column
                ].dt.floor("min")

                timeline_counts = (
                    timeline_df.groupby("Time")
                    .size()
                    .reset_index(name="Alarm Count")
                )

                timeline_fig = px.line(
                    timeline_counts,
                    x="Time",
                    y="Alarm Count",
                    markers=True,
                    title="Alarm Events Over Time",
                    template="plotly_dark",
                )

                timeline_fig.update_traces(
                    line=dict(width=3),
                    marker=dict(size=7),
                )

                timeline_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e2e8f0",
                    title_font_color="#f8fafc",
                    margin=dict(l=10, r=10, t=55, b=10),
                )

                st.plotly_chart(
                    timeline_fig,
                    use_container_width=True,
                )
            else:
                st.info(
                    "The timestamp column contains no valid dates."
                )
        else:
            st.info(
                "A timestamp, time or created_at column is needed "
                "to display the alarm timeline."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        padding: 12px 0 4px 0;
        color: #94a3b8;
        font-size: 12px;
    ">
        <span style="color: #7dd3fc; font-weight: 700;">
            AUTOMATED RCA
        </span>
        &nbsp; | &nbsp;
        Python · Streamlit · SQLite · Plotly
        <br><br>
        Network monitoring and root cause analysis dashboard
    </div>
    """,
    unsafe_allow_html=True,
)

