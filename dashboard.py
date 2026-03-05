import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import time

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# ----------------------------
# Load Data
# ----------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

df = df.dropna(subset=["Arrival"])

df["Port"] = df["Port"].astype(str).str.strip()
df["Country"] = df["Country"].astype(str).str.strip()

# ----------------------------
# Ship Selector
# ----------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# ----------------------------
# Geocode All Ports Automatically
# ----------------------------

@st.cache_data
def get_port_coordinates(ports):

    geolocator = Nominatim(user_agent="ship_route_dashboard")

    coords = {}

    for port in ports:

        try:
            location = geolocator.geocode(port + " port")

            if location:
                coords[port] = (location.latitude, location.longitude)

            time.sleep(1)

        except:
            pass

    return coords


all_ports = df["Port"].unique()
port_coords = get_port_coordinates(all_ports)

# ----------------------------
# Build Map Data
# ----------------------------

coords = []

for port in ship_data["Port"]:

    if port in port_coords:

        lat, lon = port_coords[port]

        coords.append({
            "port": port,
            "lat": lat,
            "lon": lon
        })

map_df = pd.DataFrame(coords)

# ----------------------------
# Map Visualization
# ----------------------------

if not map_df.empty:

    ports_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_color='[255,0,0]',
        get_radius=70000,
    )

    route_layer = pdk.Layer(
        "PathLayer",
        data=[{
            "path": map_df[["lon","lat"]].values.tolist()
        }],
        get_path="path",
        get_color="[0,0,255]",
        width_scale=20,
        width_min_pixels=4,
    )

    view = pdk.ViewState(
        latitude=map_df["lat"].mean(),
        longitude=map_df["lon"].mean(),
        zoom=2,
        pitch=30
    )

    deck = pdk.Deck(
        layers=[route_layer, ports_layer],
        initial_view_state=view,
        tooltip={"text": "{port}"}
    )

    st.subheader("🌍 Ship Route Map")
    st.pydeck_chart(deck)

else:
    st.warning("No coordinates found for ports.")
