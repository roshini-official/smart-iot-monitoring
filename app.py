
import random
import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="SmartBin | Waste Monitoring",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "waste_history.db"
BIN_HEIGHT_CM = 40.0
REFRESH_SECONDS = 5

BINS = [
    "Main Gate",
    "Canteen",
    "Library",
    "Parking Area",
    "Hostel",
]

# =====================================================
# 2. DATABASE SETUP
# =====================================================
def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                bin_name TEXT NOT NULL,
                distance_cm REAL NOT NULL,
                fill_level REAL NOT NULL,
                status TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'REAL SENSOR'
            )
        """)

        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(sensor_readings)"
            ).fetchall()
        ]

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE sensor_readings
                ADD COLUMN source TEXT NOT NULL DEFAULT 'REAL SENSOR'
            """)


# =====================================================
# 3. FILL-LEVEL AND STATUS CALCULATIONS
# =====================================================
def calculate_fill(distance_cm):
    distance_cm = max(0, min(BIN_HEIGHT_CM, distance_cm))
    fill = ((BIN_HEIGHT_CM - distance_cm) / BIN_HEIGHT_CM) * 100
    return round(fill, 1)


def get_status(fill_level):
    if fill_level >= 90:
        return "Critical"
    elif fill_level >= 80:
        return "Collection Required"
    elif fill_level >= 65:
        return "Nearly Full"
    else:
        return "Normal"


# =====================================================
# 4. SAVE AND LOAD READINGS
# =====================================================
def save_reading(bin_name, distance_cm, source):
    if bin_name not in BINS:
        raise ValueError("Invalid dustbin name.")

    distance_cm = float(distance_cm)

    if not 2 <= distance_cm <= BIN_HEIGHT_CM:
        raise ValueError(
            f"Distance must be between 2 and {BIN_HEIGHT_CM} cm."
        )

    fill_level = calculate_fill(distance_cm)
    status = get_status(fill_level)

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sensor_readings
            (timestamp, bin_name, distance_cm,
             fill_level, status, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            bin_name,
            distance_cm,
            fill_level,
            status,
            source,
        ))


def load_readings(limit=1000):
    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT id, timestamp, bin_name, distance_cm,
                   fill_level, status, source
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT ?
        """, conn, params=(limit,))

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
            utc=True,
        )
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp")

    return df


def generate_demo_cycle():
    """Generate clearly labelled simulated sensor readings."""
    for bin_name in BINS:
        distance = round(random.uniform(3, 38), 1)
        save_reading(bin_name, distance, "SIMULATION")


# Create the database and table if necessary.
init_db()


# =====================================================
# 5. PROFESSIONAL DASHBOARD STYLING
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #f4f7f5;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e0e8e2;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(20, 50, 30, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #526358;
    }

    .project-subtitle {
        color: #617267;
        font-size: 16px;
        margin-top: -12px;
        margin-bottom: 20px;
    }

    .simulation-banner {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 15px 0 22px 0;
        color: #1b4332;
        line-height: 1.7;
    }

    .bin-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e0e8e2;
        margin-bottom: 12px;
    }

    section[data-testid="stSidebar"] {
        background-color: #edf4ef;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# 6. SIDEBAR AND SIMULATION CONTROLS
# =====================================================
st.sidebar.title("♻️ SmartBin")
st.sidebar.caption("Smart Waste Monitoring System")
st.sidebar.divider()

st.sidebar.subheader("Simulation controls")

st.sidebar.info(
    "The current system uses software-generated readings. "
    "Real sensor data will be supported after hardware integration."
)

if st.sidebar.button(
    "Generate Demo Readings",
    type="primary",
    use_container_width=True,
):
    generate_demo_cycle()
    st.sidebar.success("Demo readings saved successfully.")
    st.rerun()

if st.sidebar.button(
    "Clear All History",
    use_container_width=True,
):
    st.session_state["confirm_clear"] = True

if st.session_state.get("confirm_clear", False):
    st.sidebar.warning(
        "This action permanently deletes saved readings."
    )

    confirm_clear = st.sidebar.checkbox(
        "I confirm that I want to delete all history."
    )

    if st.sidebar.button("Confirm Deletion"):
        if confirm_clear:
            with get_connection() as conn:
                conn.execute("DELETE FROM sensor_readings")

            st.session_state["confirm_clear"] = False
            st.rerun()
        else:
            st.sidebar.error("Please confirm before deleting.")

st.sidebar.divider()
st.sidebar.caption("Database: waste_history.db")
st.sidebar.caption("Refresh interval: 5 seconds")


# =====================================================
# 7. DASHBOARD HEADER
# =====================================================
st.title("♻️ Smart Dustbin Monitoring")

st.markdown(
    '<div class="project-subtitle">'
    'IoT-Based Waste Fill-Level Monitoring and Collection Alerts'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="simulation-banner">
    <strong>🟢 SIMULATION ENVIRONMENT</strong><br>
    The dashboard currently uses software-generated sensor readings
    to demonstrate fill-level monitoring, collection alerts, charts,
    and historical data storage. The system is designed for future
    ESP32 and ultrasonic sensor integration.
</div>
""", unsafe_allow_html=True)


