import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

st.title("🚢 Ship Route Dashboard")

# Load Excel
df = pd.read_excel("ships.xlsx")

# Fix date issues
df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

# Ship selector
ship = st.sidebar.selectbox("Select Ship", df["Ship Name"].unique())

filtered = df[df["Ship Name"] == ship]

# Sort route
route = filtered.sort_values("Arrival")

st.subheader("Journey Timeline")
st.dataframe(route)

# Convert ports → coordinates
geolocator = Nominatim(user_agent="ship_map")

coords = []

for port in route["Port"]:
    try:
        location = geolocator.geocode(port)
        if location:
            coords.append({
                "port": port,
                "lat": location.latitude,
                "lon": location.longitude
            })
    except:
        pass

map_df = pd.DataFrame(coords)

# Map visualization
if not map_df.empty:

    # Port markers
    ports = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_color='[255,0,0]',
        get_radius=60000
    )

    # Route connecting ports
    route_line = pdk.Layer(
        "PathLayer",
        data=[{
            "path": map_df[["lon", "lat"]].values.tolist()
        }],
        get_path="path",
        get_color="[0, 0, 255]",
        width_scale=20,
        width_min_pixels=3
    )

    view = pdk.ViewState(
        latitude=map_df["lat"].mean(),
        longitude=map_df["lon"].mean(),
        zoom=2
    )

    deck = pdk.Deck(
        layers=[route_line, ports],
        initial_view_state=view,
        tooltip={"text": "{port}"}
    )

    st.pydeck_chart(deck)

else:
    st.write("No coordinates found for ports.")