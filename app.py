import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای شهرستان‌های یزد")
st.title("🌡️ داشبورد تحلیل دمای شهرستان‌های استان یزد")

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
df_long["County"] = df_long["County"].replace({"Yazd":"یزد"})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛️ تنظیمات داشبورد")
st.sidebar.markdown("انتخاب شهرستان و بازه سال برای تحلیل داده‌ها")

# ---------- YEAR SLIDER ----------
year_min, year_max = st.sidebar.slider("📅 بازه سال",
                                       int(df_long["YEAR"].min()),
                                       int(df_long["YEAR"].max()),
                                       (2015, 2024),
                                       help="سال شروع و پایان بازه انتخابی")

# ---------- COUNTY BUTTONS INLINE ----------
st.sidebar.markdown("🏙️ انتخاب شهرستان (با کلیک روی دکمه)")

counties = df_long["County"].unique().tolist()
if "یزد" in counties:
    counties.remove("یزد")
counties = ["یزد"] + list(counties)

if "selected_county" not in st.session_state:
    st.session_state.selected_county = "یزد"

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
st.subheader(f"📊 شاخص‌های دمای شهرستان {county}")
col1, col2, col3 = st.columns(3)

def gauge_figure(value, title):
    color = temp_color(value)
    steps = [dict(range=[0, 20], color='lightblue'),
             dict(range=[20, 35], color='yellow'),
             dict(range=[35, 50], color='red')]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=0,  # شروع از صفر
        title={'text': title},
        gauge={'axis': {'range':[0, max(50, max_temp)]},
               'bar': {'color': color},
               'steps': steps}
    ))
    fig.update_traces(value=value)  # به مقدار واقعی حرکت کنه
    fig.update_layout(transition={'duration':800, 'easing':'cubic-in-out'})
    return fig

col1.plotly_chart(gauge_figure(avg_temp, "میانگین دما (°C)"), use_container_width=True)
col1.markdown(f"📆 بازه: {year_min} – {year_max}")

col2.plotly_chart(gauge_figure(max_temp, "بیشترین دما (°C)"), use_container_width=True)
col2.markdown(f"📆 بازه: {year_min} – {year_max}")

col3.plotly_chart(gauge_figure(min_temp, "کمترین دما (°C)"), use_container_width=True)
col3.markdown(f"📆 بازه: {year_min} – {year_max}")

# ---------------- LINE CHART ANIMATION ----------------
x_vals = filtered[x_axis].tolist()
y_vals = filtered["Temperature"].tolist()
colors = [temp_color(v) for v in y_vals]

fig_line = go.Figure()
for i in range(len(x_vals)):
    fig_line.add_trace(go.Scatter(
        x=x_vals[:i+1],
        y=y_vals[:i+1],
        mode='lines+markers',
        line=dict(color=colors[i], width=3),
        marker=dict(color=colors[i], size=8)
    ))
fig_line.update_layout(title=f"📈 روند دمای {county}",
                       template="plotly_dark",
                       xaxis_title="زمان",
                       yaxis_title="دما (°C)",
                       transition={'duration':800, 'easing':'cubic-in-out'},
                       height=400)
st.subheader(f"📊 نمودار دما برای شهرستان {county}")
st.plotly_chart(fig_line, use_container_width=True)

# ---------------- HISTOGRAM ----------------
if len(filtered) > 0:
    fig_hist = px.histogram(
        filtered,
        x="Temperature",
        nbins=30,
        template="plotly_white",
        labels={"Temperature":"دما (°C)"},
        color="Temperature",
        color_continuous_scale=px.colors.sequential.Viridis,
        height=400
    )
    fig_hist.update_layout(transition={'duration':800, 'easing':'cubic-in-out'})

# ---------------- BOX PLOT ----------------
if len(filtered) > 0:
    fig_box = px.box(filtered, y="Temperature", template="plotly_white",
                     color="Temperature", color_discrete_sequence=["blue","yellow","red"], height=400)
    fig_box.update_layout(transition={'duration':800, 'easing':'cubic-in-out'})

colL, colR = st.columns(2)
with colL:
    st.plotly_chart(fig_line, use_container_width=True)
with colR:
    if len(filtered) > 0:
        st.plotly_chart(fig_hist, use_container_width=True)
        st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 منبع داده: NASA POWER Dataset  \n🎓 پروژه دانشگاهی تحلیل اقلیم استان یزد")
