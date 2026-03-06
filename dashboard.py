import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -----------------------------
# Load Data
# -----------------------------

df = pd.read_excel("ships.xlsx")

# clean column names
df.columns = df.columns.str.strip()

# remove empty rows
df = df[df["Country"].notna()]

# -----------------------------
# Country Coordinates
# -----------------------------

coords = {
"USA":(37,-95),
"United States":(37,-95),
"China":(35,103),
"Singapore":(1.29,103.85),
"Malaysia":(4.21,101.97),
"India":(20.59,78.96),
"Brazil":(-14,-51),
"Germany":(51,10),
"France":(46,2),
"Spain":(40,-4),
"UK":(55,-3),
"Italy":(42,12),
"Turkey":(39,35),
"Belgium":(50.5,4.5),
"Netherlands":(52.13,5.29),
"Sri Lanka":(7.87,80.77),
"Panama":(8.98,-79.52),
"Colombia":(4.57,-74.29),
"Oman":(21.51,55.92),
"Korea":(36.5,127.8),
"S Korea":(36.5,127.8),
"South Korea":(36.5,127.8),
"Vietnam":(14.05,108.27),
"Mexico":(23.63,-102.55),
"Portugal":(39.4,-8.22),
"Poland":(51.92,19.14),
"Greece":(39.07,21.82),
"Pakistan":(30.37,69.35),
"Thailand":(15.87,100.99),
"Argentina":(-38.41,-63.61),
"Uruguay":(-32.52,-55.77),
"Australia":(-25.27,133.77),
"Namibia":(-22.96,18.49),
"Canada":(56.13,-106.34),
"Japan":(36.20,138.25),
"Peru":(-9.19,-75.02),
"Guatemala":(15.78,-90.23),
"Brazil":(-14.23,-51.92)
}

# assign coordinates
df["lat"] = df["Country"].map(lambda x: coords.get(x,(None,None))[0])
df["lon"] = df["Country"].map(lambda x: coords.get(x,(None,None))[1])

# remove countries without coordinates
df = df.dropna(subset=["lat"])

# -----------------------------
# Sidebar Filters
# -----------------------------

st.sidebar.title("Filters")

ships = st.sidebar.multiselect(
    "Select Ships",
    df["Ship Name"].unique(),
    default=df["Ship Name"].unique()
)

filtered = df[df["Ship Name"].isin(ships)]

# -----------------------------
# Map
# -----------------------------

st.title("🌍 Ship Country Visits")

fig = px.scatter_geo(
    filtered,
    lat="lat",
    lon="lon",
    size="Visits",
    hover_name="Country",
    hover_data=["Ship Name","Visits"]
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Table
# -----------------------------

st.header("Ship Visits Data")

st.dataframe(filtered, use_container_width=True)

# -----------------------------
# Ship Summary
# -----------------------------

st.header("Ship Summary")

summary = filtered.groupby("Ship Name")["Visits"].sum().reset_index()

summary = summary.sort_values("Visits", ascending=False)

st.dataframe(summary, use_container_width=True)
