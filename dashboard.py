import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import math

st.set_page_config(layout="wide")
st.title("🚢 Global Ship Route Dashboard (Ocean‑Curved Routes)")

# -------------------------
# Load Data
# -------------------------

df = pd.read_excel("ships.xlsx", sheet_name="Sheet2")
df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Ship Name"] = df["Ship Name"].astype(str).str.strip()
df["Port"] = df["Port"].astype(str).str.strip()
df["Country"] = df["Country"].astype(str).str.strip()

# -------------------------
# Coordinates
# -------------------------

country_coords = {
    "USA": (37.09, -95.71),
    "United States": (37.09, -95.71),
    "Mexico": (23.63, -102.55),
    "Canada": (56.13, -106.35),
    "Brazil": (-14.23, -51.92),
    "Argentina": (-38.41, -63.61),
    "Uruguay": (-32.52, -55.76),
    "Colombia": (4.57, -74.29),
    "Panama": (8.54, -80.78),
    "Bahamas": (25.03, -77.40),
    "Namibia": (-22.95, 18.49),
    "Australia": (-25.27, 133.77),
    "Singapore": (1.35, 103.82),
    "Malaysia": (4.21, 101.97),
    "Vietnam": (14.06, 108.28),
    "China": (35.86, 104.20),
    "South Korea": (36.50, 127.80),
    "Japan": (36.20, 138.25),
    "Sri Lanka": (7.87, 80.77),
    "India": (20.59, 78.96),
    "Pakistan": (30.38, 69.35),
    "Oman": (21.47, 55.98),
    "UAE": (23.42, 53.85),
    "Turkey": (38.96, 35.24),
    "Spain": (40.46, -3.75),
    "Portugal": (39.40, -8.22),
    "Italy": (41.87, 12.57),
    "France": (46.23, 2.21),
    "Germany": (51.17, 10.45),
    "Netherlands": (52.13, 5.29),
    "Belgium": (50.50, 4.47),
    "UK": (55.38, -3.44),
    "Denmark": (56.26, 9.50),
    "Sweden": (60.13, 18.64),
}

port_coords = {
    "Houston": (29.73, -95.27),
    "Mobile": (30.71, -88.04),
    "Los Angeles": (33.74, -118.26),
    "Oakland": (37.80, -122.30),
    "New York": (40.67, -74.04),
    "Norfolk": (36.95, -76.33),
    "Charleston": (32.78, -79.92),
    "Savannah": (32.08, -81.09),
    "Baltimore": (39.26, -76.58),
    "Philadelphia": (39.93, -75.13),
    "Boston": (42.35, -71.05),
    "Port Everglades": (26.09, -80.11),
    "Miami": (25.77, -80.18),
    "New Orleans": (29.95, -90.06),
    "Tampa": (27.94, -82.45),
    "Dutch Harbor": (53.89, -166.54),
    "Altamira": (22.40, -97.93),
    "Manzanillo": (19.05, -104.32),
    "Cartagena": (10.40, -75.52),
    "Callao": (-12.06, -77.15),
    "Santos": (-23.96, -46.33),
    "Suape": (-8.39, -34.96),
    "Salvador": (-12.97, -38.50),
    "Rio de Janeiro": (-22.90, -43.17),
    "Itajaí": (-26.90, -48.65),
    "Paranaguá": (-25.52, -48.51),
    "Buenos Aires": (-34.60, -58.37),
    "Montevideo": (-34.90, -56.20),
    "Antwerp": (51.26, 4.40),
    "Zeebrugge": (51.33, 3.20),
    "Le Havre": (49.49, 0.10),
    "Felixstowe": (51.96, 1.35),
    "Bremerhaven": (53.55, 8.58),
    "Hamburg": (53.54, 9.99),
    "Rotterdam": (51.95, 4.05),
    "Barcelona": (41.35, 2.16),
    "Valencia": (39.44, -0.32),
    "Sines": (37.96, -8.87),
    "Genova": (44.40, 8.93),
    "Livorno": (43.55, 10.30),
    "Napoli": (40.84, 14.27),
    "Gioia Tauro": (38.42, 15.90),
    "Singapore": (1.26, 103.84),
    "Port Klang": (3.00, 101.40),
    "Tanjung Pelepas": (1.36, 103.54),
    "Nhava Sheva": (18.95, 72.95),
    "Mundra": (22.73, 69.70),
    "Pipavav": (20.90, 71.50),
    "Colombo": (6.95, 79.84),
    "Jebel Ali": (25.01, 55.06),
    "Busan New Port": (35.08, 129.04),
    "Yantian": (22.56, 114.27),
    "Yangshan": (30.63, 122.06),
    "Ningbo": (29.87, 121.55),
    "Qingdao": (36.07, 120.32),
    "Shanghai": (31.40, 121.50),
}

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
# Build coordinates
# -------------------------

coords = []

for _, row in ship_data.iterrows():
    port = row["Port"]
    country = row["Country"]

    if port in port_coords:
        lat, lon = port_coords[port]
    else:
        lat, lon = country_coords.get(country, (None, None))

    if lat is not None:
        coords.append({"port": port, "country": country, "lat": lat, "lon": lon})

map_df = pd.DataFrame(coords)

if map_df.empty:
    st.error("No coordinates found for this ship.")
    st.stop()

# -------------------------
# Ocean‑curved arc generator
# -------------------------

def ocean_curve(p1, p2, steps=80):
    lat1, lon1 = p1
    lat2, lon2 = p2

    lats = np.linspace(lat1, lat2, steps)
    lons = np.linspace(lon1, lon2, steps)

    # Force curve outward toward ocean (west for Atlantic, east for Pacific)
    mid_lat = (lat1 + lat2) / 2
    mid_lon = (lon1 + lon2) / 2

    curve_strength = 10  # adjust curvature

    if lon1 < lon2:
        bend = -curve_strength
    else:
        bend = curve_strength

    arc = []
    for i in range(steps):
        offset = math.sin(math.pi * i / (steps - 1)) * bend
        arc.append([lons[i] + offset, lats[i]])

    return arc

# -------------------------
# Build paths
# -------------------------

paths = []
for i in range(len(map_df) - 1):
    p1 = (map_df.iloc[i]["lat"], map_df.iloc[i]["lon"])
    p2 = (map_df.iloc[i+1]["lat"], map_df.iloc[i+1]["lon"])
    paths.append({"path": ocean_curve(p1, p2)})

# -------------------------
# Satellite map layer
# -------------------------

satellite_layer = pdk.Layer(
    "TileLayer",
    data=None,
    min_zoom=0,
    max_zoom=20,
    tile_size=256,
    get_tile_url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
)

ports_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[lon, lat]',
    get_color='[255, 50, 50]',
    get_radius=70000,
    pickable=True,
)

routes_layer = pdk.Layer(
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
    layers=[satellite_layer, routes_layer, ports_layer],
    initial_view_state=view,
    map_style=None,
    tooltip={"text": "{port}, {country}"}
)

st.subheader("🌍 Ship Route Map (Ocean‑Curved)")
st.pydeck_chart(deck)
