
import os
import requests
import streamlit as st

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="SecureStack Network Security",
    page_icon="🔐",
    layout="wide"
)

# -------------------------------
# BACKEND CONFIGURATION
# -------------------------------
API_URL = os.getenv(
    "API_URL",
    "http://localhost:5000"
).rstrip("/")


# -------------------------------
# CHECK BACKEND HEALTH
# -------------------------------
def get_health():
    try:
        response = requests.get(
            f"{API_URL}/api/health",
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return None


# -------------------------------
# CHECK DATABASE STATUS
# -------------------------------
def get_status():
    try:
        response = requests.get(
            f"{API_URL}/api/status",
            timeout=5
        )

        try:
            data = response.json()
        except ValueError:
            data = None

        return response.status_code, data

    except requests.RequestException:
        return None, None


# -------------------------------
# DASHBOARD HEADER
# -------------------------------
st.title("🔐 SecureStack")
st.subheader("Network Security Monitoring Dashboard")

st.write(
    "Monitor backend availability and PostgreSQL "
    "database connectivity."
)

st.divider()


# -------------------------------
# REFRESH BUTTON
# -------------------------------
if st.button("🔄 Refresh Status"):
    st.rerun()


# -------------------------------
# FETCH STATUS
# -------------------------------
health = get_health()
status_code, status_data = get_status()


# -------------------------------
# STATUS CARDS
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🖥️ Backend")

    if health:
        st.success("ONLINE")
    else:
        st.error("OFFLINE")


with col2:
    st.markdown("### 🗄️ Database")

    if status_code == 200 and status_data:
        if status_data.get("database") == "Connected":
            st.success("CONNECTED")
        else:
            st.warning("UNKNOWN")

    elif status_code == 503:
        st.error("DISCONNECTED")

    else:
        st.warning("UNAVAILABLE")


with col3:
    st.markdown("### ❤️ API Health")

    if health:
        st.metric(
            "Status",
            health.get("status", "Unknown")
        )
    else:
        st.metric("Status", "Unavailable")


st.divider()


# -------------------------------
# BACKEND DETAILS
# -------------------------------
st.markdown("## 📊 Backend Details")

if health:
    st.json(health)
else:
    st.warning(
        "Cannot connect to Flask backend. "
        "Check that the backend is running and API_URL "
        "is configured correctly."
    )


# -------------------------------
# DATABASE DETAILS
# -------------------------------
st.markdown("## 🗄️ Database Details")

if status_data:
    st.json(status_data)

    if status_code == 200:
        st.success("PostgreSQL connection is working.")

        db_version = status_data.get(
            "database_version",
            "Unknown"
        )

        st.caption(f"Database version: {db_version}")

    elif status_code == 503:
        st.error(
            "Database connection failed. "
            "Check PostgreSQL credentials and configuration."
        )

else:
    st.warning(
        "Database status is unavailable because "
        "the Flask API could not be reached."
    )


# -------------------------------
# FOOTER
# -------------------------------
st.divider()

st.caption(
    "SecureStack | Network Security Monitoring | "
    "Streamlit Dashboard"
)

