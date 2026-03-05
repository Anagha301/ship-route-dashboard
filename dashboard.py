import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(layout="wide")

st.title("🚢 Global Ship Route Dashboard")

# -------------------------
# Load Data
# -------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Country"] = df["Country"].astype(str).str.strip()

# -------------------------
# Ship selector
# -------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# -------------------------
# Country Coordinates
# (stable for cloud)
# -------------------------

country_coords = {
    "USA": (37.09, -95.71),
    "United States": (37.09, -95.71),
    "Brazil": (-14.23, -51.92),
    "Argentina": (-38.41, -63.61),
    "Uruguay": (-32.52, -55.76),
    "Colombia": (4.57, -74.29),
    "Namibia": (-22.95, 18.49),
    "Australia": (-25.27, 133.77),
    "Singapore": (1.35, 103.82),
    "Malaysia": (4.21, 101.97)
}

coords = []

for country in ship_data["Country"]:
    if country in country_coords:
        lat, lon = country_coords[country]
        coords.append({"country": country, "lat": lat, "lon": lon})

map_df = pd.DataFrame(coords)

# -------------------------
# Create curved route lines
# -------------------------

def create_arc(p1, p2, steps=30):

    lat1, lon1 = p1
    lat2, lon2 = p2

    lats = np.linspace(lat1, lat2, steps)
    lons = np.linspace(lon1, lon2, steps)

    arc = []

    for i in range(steps):
        height = np.sin(np.pi * i / (steps-1)) * 5
        arc.append([lons[i], lats[i] + height])

    return arc


paths = []

for i in range(len(map_df) - 1):

    p1 = (map_df.iloc[i]["lat"], map_df.iloc[i]["lon"])
    p2 = (map_df.iloc[i+1]["lat"], map_df.iloc[i+1]["lon"])

    paths.append({
        "path": create_arc(p1, p2)
    })

# -------------------------
# Map Layers
# -------------------------

ports = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[lon, lat]',
    get_color='[255, 50, 50]',
    get_radius=90000,
)

routes = pdk.Layer(
    "PathLayer",
    data=paths,
    get_path="path",
    get_color="[0, 120, 255]",
    width_scale=20,
    width_min_pixels=4,
)

view = pdk.ViewState(
    latitude=map_df["lat"].mean(),
    longitude=map_df["lon"].mean(),
    zoom=2,
    pitch=30,
)

deck = pdk.Deck(
    layers=[routes, ports],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/light-v9",
    tooltip={"text": "{country}"}
)

st.subheader("🌍 Ship Route Map")
st.pydeck_chart(deck)
