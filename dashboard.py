import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# ---------------------------
# Load Data
# ---------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Country"] = df["Country"].astype(str).str.strip()

# ---------------------------
# Ship Filter
# ---------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# ---------------------------
# Get Country Coordinates
# ---------------------------

@st.cache_data
def get_country_coordinates(countries):

    geolocator = Nominatim(user_agent="ship_dashboard")

    coords = {}

    for country in countries:

        try:
            location = geolocator.geocode(country)

            if location:
                coords[country] = (location.latitude, location.longitude)

        except:
            pass

    return coords


country_list = ship_data["Country"].unique()

country_coords = get_country_coordinates(country_list)

# ---------------------------
# Build Map Data
# ---------------------------

coords = []

for country in ship_data["Country"]:

    if country in country_coords:

        lat, lon = country_coords[country]

        coords.append({
            "country": country,
            "lat": lat,
            "lon": lon
        })

map_df = pd.DataFrame(coords)

# ---------------------------
# Map
# ---------------------------

if not map_df.empty:

    countries = pdk.Layer(
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
        layers=[route, countries],
        initial_view_state=view,
        tooltip={"text": "{country}"}
    )

    st.subheader("🌍 Ship Route Map (Country Level)")
    st.pydeck_chart(deck)

else:
    st.warning("No country coordinates found.")
