import streamlit as st
import plotly.express as px
import pandas as pd
from app.data.db import connect_database
from my_app.auth import (
    require_login,
    can_create_or_update,
    can_delete,
    is_user,
    is_admin,
    is_analyst
)

from my_app.tickets import (
    insert_ticket,
    get_all_tickets,
    update_ticket_status,
    delete_ticket,
    get_tickets_by_priority,
    get_tickets_by_status,
    get_avg_resolution_time,
    get_tickets_assigned_count
)
from my_app.ai_folder.ai_chat import ai_chat, ai_summary_button

COOL_COLORS = [
    "#4C78A8",  # muted blue
    "#72B7B2",  # teal
    "#59A14F",  # soft green
    "#B279A2",  # muted purple
    "#9C755F",  # grey-brown
]

# ---------------------------------
# AUTH CHECK
# ---------------------------------
require_login()
role = st.session_state.role

st.title("🎫 IT Tickets Dashboard")
tab_table, tab_analytics = st.tabs(["📋 Data & Actions", "📊 Analytics"])


conn = connect_database()
df = get_all_tickets(conn)

with tab_table:
    # ============================================================
    # VIEW TABLE
    # ============================================================
    st.subheader("📋 All Tickets")
    st.caption(f"Total tickets: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True,
        height=650
    )

    st.markdown("---")
    # ============================================================
    # CREATE TICKET
    # ============================================================
    st.subheader("➕ Create Ticket")

    if can_create_or_update():
        with st.form("create_ticket_form"):
            tid = st.text_input("Ticket ID")
            pr = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            desc = st.text_area("Description")
            status = st.selectbox("Status", ["Open", "Assigned", "In Progress", "Resolved", "Closed"])
            assigned = st.text_input("Assigned To")
            created_at = st.text_input("Created At (YYYY-MM-DD)")
            hours = st.number_input("Resolution Time (hours)", min_value=0)

            if st.form_submit_button("Create Ticket"):
                insert_ticket(conn, tid, pr, desc, status, assigned, created_at, hours)
                st.success("Ticket created!")
    else:
        st.info("You do not have permission to create tickets.")

    st.markdown("---")


    # ============================================================
    # UPDATE TICKET STATUS
    # ============================================================
    st.subheader("✏️ Update Ticket Status")

    if len(df) > 0 and can_create_or_update():
        selected_id = st.selectbox("Select Ticket", df["ticket_id"].tolist())
        new_status = st.selectbox("New Status", ["Open", "Assigned", "In Progress", "Resolved", "Closed"])

        if st.button("Update Ticket"):
            update_ticket_status(conn, selected_id, new_status)
            st.success("Status updated!")
    elif len(df) > 0:
        st.warning("You don't have permission to update tickets.")

    st.markdown("---")


    # ============================================================
    # DELETE TICKET (Admin Only)
    # ============================================================
    st.subheader("🗑️ Delete Ticket")

    if len(df) > 0 and can_delete():
        del_id = st.selectbox("Select Ticket to Delete", df["ticket_id"].tolist())

        if st.button("Delete Ticket"):
            delete_ticket(conn, del_id)
            st.success("Ticket deleted.")
    elif len(df) > 0:
        st.warning("Only admins may delete tickets.")

    st.markdown("---")

with tab_analytics:
    # ============================================================
    # 📊 ANALYTICS SECTION
    # ============================================================
    st.subheader("📊 Ticket Analytics")

    df_full = df.copy()

    # -----------------------------------------------------
    # 1. Tickets by Priority
    # -----------------------------------------------------
    df_priority = (
        df_full
        .groupby("priority")
        .size()
        .reset_index(name="count")
    )

    if not df_priority.empty:
        fig1 = px.bar(
            df_priority,
            x="priority",
            y="count",
            color="priority",
            title="Tickets by Priority",
            color_discrete_sequence=COOL_COLORS,
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No priority data available.")


    # -----------------------------------------------------
    # 2. Tickets by Status
    # -----------------------------------------------------
    df_status = (
        df_full
        .groupby("status")
        .size()
        .reset_index(name="count")
    )

    if not df_status.empty:
        fig2 = px.bar(
            df_status,
            x="status",
            y="count",
            color="status",
            title="Tickets by Status",
            color_discrete_sequence=COOL_COLORS,
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No status data available.")


    # -----------------------------------------------------
    # 3. Tickets Assigned per User
    # -----------------------------------------------------
    df_assigned = (
        df_full
        .groupby("assigned_to")
        .size()
        .reset_index(name="count")
    )

    if not df_assigned.empty:
        fig3 = px.bar(
            df_assigned,
            x="assigned_to",
            y="count",
            color="assigned_to",
            title="Tickets Assigned per User",
            color_discrete_sequence=COOL_COLORS,
        )
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No assignment data available.")


    # -----------------------------------------------------
    # 4. Tickets Created Over Time
    # -----------------------------------------------------
    df_time = df_full.copy()
    df_time["created_at"] = pd.to_datetime(df_time["created_at"], errors="coerce")
    df_time = df_time.dropna(subset=["created_at"])

    if not df_time.empty:
        df_daily = (
            df_time
            .groupby(df_time["created_at"].dt.date)
            .size()
            .reset_index(name="count")
            .rename(columns={"created_at": "date"})
        )

        fig4 = px.line(
            df_daily,
            x="date",
            y="count",
            title="Tickets Created Over Time",
            markers=True,
            color_discrete_sequence=["#4C78A8"],
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No valid ticket dates available.")


    # -----------------------------------------------------
    # 5. Resolution Time Distribution
    # -----------------------------------------------------
    if "resolution_time_hours" in df_full.columns:
        fig5 = px.histogram(
            df_full,
            x="resolution_time_hours",
            nbins=20,
            title="Ticket Resolution Time (Hours)",
            color_discrete_sequence=["#72B7B2"],
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Resolution time data not available.")

    df_ai = get_all_tickets(conn)

    ai_priority_counts = df_ai["priority"].value_counts().to_dict()
    ai_status_counts = df_ai["status"].value_counts().to_dict()
    ai_avg_resolution = df_ai["resolution_time_hours"].mean()


    if st.session_state.role in ["analyst", "admin"]:
        ai_summary_button(
            button_label="🤖 AI: Summarise Ticket Analytics",
            system_prompt="""
    You are an IT operations analyst.
    Summarise ticket analytics, priority distribution,
    resolution times, backlog risks, and SLA concerns.
    Provide operational recommendations.
    """,
            data_description=f"""
    Total tickets: {len(df_ai)}
    Tickets by priority: {ai_priority_counts}
    Tickets by status: {ai_status_counts}
    Average resolution time: {ai_avg_resolution}
    """
        )

# CLOSE CONNECTION
conn.close()

st.markdown("---")
st.subheader("🎫 IT Operations AI Assistant")


ai_chat(
    system_prompt="""
You are an IT operations and service management assistant.
Help analyze support tickets and workflows.
Explain ticket priorities, statuses, and escalation paths.
Comment on resolution times and SLA impact.
Provide concise, actionable operational advice.
""",
    placeholder="Ask about ticket prioritisation, SLAs, or operational issues..."
)

st.markdown("---")
st.caption("IT Tickets • CRUD + Analytics + RBAC • Week 9")
