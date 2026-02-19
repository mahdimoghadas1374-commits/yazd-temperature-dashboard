import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="🌡️ داشبورد دمای استان یزد")

# ---------------- INTRO ----------------
st.markdown("""
<div style="direction: rtl; text-align: right; font-family: Tahoma; line-height: 2">

<h2>🌡️ سامانه تحلیل دمای استان یزد</h2>

این داشبورد جهت بررسی روند تغییرات دمایی شهرستان‌های استان یزد طراحی شده است.

امکانات سامانه:
<br>• مشاهده شاخص‌های دمایی
<br>• تحلیل روند تغییرات دما
<br>• بررسی توزیع آماری داده‌ها
<br>• دسترسی به داده‌های اولیه

از بخش تنظیمات سمت راست، شهرستان و بازه زمانی مورد نظر خود را انتخاب نمایید.

</div>
<hr>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("yazd Counties_temperature.csv")
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

df_long = df.melt(id_vars=["County","YEAR"], value_vars=months,
                  var_name="Month", value_name="Temperature")
month_map = {m:i+1 for i,m in enumerate(months)}
df_long["Month_Num"] = df_long["Month"].map(month_map)
df_long["Date"] = pd.to_datetime(df_long["YEAR"].astype(str) + "-" + df_long["Month_Num"].astype(str) + "-01")
df_long["Temperature"] = pd.to_numeric(df_long["Temperature"], errors="coerce")
df_long = df_long.dropna(subset=["Temperature"])

# ---------------- CITY MAP ----------------
city_map = {
    "Yazd":"یزد", "Ardakan":"اردکان", "Meybod":"میبد",
    "Taft":"تفت", "Mehriz":"مهریز", "Bafgh":"بافق",
    "Ashkezar":"اشکذر", "Abarkoh":"ابرکوه", "Khatam":"خاتم"
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

# ستون‌های انتخاب شهرستان با ریسپانسیو
cols_per_row = 3
for i in range(0, len(counties), cols_per_row):
    cols = st.sidebar.columns(cols_per_row)
    for j, c in enumerate(counties[i:i+cols_per_row]):
        if cols[j].button(c):
            st.session_state.selected_county = c

county = st.session_state.selected_county
show_data = st.sidebar.checkbox("📋 اطلاعات اولیه")

# ---------------- RAW TABLE ----------------
if show_data:
    st.subheader("📋 جدول اطلاعات اولیه")
    st.dataframe(
        df_long.sort_values(["YEAR","Month_Num","County"]).reset_index(drop=True),
        use_container_width=True,
        height=600
    )
else:
    filtered = df_long[(df_long["County"]==county) &
                       (df_long["YEAR"]>=year_min) &
                       (df_long["YEAR"]<=year_max)].copy().sort_values("Date")

    avg_temp = filtered["Temperature"].mean()
    max_temp = filtered["Temperature"].max()
    min_temp = filtered["Temperature"].min()

    # ---------------- METRICS ----------------
    st.subheader(f"📊 شاخص‌های دمای شهرستان {county}")
    if st.columns(1)[0].width < 500:  # موبایل: ستون عمودی
        col1, col2, col3 = st.columns(1)
    else:
        col1, col2, col3 = st.columns(3)

    def gauge(value, title):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={'axis': {'range':[0,50]}, 'bar': {'color':'orange'}}
        ))
        fig.update_layout(height=280)
        return fig

    col1.plotly_chart(gauge(avg_temp, "میانگین"), use_container_width=True)
    col2.plotly_chart(gauge(max_temp, "حداکثر"), use_container_width=True)
    col3.plotly_chart(gauge(min_temp, "حداقل"), use_container_width=True)

    # ---------------- SELECT BOX ----------------
    st.markdown("### 📊 انتخاب شاخص برای نمودار روند")
    selected_indicator = st.selectbox("شاخص", ["میانگین", "حداکثر", "حداقل"], index=0)

    # ---------------- TREND CHART ----------------
    fig_line = go.Figure()
    years_count = filtered["YEAR"].nunique()

    if years_count == 1:  # ماهانه
        stats = filtered.groupby("Month_Num")["Temperature"].agg(['mean','max','min']).reset_index()
        if selected_indicator=="میانگین": y_values, color = stats['mean'], 'gold'
        elif selected_indicator=="حداکثر": y_values, color = stats['max'], 'red'
        else: y_values, color = stats['min'], 'blue'

        fig_line.add_trace(go.Scatter(
            x=stats["Month_Num"], y=y_values,
            mode="lines+markers", name=selected_indicator,
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))

    else:  # سالانه
        stats = filtered.groupby("YEAR")["Temperature"].agg(['mean','max','min']).reset_index()
        if selected_indicator=="میانگین": y_values, color = stats['mean'], 'gold'
        elif selected_indicator=="حداکثر": y_values, color = stats['max'], 'red'
        else: y_values, color = stats['min'], 'blue'

        fig_line.add_trace(go.Scatter(
            x=stats["YEAR"], y=y_values,
            mode="lines+markers", name=selected_indicator,
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))

    # محور Y روی بازه داده‌ها و رزولوشن مناسب
    y_min, y_max = y_values.min()-0.5, y_values.max()+0.5
    dtick = 0.2 if y_max-y_min<5 else None

    fig_line.update_layout(
        height=420,
        title=f"روند دما — {county} ({selected_indicator})",
        xaxis_title="ماه" if years_count==1 else "سال",
        yaxis_title="دما",
        xaxis=dict(tickmode="array", tickvals=list(range(1,13)), ticktext=months) if years_count==1 else None,
        yaxis=dict(range=[y_min, y_max], dtick=dtick),
        margin=dict(t=50, b=50, l=50, r=50)
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- HIST ----------------
    st.subheader("📊 توزیع دما")
    fig_hist = px.histogram(filtered, x="Temperature", nbins=30, color_discrete_sequence=["orange"])
    st.plotly_chart(fig_hist, use_container_width=True)

    # ---------------- BOX ----------------
    st.subheader("📊 نمودار جعبه‌ای")
    fig_box = px.box(filtered, y="Temperature", color_discrete_sequence=["orange"])
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 NASA POWER Dataset")
