import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

pdk.settings.mapbox_api_key = "YOUR_MAPBOX_TOKEN"
st.set_page_config(layout="wide")
st.title("🚢 Global Ship Route Dashboard")

# -------------------------
# Load Data (use Sheet2 where voyages are)
# -------------------------

df = pd.read_excel("ships.xlsx", sheet_name="Sheet2")

# Basic cleaning
df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Ship Name"] = df["Ship Name"].astype(str).str.strip()
df["Port"] = df["Port"].astype(str).str.strip()
df["Country"] = df["Country"].astype(str).str.strip()

# -------------------------
# Static coordinates
# -------------------------

# Country centroids (fallback)
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
    "Korea": (36.50, 127.80),
    "S Korea": (36.50, 127.80),
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
    "NL": (52.13, 5.29),
    "Belgium": (50.50, 4.47),
    "UK": (55.38, -3.44),
    "United Kingdom": (55.38, -3.44),
    "Denmark": (56.26, 9.50),
    "Sweden": (60.13, 18.64),
    "Lithuania": (55.17, 23.88),
    "Poland": (51.92, 19.15),
    "Lithuania": (55.17, 23.88),
    "Benin": (9.31, 2.32),
    "Togo": (8.62, 0.82),
    "Ivory Coast": (7.54, -5.55),
    "Bahamas": (25.03, -77.40),
    "Guatemala": (15.78, -90.23),
    "Peru": (-9.19, -75.02),
    "Unknown": (0.0, 0.0),
    "(Uncertain)": (0.0, 0.0),
    "": (0.0, 0.0),
}

