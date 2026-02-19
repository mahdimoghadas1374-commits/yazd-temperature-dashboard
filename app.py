import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Yazd Climate Dashboard", layout="wide")

st.title("🌡️ Yazd Province Temperature Dashboard")

# ---------- Load Data ----------
df = pd.read_csv("yazd Counties_temperature.csv")

df = df[df["PARAMETER"] == "T2M"]

months = ["JAN","FEB","MAR","APR","MAY","JUN",
          "JUL","AUG","SEP","OCT","NOV","DEC"]

# ---------- Sidebar ----------
st.sidebar.header("Filters")

county = st.sidebar.selectbox("Select County", df["County"].unique())

year = st.sidebar.selectbox("Select Year", sorted(df["YEAR"].unique()))

# ---------- Filter Data ----------
df_filtered = df[(df["County"] == county) & (df["YEAR"] == year)]

df_long = df_filtered.melt(
    id_vars=["YEAR"],
    value_vars=months,
    var_name="Month",
    value_name="Temperature"
)

# مرتب سازی ماه‌ها
month_order = months
df_long["Month"] = pd.Categorical(df_long["Month"], categories=month_order, ordered=True)
df_long = df_long.sort_values("Month")

# ---------- Metrics ----------
col1, col2, col3 = st.columns(3)

col1.metric("Average Temp", round(df_long["Temperature"].mean(),2))
col2.metric("Max Temp", round(df_long["Temperature"].max(),2))
col3.metric("Min Temp", round(df_long["Temperature"].min(),2))

st.divider()

# ---------- Chart ----------
fig = px.line(
    df_long,
    x="Month",
    y="Temperature",
    markers=True,
    title=f"Monthly Temperature Trend — {county} ({year})",
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Temperature (°C)",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# ---------- Table ----------
st.subheader("📊 Data Table")
st.dataframe(df_long, use_container_width=True)
