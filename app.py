import streamlit as st
import pandas as pd
import plotly.express as px

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
st.sidebar.header("🎛️ تنظیمات")
county = st.sidebar.selectbox("انتخاب شهرستان", df_long["County"].unique())
year_min, year_max = st.sidebar.slider(
    "بازه سال",
    int(df_long["YEAR"].min()),
    int(df_long["YEAR"].max()),
    (2015, 2024)
)

# ------------ FILTER DATA ------------
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
fig = px.line(
    filtered,
    x=x_axis,
    y="Temperature",
    color="YEAR" if display_mode=="monthly" else None,
    title=f"📈 روند دمای {county}",
    labels={"Temperature":"دما (°C)", x_axis:"زمان"},
    markers=True
)
fig.update_layout(
    xaxis_tickformat="%Y" if display_mode=="yearly" else "%b %Y",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# ------------ FOOTER ------------
st.markdown("""
---
📊 منبع داده: NASA POWER Dataset  
🎓 پروژه دانشگاهی تحلیل اقلیم استان یزد  
""")
