import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

df = pd.read_excel("ships.xlsx")

df.columns = df.columns.str.strip()

df = df[df["Country"].notna()]

# Country coordinates
country_coords = {
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
"Sri Lanka":(7.87,80.77)
}

df["lat"] = df["Country"].map(lambda x: country_coords.get(x,(None,None))[0])
df["lon"] = df["Country"].map(lambda x: country_coords.get(x,(None,None))[1])

df = df.dropna(subset=["lat"])

st.title("🌍 Ship Country Visits")

fig = px.scatter_geo(
    df,
    lat="lat",
    lon="lon",
    size="Visits",
    hover_name="Country",
    hover_data=["Ship Name","Visits"]
)

st.plotly_chart(fig,use_container_width=True)

st.header("Ship Visits Table")

st.dataframe(df)
