import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Global Fleet Dashboard", layout="wide")

st.title("🚢 Global Fleet Port Activity Dashboard")

uploaded_file = st.file_uploader("Upload Ship Excel Data", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    required = ["Ship Name", "Port", "Country"]
    for col in required:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    # -----------------------------
    # BASIC METRICS
    # -----------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Ships", df["Ship Name"].nunique())
    c2.metric("Total Ports", df["Port"].nunique())
    c3.metric("Total Countries", df["Country"].nunique())

    st.divider()

    # -----------------------------
    # PORT VISITS
    # -----------------------------

    port_stats = df.groupby(["Port","Country"]).agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits", ascending=False)

    st.subheader("📊 Port Visit Summary")
    st.dataframe(port_stats)

    st.divider()

    # -----------------------------
    # COUNTRY VISITS
    # -----------------------------

    country_stats = df.groupby("Country").agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index().sort_values("Visits", ascending=False)

    st.subheader("🌍 Country Activity")
    st.dataframe(country_stats)

    st.divider()

    # -----------------------------
    # SHIP ACTIVITY
    # -----------------------------

    ship_stats = df.groupby("Ship Name").agg(
        Ports_Visited=("Port","nunique"),
        Countries_Visited=("Country","nunique"),
        Total_Visits=("Port","count")
    ).reset_index().sort_values("Total_Visits", ascending=False)

    st.subheader("🚢 Ship Activity")
    st.dataframe(ship_stats)

    st.divider()

    # -----------------------------
    # MAP DATA
    # -----------------------------

    # simple approximate coordinates by country
    country_coords = {
        "USA":[37,-95],
        "Netherlands":[52,5],
        "Singapore":[1.35,103.8],
        "Panama":[8.5,-80],
        "Colombia":[4.5,-74],
        "Germany":[51,10]
    }

    port_stats["lat"] = port_stats["Country"].map(lambda x: country_coords.get(x,[None,None])[0])
    port_stats["lon"] = port_stats["Country"].map(lambda x: country_coords.get(x,[None,None])[1])

    map_data = port_stats.dropna(subset=["lat","lon"])

    st.subheader("🌍 Global Port Activity Map")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_radius="Visits * 50000",
        pickable=True
    )

    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1)

    deck = pdk.Deck(layers=[layer], initial_view_state=view_state)

    st.pydeck_chart(deck)

else:

    st.info("Upload your Excel fleet dataset.")
