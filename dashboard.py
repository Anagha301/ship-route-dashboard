import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# -----------------------------
# Load Data
# -----------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

df = df.dropna(subset=["Arrival"])

df["Port"] = df["Port"].astype(str).str.strip()
df["Country"] = df["Country"].astype(str).str.strip()

# -----------------------------
# Ship Filter
# -----------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# -----------------------------
# Geocoder (cached)
# -----------------------------

@st.cache_data
def get_coordinates(port, country):

    geolocator = Nominatim(user_agent="ship_dashboard")

    try:
        # Try port + country
        location = geolocator.geocode(f"{port} port {country}")

        if location:
            return location.latitude, location.longitude

        # fallback to country center
        location = geolocator.geocode(country)

        if location:
            return location.latitude, location.longitude

    except:
        pass

    return None


coords = []

for _, row in ship_data.iterrows():

    result = get_coordinates(row["Port"], row["Country"])

    if result:
        lat, lon = result

        coords.append({
            "port": row["Port"],
            "lat": lat,
            "lon": lon
        })


map_df = pd.DataFrame(coords)

# -----------------------------
# Map
# -----------------------------

if not map_df.empty:

    ports = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[lon, lat]',
        get_color='[255,0,0]',
        get_radius=60000,
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
    st.warning("No coordinates found.")
