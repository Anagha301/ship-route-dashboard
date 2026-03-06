import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(page_title="Ship Movement Dashboard", layout="wide")

st.title("🚢 Global Ship Movement Dashboard")

# Load file
uploaded_file = st.file_uploader("Upload ships.xlsx", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="Sheet3")
    df.columns = df.columns.str.strip()

    # Handle missing values
    df["Country"] = df["Country"].fillna("Unknown")

    df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

    # -----------------------------
    # Sidebar filters
    # -----------------------------

    st.sidebar.header("Filters")

    ship_filter = st.sidebar.multiselect(
        "Ships",
        df["Ship Name"].unique(),
        default=df["Ship Name"].unique()
    )

    df = df[df["Ship Name"].isin(ship_filter)]

    # -----------------------------
    # Geocode ports
    # -----------------------------

    geolocator = Nominatim(user_agent="ships")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    ports = df[["Port", "Country"]].drop_duplicates()

    coords = []

    for _, row in ports.iterrows():
        location = geocode(f"{row['Port']}, {row['Country']}")
        if location:
            coords.append((location.latitude, location.longitude))
        else:
            coords.append((None, None))

    ports["lat"] = [c[0] for c in coords]
    ports["lon"] = [c[1] for c in coords]

    df = df.merge(ports, on=["Port","Country"])

    df = df.dropna(subset=["lat","lon"])

    # -----------------------------
    # Port visit stats
    # -----------------------------

    port_stats = df.groupby(
        ["Port","Country","lat","lon"]
    ).size().reset_index(name="Visits")

    st.subheader("🌍 Port Activity Map")

    fig = px.scatter_geo(
        port_stats,
        lat="lat",
        lon="lon",
        size="Visits",
        hover_name="Port",
        hover_data=["Country","Visits"],
        projection="natural earth"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Select port
    # -----------------------------

    st.subheader("⚓ Ships Visiting Selected Port")

    selected_port = st.selectbox("Select Port", port_stats["Port"])

    port_table = df[df["Port"] == selected_port]

    port_ship_counts = port_table.groupby("Ship Name").size().reset_index(name="Visits")

    st.dataframe(port_ship_counts)

    # -----------------------------
    # Ship overview
    # -----------------------------

    st.subheader("🚢 Ship Overview")

    ship_summary = df.groupby("Ship Name").agg(
        Total_Visits=("Port","count"),
        Unique_Ports=("Port","nunique"),
        Unique_Countries=("Country","nunique"),
        First_Seen=("Arrival","min"),
        Last_Seen=("Arrival","max")
    ).reset_index()

    st.dataframe(ship_summary)

    # -----------------------------
    # Ship → Port
    # -----------------------------

    st.subheader("Ship → Port Visits")

    ship_ports = df.groupby(["Ship Name","Port"]).size().reset_index(name="Visits")

    st.dataframe(ship_ports)

    # -----------------------------
    # Ship → Country
    # -----------------------------

    st.subheader("Ship → Country Visits")

    ship_countries = df.groupby(["Ship Name","Country"]).size().reset_index(name="Visits")

    st.dataframe(ship_countries)

else:

    st.info("Upload ships.xlsx to begin.")
