import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای استان یزد")

# ---------------- RTL + FONT ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ---------------- INTRO ----------------
st.markdown("""
# 🌡️ سامانه تحلیل دمای استان یزد

این داشبورد جهت تحلیل روند تغییرات دمایی شهرستان‌های استان یزد طراحی شده است.

امکانات:
- مشاهده شاخص‌های دمایی
- بررسی روند تغییرات دما
- تحلیل توزیع آماری داده‌ها
- دسترسی به داده‌های اولیه ماهانه

از بخش تنظیمات سمت راست، شهرستان و بازه زمانی مورد نظر خود را انتخاب نمایید.
---
""")

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

# ---------------- CITY MAP ----------------
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

show_data = st.sidebar.checkbox("📋 اطلاعات اولیه")

# ---------------- SHOW RAW DATA ----------------
if show_data:
    st.subheader("📋 جدول اطلاعات اولیه")
    st.dataframe(
        df_long.sort_values(["YEAR","Month_Num","County"]).reset_index(drop=True),
        use_container_width=True
    )

else:
    # ---------------- FILTER ----------------
    filtered = df_long[
        (df_long["County"] == county) &
        (df_long["YEAR"] >= year_min) &
        (df_long["YEAR"] <= year_max)
    ].copy().sort_values("Date")

    # ---------------- METRICS ----------------
    avg_temp = filtered["Temperature"].mean()
    max_temp = filtered["Temperature"].max()
    min_temp = filtered["Temperature"].min()

    st.subheader(f"📊 شاخص‌های دمای شهرستان {county}")
    col1, col2, col3 = st.columns(3)

    def gauge(value, title):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={'axis': {'range':[0, 50]},
                   'bar': {'color':'orange'}}
        ))
        fig.update_layout(height=280)
        return fig

    col1.plotly_chart(gauge(avg_temp, "میانگین"), use_container_width=True)
    col2.plotly_chart(gauge(max_temp, "حداکثر"), use_container_width=True)
    col3.plotly_chart(gauge(min_temp, "حداقل"), use_container_width=True)

    # ---------------- SMART LINE CHART ----------------
    years_count = filtered["YEAR"].nunique()

    st.subheader("📈 روند دما")

    if years_count == 1:
        # حالت ماهانه
        fig_line = px.line(
            filtered,
            x="Date",
            y="Temperature",
            title=f"روند ماهانه دما — {county}",
            labels={"Temperature":"دما", "Date":"ماه"},
            color_discrete_sequence=["orange"],
            line_shape="spline"
        )
    else:
        # حالت سالانه
        annual_avg = filtered.groupby("YEAR")["Temperature"].mean().reset_index()

        fig_line = px.line(
            annual_avg,
            x="YEAR",
            y="Temperature",
            title=f"روند سالانه دما — {county}",
            labels={"Temperature":"میانگین دما", "YEAR":"سال"},
            color_discrete_sequence=["orange"],
            line_shape="spline"
        )

    fig_line.update_traces(mode="lines+markers")
    fig_line.update_layout(height=420)
    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- HIST ----------------
    st.subheader("📊 توزیع دما")
    fig_hist = px.histogram(
        filtered, x="Temperature", nbins=30,
        color_discrete_sequence=["orange"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # ---------------- BOX ----------------
    st.subheader("📊 نمودار جعبه‌ای")
    fig_box = px.box(filtered, y="Temperature", color_discrete_sequence=["orange"])
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 NASA POWER Dataset")
