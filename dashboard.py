import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="Ship Port Dashboard", layout="wide")

st.title("🚢 Global Ship Port Activity Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload ship data Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    if "Ship Name" not in df.columns or "Port" not in df.columns:
        st.error("Excel must contain columns: Ship Name and Port")
        st.stop()

    # If country missing create empty
    if "Country" not in df.columns:
        df["Country"] = ""

    # Create location string
    df["Location"] = df["Port"] + ", " + df["Country"]

    st.write("Finding coordinates for ports...")

    geolocator = Nominatim(user_agent="ship_dashboard")

    coords = {}

    for loc in df["Location"].unique():
        try:
            location = geolocator.geocode(loc)
            if location:
                coords[loc] = (location.latitude, location.longitude)
            else:
                coords[loc] = (None, None)
        except:
            coords[loc] = (None, None)

        time.sleep(1)

    df["Latitude"] = df["Location"].map(lambda x: coords[x][0])
    df["Longitude"] = df["Location"].map(lambda x: coords[x][1])

    df = df.dropna(subset=["Latitude", "Longitude"])

    # PORT STATISTICS
    port_stats = df.groupby(
        ["Port", "Latitude", "Longitude"]
    ).agg(
        Visits=("Ship Name", "count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits", ascending=False)

    # KPI metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Ships", df["Ship Name"].nunique())
    col2.metric("Total Ports", df["Port"].nunique())
    col3.metric("Total Visits", len(df))

    st.divider()

    # Top ports chart
    st.subheader("📊 Most Visited Ports")

    top_ports = port_stats.head(10)

    fig_bar = px.bar(
        top_ports,
        x="Port",
        y="Visits",
        color="Visits"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # MAP
    st.subheader("🌍 Port Activity Map")

    fig = px.scatter_mapbox(
        port_stats,
        lat="Latitude",
        lon="Longitude",
        size="Visits",
        color="Visits",
        hover_name="Port",
        hover_data={"Ships": True, "Visits": True},
        zoom=1,
        height=600
    )

    fig.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Table
    st.subheader("📋 Port Visit Details")

    st.dataframe(port_stats)

else:

    st.info("Upload an Excel file to start.")
