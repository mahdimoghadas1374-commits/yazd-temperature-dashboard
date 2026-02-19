import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای شهرستان‌های یزد")
st.title("🌡️ داشبورد تحلیل دمای شهرستان‌های استان یزد")

# ---------------- LOAD DATA ----------------
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

# ---------------- SIDEBAR ----------------
st.sidebar.header("🎛️ تنظیمات")
county = st.sidebar.selectbox("انتخاب شهرستان", df_long["County"].unique())
year_min, year_max = st.sidebar.slider(
    "بازه سال",
    int(df_long["YEAR"].min()),
    int(df_long["YEAR"].max()),
    (2015, 2024)
)

# ---------------- FILTER DATA ----------------
filtered = df_long[
    (df_long["County"] == county) &
    (df_long["YEAR"] >= year_min) &
    (df_long["YEAR"] <= year_max)
].copy()

# ---------------- DISPLAY MODE ----------------
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

# ---------------- CALCULATE METRICS ----------------
avg_temp = filtered["Temperature"].mean()
max_temp = filtered["Temperature"].max()
min_temp = filtered["Temperature"].min()

# ---------------- LAYOUT ----------------
st.subheader(f"📊 شاخص‌های دمای شهرستان {county}")
col1, col2, col3 = st.columns(3)

# گیج میانگین
fig_gauge_avg = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_temp,
    title={'text': "میانگین دما (°C)"},
    gauge={'axis': {'range': [0, max(50, max_temp)]},
           'bar': {'color': "orange"},
           'steps': [
               {'range': [0, 20], 'color': "lightblue"},
               {'range': [20, 35], 'color': "yellow"},
               {'range': [35, 50], 'color': "red"}]}
))
col1.plotly_chart(fig_gauge_avg, use_container_width=True)

# گیج بیشینه
fig_gauge_max = go.Figure(go.Indicator(
    mode="gauge+number",
    value=max_temp,
    title={'text': "بیشترین دما (°C)"},
    gauge={'axis': {'range': [0, max(50, max_temp)]},
           'bar': {'color': "red"}}
))
col2.plotly_chart(fig_gauge_max, use_container_width=True)

# گیج کمینه
fig_gauge_min = go.Figure(go.Indicator(
    mode="gauge+number",
    value=min_temp,
    title={'text': "کمترین دما (°C)"},
    gauge={'axis': {'range': [0, max(50, max_temp)]},
           'bar': {'color': "blue"}}
))
col3.plotly_chart(fig_gauge_min, use_container_width=True)

# ---------------- LINE CHART ----------------
fig_line = px.line(
    filtered,
    x=x_axis,
    y="Temperature",
    color="YEAR" if display_mode=="monthly" else None,
    title=f"📈 روند دمای {county}",
    labels={"Temperature":"دما (°C)", x_axis:"زمان"},
    markers=True,
    template="plotly_dark"
)
fig_line.update_layout(
    xaxis_tickformat="%Y" if display_mode=="yearly" else "%b %Y",
    height=400
)

# ---------------- HISTOGRAM ----------------
fig_hist = px.histogram(
    filtered,
    x="Temperature",
    nbins=30,
    title="📊 توزیع دما در بازه انتخابی",
    labels={"Temperature":"دما (°C)"},
    template="plotly_white",
    height=400
)

# ---------------- BOX PLOT ----------------
fig_box = px.box(
    filtered,
    y="Temperature",
    title="📌 پراکندگی دما (Box Plot)",
    template="plotly_white",
    height=400
)

# ---------------- DISPLAY CHARTS ----------------
st.subheader(f"📊 نمودارها برای شهرستان {county}")
colL, colR = st.columns(2)

with colL:
    st.plotly_chart(fig_line, use_container_width=True)

with colR:
    st.plotly_chart(fig_hist, use_container_width=True)
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("""
---
📊 منبع داده: NASA POWER Dataset  
🎓 پروژه دانشگاهی تحلیل اقلیم استان یزد  
""")
