import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# Load Excel
df = pd.read_excel("ships.xlsx")

# Clean dates
df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

df = df.dropna(subset=["Arrival"])

df["Port"] = df["Port"].str.strip()
df["Country"] = df["Country"].str.strip()

# Ship selector
ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# --------------------------------------------------
# Port coordinates (stable for cloud deployment)
# --------------------------------------------------

port_coords = {
    "Houston": (29.73, -95.26),
    "Cartagena": (10.39, -75.52),
    "Suape": (-8.39, -34.96),
    "Santos": (-23.95, -46.33),
    "Buenos Aires": (-34.61, -58.37),
    "Montevideo": (-34.90, -56.16),
    "Itajaí": (-26.91, -48.66),
    "Paranaguá": (-25.51, -48.51),
    "Tanjung Pelepas": (1.36, 103.53),
    "Brisbane": (-27.38, 153.17),
    "Singapore": (1.26, 103.84),
    "Walvis Bay": (-22.95, 14.51),
    "Mobile": (30.69, -88.04),
    "Los Angeles": (33.74, -118.27)
}

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

# --------------------------------------------------
# Map
# --------------------------------------------------

if not map_df.empty:

    ports = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_color='[255,0,0]',
        get_radius=70000,
    )

    route = pdk.Layer(
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
        layers=[route, ports],
        initial_view_state=view,
        tooltip={"text": "{port}"}
    )

    st.subheader("🌍 Ship Route Map")
    st.pydeck_chart(deck)

else:
    st.warning("No matching ports found in coordinate database.")
