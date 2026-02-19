import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# ---------------- RAW TABLE ----------------
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

    # ---------------- SMART TREND CHART ----------------
    st.subheader("📈 روند دما")
    years_count = filtered["YEAR"].nunique()

    if years_count == 1:
        # ماهانه — میانگین، حداقل، حداکثر
        monthly_stats = filtered.groupby("Month_Num")["Temperature"].agg(['mean','max','min']).reset_index()
        fig_line = go.Figure()
        
        fig_line.add_trace(go.Scatter(
            x=monthly_stats["Month_Num"],
            y=monthly_stats["mean"],
            mode="lines+markers",
            name="میانگین",
            line=dict(color="gold", width=3),
            marker=dict(size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=monthly_stats["Month_Num"],
            y=monthly_stats["max"],
            mode="lines+markers",
            name="حداکثر",
            line=dict(color="red", width=3),
            marker=dict(size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=monthly_stats["Month_Num"],
            y=monthly_stats["min"],
            mode="lines+markers",
            name="حداقل",
            line=dict(color="blue", width=3),
            marker=dict(size=8)
        ))

        fig_line.update_layout(
            height=420,
            title=f"روند ماهانه دما — {county}",
            xaxis_title="ماه",
            yaxis_title="دما",
            xaxis=dict(tickmode="array", tickvals=list(range(1,13)), ticktext=months),
            legend_title_text="📌 توضیح رنگ‌ها",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )
        
    else:
        # سالانه — میانگین، حداقل، حداکثر
        annual_stats = filtered.groupby("YEAR")["Temperature"].agg(['mean','max','min']).reset_index()
        fig_line = go.Figure()
        
        fig_line.add_trace(go.Scatter(
            x=annual_stats["YEAR"],
            y=annual_stats["mean"],
            mode="lines+markers",
            name="میانگین",
            line=dict(color="gold", width=3),
            marker=dict(size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=annual_stats["YEAR"],
            y=annual_stats["max"],
            mode="lines+markers",
            name="حداکثر",
            line=dict(color="red", width=3),
            marker=dict(size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=annual_stats["YEAR"],
            y=annual_stats["min"],
            mode="lines+markers",
            name="حداقل",
            line=dict(color="blue", width=3),
            marker=dict(size=8)
        ))

        fig_line.update_layout(
            height=420,
            title=f"روند سالانه دما — {county}",
            xaxis_title="سال",
            yaxis_title="دما",
            legend_title_text="📌 توضیح رنگ‌ها",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )

    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- HIST ----------------
    st.subheader("📊 توزیع دما")
    fig_hist = px.histogram(filtered, x="Temperature", nbins=30,
                            color_discrete_sequence=["orange"])
    st.plotly_chart(fig_hist, use_container_width=True)

    # ---------------- BOX ----------------
    st.subheader("📊 نمودار جعبه‌ای")
    fig_box = px.box(filtered, y="Temperature",
                     color_discrete_sequence=["orange"])
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---\n📊 NASA POWER Dataset")
