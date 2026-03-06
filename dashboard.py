import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fleet Port Analysis", layout="wide")

st.title("🚢 Fleet Port Activity Dashboard")

uploaded_file = st.file_uploader("Upload Ship Excel Data", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -------------------------
    # BASIC DATA INFO
    # -------------------------

    total_ships = df["Ship Name"].nunique()
    total_ports = df["Port"].nunique()
    total_visits = len(df)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Ships", total_ships)
    c2.metric("Total Ports", total_ports)
    c3.metric("Total Port Visits", total_visits)

    st.divider()

    # -------------------------
    # PORT VISIT ANALYSIS
    # -------------------------

    port_visits = df.groupby("Port").agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_visits = port_visits.sort_values("Visits", ascending=False)

    # -------------------------
    # TOP PORTS CHART
    # -------------------------

    st.subheader("📊 Most Visited Ports (Fleet)")

    fig = px.bar(
        port_visits.head(15),
        x="Port",
        y="Visits",
        color="Visits"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # PORT TABLE
    # -------------------------

    st.subheader("📋 Port Usage")

    st.dataframe(port_visits)

    st.divider()

    # -------------------------
    # SHIP ANALYSIS
    # -------------------------

    st.subheader("🚢 Ship Activity")

    ship_activity = df.groupby("Ship Name").agg(
        Ports_Visited=("Port","nunique"),
        Total_Visits=("Port","count")
    ).reset_index()

    ship_activity = ship_activity.sort_values("Total_Visits", ascending=False)

    st.dataframe(ship_activity)

else:

    st.info("Upload your fleet Excel data to begin.")