# Port-level coordinates (add more over time as needed)
port_coords = {
    # USA
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
    "Fort Lauderdale": (26.12, -80.14),
    "Miami": (25.77, -80.18),
    "New Orleans": (29.95, -90.06),
    "Tampa": (27.94, -82.45),
    "Savannah": (32.08, -81.09),
    "Dutch Harbor": (53.89, -166.54),

    # Mexico
    "Altamira": (22.40, -97.93),
    "Manzanillo": (19.05, -104.32),
    "Ensenada": (31.85, -116.63),

    # Panama
    "Manzanillo": (9.36, -79.90),
    "Colon": (9.36, -79.90),
    "Rodman": (8.94, -79.57),

    # Colombia
    "Cartagena": (10.40, -75.52),
    "Buenaventura": (3.88, -77.03),

    # Peru
    "Callao": (-12.06, -77.15),

    # Brazil
    "Santos": (-23.96, -46.33),
    "Suape": (-8.39, -34.96),
    "Salvador": (-12.97, -38.50),
    "Rio de Janeiro": (-22.90, -43.17),
    "Itajaí": (-26.90, -48.65),
    "Paranaguá": (-25.52, -48.51),
    "Itapoá": (-26.12, -48.61),

    # Argentina / Uruguay
    "Buenos Aires": (-34.60, -58.37),
    "Montevideo": (-34.90, -56.20),

    # Europe
    "Antwerp": (51.26, 4.40),
    "Zeebrugge": (51.33, 3.20),
    "Le Havre": (49.49, 0.10),
    "Felixstowe": (51.96, 1.35),
    "Bremerhaven": (53.55, 8.58),
    "Hamburg": (53.54, 9.99),
    "Maasvlakte – Rotterdam": (51.95, 4.05),
    "Rotterdam": (51.95, 4.05),
    "Aarhus": (56.15, 10.22),
    "Goteborg": (57.70, 11.96),
    "Barcelona": (41.35, 2.16),
    "Valencia": (39.44, -0.32),
    "Sines": (37.96, -8.87),
    "Genova": (44.40, 8.93),
    "Livorno": (43.55, 10.30),
    "Napoli": (40.84, 14.27),
    "Gioia Tauro": (38.42, 15.90),
    "Freeport (BS)": (26.53, -78.70),
    "Freeport": (26.53, -78.70),
    "Klaipeda": (55.71, 21.13),
    "Gdynia": (54.52, 18.55),
    "Gemlik": (40.43, 29.16),
    "Ambarli": (40.97, 28.68),
    "Diliskele": (40.77, 29.77),
    "Nemrut": (38.44, 27.15),
    "Piraeus": (37.94, 23.63),

    # Asia
    "Singapore": (1.26, 103.84),
    "Port Klang": (3.00, 101.40),
    "Tanjung Pelepas": (1.36, 103.54),
    "Laem Chabang": (13.09, 100.89),
    "Nhava Sheva": (18.95, 72.95),
    "Mundra": (22.73, 69.70),
    "Pipavav": (20.90, 71.50),
    "Port Qasim": (24.79, 67.34),
    "Colombo": (6.95, 79.84),
    "Jebel Ali": (25.01, 55.06),
    "Salalah": (17.02, 54.09),
    "Sohar": (24.50, 56.65),
    "Busan New Port": (35.08, 129.04),
    "Gwangyang": (34.91, 127.70),
    "Yantian": (22.56, 114.27),
    "Yangshan": (30.63, 122.06),
    "Ningbo": (29.87, 121.55),
    "Qingdao": (36.07, 120.32),
    "Nansha": (22.71, 113.60),
    "Shanghai": (31.40, 121.50),
    "Shenzhen, China": (22.54, 114.06),
    "Kaohsiung": (22.62, 120.30),
    "Cai Mep": (10.50, 107.00),
    "Vung Tau": (10.35, 107.08),
    "Hambantota": (6.12, 81.12),
    "Tianjin": (38.98, 117.74),
    "Yangshan": (30.63, 122.06),

    # Africa / others
    "Walvis Bay": (-22.95, 14.51),
    "Lome": (6.13, 1.22),
    "Cotonou": (6.36, 2.43),
    "Abidjan": (5.32, -4.02),
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
# Build coordinates for this ship
# -------------------------

coords = []

for _, row in ship_data.iterrows():
    port = row["Port"]
    country = row["Country"]

    lat, lon = None, None

    # Prefer port coordinates
    if port in port_coords:
        lat, lon = port_coords[port]
    # Fallback to country centroid
    elif country in country_coords:
        lat, lon = country_coords[country]

    if lat is not None and lon is not None:
        coords.append({
            "port": port,
            "country": country,
            "lat": lat,
            "lon": lon
        })

map_df = pd.DataFrame(coords)

# -------------------------
# Safety checks
# -------------------------

if map_df.empty:
    st.error("No valid coordinates found for this ship. Check port/country names or coordinate mappings.")
    st.stop()

if len(map_df) < 2:
    st.warning("Not enough points to draw a route (need at least 2). Showing ports only.")
    draw_routes = False
else:
    draw_routes = True

# -------------------------
# Create curved route arcs
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
if draw_routes:
    for i in range(len(map_df) - 1):
        p1 = (map_df.iloc[i]["lat"], map_df.iloc[i]["lon"])
        p2 = (map_df.iloc[i+1]["lat"], map_df.iloc[i+1]["lon"])
        paths.append({"path": create_arc(p1, p2)})

# -------------------------
# Map Layers
# -------------------------

ports_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[lon, lat]',
    get_color='[255, 50, 50]',
    get_radius=70000,
    pickable=True,
)

layers = [ports_layer]

if draw_routes and paths:
    routes_layer = pdk.Layer(
        "PathLayer",
        data=paths,
        get_path="path",
        get_color="[0, 120, 255]",
        width_scale=20,
        width_min_pixels=4,
    )
    layers.append(routes_layer)

view = pdk.ViewState(
    latitude=map_df["lat"].mean(),
    longitude=map_df["lon"].mean(),
    zoom=2,
    pitch=30,
)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view,
    # Geopolitical basemap
    map_style="mapbox://styles/mapbox/streets-v11",
    tooltip={"text": "{port}, {country}"}
)

st.subheader("🌍 Ship Route Map")
st.pydeck_chart(deck)

