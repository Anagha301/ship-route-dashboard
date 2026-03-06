import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

# ------------------------------------------------
# Load Data
# ------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("ships.xlsx", sheet_name="Sheet1")

    # Clean column names (important fix)
    df.columns = df.columns.str.strip()

    # Ensure required columns exist
    required = ["Ship Name", "Port", "Country", "Arrival", "Departure"]
    for col in required:
        if col not in df.columns:
            df[col] = None

    # Fill missing country
    df["Country"] = df["Country"].fillna("Unknown")

    # Convert dates safely
    df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

    # Remove rows without port
    df = df.dropna(subset=["Port"])

    return df


df = load_data()

# ------------------------------------------------
# Sidebar Filters
# ------------------------------------------------

st.sidebar.header("Filters")

ship_filter = st.sidebar.multiselect(
    "Select Ships",
    df["Ship Name"].dropna().unique(),
    default=df["Ship Name"].dropna().unique()
)

date_range = st.sidebar.date_input(
    "Arrival Date Range",
    [df["Arrival"].min(), df["Arrival"].max()]
)

filtered = df[
    (df["Ship Name"].isin(ship_filter)) &
    (df["Arrival"] >= pd.to_datetime(date_range[0])) &
    (df["Arrival"] <= pd.to_datetime(date_range[1]))
]

# ------------------------------------------------
# Geocode Ports
# ------------------------------------------------

@st.cache_data
def get_coordinates(port, country):

    geolocator = Nominatim(user_agent="ship_dashboard")

    try:
        location = geolocator.geocode(f"{port}, {country}", timeout=10)

        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    except:
        return None, None


ports = filtered[["Port", "Country"]].drop_duplicates()

coords = []

for _, row in ports.iterrows():

    lat, lon = get_coordinates(row["Port"], row["Country"])

    coords.append({
        "Port": row["Port"],
        "Country": row["Country"],
        "lat": lat,
        "lon": lon
    })

coord_df = pd.DataFrame(coords)

filtered = filtered.merge(coord_df, on=["Port", "Country"], how="left")

filtered = filtered.dropna(subset=["lat", "lon"])

# ------------------------------------------------
# Port Visit Summary
# ------------------------------------------------

port_visits = filtered.groupby(
    ["Port", "Country", "lat", "lon"]
).agg(
    Visits=("Ship Name", "count"),
    Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
).reset_index()

# ------------------------------------------------
# MAP
# ------------------------------------------------

st.title("🌍 Ship Port Activity Map")

fig = px.scatter_geo(
    port_visits,
    lat="lat",
    lon="lon",
    size="Visits",
    hover_name="Port",
    hover_data={
        "Country": True,
        "Visits": True,
        "Ships": True,
        "lat": False,
        "lon": False
    }
)

fig.update_layout(
    height=650,
    geo=dict(
        showland=True,
        landcolor="rgb(243,243,243)",
    )
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Port Detail Table
# ------------------------------------------------

st.header("⚓ Port Visit Details")

selected_port = st.selectbox(
    "Select Port",
    sorted(port_visits["Port"].unique())
)

port_data = filtered[filtered["Port"] == selected_port]

ship_visits = port_data.groupby("Ship Name").size().reset_index(name="Visits")

st.dataframe(ship_visits, use_container_width=True)

# ------------------------------------------------
# Ship Summary Table
# ------------------------------------------------

st.header("🚢 Ship Summary")

ship_summary = filtered.groupby("Ship Name").agg(
    Total_Visits=("Port", "count"),
    Unique_Ports=("Port", "nunique"),
    Unique_Countries=("Country", "nunique"),
    First_Arrival=("Arrival", "min"),
    Last_Arrival=("Arrival", "max")
).reset_index()

st.dataframe(ship_summary, use_container_width=True)

# ------------------------------------------------
# Ship → Port Table
# ------------------------------------------------

st.header("📊 Ship → Port Visits")

ship_port = filtered.groupby(
    ["Ship Name", "Port"]
).size().reset_index(name="Visits")

st.dataframe(ship_port, use_container_width=True)

# ------------------------------------------------
# Ship → Country Table
# ------------------------------------------------

st.header("🌎 Ship → Country Visits")

ship_country = filtered.groupby(
    ["Ship Name", "Country"]
).size().reset_index(name="Visits")

st.dataframe(ship_country, use_container_width=True)
