import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import math

st.set_page_config(layout="wide")
st.title("🚢 Global Ship Route Dashboard (Ocean‑Only Curved Routes)")

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
# Ocean waypoints to avoid land
# -------------------------

ocean_waypoints = {
    ("Brazil", "China"): [
        (-30, -10),
        (-35, 20),
        (-25, 70),
    ],
    ("Argentina", "China"): [
        (-40, -20),
        (-35, 20),
        (-25, 70),
    ],
    ("Brazil", "India"): [
        (-25, -15),
        (-30, 20),
        (-20, 60),
    ],
    ("Europe", "China"): [
        (30, 20),
        (10, 60),
    ],
}

# -------------------------
# Great-circle arc
# -------------------------

def great_circle_arc(p1, p2, steps=80):
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)

    d = 2 * math.asin(
        math.sqrt(
            math.sin((lat2 - lat1) / 2)**2 +
            math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2)**2
        )
    )

    if d == 0:
        return [[math.degrees(lon1), math.degrees(lat1)]]

    arc = []
    for i in range(steps):
        f = i / (steps - 1)
        A = math.sin((1 - f) * d) / math.sin(d)
        B = math.sin(f * d) / math.sin(d)

        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)

        lat = math.atan2(z, math.sqrt(x * x + y * y))
        lon = math.atan2(y, x)

        arc.append([math.degrees(lon), math.degrees(lat)])

    return arc

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

# -------------------------
# Build paths with ocean waypoints
# -------------------------

paths = []

for i in range(len(map_df) - 1):
    row1 = map_df.iloc[i]
    row2 = map_df.iloc[i+1]

    p1 = (row1["lat"], row1["lon"])
    p2 = (row2["lat"], row2["lon"])

    c1 = row1["country"]
    c2 = row2["country"]

    wp = ocean_waypoints.get((c1, c2), None)

    full_path = []

    if wp:
        pts = [p1] + wp + [p2]
        for j in range(len(pts) - 1):
            seg = great_circle_arc(pts[j], pts[j+1])
            if j > 0:
                seg = seg[1:]
            full_path.extend(seg)
    else:
        full_path = great_circle_arc(p1, p2)

    paths.append({"path": full_path})

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

st.subheader("🌍 Ship Route Map (Ocean‑Only Curved Routes)")
st.pydeck_chart(deck)
