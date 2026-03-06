import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ------------------------------------------------
# Load Data
# ------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("ships.xlsx", sheet_name="Sheet1")

    df.columns = df.columns.str.strip()

    df["Country"] = df["Country"].fillna("Unknown")

    df["Arrival"] = pd.to_datetime(df["Arrival"], errors="coerce")
    df["Departure"] = pd.to_datetime(df["Departure"], errors="coerce")

    df = df.dropna(subset=["Port"])

    return df


df = load_data()

# ------------------------------------------------
# Port Coordinates Dictionary
# ------------------------------------------------

PORT_COORDS = {
    "Singapore": (1.29, 103.85),
    "Rotterdam": (51.95, 4.14),
    "Colombo": (6.93, 79.84),
    "Port Klang": (3.00, 101.39),
    "Shanghai": (31.23, 121.47),
    "Dubai": (25.27, 55.29),
    "Busan": (35.10, 129.04),
    "Antwerp": (51.22, 4.40),
    "Hamburg": (53.54, 9.99),
    "Los Angeles": (33.74, -118.27),
    "New York": (40.68, -74.04),
    "Mumbai": (18.94, 72.84)
}

def get_coords(port):
    return PORT_COORDS.get(port, (None, None))


df["lat"] = df["Port"].apply(lambda x: get_coords(x)[0])
df["lon"] = df["Port"].apply(lambda x: get_coords(x)[1])

df = df.dropna(subset=["lat","lon"])

# ------------------------------------------------
# Sidebar Filters
# ------------------------------------------------

st.sidebar.header("Filters")

ships = st.sidebar.multiselect(
    "Ships",
    df["Ship Name"].unique(),
    default=df["Ship Name"].unique()
)

min_date = df["Arrival"].min()
max_date = df["Arrival"].max()

date_range = st.sidebar.date_input(
    "Arrival Range",
    (min_date, max_date)
)

filtered = df[
    (df["Ship Name"].isin(ships)) &
    (df["Arrival"] >= pd.to_datetime(date_range[0])) &
    (df["Arrival"] <= pd.to_datetime(date_range[1]))
]

# ------------------------------------------------
# Port Visits
# ------------------------------------------------

port_visits = filtered.groupby(
    ["Port","Country","lat","lon"]
).agg(
    Visits=("Ship Name","count"),
    Ships=("Ship Name", lambda x: ", ".join(x.unique()))
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
        "Country":True,
        "Visits":True,
        "Ships":True
    }
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Port Detail Table
# ------------------------------------------------

st.header("⚓ Port Details")

selected_port = st.selectbox(
    "Select Port",
    sorted(port_visits["Port"].unique())
)

port_data = filtered[filtered["Port"] == selected_port]

ship_visits = port_data.groupby(
    "Ship Name"
).size().reset_index(name="Visits")

st.dataframe(ship_visits, use_container_width=True)

# ------------------------------------------------
# Ship Summary
# ------------------------------------------------

st.header("🚢 Ship Summary")

ship_summary = filtered.groupby("Ship Name").agg(
    Total_Visits=("Port","count"),
    Unique_Ports=("Port","nunique"),
    Unique_Countries=("Country","nunique"),
    First_Arrival=("Arrival","min"),
    Last_Arrival=("Arrival","max")
).reset_index()

st.dataframe(ship_summary, use_container_width=True)

# ------------------------------------------------
# Ship → Port
# ------------------------------------------------

st.header("📊 Ship → Port Visits")

ship_port = filtered.groupby(
    ["Ship Name","Port"]
).size().reset_index(name="Visits")

st.dataframe(ship_port, use_container_width=True)

# ------------------------------------------------
# Ship → Country
# ------------------------------------------------

st.header("🌎 Ship → Country Visits")

ship_country = filtered.groupby(
    ["Ship Name","Country"]
).size().reset_index(name="Visits")

st.dataframe(ship_country, use_container_width=True)
