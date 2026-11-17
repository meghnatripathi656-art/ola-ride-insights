"""Ola Ride Insights - data cleaning & feature engineering.
Run: python ola_cleaning.py   (OLA_DataSet.xlsx must be in the same folder; needs openpyxl)
Output: ola_clean.csv
"""
import pandas as pd

# 1. Load main sheet
df = pd.read_excel("OLA_DataSet.xlsx", sheet_name="July")
print("Shape:", df.shape)
print(df.isnull().sum())

# 2. Types, formats, derived features
df["Date"] = pd.to_datetime(df["Date"])
df["Time"] = df["Time"].astype(str)  # keep as HH:MM:SS text
df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
df["Day_Name"] = df["Date"].dt.day_name()
df["Day"] = df["Date"].dt.day
df["Month"] = df["Date"].dt.month_name()
df["Vehicle_Type"] = df["Vehicle_Type"].replace({"eBike": "E-Bike"})  # matches the slides

# 3. Missing values
# Ratings, TAT, distance etc. are blank for cancelled rides - this is expected.
# Keep ratings/TAT as NULL (do NOT fill with 0, it would pull averages down).
text_cols = ["Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
             "Incomplete_Rides", "Incomplete_Rides_Reason", "Payment_Method"]
df[text_cols] = df[text_cols].fillna("Not Applicable")

# 4. Cleanup
df = df.drop_duplicates(subset="Booking_ID")
df = df.drop(columns=["Vehicle Images"])  # image links live in Sheet2 if Power BI needs them
df.columns = df.columns.str.strip()

# 5. Save
df.to_csv("ola_clean.csv", index=False)
print("Saved ola_clean.csv", df.shape)
print(df["Booking_Status"].value_counts())
