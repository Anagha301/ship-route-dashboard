import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from geopy.geocoders import Nominatim
from functools import lru_cache

st.set_page_config(layout="wide")
st.title("🚢 Global Ship Route Dashboard")

# -------------------------
# Load Data
# -------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Port"] = df["Port"].astype(str).str.strip()
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
# Geocoding (Port-level)
# -------------------------

geolocator = Nominatim(user_agent="ship_routes")

@lru_cache(maxsize=500)
def get_coords(port, country):
    """Try multiple geocoding patterns for better accuracy."""
    try:
        queries = [
            f"{port} Port, {country}",
            f"{port} Harbour, {country}",
            f"{port}, {country}",
            f"{port}"
        ]
        for q in queries:
            loc = geolocator.geocode(q, timeout=10)
            if loc:
                return loc.latitude, loc.longitude
    except:
        return None, None
    return None, None


coords = []

for _, row in ship_data.iterrows():
    lat, lon = get_coords(row["Port"], row["Country"])
    if lat and lon:
        coords.append({
            "port": row["Port"],
            "country": row["Country"],
            "lat": lat,
            "lon": lon
        })

map_df = pd.DataFrame(coords)

# -------------------------
# Prevent crash if no coordinates
# -------------------------

if map_df.empty:
    st.error("No valid coordinates found for this ship's ports. Check port names or geocoding.")
    st.stop()

# -------------------------
# Create curved sea route arcs
# -------------------------

def create_arc(p1, p2, steps=50):
    lat1, lon1 = p1
    lat2, lon2 = p2

    lats = np.linspace(lat1, lat2, steps)
    lons = np.linspace(lon1, lon2, steps)

    arc = []
    for i in range(steps):
        height = np.sin(np.pi * i / (steps - 1)) * 3
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
    get_radius=60000,
    pickable=True
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
    tooltip={"text": "{port}, {country}"}
)

st.subheader("🌍 Ship Route Map")
st.pydeck_chart(deck)
