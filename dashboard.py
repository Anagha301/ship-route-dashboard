import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(page_title="Ship Movement Dashboard", layout="wide")

st.title("🚢 Global Ship Movement Dashboard")

uploaded_file = st.file_uploader("Upload ships.xlsx", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")

    # Clean column names
    df.columns = df.columns.str.strip()

    st.write("Detected columns:", df.columns)

    # Rename possible column variations
    column_map = {
        "Country Name": "Country",
        "Country/Region": "Country",
        "Port Name": "Port"
    }

    df = df.rename(columns=column_map)

    # If country still missing create one
    if "Country" not in df.columns:
        df["Country"] = "Unknown"

    df["Country"] = df["Country"].fillna("Unknown")

    # Convert dates
    df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

    # -----------------------------
    # Geocode ports
    # -----------------------------

    geolocator = Nominatim(user_agent="ships")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    ports = df[["Port","Country"]].drop_duplicates()

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
    # Port stats
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

else:

    st.info("Upload ships.xlsx to begin.")


