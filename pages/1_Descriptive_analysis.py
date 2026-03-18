import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import folium
import geopandas as gpd
import json
from streamlit_folium import st_folium
 
st.set_page_config(page_title="Descriptive Analysis", page_icon="📊", layout="wide")
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}
 
.stApp {
    background: #0a1628;
}
 
.page-header {
    margin-bottom: 32px;
}
 
.page-tag {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #00c8b4;
    margin-bottom: 8px;
}
 
.page-title {
    font-size: 36px;
    font-weight: 700;
    color: #e8f0f8;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
 
.page-desc {
    font-size: 14px;
    color: #667788;
    max-width: 500px;
}
 
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
    transition: border-color 0.2s;
}
 
.metric-card:hover {
    border-color: rgba(0,200,180,0.25);
}
 
.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #556677;
    margin-bottom: 10px;
    font-family: 'Space Mono', monospace;
}
 
.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #00c8b4;
    line-height: 1;
}
 
.metric-sub {
    font-size: 12px;
    color: #889aaa;
    margin-top: 6px;
}
 
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #ccd8e4;
    margin: 0 0 4px 0;
}
 
.section-sub {
    font-size: 12px;
    color: #556677;
    margin-bottom: 18px;
}
 
.chart-container {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 24px;
}
 
.divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 32px 0;
}
</style>
""", unsafe_allow_html=True)
 
#  Data 
csv_path = os.path.join(os.path.dirname(__file__), "..", "Data",
    "cfafrica-data-team-outbreak-covid19-data-openafrica-uploads-kenya-diabetes (1).csv")
df = pd.read_csv(csv_path)
df["Geography"] = df["Geography"].str.upper().replace({
    "TAITA / TAVETA": "TAITA TAVETA",
    "ELGEYO / MARAKWET": "ELGEYO-MARAKWET",
    "NAIROBI CITY": "NAIROBI"
})
PREV_COL = "Percentage of the Population that reported having Diabetes"
 
avg_prev  = df[PREV_COL].mean()
max_row   = df.loc[df[PREV_COL].idxmax()]
min_row   = df.loc[df[PREV_COL].idxmin()]
median_prev = df[PREV_COL].median()
 
# Page Header 
st.markdown("""
<div class="page-header">
    <div class="page-tag">📊 Page 1</div>
    <div class="page-title">Descriptive Analysis</div>
    <div class="page-desc">County-level diabetes prevalence across Kenya's 47 counties.</div>
</div>
""", unsafe_allow_html=True)
 
# Metric Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Prevalence</div>
        <div class="metric-value">{avg_prev:.2f}%</div>
        <div class="metric-sub">Across all counties</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Median Prevalence</div>
        <div class="metric-value">{median_prev:.2f}%</div>
        <div class="metric-sub">Midpoint county</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Highest County</div>
        <div class="metric-value">{max_row[PREV_COL]:.1f}%</div>
        <div class="metric-sub">{max_row['Geography'].title()}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Lowest County</div>
        <div class="metric-value">{min_row[PREV_COL]:.1f}%</div>
        <div class="metric-sub">{min_row['Geography'].title()}</div>
    </div>""", unsafe_allow_html=True)
 
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
 
# Choropleth Map 
st.markdown('<div class="section-title">🗺️ Prevalence Map</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Hover over a county to see its diabetes rate</div>', unsafe_allow_html=True)
 
url = "https://raw.githubusercontent.com/mikelmaron/kenya-election-data/master/data/counties.geojson"
gdf = gpd.read_file(url)
gdf_counties = gdf.dissolve(by="COUNTY_NAM").reset_index()
counties_geo = json.loads(gdf_counties.to_json())
 
for feature in counties_geo["features"]:
    feature["id"] = feature["properties"]["COUNTY_NAM"]
 
diabetes_dict = dict(zip(df["Geography"], df[PREV_COL]))
for feature in counties_geo["features"]:
    cn = feature["properties"]["COUNTY_NAM"].upper()
    feature["properties"]["Diabetes"] = diabetes_dict.get(cn, "No data")
 
m = folium.Map(location=[0.0236, 37.9062], zoom_start=6,
               tiles="CartoDB dark_matter")
 
folium.Choropleth(
    geo_data=counties_geo,
    name="choropleth",
    data=df,
    columns=["Geography", PREV_COL],
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.75,
    line_opacity=0,
    legend_name="Diabetes Prevalence (%)"
).add_to(m)
 