# =====================================================
# 8. LIVE-REFRESHING MONITORING DASHBOARD
# =====================================================
@st.fragment(run_every=f"{REFRESH_SECONDS}s")
def monitoring_panel():

    df = load_readings()

    # Empty state before the first simulation cycle.
    if df.empty:
        st.info(
            "No readings are available yet. "
            "Click 'Generate Demo Readings' in the sidebar to begin."
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Configured Dustbins", len(BINS))
        c2.metric("Average Fill Level", "—")
        c3.metric("Critical Dustbins", 0)
        c4.metric("Collection Required", 0)

        st.subheader("Dustbin Status")
        columns = st.columns(3)

        for index, bin_name in enumerate(BINS):
            with columns[index % 3]:
                st.markdown(
                    f'<div class="bin-card"><b>{bin_name}</b><br>'
                    'Waiting for readings</div>',
                    unsafe_allow_html=True,
                )

        return

    # Select the most recent reading for each bin.
    latest = (
        df.sort_values("timestamp")
        .groupby("bin_name", as_index=False)
        .tail(1)
        .copy()
    )

    critical_count = int(
        (latest["status"] == "Critical").sum()
    )

    collection_count = int(
        (latest["status"] == "Collection Required").sum()
    )

    average_fill = round(latest["fill_level"].mean(), 1)

    # Top summary metrics.
    st.subheader("System Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Configured Dustbins", len(BINS))
    col2.metric("Average Latest Fill", f"{average_fill}%")
    col3.metric("Critical Dustbins", critical_count)
    col4.metric("Collection Required", collection_count)

    st.caption(
        f"Latest readings available for {len(latest)} "
        f"of {len(BINS)} configured dustbins."
    )

    # -------------------------------------------------
    # DUSTBIN CARDS
    # -------------------------------------------------
    st.subheader("Dustbin Status Overview")

    card_columns = st.columns(3)

    for index, bin_name in enumerate(BINS):

        with card_columns[index % 3]:

            st.markdown(
                '<div class="bin-card">',
                unsafe_allow_html=True,
            )

            st.markdown(f"#### 🗑️ {bin_name}")

            rows = latest[latest["bin_name"] == bin_name]

            if rows.empty:
                st.caption("No readings recorded")
                st.progress(0)
                st.caption("Waiting for data")

            else:
                row = rows.iloc[0]

                fill_level = float(row["fill_level"])
                progress_value = int(
                    max(0, min(100, fill_level))
                )

                st.metric("Fill Level", f"{fill_level:.1f}%")
                st.progress(progress_value)

                st.caption(
                    f'Distance from sensor: '
                    f'{row["distance_cm"]:.1f} cm'
                )

                if row["status"] == "Critical":
                    st.error("🔴 CRITICAL — Collect waste")
                elif row["status"] == "Collection Required":
                    st.warning("🟠 Collection required")
                elif row["status"] == "Nearly Full":
                    st.info("🟡 Nearly full")
                else:
                    st.success("🟢 Normal")

                st.caption(f'Source: {row["source"]}')

                reading_time = row["timestamp"].strftime(
                    "%d %b %Y, %H:%M:%S UTC"
                )

                st.caption(f"Last recorded: {reading_time}")

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # ALERT PANEL
    # -------------------------------------------------
    st.subheader("🚨 Collection Alerts")

    alerts = latest[
        latest["status"].isin(
            ["Critical", "Collection Required"]
        )
    ]

    if alerts.empty:
        st.success(
            "No collection alerts based on the latest recorded readings."
        )
    else:
        for _, row in alerts.iterrows():
            if row["status"] == "Critical":
                st.error(
                    f'🔴 {row["bin_name"]}: '
                    f'{row["fill_level"]}% full — CRITICAL'
                )
            else:
                st.warning(
                    f'🟠 {row["bin_name"]}: '
                    f'{row["fill_level"]}% full — '
                    'collection required'
                )

    # -------------------------------------------------
    # HISTORICAL CHART
    # -------------------------------------------------
    st.subheader("📈 Fill-Level History")

    chart_data = df.copy()

    fig = px.line(
        chart_data,
        x="timestamp",
        y="fill_level",
        color="bin_name",
        markers=True,
        hover_data=["distance_cm", "status", "source"],
        labels={
            "timestamp": "Reading Time",
            "fill_level": "Fill Level (%)",
            "bin_name": "Dustbin",
            "distance_cm": "Distance (cm)",
            "status": "Status",
            "source": "Data Source",
        },
    )

    fig.update_yaxes(
        range=[0, 100],
        ticksuffix="%",
    )

    fig.update_layout(
        template="plotly_white",
        height=400,
        legend_title_text="Dustbin",
        margin=dict(l=15, r=15, t=25, b=15),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # -------------------------------------------------
    # DATABASE HISTORY AND CSV EXPORT
    # -------------------------------------------------
    st.subheader("🗂️ Reading History")

    source_filter = st.selectbox(
        "Filter by data source",
        ["All Sources", "SIMULATION", "REAL SENSOR"],
    )

    filtered = df.copy()

    if source_filter != "All Sources":
        filtered = filtered[
            filtered["source"] == source_filter
        ]

    display_df = filtered.copy()

    display_df["timestamp"] = (
        display_df["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    )

    st.dataframe(
        display_df.sort_values(
            "timestamp",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download History as CSV",
        data=csv_data,
        file_name="smartbin_history.csv",
        mime="text/csv",
        use_container_width=False,
    )

    st.caption(
        f"Displaying up to 1,000 recent readings. "
        f"Total readings in this view: {len(filtered)}."
    )


monitoring_panel()


# =====================================================
# 9. FOOTER
# =====================================================
st.divider()

st.caption(
    "SmartBin | IoT-Based Smart Dustbin Fill-Level Monitoring System"
)

st.caption(
    "Current mode: Software simulation. "
    "Real sensor readings require hardware and receiver integration."
)
