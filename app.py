import pandas as pd
import matplotlib.pyplot as plt

# 1) خواندن فایل اکسل / CSV
df = pd.read_csv("yazd Counties_temperature.csv")

# 2) نمایش اطلاعات اولیه (برای اطمینان)
print("Columns:", df.columns)
print("Counties:", df["County"].unique())
print("Parameters:", df["PARAMETER"].unique())

# 3) فیلتر استان یزد (فارسی یا انگلیسی)
df_yazd = df[df["County"].str.contains("Yazd|یزد", na=False)]

# 4) فقط دما (NASA POWER معمولاً T2M است)
df_yazd = df_yazd[df_yazd["PARAMETER"] == "T2M"]

# 5) مرتب‌سازی بر اساس سال
df_yazd = df_yazd.sort_values("YEAR")

# 6) محاسبه میانگین سالانه (ستون ANN)
years = df_yazd["YEAR"]
annual_temp = df_yazd["ANN"]

# 7) رسم نمودار
plt.figure(figsize=(10,5))
plt.plot(years, annual_temp, marker="o")
plt.xlabel("Year")
plt.ylabel("Annual Mean Temperature (C)")
plt.title("Yazd Annual Mean Temperature - NASA POWER")
plt.grid(True)
plt.tight_layout()
plt.show()
