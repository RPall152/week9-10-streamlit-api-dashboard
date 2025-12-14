import streamlit as st
import plotly.express as px
import pandas as pd
from app.data.db import connect_database

from my_app.datasets import (
    insert_dataset,
    get_all_datasets,
    delete_dataset,
    get_datasets_by_uploader,
    get_dataset_size_stats
)
from my_app.auth import (
    require_login,
    can_create_or_update,
    can_delete,
    is_user,
    is_admin,
    is_analyst
)

from my_app.ai_folder.ai_chat import ai_chat, ai_summary_button

# -----------------------------
# AUTH CHECK
# -----------------------------
require_login()
role = st.session_state.role

# Permission flags
CAN_MODIFY_DATASETS = role in ["admin", "analyst"]


st.title("📊 Dataset Management Dashboard")

tab_table, tab_analytics = st.tabs(["📋 Data & Actions", "📊 Analytics"])


conn = connect_database()
with tab_table:
    df = get_all_datasets(conn)

    st.subheader("📋 All Datasets")

    st.caption(f"Total datasets: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True,
        height=700
    )


    st.markdown("---")
    # =====================================================
    # 🟢 SECTION 1 — ADD NEW DATASET
    # =====================================================
    st.subheader("➕ Add New Dataset")
    if CAN_MODIFY_DATASETS:
        with st.form("add_dataset_form"):
            dataset_id = st.text_input("Dataset ID")
            name = st.text_input("Dataset Name")
            rows = st.number_input("Number of Rows", min_value=0)
            columns = st.number_input("Number of Columns", min_value=0)
            uploaded_by = st.text_input("Uploaded By (username)")
            upload_date = st.text_input("Upload Date (YYYY-MM-DD)")

            submitted = st.form_submit_button("Add Dataset")

            if submitted:
                new_id = insert_dataset(
                    conn,
                    dataset_id,
                    name,
                    rows,
                    columns,
                    uploaded_by,
                    upload_date
                )
                st.success(f"Dataset created with database ID: {new_id}")
    else:
        st.info("You do not have permission to create datasets.")

    st.markdown("---")

    # =====================================================
    # 🔴 SECTION 2 — DELETE DATASET
    # =====================================================
    st.subheader("🗑️ Delete Dataset")
    if CAN_MODIFY_DATASETS:
        if len(df) > 0:
            delete_id = st.selectbox("Select dataset to delete", df["dataset_id"].tolist())

            if st.button("Delete Dataset"):
                delete_dataset(conn, delete_id)
        else:
            st.info("No datasets available to delete.")
    else:
        st.info("You do not have permission to delete datasets.")
        
    st.markdown("---")

with tab_analytics:
    # =====================================================
    # 📊 SECTION 4 — DATASET ANALYTICS
    # =====================================================

    COOL_COLORS = [
        "#4C78A8",  # muted blue
        "#72B7B2",  # teal
        "#59A14F",  # soft green
        "#B279A2",  # muted purple
        "#9C755F",  # brown-grey
    ]


    st.subheader("📊 Dataset Analytics")

    df_full = df.copy()

    # -----------------------------------------------------
    # 1. Datasets uploaded by user
    # -----------------------------------------------------
    df_by_user = (
        df_full
        .groupby("uploaded_by")
        .size()
        .reset_index(name="count")
    )

    if not df_by_user.empty:
        fig1 = px.bar(
            df_by_user,
            x="uploaded_by",
            y="count",
            title="Datasets Uploaded by User",
            color="uploaded_by",
            color_discrete_sequence=COOL_COLORS,
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No dataset upload data available.")


    # -----------------------------------------------------
    # 2. Dataset sizes (rows)
    # -----------------------------------------------------
    fig2 = px.histogram(
        df_full,
        x="rows",
        nbins=20,
        title="Distribution of Dataset Sizes (Rows)",
        color_discrete_sequence=["#4C78A8"],
    )
    st.plotly_chart(fig2, use_container_width=True)


    # -----------------------------------------------------
    # 3. Rows vs Columns (scatter)
    # -----------------------------------------------------
    fig3 = px.scatter(
        df_full,
        x="rows",
        y="columns",
        title="Rows vs Columns per Dataset",
        color="uploaded_by",
        color_discrete_sequence=COOL_COLORS,
    )
    st.plotly_chart(fig3, use_container_width=True)


    # -----------------------------------------------------
    # 4. Datasets uploaded over time
    # -----------------------------------------------------
    df_time = df_full.copy()
    df_time["upload_date"] = pd.to_datetime(df_time["upload_date"], errors="coerce")
    df_time = df_time.dropna(subset=["upload_date"])

    if not df_time.empty:
        df_daily = (
            df_time
            .groupby(df_time["upload_date"].dt.date)
            .size()
            .reset_index(name="count")
            .rename(columns={"upload_date": "date"})
        )

        fig4 = px.line(
            df_daily,
            x="date",
            y="count",
            title="Datasets Uploaded Over Time",
            markers=True,
            color_discrete_sequence=["#72B7B2"],
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No valid upload dates available.")


    # -----------------------------------------------------
    # 5. Average dataset size by user
    # -----------------------------------------------------
    df_avg_size = (
        df_full
        .groupby("uploaded_by")[["rows", "columns"]]
        .mean()
        .reset_index()
    )

    if not df_avg_size.empty:
        fig5 = px.bar(
            df_avg_size,
            x="uploaded_by",
            y="rows",
            title="Average Dataset Size (Rows) by User",
            color="uploaded_by",
            color_discrete_sequence=COOL_COLORS,
        )
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No data available for average dataset size.")
   
    df_ai = get_all_datasets(conn)

    ai_uploads_by_user = df_ai["uploaded_by"].value_counts().to_dict()
    ai_avg_rows = df_ai["rows"].mean()
    ai_avg_cols = df_ai["columns"].mean()

    
    if st.session_state.role in ["analyst", "admin"]:
        ai_summary_button(
            button_label="🤖 AI: Summarise Dataset Analytics",
            system_prompt="""
    You are a data science expert.
    Summarise dataset analytics, size distribution, upload trends,
    and potential data quality insights.
    Suggest analytical opportunities.
    """,
            data_description=f"""
    Total datasets: {len(df_ai)}
    Average rows: {ai_avg_rows}
    Average columns: {ai_avg_cols}
    Uploads by user: {ai_uploads_by_user}
    """
        )


# -----------------------------
# CLOSE CONNECTION
# -----------------------------
conn.close()

st.markdown("---")

st.subheader("📊 Data Science AI Assistant")

ai_chat(
    system_prompt="""
You are a data science and analytics assistant.
Help analyze dataset metadata.
Explain trends, distributions, and dataset size implications.
Suggest appropriate visualizations and preprocessing steps.
Provide clear, structured, technical explanations.
""",
    placeholder="Ask about dataset trends, metadata, or analysis ideas..."
)

st.markdown("---")


st.caption("Datasets • CRUD + Visualization • Week 9")
