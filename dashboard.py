import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------
# LOAD DATA
# -------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("ships.xlsx", sheet_name="Sheet1")

    # Force first 3 columns
    df = df.iloc[:,0:3]
    df.columns = ["Ship Name","Country","Visits"]

    # Convert visits to numbers
    df["Visits"] = pd.to_numeric(df["Visits"], errors="coerce")

    # Clean country names
    df["Country"] = df["Country"].replace({
        "USA":"United States",
        "UK":"United Kingdom",
        "NL":"Netherlands",
        "UAE":"United Arab Emirates",
        "S Korea":"South Korea",
        "(Uncertain)":None,
        "(blank)":None
    })

    df = df.dropna(subset=["Country"])

    return df


df = load_data()

# -------------------------
# FILTER
# -------------------------

st.sidebar.title("Filters")

ships = st.sidebar.multiselect(
    "Select Ships",
    df["Ship Name"].unique(),
    default=df["Ship Name"].unique()
)

filtered = df[df["Ship Name"].isin(ships)]

# -------------------------
# MAP
# -------------------------

st.title("🌍 Ship Country Visits")

fig = px.scatter_geo(
    filtered,
    locations="Country",
    locationmode="country names",
    size="Visits",
    hover_name="Country",
    hover_data=["Ship Name","Visits"]
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABLE
# -------------------------

st.header("Ship Visits")

st.dataframe(filtered)

# -------------------------
# SUMMARY
# -------------------------

st.header("Ship Summary")

summary = filtered.groupby("Ship Name")["Visits"].sum().reset_index()

summary = summary.sort_values("Visits", ascending=False)

st.dataframe(summary)
