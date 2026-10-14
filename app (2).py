import os
import requests
import streamlit as st

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="SecureStack | Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set API_URL in your deployment environment when needed.
API_URL = os.getenv("API_URL", "http://localhost:5000").rstrip("/")

# ==================================================
# CYBER THEME
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f, #0b1728, #101d30);
        color: #e6f1ff;
    }
    .block-container { padding-top: 1.5rem; max-width: 1400px; }
    h1, h2, h3 { color: #e6f1ff !important; }
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
    .subtle { color: #9db3c9; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# API HELPERS - NEVER SHOW RAW EXCEPTION DETAILS
# ==================================================
def fetch_endpoint(path):
    """Return (HTTP status, JSON data, friendly error)."""
    try:
        response = requests.get(f"{API_URL}{path}", timeout=4)
        try:
            data = response.json()
        except ValueError:
            data = {"message": "The backend returned an unreadable response."}

        if not response.ok:
            return response.status_code, data, (
                f"The service returned HTTP {response.status_code}."
            )

        return response.status_code, data, None

    except requests.exceptions.Timeout:
        return None, {}, (
            "The backend took too long to respond. Check that the service is running."
        )
    except requests.exceptions.ConnectionError:
        return None, {}, (
            "Cannot connect to the backend. Make sure Flask is running "
            "and the API URL is correct."
        )
    except requests.exceptions.RequestException:
        return None, {}, (
            "The request could not be completed. Check the backend URL and network."
        )


def safe_message(data, fallback):
    """Use only a generic UI message; don't expose internal exception strings."""
    if isinstance(data, dict) and data.get("error"):
        return fallback
    return fallback


# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown("## 🛡️ SECURESTACK")
    st.caption("CYBER DEFENSE CONSOLE")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Overview", "API Inspector", "System Diagnostics"],
    )

    st.divider()
    st.markdown("### ⚙️ Configuration")
    st.code(API_URL, language="text")
    st.caption("Configure API_URL to match your Flask backend.")

    if st.button("↻ Retry connection", use_container_width=True):
        st.rerun()

# ==================================================
# HEADER
# ==================================================
st.markdown(
    """
    <div class="cyber-banner">
        <div class="eyebrow">NETWORK OPERATIONS CENTER</div>
        <h1>SecureStack Cyber Defense</h1>
        <p class="subtle">
            Backend availability • Database connectivity • API diagnostics
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

health_code, health_data, health_error = fetch_endpoint("/api/health")
db_code, db_data, db_error = fetch_endpoint("/api/status")

backend_online = (
    health_code == 200
    and isinstance(health_data, dict)
    and health_data.get("status") == "Online"
)

database_online = (
    db_code == 200
    and isinstance(db_data, dict)
    and db_data.get("database") == "Connected"
)

# ==================================================
# OVERVIEW
# ==================================================
if page == "Overview":
    st.markdown("### ◈ Infrastructure Overview")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("BACKEND", "ONLINE" if backend_online else "OFFLINE")
        if backend_online:
            st.success("Health check passed.")
        else:
            st.error("Backend unavailable.")

    with c2:
        st.metric(
            "POSTGRESQL",
            "CONNECTED" if database_online else "NOT CONNECTED",
        )
        if database_online:
            st.success("Database query successful.")
        elif db_code == 503:
            st.error("The backend could not connect to the database.")
        else:
            st.warning("Database status could not be verified.")

    with c3:
        st.metric(
            "API STATUS",
            str(db_code) if db_code is not None else "N/A",
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
                safe_message(
                    health_data,
                    health_error or "The health endpoint is unavailable.",
                )
            )
            st.markdown("**Try these steps:**")
            st.markdown(
                "1. Confirm the Flask backend is running.\n"
                "2. Check that `API_URL` points to the backend.\n"
                "3. If deployed in the cloud, use the backend's reachable URL."
            )

    with right:
        st.markdown("### 🗄️ Database Intelligence")
        if database_online:
            st.success("PostgreSQL connection verified.")
            st.write(
                db_data.get("database_version", "Version unavailable")
            )
        elif db_code == 503:
            st.error(
                "Flask is reachable, but the database connection failed. "
                "Check database credentials, hostname, and availability."
            )
        else:
            st.warning(
                safe_message(
                    db_data,
                    db_error or "Database details are unavailable.",
                )
            )

    st.caption(
        "Connectivity monitoring only. This dashboard does not perform "
        "intrusion detection or a full security audit."
    )

# ==================================================
# API INSPECTOR
# ==================================================
elif page == "API Inspector":
    st.markdown("### ◈ API Inspector")
    st.write("Send a GET request to a supported Flask endpoint.")

    endpoint = st.selectbox(
        "Choose endpoint",
        ["/api/health", "/api/status"],
    )

    if st.button("Run API Request"):
        code, result, error = fetch_endpoint(endpoint)

        st.markdown("#### Result")
        st.metric(
            "HTTP Status",
            str(code) if code is not None else "Unavailable",
        )

        if code == 200:
            st.success("Request completed successfully.")
            st.json(result)
        elif code is not None:
            st.error(f"Request failed: HTTP {code}.")
            st.warning(
                safe_message(
                    result,
                    error or "The backend could not complete this request.",
                )
            )
        else:
            st.error("Backend connection failed.")
            st.warning(
                error or "Check that the Flask service is running and reachable."
            )

    st.info(
        "This inspector sends GET requests only. It does not perform "
        "penetration testing or vulnerability scanning."
    )

# ==================================================
# SYSTEM DIAGNOSTICS
# ==================================================
elif page == "System Diagnostics":
    st.markdown("### ◈ System Diagnostics")

    st.markdown("#### Backend configuration")
    st.code(API_URL, language="text")

    st.markdown("#### Health endpoint")
    st.write(
        f"HTTP status: {health_code}"
        if health_code is not None
        else "HTTP status: No response"
    )
    if backend_online:
        st.success("Backend is reachable.")
    else:
        st.error(
            safe_message(
                health_data,
                health_error or "Health endpoint is unavailable.",
            )
        )

    st.markdown("#### Database endpoint")
    st.write(
        f"HTTP status: {db_code}"
        if db_code is not None
        else "HTTP status: No response"
    )
    if database_online:
        st.success("Database is connected.")
        st.json(db_data)
    elif db_code == 503:
        st.error(
            "Flask responded, but PostgreSQL is disconnected. "
            "Check the database service and environment variables."
        )
    else:
        st.warning(
            safe_message(
                db_data,
                db_error or "Database status is unavailable.",
            )
        )

    st.markdown("#### Troubleshooting checklist")
    st.markdown(
        "- Run the Flask backend and confirm it listens on port 5000.\n"
        "- Test `/api/health` from the same environment that runs Streamlit.\n"
        "- Set `API_URL` to the reachable Flask URL.\n"
        "- For Docker Compose, use the Flask service name on the shared network.\n"
        "- For Streamlit Cloud, deploy Flask separately; cloud `localhost` "
        "does not refer to your laptop.\n"
        "- Confirm PostgreSQL is running and the database environment variables "
        "match your deployment."
    )

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.markdown(
    '<p class="subtle">SECURESTACK • CYBER DEFENSE CONSOLE '
    '• Connectivity monitoring</p>',
    unsafe_allow_html=True,
)
