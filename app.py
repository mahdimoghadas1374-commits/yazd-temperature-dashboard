import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------------- TITLE ----------------
st.title("🌡️ داشبورد تحلیل دمای شهرستان‌های استان یزد")

# ---------------- DESCRIPTION ----------------
st.markdown("""
### 📌 هدف این سامانه

این داشبورد برای **تحلیل و پایش تغییرات دمایی شهرستان‌های استان یزد** طراحی شده است.

کاربردها:

- بررسی روند تغییرات دما در سال‌های مختلف  
- مقایسه دمای شهرستان‌ها  
- تحلیل میانگین دما در بازه زمانی دلخواه  
- کمک به مطالعات اقلیمی و زیست‌محیطی  

---

### 🧭 نحوه استفاده

1️⃣ از سمت چپ، **شهرستان مورد نظر** را انتخاب کنید.  
2️⃣ بازه سال مورد نظر را مشخص کنید.  
3️⃣ نمودار تغییرات دما نمایش داده می‌شود.  
4️⃣ میانگین دما در بازه انتخابی نیز محاسبه خواهد شد.

---
""")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("yazd Counties_temperature.csv")

# تبدیل داده ماهانه به طولی
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

df_long = df.melt(
    id_vars=["County","YEAR"],
    value_vars=months,
    var_name="Month",
    value_name="Temperature"
)

# تبدیل نام ماه به عدد
month_map = {m:i+1 for i,m in enumerate(months)}
df_long["Month_Num"] = df_long["Month"].map(month_map)

# درست کردن ستون تاریخ (روز اول هر ماه)
df_long["Date"] = pd.to_datetime(
    df_long["YEAR"].astype(str) + "-" + df_long["Month_Num"].astype(str) + "-01"
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("🎛️ تنظیمات")

county = st.sidebar.selectbox(
    "انتخاب شهرستان",
    df_long["County"].unique()
)

year_range = st.sidebar.slider(
    "بازه سال",
    int(df_long["YEAR"].min()),
    int(df_long["YEAR"].max()),
    (2015, 2024)
)

# ---------------- FILTER ----------------
filtered = df_long[
    (df_long["County"] == county) &
    (df_long["YEAR"] >= year_range[0]) &
    (df_long["YEAR"] <= year_range[1])
]

# مرتب سازی زمانی
filtered["Temperature"] = pd.to_numeric(filtered["Temperature"], errors="coerce")
filtered = filtered.dropna(subset=["Temperature"])
filtered = filtered.sort_values("Date")

# ---------------- AVERAGE ----------------
avg_temp = filtered["Temperature"].mean()

st.metric(
    "میانگین دما در بازه انتخابی",
    f"{avg_temp:.2f} °C"
)

# ---------------- CHART ----------------
fig = px.line(
    filtered,
    x="Date",
    y="Temperature",
    color="YEAR",
    title=f"روند تغییرات دمای {county}",
    labels={"Temperature":"دما (°C)", "Date":"زمان"},
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("""
---
📊 منبع داده: NASA POWER Dataset  
🎓 پروژه دانشگاهی تحلیل اقلیم استان یزد  
""")
