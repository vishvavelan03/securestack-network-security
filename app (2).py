
import os
import requests
import streamlit as st
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="SecureStack Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv("API_URL", "http://localhost:5000").rstrip("/")

# ==========================================
# CYBER THEME
# ==========================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #0b1728, #101d30);
    color: #e6f1ff;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1400px;
}
h1, h2, h3 {
    color: #e6f1ff !important;
}
[data-testid="stMetric"] {
    background: #101f32;
    border: 1px solid #21405b;
    padding: 18px;
    border-radius: 14px;
}
.cyber-banner {
    background: linear-gradient(100deg, #102d42, #10213a);
    border: 1px solid #00dca5;
    border-radius: 16px;
    padding: 24px;
}
.eyebrow {
    color: #00e6ac;
    letter-spacing: 3px;
    font-size: 12px;
    font-weight: 800;
}
.subtle {
    color: #9db3c9;
}
.service-alert {
    background: #251c27;
    border: 1px solid #a85566;
    border-radius: 12px;
    padding: 18px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# API CONNECTION
# ==========================================
def fetch_endpoint(path):
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=4
        )

        try:
            data = response.json()
        except ValueError:
            data = {}

        return response.status_code, data

    except requests.exceptions.Timeout:
        return None, {"message": "timeout"}

    except requests.exceptions.RequestException:
        return None, {"message": "unavailable"}


def show_connection_error():
    st.markdown("""
    <div class="service-alert">
        <h3>⚠️ Backend Service Unavailable</h3>
        <p>
            The monitoring service is temporarily unreachable.
            System status cannot be verified at this time.
        </p>
        <p>
            Please check the service configuration or try again later.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 🛡️ SECURESTACK")
    st.caption("CYBER DEFENSE CONSOLE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Overview", "API Inspector", "System Diagnostics"]
    )

    st.divider()

    if st.button("🔄 Refresh Monitoring", use_container_width=True):
        st.rerun()

    st.caption("Infrastructure Monitoring Console")


# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="cyber-banner">
    <div class="eyebrow">NETWORK OPERATIONS CENTER</div>
    <h1>SecureStack Cyber Defense</h1>
    <p class="subtle">
        Backend Monitoring • Database Connectivity • API Diagnostics
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ==========================================
# GET STATUS
# ==========================================
health_code, health_data = fetch_endpoint("/api/health")
db_code, db_data = fetch_endpoint("/api/status")

backend_online = (
    health_code == 200
    and health_data.get("status") == "Online"
)

database_online = (
    db_code == 200
    and db_data.get("database") == "Connected"
)


# ==========================================
# OVERVIEW
# ==========================================
if page == "Overview":

    st.markdown("### ◈ Infrastructure Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "BACKEND SERVICE",
            "ONLINE" if backend_online else "UNAVAILABLE"
        )

    with col2:
        st.metric(
            "DATABASE",
            "CONNECTED" if database_online else "UNAVAILABLE"
        )

    with col3:
        st.metric(
            "API RESPONSE",
            str(db_code) if db_code is not None else "NO RESPONSE"
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### 🖥️ Backend Health")

        if backend_online:
            st.success("Backend service operational")
            st.json(health_data)
        else:
            show_connection_error()

    with right:
        st.markdown("### 🗄️ Database Health")

        if database_online:
            st.success("Database connection operational")
            st.write(
                db_data.get("database_version", "Version unavailable")
            )

        elif db_code == 503:
            st.warning(
                "Database connection failed. "
                "The backend is reachable, but database status is unhealthy."
            )

        else:
            st.info(
                "Database status is currently unavailable. "
                "The backend connection must be restored first."
            )


# ==========================================
# API INSPECTOR
# ==========================================
elif page == "API Inspector":

    st.markdown("### ◈ API Inspector")

    endpoint = st.selectbox(
        "Select monitoring endpoint",
        ["/api/health", "/api/status"]
    )

    if st.button("Execute Request"):

        code, result = fetch_endpoint(endpoint)

        if code == 200:
            st.success("API request successful")
            st.json(result)

        elif code is None:
            show_connection_error()

        else:
            st.warning(
                f"API request returned HTTP {code}. "
                "Please review backend service health."
            )


# ==========================================
# SYSTEM DIAGNOSTICS
# ==========================================
elif page == "System Diagnostics":

    st.markdown("### ◈ System Diagnostics")

    st.markdown("#### Backend Configuration")
    st.code(API_URL)

    st.markdown("#### Health Endpoint")

    if backend_online:
        st.success("Backend service is operational")
    else:
        st.error("Backend Service Unavailable")
        st.caption(
            "The health endpoint could not confirm backend availability."
        )

    st.markdown("#### Database Endpoint")

    if database_online:
        st.success("Database connection operational")
        st.json(db_data)

    elif db_code == 503:
        st.warning(
            "Backend responded, but the database connection is unhealthy."
        )

    else:
        st.info(
            "Database status cannot be verified until the backend is reachable."
        )

    st.markdown("#### Recommended Checks")

    st.markdown("""
    - Verify that the Flask service is running.
    - Confirm the configured backend URL.
    - Check the deployment environment and network access.
    - Verify PostgreSQL connectivity and credentials.
    - If deployed in the cloud, configure the actual backend URL.
    """)


# ==========================================
# FOOTER
# ==========================================
st.divider()

st.caption(
    "SECURESTACK • CYBER DEFENSE CONSOLE • "
    "INFRASTRUCTURE MONITORING"
)

