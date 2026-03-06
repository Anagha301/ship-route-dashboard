import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fleet Shipping Dashboard", layout="wide")

st.title("🚢 Global Fleet Shipping Analysis")

uploaded_file = st.file_uploader("Upload ship Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -----------------------------
    # PORT COORDINATE DATABASE
    # (add ports if needed)
    # -----------------------------

    port_coords = {
        "Rotterdam": (51.9244, 4.4777),
        "Hamburg": (53.5511, 9.9937),
        "New York": (40.7128, -74.0060),
        "Singapore": (1.3521, 103.8198),
        "Cartagena": (10.3910, -75.4794),
        "Manzanillo": (19.1138, -104.3385),
        "Fort Lauderdale": (26.1224, -80.1373),
        "Port Everglades": (26.0903, -80.1164),
        "Panama": (8.9824, -79.5199)
    }

    df["Latitude"] = df["Port"].map(lambda x: port_coords.get(x,(None,None))[0])
    df["Longitude"] = df["Port"].map(lambda x: port_coords.get(x,(None,None))[1])

    df = df.dropna(subset=["Latitude","Longitude"])

    # -----------------------------
    # METRICS
    # -----------------------------

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Ships", df["Ship Name"].nunique())
    c2.metric("Total Ports", df["Port"].nunique())
    c3.metric("Total Countries", df["Country"].nunique())

    st.divider()

    # -----------------------------
    # PORT ACTIVITY
    # -----------------------------

    port_stats = df.groupby(
        ["Port","Country","Latitude","Longitude"]
    ).agg(
        Visits=("Ship Name","count"),
        Ships=("Ship Name",lambda x: ", ".join(sorted(x.unique())))
    ).reset_index()

    port_stats = port_stats.sort_values("Visits",ascending=False)

    st.subheader("🌍 Global Port Activity Map")

    fig = px.scatter_mapbox(
        port_stats,
        lat="Latitude",
        lon="Longitude",
        size="Visits",
        color="Visits",
        hover_name="Port",
        hover_data={
            "Country":True,
            "Visits":True,
            "Ships":True
        },
        zoom=1,
        height=650
    )

    fig.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    # -----------------------------
    # SHIP → PORT ANALYSIS
    # -----------------------------

    st.subheader("🚢 Ship Port Visits")

    ship_ports = df.groupby(["Ship Name","Port"]).size().reset_index(name="Visits")

    ship_ports = ship_ports.sort_values(["Ship Name","Visits"],ascending=[True,False])

    st.dataframe(ship_ports,use_container_width=True)

    st.divider()

    # -----------------------------
    # SHIP → COUNTRY ANALYSIS
    # -----------------------------

    st.subheader("🌍 Ship Country Visits")

    ship_countries = df.groupby(["Ship Name","Country"]).size().reset_index(name="Visits")

    ship_countries = ship_countries.sort_values(["Ship Name","Visits"],ascending=[True,False])

    st.dataframe(ship_countries,use_container_width=True)

    st.divider()

    # -----------------------------
    # PORT SUMMARY
    # -----------------------------

    st.subheader("📊 Port Visit Summary")

    st.dataframe(port_stats,use_container_width=True)

else:

    st.info("Upload your fleet Excel dataset to start.")
