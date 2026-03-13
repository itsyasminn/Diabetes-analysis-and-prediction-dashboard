import streamlit as st
import pandas as pd
import os
import plotly.express as px
import folium
import geopandas as gpd
import json
from streamlit_folium import st_folium


st.title("Diabetes Prevalence in Kenya")

csv_path = os.path.join(os.path.dirname(__file__), "..", "Data",
                        "cfafrica-data-team-outbreak-covid19-data-openafrica-uploads-kenya-diabetes (1).csv")

df = pd.read_csv(csv_path)

df["Geography"] = df["Geography"].str.upper()
df["Geography"] = df["Geography"].replace({
    "TAITA / TAVETA": "TAITA TAVETA",
    "ELGEYO / MARAKWET": "ELGEYO-MARAKWET",
    "NAIROBI CITY": "NAIROBI"
})

st.subheader("Key Statistics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Prevalence",
    f"{df['Percentage of the Population that reported having Diabetes'].mean():.2f}%"
)

col2.metric(
    "Highest County",
    df.loc[df['Percentage of the Population that reported having Diabetes'].idxmax(), "Geography"]
)

col3.metric(
    "Lowest County",
    df.loc[df['Percentage of the Population that reported having Diabetes'].idxmin(), "Geography"]
)

st.divider()

url = "https://raw.githubusercontent.com/mikelmaron/kenya-election-data/master/data/counties.geojson"
gdf = gpd.read_file(url)

gdf_counties = gdf.dissolve(by="COUNTY_NAM").reset_index()

counties_geo = json.loads(gdf_counties.to_json())

for feature in counties_geo["features"]:
    feature["id"] = feature["properties"]["COUNTY_NAM"]

diabetes_dict = dict(zip(
    df["Geography"],
    df["Percentage of the Population that reported having Diabetes"]
))

for feature in counties_geo["features"]:
    county_name = feature["properties"]["COUNTY_NAM"].upper()
    feature["properties"]["Diabetes"] = diabetes_dict.get(county_name, "No data")

m = folium.Map(location=[0.0236, 37.9062], zoom_start=6)

folium.Choropleth(
    geo_data=counties_geo,
    name="choropleth",
    data=df,
    columns=[
        "Geography",
        "Percentage of the Population that reported having Diabetes"
    ],
    key_on="feature.id",
    fill_color="PuBu",
    fill_opacity=0.7,
    line_opacity=0,
    legend_name="Diabetes Prevalence (%)"
).add_to(m)

folium.GeoJson(
    counties_geo,
    name="County Borders",
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "black",
        "weight": 1,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["COUNTY_NAM", "Diabetes"],
        aliases=["County:", "Diabetes %:"],
        localize=True
    )
).add_to(m)

st.subheader("Diabetes Prevalence by County (Map)")

st_folium(m, width=900, height=500)

st.divider()

st.subheader("County Comparison")

fig_bar = px.bar(
    df,
    x="Geography",
    y="Percentage of the Population that reported having Diabetes",
    title="Diabetes Prevalence by County"
)

st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

top10 = df.sort_values(
    "Percentage of the Population that reported having Diabetes",
    ascending=False
).head(10)

st.subheader("Top 10 Counties with Highest Prevalence")

fig_top = px.bar(
    top10,
    x="Percentage of the Population that reported having Diabetes",
    y="Geography",
    orientation="h"
)

st.plotly_chart(fig_top, use_container_width=True)

st.divider()

st.subheader("Distribution of Diabetes Prevalence")

fig_hist = px.histogram(
    df,
    x="Percentage of the Population that reported having Diabetes",
    nbins=10
)

st.plotly_chart(fig_hist, use_container_width=True)

