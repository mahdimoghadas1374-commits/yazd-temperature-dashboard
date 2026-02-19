import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="🌡️ Yazd Temperature Dashboard")
st.title("🌡️ Yazd Province Temperature Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("yazd Counties_temperature.csv")
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

df_long = df.melt(id_vars=["County","YEAR"], value_vars=months, var_name="Month", value_name="Temperature")
month_map = {m:i+1 for i,m in enumerate(months)}
df_long["Month_Num"] = df_long["Month"].map(month_map)
df_long["Date"] = pd.to_datetime(df_long["YEAR"].astype(str) + "-" + df_long["Month_Num"].astype(str) + "-01")
df_long["Temperature"] = pd.to_numeric(df_long["Temperature"], errors="coerce")
df_long = df_long.dropna(subset=["Temperature"])

# ---------------- STANDARDIZE CITY NAME ----------------
df_long["County"] = df_long["County"].replace({"یزد":"Yazd", "Yazd":"Yazd"})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛️ Dashboard Settings")
st.sidebar.markdown("Select county and year range for analysis")

# ---------- YEAR SLIDER ----------
year_min, year_max = st.sidebar.slider("📅 Year Range",
                                       int(df_long["YEAR"].min()),
                                       int(df_long["YEAR"].max()),
                                       (2015, 2024),
                                       help="Select start and end year")

# ---------- COUNTY BUTTONS INLINE ----------
st.sidebar.markdown("🏙️ Select County (Click button)")

counties = df_long["County"].unique().tolist()
if "Yazd" in counties:
    counties.remove("Yazd")
counties = ["Yazd"] + list(counties)

if "selected_county" not in st.session_state:
    st.session_state.selected_county = "Yazd"

cols_per_row = 3
for i in range(0, len(counties), cols_per_row):
    cols = st.sidebar.columns(cols_per_row)
    for j, c in enumerate(counties[i:i+cols_per_row]):
        if cols[j].button(c):
            st.session_state.selected_county = c

county = st.session_state.selected_county

# ---------------- FILTER DATA ----------------
filtered = df_long[(df_long["County"] == county) &
                   (df_long["YEAR"] >= year_min) &
                   (df_long["YEAR"] <= year_max)].copy()

# ---------------- DISPLAY MODE ----------------
if (year_max - year_min + 1) > 3:
    display_mode = "yearly"
    filtered = filtered.groupby("YEAR", as_index=False).agg(Temperature=("Temperature", "mean"))
    filtered["Date"] = pd.to_datetime(filtered["YEAR"].astype(str) + "-06-01")
    x_axis = "YEAR"
else:
    display_mode = "monthly"
    filtered = filtered.sort_values("Date")
    x_axis = "Date"

# ---------------- METRICS ----------------
avg_temp = filtered["Temperature"].mean()
max_temp = filtered["Temperature"].max()
min_temp = filtered["Temperature"].min()

# ---------------- COLOR FUNCTION ----------------
def temp_color(val):
    if val < 20:
        return "blue"
    elif val <= 35:
        return "yellow"
    else:
        return "red"

# ---------------- GAUGES ----------------
st.subheader(f"📊 Temperature Indicators for {county}")
col1, col2, col3 = st.columns(3)

def animated_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=0,
        title={'text': title},
        gauge={'axis': {'range':[0, max(50, max_temp)]},
               'bar': {'color':'orange'},
               'steps':[dict(range=[0, 20], color='lightblue'),
                        dict(range=[20, 35], color='yellow'),
                        dict(range=[35, 50], color='red')]}
    ))
    fig.update_layout(height=300)
    # Animation loop
    for v in np.linspace(0, value, 30):
        fig.update_traces(value=v)
        col1.plotly_chart(fig, use_container_width=True)
        time.sleep(0.02)
    fig.update_traces(value=value)
    return fig

# Draw gauges (once with animation)
col1.plotly_chart(animated_gauge(avg_temp, "Average Temp (°C)"), use_container_width=True)
col2.plotly_chart(animated_gauge(max_temp, "Max Temp (°C)"), use_container_width=True)
col3.plotly_chart(animated_gauge(min_temp, "Min Temp (°C)"), use_container_width=True)

# ---------------- LINE CHART ANIMATION ----------------
st.subheader(f"📈 Temperature Trend for {county}")
x_vals = filtered[x_axis].tolist()
y_vals = filtered["Temperature"].tolist()
colors = [temp_color(v) for v in y_vals]

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=[], y=[], mode='lines+markers',
                              line=dict(color='orange', width=3),
                              marker=dict(size=8)))

line_chart = st.plotly_chart(fig_line, use_container_width=True)

# Animate line
for i in range(len(x_vals)):
    fig_line.data[0].x = x_vals[:i+1]
    fig_line.data[0].y = y_vals[:i+1]
    fig_line.data[0].marker.color = colors[:i+1]
    line_chart.plotly_chart(fig_line)
    time.sleep(0.05)

# ---------------- HISTOGRAM ----------------
st.subheader("📊 Temperature Distribution")
if len(filtered) > 0:
    fig_hist = px.histogram(filtered, x="Temperature", nbins=30,
                            template="plotly_white",
                            labels={"Temperature":"Temp (°C)"},
                            color_discrete_sequence=["orange"],
                            height=400)
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------------- BOX PLOT ----------------
st.subheader("📊 Temperature Boxplot")
if len(filtered) > 0:
    fig_box = px.box(filtered, y="Temperature",
                     template="plotly_white",
                     color_discrete_sequence=["orange"],
                     height=400)
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 Data Source: NASA POWER Dataset  \n🎓 Yazd Climate Analysis Project")
