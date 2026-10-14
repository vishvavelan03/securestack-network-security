
import os
import time
import requests
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SecureStack | Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv(
    "API_URL", "http://localhost:5000"
).rstrip("/")

# =========================
# CUSTOM CYBER UI
# =========================
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
div.stButton > button {
    background: #00dca5;
    color: #06121b;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}
div.stButton > button:hover {
    background: #65ffcf;
    color: #06121b;
}
div[data-testid="stAlert"] {
    border-radius: 10px;
}
.cyber-banner {
    background: linear-gradient(100deg, #102d42, #10213a);
    border: 1px solid #00dca5;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 22px;
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
.panel {
    background: #101f32;
    border: 1px solid #21405b;
    border-radius: 14px;
    padding: 18px;
    min-height: 115px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# API FUNCTIONS
# =========================
def fetch_endpoint(path):
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=4
        )
        try:
            data = response.json()
        except ValueError:
            data = {"message": "Invalid API response"}

        return response.status_code, data

    except requests.RequestException as exc:
        return None, {"error": str(exc)}


def is_database_connected(code, data):
    return (
        code == 200
        and data.get("database") == "Connected"
    )


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 🛡️ SECURESTACK")
    st.caption("CYBER DEFENSE CONSOLE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "API Inspector",
            "System Diagnostics"
        ]
    )

    st.divider()
    st.markdown("### ⚙️ Configuration")
    st.code(API_URL, language="text")

    if st.button("↻ Refresh Dashboard", use_container_width=True):
        st.rerun()

    st.caption("Monitoring interface • Demo edition")

# =========================
# HEADER
# =========================
st.markdown("""
<div class="cyber-banner">
    <div class="eyebrow">NETWORK OPERATIONS CENTER</div>
    <h1>SecureStack Cyber Defense</h1>
    <p class="subtle">
        Backend availability • Database connectivity • API diagnostics
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch data when the page loads or reruns
health_code, health_data = fetch_endpoint("/api/health")
db_code, db_data = fetch_endpoint("/api/status")

backend_online = (
    health_code is not None
    and health_code == 200
    and health_data.get("status") == "Online"
)

database_online = is_database_connected(db_code, db_data)

# =========================
# OVERVIEW
# =========================
if page == "Overview":
    st.markdown("### ◈ Infrastructure Overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "BACKEND",
            "ONLINE" if backend_online else "OFFLINE"
        )
        if backend_online:
            st.success("API health check passed")
        else:
            st.error("Backend unavailable")

    with c2:
        st.metric(
            "POSTGRESQL",
            "CONNECTED" if database_online else "DISCONNECTED"
        )
        if database_online:
            st.success("Database query successful")
        elif db_code == 503:
            st.error("Database connection failed")
        else:
            st.warning("Database status unavailable")

    with c3:
        st.metric(
            "HTTP STATUS",
            str(db_code) if db_code is not None else "N/A"
        )
        st.caption("Response from /api/status")

    st.divider()

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### 🟢 Health Endpoint")
        if health_data:
            st.json(health_data)
        else:
            st.info("No health response available.")

    with right:
        st.markdown("### 🗄️ Database Intelligence")
        if database_online:
            st.success("PostgreSQL connection verified")
            st.write(
                db_data.get("database_version", "Version unavailable")
            )
        else:
            st.warning(
                "Database details unavailable. "
                "Inspect the backend configuration."
            )

    st.caption(
        "Note: These indicators report API/database connectivity, "
        "not a full security audit."
    )

# =========================
# API INSPECTOR
# =========================
elif page == "API Inspector":
    st.markdown("### ◈ API Inspector")
    st.write("Inspect responses from your Flask service.")

    endpoint = st.selectbox(
        "Choose endpoint",
        ["/api/health", "/api/status"]
    )

    if st.button("Run API Request"):
        code, result = fetch_endpoint(endpoint)

        st.markdown("#### Response")
        st.metric(
            "HTTP Status",
            str(code) if code is not None else "Request failed"
        )
        st.json(result)

        if code == 200:
            st.success("Request completed successfully")
        elif code is not None:
            st.warning(f"Endpoint returned HTTP {code}")
        else:
            st.error("Could not reach the Flask backend")

    st.info(
        "This inspector sends GET requests only. "
        "It does not perform penetration testing."
    )

# =========================
# SYSTEM DIAGNOSTICS
# =========================
elif page == "System Diagnostics":
    st.markdown("### ◈ System Diagnostics")

    st.markdown("#### Backend")
    st.write("Configured API URL:")
    st.code(API_URL)

    st.write("Health endpoint response:")
    st.code(
        str(health_code) if health_code is not None else "Connection failed"
    )

    st.markdown("#### Database")
    st.write("Database endpoint response:")
    st.code(
        str(db_code) if db_code is not None else "Connection failed"
    )

    st.write("Database status payload:")
    st.json(db_data if db_data else {})

    st.markdown("#### Troubleshooting")
    st.markdown("""
    - Verify that the Flask backend is running.
    - Check the `API_URL` environment variable.
    - Verify PostgreSQL credentials and database hostname.
    - In Docker, use the Flask service name instead of `localhost`
      when both containers share the same network.
    """)

# =========================
# FOOTER
# =========================
st.divider()
st.markdown(
    '<p class="subtle">SECURESTACK • CYBER DEFENSE CONSOLE '
    '• Connectivity monitoring</p>',
    unsafe_allow_html=True
)

