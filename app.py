import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("Yazd Temperature Dashboard")

df = pd.read_csv("yazd Counties_temperature.csv")

# فقط پارامتر دما
df = df[df["PARAMETER"] == "T2M"]

# انتخاب شهرستان
county = st.selectbox("Select County", df["County"].unique())

df_county = df[df["County"] == county]

# تبدیل داده ماهانه به long format
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

df_long = df_county.melt(
    id_vars=["YEAR"],
    value_vars=months,
    var_name="Month",
    value_name="Temperature"
)

# رسم نمودار
fig, ax = plt.subplots()

ax.plot(df_long["Temperature"])
ax.set_title(f"Temperature Trend - {county}")

st.pyplot(fig)

# نمایش جدول
st.dataframe(df_long)
