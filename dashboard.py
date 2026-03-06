import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fleet Port Dashboard", layout="wide")

st.title("🚢 Global Fleet Port Activity")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -----------------------------
    # BASIC METRICS
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Ships", df["Ship Name"].nunique())
    col2.metric("Total Ports", df["Port"].nunique())
    col3.metric("Total Countries", df["Country"].nunique())

    st.divider()

    # -----------------------------
    # PORT VISITS
    # -----------------------------

    port_stats = df.groupby(["Port","Country"]).agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits", ascending=False)

    # -----------------------------
    # MAP
    # -----------------------------

    st.subheader("🌍 Port Activity Map")

    fig = px.scatter_geo(
        port_stats,
        locations="Country",
        locationmode="country names",
        size="Visits",
        hover_name="Port",
        hover_data={
            "Visits":True,
            "Ships":True
        },
        projection="natural earth"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -----------------------------
    # PORT TABLE
    # -----------------------------

    st.subheader("📊 Port Visits")

    st.dataframe(port_stats)

    st.divider()

    # -----------------------------
    # SHIPS PER PORT
    # -----------------------------

    st.subheader("🚢 Ships Visiting Each Port")

    ships_per_port = df.groupby("Port")["Ship Name"].apply(
        lambda x: ", ".join(sorted(x.unique()))
    ).reset_index()

    st.dataframe(ships_per_port)

    st.divider()

    # -----------------------------
    # COUNTRY ACTIVITY
    # -----------------------------

    st.subheader("🌍 Country Activity")

    country_stats = df.groupby("Country").agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    st.dataframe(country_stats)

else:

    st.info("Upload your fleet Excel dataset.")
