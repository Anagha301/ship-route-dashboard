import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(page_title="Ship Movement Dashboard", layout="wide")

st.title("🚢 Ship Movement Interactive World Map")

# -----------------------------
# LOAD DATA
# -----------------------------

uploaded_file = st.file_uploader("Upload ships.xlsx", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    # Handle missing values
    df["Country"] = df["Country"].fillna("Unknown")
    df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

    # -----------------------------
    # SIDEBAR FILTERS
    # -----------------------------

    st.sidebar.header("Filters")

    ships = st.sidebar.multiselect(
        "Filter by Ship",
        options=df["Ship Name"].unique(),
        default=df["Ship Name"].unique()
    )

    df = df[df["Ship Name"].isin(ships)]

    date_range = st.sidebar.date_input(
        "Filter by Arrival Date",
        []
    )

    if len(date_range) == 2:
        df = df[(df["Arrival"] >= pd.to_datetime(date_range[0])) &
                (df["Arrival"] <= pd.to_datetime(date_range[1]))]

    # -----------------------------
    # GEOCODING PORTS
    # -----------------------------

    geolocator = Nominatim(user_agent="ship_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    ports = df[["Port","Country"]].drop_duplicates()

    if "Latitude" not in ports.columns:

        coords = []

        for _, row in ports.iterrows():

            location = geocode(f"{row['Port']}, {row['Country']}")

            if location:
                coords.append((location.latitude, location.longitude))
            else:
                coords.append((None,None))

        ports["Latitude"] = [c[0] for c in coords]
        ports["Longitude"] = [c[1] for c in coords]

    df = df.merge(ports, on=["Port","Country"], how="left")

    df = df.dropna(subset=["Latitude","Longitude"])

    # -----------------------------
    # PORT VISIT STATS
    # -----------------------------

    port_stats = df.groupby(
        ["Port","Country","Latitude","Longitude"]
    ).agg(
        Visits=("Ship Name","count")
    ).reset_index()

    # -----------------------------
    # MAP
    # -----------------------------

    st.subheader("🌍 Global Port Activity")

    fig = px.scatter_geo(
        port_stats,
        lat="Latitude",
        lon="Longitude",
        size="Visits",
        hover_name="Port",
        hover_data={"Country":True,"Visits":True},
        projection="natural earth"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # PORT DETAIL TABLE
    # -----------------------------

    st.subheader("⚓ Port Visit Details")

    selected_port = st.selectbox(
        "Select Port",
        port_stats["Port"].unique()
    )

    port_detail = df[df["Port"] == selected_port]

    port_ship_counts = port_detail.groupby("Ship Name").size().reset_index(name="Visits")

    st.dataframe(port_ship_counts)

    # -----------------------------
    # SHIP OVERVIEW TABLE
    # -----------------------------

    st.subheader("🚢 Ship Overview")

    ship_summary = df.groupby("Ship Name").agg(
        Total_Visits=("Port","count"),
        Unique_Ports=("Port","nunique"),
        First_Seen=("Arrival","min"),
        Last_Seen=("Arrival","max")
    ).reset_index()

    st.dataframe(ship_summary)

else:

    st.info("Upload ships.xlsx to begin analysis.")
