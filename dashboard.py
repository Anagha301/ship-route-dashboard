import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(layout="wide")

st.title("🚢 Global Ship Route Dashboard (Ocean Routes)")

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
# Country Coordinates
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

# -------------------------
# Port Coordinates
# -------------------------

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
    "Cartagena": (10.40, -75.52),
    "Santos": (-23.96, -46.33),
    "Buenos Aires": (-34.60, -58.37),
    "Montevideo": (-34.90, -56.20),
    "Antwerp": (51.26, 4.40),
    "Le Havre": (49.49, 0.10),
    "Felixstowe": (51.96, 1.35),
    "Bremerhaven": (53.55, 8.58),
    "Hamburg": (53.54, 9.99),
    "Rotterdam": (51.95, 4.05),
    "Barcelona": (41.35, 2.16),
    "Valencia": (39.44, -0.32),
    "Genova": (44.40, 8.93),
    "Napoli": (40.84, 14.27),
    "Singapore": (1.26, 103.84),
    "Port Klang": (3.00, 101.40),
    "Nhava Sheva": (18.95, 72.95),
    "Colombo": (6.95, 79.84),
    "Jebel Ali": (25.01, 55.06),
    "Busan New Port": (35.08, 129.04),
    "Shanghai": (31.40, 121.50),
}

# -------------------------
# Great Circle Arc
# -------------------------

def great_circle_arc(p1, p2, steps=80):

    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)

    d = 2 * math.asin(
        math.sqrt(
            math.sin((lat2 - lat1) / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
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
# Ocean Midpoint Generator
# -------------------------

def ocean_midpoint(p1, p2):

    lat1, lon1 = p1
    lat2, lon2 = p2

    mid_lat = (lat1 + lat2) / 2
    mid_lon = (lon1 + lon2) / 2

    # push midpoint into ocean
    if mid_lat > 0:
        mid_lat -= 15
    else:
        mid_lat += 15

    return (mid_lat, mid_lon)


# -------------------------
# Ship Selector
# -------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# -------------------------
# Build Coordinates
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
        coords.append(
            {
                "port": port,
                "country": country,
                "lat": lat,
                "lon": lon,
            }
        )

map_df = pd.DataFrame(coords)

# -------------------------
# Build Ocean Curved Routes
# -------------------------

paths = []

for i in range(len(map_df) - 1):

    row1 = map_df.iloc[i]
    row2 = map_df.iloc[i + 1]

    p1 = (row1["lat"], row1["lon"])
    p2 = (row2["lat"], row2["lon"])

    mid = ocean_midpoint(p1, p2)

    arc1 = great_circle_arc(p1, mid)
    arc2 = great_circle_arc(mid, p2)[1:]

    full_path = arc1 + arc2

    paths.append({"path": full_path})


# -------------------------
# Map Layers
# -------------------------

satellite_layer = pdk.Layer(
    "TileLayer",
    data=None,
    min_zoom=0,
    max_zoom=20,
    tile_size=256,
    get_tile_url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
)

ports_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[lon, lat]",
    get_color="[255,50,50]",
    get_radius=70000,
    pickable=True,
)

routes_layer = pdk.Layer(
    "PathLayer",
    data=paths,
    get_path="path",
    get_color="[0,120,255]",
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
    tooltip={"text": "{port}, {country}"},
)

st.subheader("🌍 Ship Route Map (Ocean Curved Routes)")
st.pydeck_chart(deck)
