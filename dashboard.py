import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fleet Port Activity Dashboard", layout="wide")

st.title("🚢 Fleet Port Activity Dashboard")

uploaded_file = st.file_uploader("Upload Ship Data Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # ---------------------------------
    # PORT COORDINATE DATABASE
    # ---------------------------------

    port_coords = {
        "Cartagena": (10.391, -75.479),
        "New York": (40.7128, -74.0060),
        "Rotterdam": (51.9244, 4.4777),
        "Singapore": (1.3521, 103.8198),
        "Hamburg": (53.5511, 9.9937),
        "Manzanillo": (19.1138, -104.3385),
        "Fort Lauderdale": (26.1224, -80.1373),
        "Port Everglades": (26.0903, -80.1164),
        "USNWK": (40.6895, -74.1745),
        "Panama": (8.9824, -79.5199)
    }

    # Add coordinates
    df["Latitude"] = df["Port"].map(lambda x: port_coords.get(x, (None,None))[0])
    df["Longitude"] = df["Port"].map(lambda x: port_coords.get(x, (None,None))[1])

    df = df.dropna(subset=["Latitude","Longitude"])

    # ---------------------------------
    # PORT VISITS
    # ---------------------------------

    port_stats = df.groupby(
        ["Port","Latitude","Longitude"]
    ).agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits", ascending=False)

    # ---------------------------------
    # DASHBOARD METRICS
    # ---------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Ships", df["Ship Name"].nunique())
    c2.metric("Total Ports", df["Port"].nunique())
    c3.metric("Total Visits", len(df))

    st.divider()

    # ---------------------------------
    # MAP
    # ---------------------------------

    st.subheader("🌍 Port Activity Map")

    fig = px.scatter_mapbox(
        port_stats,
        lat="Latitude",
        lon="Longitude",
        size="Visits",
        color="Visits",
        hover_name="Port",
        hover_data={
            "Visits":True,
            "Ships":True
        },
        zoom=1,
        height=600
    )

    fig.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------------------------
    # PORT VISITS TABLE
    # ---------------------------------

    st.subheader("📊 Port Visit Summary")

    st.dataframe(port_stats)

    st.divider()

    # ---------------------------------
    # SHIPS PER PORT TABLE
    # ---------------------------------

    st.subheader("🚢 Ships Visiting Each Port")

    ships_per_port = df.groupby("Port")["Ship Name"].apply(
        lambda x: ", ".join(sorted(x.unique()))
    ).reset_index()

    st.dataframe(ships_per_port)

else:

    st.info("Upload your Excel file to start the analysis.")
