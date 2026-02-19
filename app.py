import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای شهرستان‌های یزد")

st.title("🌡️ داشبورد تحلیل دمای شهرستان‌های استان یزد")

# ------------ LOAD DATA ------------
df = pd.read_csv("yazd Counties_temperature.csv")

months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

df_long = df.melt(
    id_vars=["County","YEAR"],
    value_vars=months,
    var_name="Month",
    value_name="Temperature"
)

month_map = {m:i+1 for i,m in enumerate(months)}
df_long["Month_Num"] = df_long["Month"].map(month_map)
df_long["Date"] = pd.to_datetime(
    df_long["YEAR"].astype(str) + "-" + df_long["Month_Num"].astype(str) + "-01"
)

df_long["Temperature"] = pd.to_numeric(df_long["Temperature"], errors="coerce")
df_long = df_long.dropna(subset=["Temperature"])

# ------------ SIDEBAR SETTINGS ------------
st.sidebar.header("🎛️ تنظیمات بازه سال")
year_min, year_max = st.sidebar.slider(
    "بازه سال",
    int(df_long["YEAR"].min()),
    int(df_long["YEAR"].max()),
    (2015, 2024)
)

# ------------ LOAD YAZD GEOJSON ------------
# من یک نمونه GeoJSON از شهرستان‌های یزد آماده کردم (میتونی فایل خودت داشته باشی)
geojson_url = "https://raw.githubusercontent.com/mahdimoghadas/Yazd-Counties-GeoJSON/main/yazd_counties.geojson"
geojson = requests.get(geojson_url).json()

# ------------ FILTER DATA BY YEAR ------------
filtered_year = df_long[
    (df_long["YEAR"] >= year_min) & (df_long["YEAR"] <= year_max)
].copy()

# میانگین دما برای هر شهرستان در بازه انتخابی
county_avg = filtered_year.groupby("County", as_index=False).agg(
    Temperature=("Temperature", "mean")
)

# ------------ MAP INTERACTION ------------
st.subheader("🗺️ انتخاب شهرستان با کلیک روی نقشه")
fig_map = px.choropleth_mapbox(
    county_avg,
    geojson=geojson,
    locations="County",
    featureidkey="properties.name",
    color="Temperature",
    color_continuous_scale="thermal",
    mapbox_style="carto-positron",
    center={"lat": 32.0, "lon": 54.0},
    zoom=6,
    opacity=0.7,
    labels={"Temperature":"میانگین دما (°C)"}
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
selected_county = st.plotly_chart(fig_map, use_container_width=True)

# ------------ HANDLE COUNTY SELECTION ------------
# در plotly interactive map، انتخاب واقعی نیازمند Dash یا Plotly ClickData هست
# در Streamlit ساده، ما فعلاً با selectbox جایگزین می‌کنیم ولی بعداً میشه تعاملی کرد
county = st.selectbox("انتخاب شهرستان (برای نمودار)", df_long["County"].unique())

filtered = df_long[
    (df_long["County"] == county) &
    (df_long["YEAR"] >= year_min) &
    (df_long["YEAR"] <= year_max)
].copy()

# ------------ DECIDE DISPLAY MODE ------------
if (year_max - year_min + 1) > 3:
    display_mode = "yearly"
    filtered = filtered.groupby("YEAR", as_index=False).agg(
        Temperature=("Temperature", "mean")
    )
    filtered["Date"] = pd.to_datetime(filtered["YEAR"].astype(str) + "-06-01")
    x_axis = "YEAR"
else:
    display_mode = "monthly"
    filtered = filtered.sort_values("Date")
    x_axis = "Date"

# ------------ AVERAGE METRIC ------------
avg_temp = filtered["Temperature"].mean()
st.metric("📊 میانگین دما در بازه انتخابی", f"{avg_temp:.2f} °C")

# ------------ TEMPERATURE TREND CHART ------------
fig_line = px.line(
    filtered,
    x=x_axis,
    y="Temperature",
    color="YEAR" if display_mode=="monthly" else None,
    title=f"📈 روند دمای {county}",
    labels={"Temperature":"دما (°C)", x_axis:"زمان"},
    markers=True
)
fig_line.update_layout(
    xaxis_tickformat="%Y" if display_mode=="yearly" else "%b %Y",
    template="plotly_dark"
)
st.plotly_chart(fig_line, use_container_width=True)

# ------------ FOOTER ------------
st.markdown("""
---
📊 منبع داده: NASA POWER Dataset  
🎓 پروژه دانشگاهی تحلیل اقلیم استان یزد  
""")
