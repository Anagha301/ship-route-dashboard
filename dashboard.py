import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# -----------------------------
# Load Data
# -----------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

df = df.dropna(subset=["Arrival"])

df["Port"] = df["Port"].str.strip()

# -----------------------------
# Ship selector
# -----------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# -----------------------------
# Automatic Port Coordinates
# -----------------------------

# Simple deterministic coordinates based on hash
# (fast and works for all ports)

def generate_coordinates(port):

    import hashlib

    h = int(hashlib.md5(port.encode()).hexdigest(),16)

    lat = (h % 180) - 90
    lon = ((h // 1000) % 360) - 180

    return lat, lon


coords = []

for port in ship_data["Port"]:

    lat, lon = generate_coordinates(port)

    coords.append({
        "port": port,
        "lat": lat,
        "lon": lon
    })

map_df = pd.DataFrame(coords)

# -----------------------------
# Map
# -----------------------------

ports = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[lon, lat]',
    get_color='[255,0,0]',
    get_radius=70000
)

route = pdk.Layer(
    "PathLayer",
    data=[{
        "path": map_df[["lon","lat"]].values.tolist()
    }],
    get_path="path",
    get_color="[0,0,255]",
    width_scale=20,
    width_min_pixels=4
)

view = pdk.ViewState(
    latitude=map_df["lat"].mean(),
    longitude=map_df["lon"].mean(),
    zoom=2,
    pitch=30
)

deck = pdk.Deck(
    layers=[route, ports],
    initial_view_state=view,
    tooltip={"text": "{port}"}
)

st.subheader("🌍 Ship Route Map")
st.pydeck_chart(deck)
