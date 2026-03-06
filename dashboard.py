import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="Ship Port Activity Dashboard", layout="wide")

st.title("🚢 Global Ship Port Activity Dashboard")

uploaded_file = st.file_uploader("Upload Ship Data Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Create port + country column
    df["Location"] = df["Port"] + ", " + df["Country"].fillna("")

    # -------------------------
    # GEOCODER
    # -------------------------

    geolocator = Nominatim(user_agent="ship_dashboard")

    @st.cache_data
    def get_coordinates(location):
        try:
            location_data = geolocator.geocode(location)
            if location_data:
                return location_data.latitude, location_data.longitude
            else:
                return None, None
        except:
            return None, None

    # Unique ports
    unique_ports = df["Location"].unique()

    coord_list = []

    st.write("🌍 Getting coordinates for ports...")

    for loc in unique_ports:
        lat, lon = get_coordinates(loc)
        coord_list.append([loc, lat, lon])
        time.sleep(1)  # avoid API block

    coord_df = pd.DataFrame(coord_list, columns=["Location","Latitude","Longitude"])

    # Merge back to main dataframe
    df = df.merge(coord_df, on="Location", how="left")

    df = df.dropna(subset=["Latitude","Longitude"])

    # -------------------------
    # PORT STATISTICS
    # -------------------------

    port_stats = df.groupby(
        ["Port","Country","Latitude","Longitude"]
    ).agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits", ascending=False)

    # -------------------------
    # METRICS
    # -------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Ships", df["Ship Name"].nunique())
    col2.metric("Total Ports", df["Port"].nunique())
    col3.metric("Total Visits", len(df))

    st.divider()

    # -------------------------
    # TOP PORTS CHART
    # -------------------------

    st.subheader("📊 Top 10 Most Visited Ports")

    top_ports = port_stats.head(10)

    fig_bar = px.bar(
        top_ports,
        x="Port",
        y="Visits",
        color="Visits"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # -------------------------
    # MAP
    # -------------------------

    st.subheader("🌍 Global Port Activity Map")

    fig_map = px.scatter_mapbox(
        port_stats,
        lat="Latitude",
        lon="Longitude",
        size="Visits",
        color="Visits",
        hover_name="Port",
        hover_data={
            "Country":True,
            "Visits":True,
            "Ships":True
        },
        zoom=1,
        height=600
    )

    fig_map.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    # -------------------------
    # TABLE
    # -------------------------

    st.subheader("📋 Port Visit Details")

    st.dataframe(port_stats, use_container_width=True)
 



