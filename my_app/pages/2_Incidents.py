import streamlit as st
import plotly.express as px

from app.data.db import connect_database
from my_app.incidents import *
from my_app.auth import (
    require_login,
    is_admin,
    is_analyst,
    is_user,
    can_create_or_update,
    can_delete
)

from my_app.ai_folder.ai_chat import ai_chat
from my_app.ai_folder.ai_chat import ai_summary_button



require_login()
role = st.session_state.role

st.title("📂 Cyber Incidents Dashboard")
tab_table, tab_analytics = st.tabs(["📋 Data & Actions", "📊 Analytics"])


conn = connect_database()

# =======================================
# CREATE NEW INCIDENT
# =======================================
with tab_table:
    # =======================================
    # TABLE VIEW
    # =======================================
    st.subheader("📋 All Incidents")

    df = get_all_incidents(conn)

    st.dataframe(
        df,
        use_container_width=True,
        height=700, 
    )

    st.markdown("---")


    st.subheader("➕ Create New Incident")

    if can_create_or_update():
        with st.form("create_incident"):
            incident_id = st.text_input("Incident ID")
            timestamp = st.text_input("Timestamp (YYYY-MM-DD HH:MM:SS)")
            incidents_type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            category = st.text_input("Category")
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            description = st.text_area("Description")

            if st.form_submit_button("Create"):
                new = insert_incident(conn, incident_id, timestamp, incidents_type, severity, category, status, description)
                st.success(f"Incident created with DB ID: {new}")
    else:
        st.info("You do not have permission to create incidents.")

    st.markdown("---")

    # =======================================
    # UPDATE INCIDENT
    # =======================================
    st.subheader("✏️ Update Incident Status")

    df = get_all_incidents(conn)
    if len(df) > 0 and can_create_or_update():
        inc_id = st.selectbox("Incident ID", df["incident_id"].tolist())
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
        if st.button("Update Status"):
            update_incident_status(conn, inc_id, new_status)
            st.success("Updated!")
    elif len(df) > 0:
        st.info("You cannot update incidents.")

    st.markdown("---")

    # =======================================
    # DELETE INCIDENT
    # =======================================
    st.subheader("🗑️ Delete Incident")

    if len(df) > 0 and can_delete():
        del_id = st.selectbox("Delete Incident", df["incident_id"].tolist())
        if st.button("Delete"):
            delete_incident(conn, del_id)
            st.success("Deleted.")
    elif len(df) > 0:
        st.warning("Only admin can delete incidents.")

    st.markdown("---")


# =====================================================
# INCIDENT ANALYTICS
# =====================================================
with tab_analytics:
    st.subheader("📊 Incident Analytics")

    df_full = df.copy()

    # Fix missing incident types: if incidents_type is null OR blank, use category
    df_full["incidents_type"] = df_full["incidents_type"].fillna("").astype(str).str.strip()
    df_full.loc[df_full["incidents_type"].eq(""), "incidents_type"] = df_full.loc[df_full["incidents_type"].eq(""), "category"]

    # -----------------------------------------------------
    # 1. Incidents by Type
    # -----------------------------------------------------
    df_by_type = (
        df_full
        .groupby("incidents_type")
        .size()
        .reset_index(name="count")
    )

    if not df_by_type.empty:
        fig1 = px.bar(
            df_by_type,
            x="incidents_type",
            y="count",
            color="incidents_type",
            title="Incidents by Type",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig1.update_layout(
            xaxis_title="Type",
            yaxis_title="Number of Incidents",
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No incident type data available yet.")

    # -----------------------------------------------------
    # 2. Incidents by Severity
    # -----------------------------------------------------
    df_sev = (
        df_full
        .groupby("severity")
        .size()
        .reset_index(name="count")
    )

    if not df_sev.empty:
        fig2 = px.pie(
            df_sev,
            names="severity",
            values="count",
            title="Incidents by Severity",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No severity data available.")

    # -----------------------------------------------------
    # 3. Incidents by Status
    # -----------------------------------------------------
    df_status = (
        df_full
        .groupby("status")
        .size()
        .reset_index(name="count")
    )

    if not df_status.empty:
        fig3 = px.bar(
            df_status,
            x="status",
            y="count",
            color="status",
            title="Incidents by Status",
            color_discrete_sequence=px.colors.qualitative.Pastel1,
        )
        fig3.update_layout(
            xaxis_title="Status",
            yaxis_title="Number of Incidents",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No status data available.")

    # -----------------------------------------------------
    # 4. Incidents Over Time (daily)
    # -----------------------------------------------------
    # convert timestamp to datetime
    df_time = df_full.copy()
    df_time["timestamp"] = pd.to_datetime(df_time["timestamp"], errors="coerce")
    df_time = df_time.dropna(subset=["timestamp"])

    if not df_time.empty:
        df_daily = (
            df_time
            .groupby(df_time["timestamp"].dt.date)
            .size()
            .reset_index(name="count")
            .rename(columns={"timestamp": "date"})
        )

        fig4 = px.line(
            df_daily,
            x="date",
            y="count",
            title="Incidents Over Time (Daily)",
            markers=True,
            color_discrete_sequence=["#636EFA"],
        )
        fig4.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Incidents",
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No valid timestamps available for time-series analysis.")

    # -----------------------------------------------------
    # 5. Severity by Category (stacked bar)
    # -----------------------------------------------------
    df_cat_sev = (
        df_full
        .groupby(["category", "severity"])
        .size()
        .reset_index(name="count")
    )

    if not df_cat_sev.empty:
        fig5 = px.bar(
            df_cat_sev,
            x="category",
            y="count",
            color="severity",
            barmode="stack",
            title="Incident Severity by Category",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig5.update_layout(
            xaxis_title="Category",
            yaxis_title="Number of Incidents",
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No category/severity data available.")
    if st.session_state.role in ["analyst", "admin"]:

        # -----------------------------
        # AI summary analytics
        # -----------------------------

        df_ai = get_all_incidents(conn)

        ai_incident_type_counts = (
            df_ai["incidents_type"]
            .value_counts()
            .to_dict()
        )

        ai_high_severity_by_status = (
            df_ai[df_ai["severity"] == "High"]["status"]
            .value_counts()
            .to_dict()
        )

        ai_summary_button(
            button_label="🤖 AI: Summarise Incident Analytics",
            system_prompt="""
        You are a cybersecurity analyst.
        Summarise incident analytics, highlight trends, common attack types,
        severity distribution, and operational risks.
        Use professional security terminology.
        """,
                data_description=f"""
        Total incidents: {len(df_ai)}
        Incident types: {ai_incident_type_counts}
        High severity by status: {ai_high_severity_by_status}
        """
        )


conn.close()

st.markdown("---")

st.subheader("🛡 Cybersecurity AI Assistant")

ai_chat(
    system_prompt="""
You are a cybersecurity expert assistant.
Analyze cyber incidents and attack patterns.
Explain threats such as phishing, malware, ransomware, and misconfiguration.
Use professional frameworks like MITRE ATT&CK when relevant.
Provide actionable remediation and prevention steps.
Tone: technical, structured, professional.
""",
    placeholder="Ask about incidents, threats, or security mitigation..."
)
st.markdown("---")

st.caption("Cyber Incidents • CRUD + Visualization • Week 9")