folium.GeoJson(
    counties_geo,
    name="County Borders",
    style_function=lambda f: {
        "fillColor": "transparent",
        "color": "rgba(255,255,255,0.3)",
        "weight": 0.8,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["COUNTY_NAM", "Diabetes"],
        aliases=["County:", "Prevalence (%):"],
        localize=True,
        style="background-color:#1a2a3a; color:#e0e8f0; font-family:Sora,sans-serif; border:none; border-radius:8px; padding:8px 12px;"
    )
).add_to(m)
 
st_folium(m, width=None, height=500, use_container_width=True)
 
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
 
#  Top 10 + Bottom 10 Side by Side 
col_left, col_right = st.columns(2)
 
with col_left:
    st.markdown('<div class="section-title">🔴 Top 10 Highest</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Counties with most reported cases</div>', unsafe_allow_html=True)
    top10 = df.sort_values(PREV_COL, ascending=True).tail(10)
    fig_top = px.bar(
        top10, x=PREV_COL, y="Geography", orientation="h",
        color=PREV_COL,
        color_continuous_scale="YlOrRd",
        labels={PREV_COL: "Prevalence (%)", "Geography": ""},
    )
    fig_top.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa", family="Sora"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11, color="#aabbcc")),
        height=320,
    )
    st.plotly_chart(fig_top, use_container_width=True)
 
with col_right:
    st.markdown('<div class="section-title">🟢 Top 10 Lowest</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Counties with fewest reported cases</div>', unsafe_allow_html=True)
    bot10 = df.sort_values(PREV_COL, ascending=False).tail(10)
    fig_bot = px.bar(
        bot10, x=PREV_COL, y="Geography", orientation="h",
        color=PREV_COL,
        color_continuous_scale="Blues",
        labels={PREV_COL: "Prevalence (%)", "Geography": ""},
    )
    fig_bot.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa", family="Sora"),
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11, color="#aabbcc")),
        height=320,
    )
    st.plotly_chart(fig_bot, use_container_width=True)
 
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
 
# Full County Bar Chart 
st.markdown('<div class="section-title">📊 All Counties — Prevalence Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Sorted by prevalence rate</div>', unsafe_allow_html=True)
 
df_sorted = df.sort_values(PREV_COL, ascending=False)
fig_all = px.bar(
    df_sorted,
    x="Geography",
    y=PREV_COL,
    color=PREV_COL,
    color_continuous_scale="Teal",
    labels={PREV_COL: "Prevalence (%)", "Geography": "County"},
)
fig_all.add_hline(y=avg_prev, line_dash="dot", line_color="#f39c12",
                  annotation_text=f"  Avg: {avg_prev:.2f}%",
                  annotation_font_color="#f39c12", annotation_font_size=11)
fig_all.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8899aa", family="Sora"),
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=10, b=80),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickangle=-45, tickfont=dict(size=10)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
    height=400,
)
st.plotly_chart(fig_all, use_container_width=True)
 
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
 
#  Distribution + Box Plot 
col_a, col_b = st.columns(2)
 
with col_a:
    st.markdown('<div class="section-title">📈 Prevalence Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Histogram with KDE overlay</div>', unsafe_allow_html=True)
    fig_hist = px.histogram(
        df, x=PREV_COL, nbins=12,
        color_discrete_sequence=["#00c8b4"],
        labels={PREV_COL: "Prevalence (%)"},
        marginal="violin",
    )
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa", family="Sora"),
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=320,
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)
 
with col_b:
    st.markdown('<div class="section-title">📦 Statistical Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Box plot of county-level spread</div>', unsafe_allow_html=True)
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=df[PREV_COL],
        name="Prevalence",
        marker_color="#00c8b4",
        line_color="#00c8b4",
        fillcolor="rgba(0,200,180,0.12)",
        boxmean=True,
    ))
    fig_box.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa", family="Sora"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Prevalence (%)"),
        margin=dict(l=0, r=0, t=10, b=10),
        height=320,
        showlegend=False,
    )
    st.plotly_chart(fig_box, use_container_width=True)
 
# Raw Data Table 
with st.expander("📋 View Raw Data Table"):
    df_display = df[["Geography", PREV_COL]].sort_values(PREV_COL, ascending=False).reset_index(drop=True)
    df_display.columns = ["County", "Diabetes Prevalence (%)"]
    df_display["Diabetes Prevalence (%)"] = df_display["Diabetes Prevalence (%)"].round(2)
    st.dataframe(df_display, use_container_width=True, height=400)
 