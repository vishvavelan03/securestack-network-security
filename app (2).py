
        return None, None


st.title("🔐 SecureStack Dashboard")
st.caption("Backend & PostgreSQL Monitoring")
st.divider()

if st.button("🔄 Refresh Status"):
    st.rerun()

health = get_health()
status_code, status_data = get_status()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Backend")
    if health:
        st.success("🟢 Online")
    else:
        st.error("🔴 Offline")

with col2:
    st.subheader("Database")
    if status_code == 200 and status_data:
        st.success("🟢 Connected")
    elif status_code == 503:
        st.error("🔴 Disconnected")
    else:
        st.warning("⚪ Unknown")

with col3:
    st.subheader("API Health")
    st.metric(
        "Status",
        health.get("status", "Unavailable") if health else "Unavailable",
    )

st.divider()
st.subheader("📊 System Details")

if health:
    st.write("**Health Endpoint Response**")
    st.json(health)
else:
    st.warning(
        "Cannot reach Flask backend. Check that the backend is running "
        "and API_URL is correct."
    )

if status_data:
    st.write("**Database Status Response**")
    st.json(status_data)

    if status_code == 200:
        st.info(
            "PostgreSQL Version: "
            + status_data.get("database_version", "Unknown")
        )
    elif status_code == 503:
        st.error("Database connection failed. Check database settings.")
else:
    st.warning("Status endpoint is unavailable.")

st.caption("SecureStack • Monitoring Dashboard")
