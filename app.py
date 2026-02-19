import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای استان یزد")
st.title("🌡️ داشبورد دمای شهرستان‌های استان یزد")

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

# ---------------- STANDARDIZE CITY NAME ----------------
city_map = {
    "Yazd":"یزد",
    "Ardakan":"اردکان",
    "Meybod":"میبد",
    "Taft":"تفت",
    "Mehriz":"مهریز",
    "Bafgh":"بافق",
    "Ashkezar":"اشکذر",
    "Abarkoh":"ابرکوه",
    "Khatam":"خاتم"
}
df_long["County"] = df_long["County"].map(city_map)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛️ تنظیمات داشبورد")
year_min, year_max = st.sidebar.slider(
    "📅 بازه سال",
    int(df_long["YEAR"].min()),
    int(df_long["YEAR"].max()),
    (2015, 2024)
)

counties = list(city_map.values())
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
filtered = df_long[
    (df_long["County"] == county) &
    (df_long["YEAR"] >= year_min) &
    (df_long["YEAR"] <= year_max)
].copy()
filtered = filtered.sort_values("Date")

# ---------------- METRICS ----------------
avg_temp = filtered["Temperature"].mean()
max_temp = filtered["Temperature"].max()
min_temp = filtered["Temperature"].min()

st.subheader(f"📊 شاخص‌های دمای شهرستان {county}")
col1, col2, col3 = st.columns(3)

def gauge(value, title, max_range=50):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range':[0, max(max_range, value+5)]},
               'bar': {'color':'orange'},
               'steps':[dict(range=[0, 20], color='lightblue'),
                        dict(range=[20, 35], color='yellow'),
                        dict(range=[35, 50], color='red')]}
    ))
    fig.update_layout(height=300)
    return fig

col1.plotly_chart(gauge(avg_temp, "میانگین دما (°C)"), use_container_width=True)
col2.plotly_chart(gauge(max_temp, "حداکثر دما (°C)"), use_container_width=True)
col3.plotly_chart(gauge(min_temp, "حداقل دما (°C)"), use_container_width=True)

# ---------------- LINE CHART ----------------
st.subheader(f"📈 روند دما در {county}")
fig_line = px.line(
    filtered,
    x='Date',
    y='Temperature',
    labels={"Temperature":"دما (°C)", "Date":"تاریخ"},
    title=f"روند دمای شهرستان {county}",
    color_discrete_sequence=["orange"],
    line_shape='spline'  # خطوط smooth و خمیده
)
fig_line.update_traces(mode='lines+markers')
fig_line.update_layout(height=400)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------- HISTOGRAM ----------------
st.subheader("📊 توزیع دما")
fig_hist = px.histogram(
    filtered,
    x="Temperature",
    nbins=30,
    template="plotly_white",
    labels={"Temperature":"دما (°C)"},
    color_discrete_sequence=["orange"],
    height=400
)
st.plotly_chart(fig_hist, use_container_width=True)

# ---------------- BOX PLOT ----------------
st.subheader("📊 نمودار جعبه‌ای دما")
fig_box = px.box(
    filtered,
    y="Temperature",
    template="plotly_white",
    color_discrete_sequence=["orange"],
    height=400
)
st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 منبع داده: NASA POWER Dataset \n🎓 پروژه تحلیل اقلیم استان یزد")
