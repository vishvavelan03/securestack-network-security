
import os
import requests
import streamlit as st

# ==============================
# PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="SecureStack | Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv(
    "API_URL",
    "http://localhost:5000"
).rstrip("/")

# ==============================
# CUSTOM CYBER THEME
# ==============================
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
</style>
""", unsafe_allow_html=True)


# ==============================
# API REQUEST HANDLER
# ==============================
def fetch_endpoint(path):
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=4
        )

        try:
            data = response.json()
        except ValueError:
            data = {
                "message": "Backend returned an invalid response."
            }

        if not response.ok:
            return response.status_code, data, (
                f"The service returned HTTP {response.status_code}."
            )

        return response.status_code, data, None

    except requests.exceptions.Timeout:
        return None, {}, (
            "The backend took too long to respond. "
            "Check whether the service is running."
        )

    except requests.exceptions.ConnectionError:
        return None, {}, (
            "Cannot connect to the backend. "
            "Check the Flask service and API URL."
        )

    except requests.exceptions.RequestException:
        return None, {}, (
            "The request failed. Check your network and backend URL."
        )


# ==============================
# SIDEBAR
# ==============================
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
    st.code(API_URL)

    if st.button("↻ Retry Connection", use_container_width=True):
        st.rerun()


# ==============================
# DASHBOARD HEADER
# ==============================
st.markdown("""
<div class="cyber-banner">
    <div class="eyebrow">NETWORK OPERATIONS CENTER</div>
    <h1>SecureStack Cyber Defense</h1>
    <p class="subtle">
        Backend Monitoring • Database Connectivity • API Diagnostics
    </p>
</div>
""", unsafe_allow_html=True)


# ==============================
# FETCH STATUS
# ==============================
health_code, health_data, health_error = fetch_endpoint(
    "/api/health"
)

db_code, db_data, db_error = fetch_endpoint(
    "/api/status"
)

backend_online = (
    health_code == 200
    and health_data.get("status") == "Online"
)

database_online = (
    db_code == 200
    and db_data.get("database") == "Connected"
)


# ==============================
# OVERVIEW PAGE
# ==============================
if page == "Overview":

    st.markdown("### ◈ Infrastructure Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "BACKEND",
            "ONLINE" if backend_online else "OFFLINE"
        )

        if backend_online:
            st.success("Health check passed")
        else:
            st.error("Backend unavailable")

    with col2:
        st.metric(
            "POSTGRESQL",
            "CONNECTED" if database_online else "NOT CONNECTED"
        )

        if database_online:
            st.success("Database query successful")
        elif db_code == 503:
            st.error("Database connection failed")
        else:
            st.warning("Database status unavailable")

    with col3:
        st.metric(
            "API STATUS",
            str(db_code) if db_code is not None else "N/A"
        )

        st.caption("HTTP response from /api/status")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### 🟢 Health Endpoint")

        if backend_online:
            st.json(health_data)
        else:
            st.warning(
                health_error
                or "The health endpoint is unavailable."
            )

            st.markdown("**Troubleshooting:**")
            st.markdown("""
            1. Check whether Flask is running.
            2. Verify the API URL.
            3. For cloud deployment, use the deployed backend URL.
            """)

    with right:
        st.markdown("### 🗄️ Database Intelligence")

        if database_online:
            st.success("PostgreSQL connection verified")

            st.write(
                db_data.get(
                    "database_version",
                    "Version unavailable"
                )
            )

        elif db_code == 503:
            st.error(
                "Flask is reachable, but the database connection failed. "
                "Check PostgreSQL credentials and configuration."
            )

        else:
            st.warning(
                db_error or "Database details are unavailable."
            )

    st.caption(
        "Connectivity monitoring only. "
        "This dashboard does not perform a full security audit."
    )


# ==============================
# API INSPECTOR PAGE
# ==============================
elif page == "API Inspector":

    st.markdown("### ◈ API Inspector")

    endpoint = st.selectbox(
        "Choose endpoint",
        [
            "/api/health",
            "/api/status"
        ]
    )

    if st.button("Run API Request"):

        code, result, error = fetch_endpoint(endpoint)

        st.markdown("#### API Response")

        st.metric(
            "HTTP STATUS",
            str(code) if code is not None else "Unavailable"
        )

        if code == 200:
            st.success("Request completed successfully")
            st.json(result)

        elif code is not None:
            st.error(f"Request failed: HTTP {code}")
            st.warning(
                error or "The backend could not complete the request."
            )

        else:
            st.error("Backend connection failed")
            st.warning(
                error or "Check whether the backend is running."
            )

    st.info(
        "This tool sends GET requests only. "
        "It does not perform penetration testing."
    )


# ==============================
# SYSTEM DIAGNOSTICS PAGE
# ==============================
elif page == "System Diagnostics":

    st.markdown("### ◈ System Diagnostics")

    st.markdown("#### Backend Configuration")
    st.code(API_URL)

    st.markdown("#### Health Endpoint")

    if backend_online:
        st.success("Backend is reachable")
        st.json(health_data)
    else:
        st.error(
            health_error or "Health endpoint unavailable."
        )

    st.markdown("#### Database Endpoint")

    if database_online:
        st.success("Database is connected")
        st.json(db_data)

    elif db_code == 503:
        st.error(
            "PostgreSQL is disconnected. "
            "Check the database service and credentials."
        )

    else:
        st.warning(
            db_error or "Database status unavailable."
        )

    st.markdown("#### Troubleshooting Checklist")

    st.markdown("""
    - Start the Flask backend.
    - Check that the backend listens on port 5000.
    - Configure the correct API_URL.
    - Verify PostgreSQL credentials and hostname.
    - In Docker, use the backend service name.
    - In Streamlit Cloud, deploy Flask separately and use its public URL.
    """)


# ==============================
# FOOTER
# ==============================
st.divider()

st.markdown(
    '<p class="subtle">SECURESTACK • CYBER DEFENSE CONSOLE '
    '• CONNECTIVITY MONITORING</p>',
    unsafe_allow_html=True
)


