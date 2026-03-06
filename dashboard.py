import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -----------------------
# LOAD DATA
# -----------------------

@st.cache_data
def load_data():
    df = pd.read_excel("ships.xlsx", sheet_name="Sheet1")

    # Keep only first 3 columns
    df = df.iloc[:, 0:3]
    df.columns = ["Ship Name", "Country", "Visits"]

    # Clean text
    df["Ship Name"] = df["Ship Name"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    # Convert Visits to number
    df["Visits"] = pd.to_numeric(df["Visits"], errors="coerce")

    # Fix common country name issues
    df["Country"] = df["Country"].replace({
        "USA": "United States",
        "U.S.A": "United States",
        "UK": "United Kingdom",
        "UAE": "United Arab Emirates",
        "S Korea": "South Korea",
        "Korea": "South Korea",
        "NL": "Netherlands"
    })

    # Remove invalid rows
    df = df.dropna(subset=["Country", "Visits"])
    df = df[df["Country"] != "(blank)"]
    df = df[df["Country"] != "(Uncertain)"]

    return df


df = load_data()

# -----------------------
# DEBUG (to ensure data loads)
# -----------------------

st.write("Loaded data preview:", df.head())

# -----------------------
# SIDEBAR FILTER
# -----------------------

st.sidebar.title("Filters")

ships = st.sidebar.multiselect(
    "Select Ships",
    df["Ship Name"].unique(),
    default=df["Ship Name"].unique()
)

filtered = df[df["Ship Name"].isin(ships)]

# -----------------------
# MAP
# -----------------------

st.title("🌍 Ship Country Visits")

try:
    fig = px.scatter_geo(
        filtered,
        locations="Country",
        locationmode="country names",
        size="Visits",
        hover_name="Country",
        hover_data=["Ship Name", "Visits"]
    )

    fig.update_layout(height=650)

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("Map could not be generated. Showing table instead.")
    st.write(e)

# -----------------------
# DATA TABLE
# -----------------------

st.header("Ship Visits Data")

st.dataframe(filtered, use_container_width=True)

# -----------------------
# SHIP SUMMARY
# -----------------------

st.header("Ship Summary")

summary = (
    filtered.groupby("Ship Name")["Visits"]
    .sum()
    .reset_index()
    .sort_values("Visits", ascending=False)
)

st.dataframe(summary, use_container_width=True)
