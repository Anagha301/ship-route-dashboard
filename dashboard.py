import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")

st.title("🚢 Ship Route Dashboard")

# ----------------------------
# Load data
# ----------------------------

df = pd.read_excel("ships.xlsx")

df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
df = df.dropna(subset=["Arrival"])

df["Country"] = df["Country"].astype(str).str.strip()

# ----------------------------
# Ship selector
# ----------------------------

ship = st.sidebar.selectbox(
    "Select Ship",
    sorted(df["Ship Name"].unique())
)

ship_data = df[df["Ship Name"] == ship].sort_values("Arrival")

st.subheader("Voyage Timeline")
st.dataframe(ship_data)

# ----------------------------
# Country coordinate database
# ----------------------------

country_coords = {
    "USA": (37.0902, -95.7129),
    "United States": (37.0902, -95.7129),
    "Brazil": (-14.2350, -51.9253),
    "Argentina": (-38.4161, -63.6167),
    "Uruguay": (-32.5228, -55.7658),
    "Colombia": (4.5709, -74.2973),
    "Namibia": (-22.9576, 18.4904),
    "Australia": (-25.2744, 133.7751),
    "Singapore": (1.3521, 103.8198),
    "Malaysia": (4.2105, 101.9758)
}

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

# ----------------------------
# Map
# ----------------------------

if not map_df.empty:

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
        zoom=2
    )

    deck = pdk.Deck(
        layers=[route, ports],
        initial_view_state=view,
        tooltip={"text": "{country}"}
    )

    st.subheader("🌍 Ship Route Map")
    st.pydeck_chart(deck)

else:
    st.warning("Countries not found in coordinate list.")
