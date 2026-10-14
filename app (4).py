import os
import requests
import streamlit as st

st.set_page_config(
    page_title="SecureStack | Cyber Defense Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configure API_URL in Streamlit Cloud > App settings > Secrets:
# API_URL = "https://your-backend-service.onrender.com"
try:
    API_URL = str(st.secrets.get("API_URL", os.getenv("API_URL", ""))).strip().rstrip("/")
except Exception:
    API_URL = os.getenv("API_URL", "").strip().rstrip("/")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #0c1c30 55%, #101827 100%);
        color: #edf4ff;
    }
    [data-testid="stSidebar"] {
        background: #20232d;
        border-right: 1px solid #344256;
    }
    .hero {
        padding: 1.5rem 1.7rem;
        border: 1px solid #00cba9;
        border-radius: 18px;
        background: linear-gradient(120deg, #102b40, #102033);
        margin-bottom: 1.4rem;
    }
    .hero h1 { margin: 0; color: #f5f9ff; }
    .hero p { color: #a9c9e8; margin: .55rem 0 0 0; }
    .metric-card {
        background: #111f31;
        border: 1px solid #24435f;
        border-radius: 15px;
        padding: 1.1rem;
        min-height: 115px;
    }
    .metric-label { font-size: .85rem; color: #b8cbe0; }
    .metric-value { font-size: 1.55rem; font-weight: 700; margin-top: .45rem; }
    .small-muted { color: #a9b8ca; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api(path, timeout=8):
    """Request the configured public backend endpoint safely."""
    if not API_URL:
        return None, (
            "Backend URL is not configured. Open Streamlit Cloud → "
            "App settings → Secrets and add API_URL with your deployed "
            "backend's public HTTPS URL."
        )

    url = f"{API_URL}{path}"
    try:
        response = requests.get(url, timeout=timeout)
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": "Backend returned a non-JSON response."}

        if not response.ok:
            message = payload.get("message", f"Backend returned HTTP {response.status_code}.")
            return {"http_status": response.status_code, **payload}, str(message)

        return {"http_status": response.status_code, **payload}, None

    except requests.exceptions.Timeout:
        return None, "Backend timed out. Check whether the backend service is running."
    except requests.exceptions.ConnectionError:
        return None, "Could not reach the backend. Verify the public backend URL and deployment status."
    except requests.exceptions.RequestException:
        return None, "A network error occurred while contacting the backend."


def status_value(payload, key, fallback="Unknown"):
    if not payload:
        return fallback
    return str(payload.get(key, fallback)).upper()


with st.sidebar:
    st.markdown("## 🛡️ SECURESTACK")
    st.caption("CYBER DEFENSE CONSOLE")
    st.divider()
    page = st.radio(
        "NAVIGATION",
        ["Overview", "API Inspector", "System Diagnostics"],
        label_visibility="visible",
    )
    st.divider()
    refresh = st.button("🔄 Refresh Monitoring", use_container_width=True)
    st.caption("Infrastructure Monitoring Console")
    if API_URL:
        st.caption(f"Backend: {API_URL}")
    else:
        st.caption("Backend URL: Not configured")

if refresh:
    st.rerun()

st.markdown(
    """
    <div class="hero">
      <h1>🛡️ SecureStack</h1>
      <p>Backend Monitoring • Database Connectivity • API Diagnostics</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Overview":
    health, health_error = get_api("/api/health")
    status, status_error = get_api("/api/status")

    backend_state = "ONLINE" if health and health.get("backend") == "Connected" else "UNAVAILABLE"
    database_state = status_value(status, "database", "UNAVAILABLE")
    api_state = f"HTTP {health['http_status']}" if health else "NO RESPONSE"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">BACKEND SERVICE</div>'
            f'<div class="metric-value">{backend_state}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">DATABASE</div>'
            f'<div class="metric-value">{database_state}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">API RESPONSE</div>'
            f'<div class="metric-value">{api_state}</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("🖥️ Backend Health")
        if health:
            st.success("Backend service is reachable.")
            st.json(health)
        else:
            st.error("Backend service is unavailable.")
            st.write(health_error)
            st.caption("Check the deployed backend URL and its service logs.")

    with right:
        st.subheader("🗄️ Database Health")
        if status and status.get("database") == "Connected":
            st.success("Database connection is healthy.")
            if status.get("database_version"):
                st.caption(f"Database version: {status['database_version']}")
        elif status:
            st.warning(status.get("message", "Backend responded, but the database is not connected."))
        else:
            st.info("Database status cannot be checked until the backend is reachable.")
            if status_error:
                st.caption(status_error)

elif page == "API Inspector":
    st.subheader("🔎 API Inspector")
    st.write("Check the public backend endpoints configured for this app.")
    endpoint = st.selectbox(
        "Choose endpoint",
        ["/", "/api/health", "/api/status", "/api/ready"],
    )
    if st.button("Send GET Request", type="primary"):
        with st.spinner("Contacting backend..."):
            result, error = get_api(endpoint)
        if result is not None:
            st.write(f"HTTP status: {result.get('http_status', 'Unknown')}")
            if error:
                st.warning(error)
            st.json(result)
        else:
            st.error(error)

elif page == "System Diagnostics":
    st.subheader("🧰 System Diagnostics")
    st.write("This page checks configuration and backend reachability.")
    st.markdown("**Backend URL configured:** " + ("Yes" if API_URL else "No"))
    if API_URL:
        st.code(API_URL, language=None)
        if st.button("Run Diagnostics", type="primary"):
            with st.spinner("Running checks..."):
                health, health_error = get_api("/api/health")
                status, status_error = get_api("/api/status")
            st.markdown("**Backend health**")
            if health:
                st.success("Reachable")
                st.json(health)
            else:
                st.error(health_error)
            st.markdown("**Database status**")
            if status and status.get("database") == "Connected":
                st.success("Connected")
                st.json(status)
            elif status:
                st.warning(status.get("message", "Database is disconnected."))
                st.json(status)
            else:
                st.info(status_error or "Database status is unavailable.")
    else:
        st.error(
            'Add this to Streamlit Cloud → App settings → Secrets, '
            'using your real deployed backend URL:\n\n'
            'API_URL = "https://your-backend-service.onrender.com"'
        )

st.divider()
st.markdown(
    '<p class="small-muted">SecureStack • Monitoring is based on responses from your configured backend.</p>',
    unsafe_allow_html=True,
)
