"""Ola Ride Insights - Streamlit app.
Run:  pip install streamlit pandas plotly
      streamlit run streamlit_app.py
Keep ola_clean.csv in the same folder.
(Swap the sqlite connection for mysql.connector / SQLAlchemy if you want to query your MySQL database.)
"""
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Ola Ride Insights", page_icon="🚖", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv("ola_clean.csv", parse_dates=["Date"])


df = load_data()
conn = sqlite3.connect(":memory:", check_same_thread=False)
df.to_sql("ola_rides", conn, index=False, if_exists="replace")

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
vehicles = st.sidebar.multiselect("Vehicle type", sorted(df.Vehicle_Type.unique()), default=sorted(df.Vehicle_Type.unique()))
status = st.sidebar.multiselect("Booking status", sorted(df.Booking_Status.unique()), default=sorted(df.Booking_Status.unique()))
dmin, dmax = df.Date.min().date(), df.Date.max().date()
date_range = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
if len(date_range) != 2:
    st.stop()

f = df[
    df.Vehicle_Type.isin(vehicles)
    & df.Booking_Status.isin(status)
    & (df.Date.dt.date >= date_range[0])
    & (df.Date.dt.date <= date_range[1])
]
succ = f[f.Booking_Status == "Success"]

st.title("🚖 Ola Ride Insights")
tab_overview, tab_sql, tab_pbi = st.tabs(["Overview", "SQL Insights", "Power BI"])

# ---------- overview ----------
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total bookings", f"{len(f):,}")
    c2.metric("Success rate", f"{(len(succ) / len(f) * 100 if len(f) else 0):.1f}%")
    c3.metric("Success booking value", f"₹{succ.Booking_Value.sum():,.0f}")
    c4.metric("Avg distance (success)", f"{succ.Ride_Distance.mean() if len(succ) else 0:.1f} km")

    left, right = st.columns(2)
    daily = f.groupby(f.Date.dt.date).size().reset_index(name="Rides")
    left.plotly_chart(px.line(daily, x="Date", y="Rides", title="Ride volume over time"), use_container_width=True)
    right.plotly_chart(px.pie(f, names="Booking_Status", hole=0.5, title="Booking status breakdown"), use_container_width=True)

    left, right = st.columns(2)
    pay = succ[succ.Payment_Method != "Not Applicable"].groupby("Payment_Method").Booking_Value.sum().reset_index()
    left.plotly_chart(px.bar(pay, x="Payment_Method", y="Booking_Value", title="Revenue by payment method"), use_container_width=True)
    rate = succ.groupby("Vehicle_Type")[["Driver_Ratings", "Customer_Rating"]].mean().reset_index()
    right.plotly_chart(
        px.bar(rate.melt("Vehicle_Type"), x="Vehicle_Type", y="value", color="variable", barmode="group",
               title="Average ratings by vehicle type", range_y=[0, 5]),
        use_container_width=True,
    )

    cc, dc = st.columns(2)
    cust = f[f.Canceled_Rides_by_Customer != "Not Applicable"].Canceled_Rides_by_Customer.value_counts().reset_index()
    cust.columns = ["Reason", "Rides"]
    cc.plotly_chart(px.bar(cust, x="Rides", y="Reason", orientation="h", title="Cancellation reasons (Customer)"), use_container_width=True)
    drv = f[f.Canceled_Rides_by_Driver != "Not Applicable"].Canceled_Rides_by_Driver.value_counts().reset_index()
    drv.columns = ["Reason", "Rides"]
    dc.plotly_chart(px.bar(drv, x="Rides", y="Reason", orientation="h", title="Cancellation reasons (Driver)"), use_container_width=True)

# ---------- SQL insights ----------
QUERIES = {
    "1. Successful bookings": "SELECT * FROM ola_rides WHERE Booking_Status = 'Success' LIMIT 1000",
    "2. Avg ride distance per vehicle type": "SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_distance FROM ola_rides WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type ORDER BY avg_distance DESC",
    "3. Rides cancelled by customers": "SELECT COUNT(*) AS cancelled_by_customer FROM ola_rides WHERE Booking_Status = 'Canceled by Customer'",
    "4. Top 5 customers by rides": "SELECT Customer_ID, COUNT(Booking_ID) AS total_rides FROM ola_rides GROUP BY Customer_ID ORDER BY total_rides DESC, Customer_ID LIMIT 5",
    "5. Driver cancels: personal & car issue": "SELECT COUNT(*) AS driver_personal_car_issue FROM ola_rides WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue'",
    "6. Prime Sedan driver rating (max/min)": "SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating FROM ola_rides WHERE Vehicle_Type = 'Prime Sedan'",
    "7. UPI rides": "SELECT * FROM ola_rides WHERE Payment_Method = 'UPI' LIMIT 1000",
    "8. Avg customer rating per vehicle type": "SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating FROM ola_rides GROUP BY Vehicle_Type ORDER BY avg_customer_rating DESC",
    "9. Total value of successful rides": "SELECT SUM(Booking_Value) AS total_success_booking_value FROM ola_rides WHERE Booking_Status = 'Success'",
    "10. Incomplete rides with reason": "SELECT Booking_ID, Customer_ID, Vehicle_Type, Incomplete_Rides_Reason FROM ola_rides WHERE Incomplete_Rides = 'Yes'",
}

with tab_sql:
    st.caption("Queries run on the full cleaned dataset (sidebar filters do not apply). Tables 1 and 7 are limited to 1,000 rows for display.")
    choice = st.selectbox("Choose a query", list(QUERIES))
    st.code(QUERIES[choice], language="sql")
    result = pd.read_sql(QUERIES[choice], conn)
    search = st.text_input("Search in results")
    if search:
        mask = result.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        result = result[mask]
    st.dataframe(result, use_container_width=True)
    st.download_button("Download CSV", result.to_csv(index=False), file_name="query_result.csv")

# ---------- Power BI ----------
with tab_pbi:
    st.subheader("Power BI dashboard")
    url = st.text_input("Power BI embed URL (optional)", help="Paste the 'Publish to web' embed link to show the live report here.")
    if url:
        components.iframe(url, height=700, scrolling=True)
    else:
        st.caption("Dashboard pages exported from Power BI Desktop (OLA project.pbix).")
        from pathlib import Path
        pages = [
            ("Overall", "dashboard_overall.png"),
            ("Vehicle Type", "dashboard_vehicle_type.png"),
            ("Revenue", "dashboard_revenue.png"),
            ("Cancellation", "dashboard_cancellation.png"),
            ("Ratings", "dashboard_ratings.png"),
        ]
        shown = False
        for title, fname in pages:
            path = Path(__file__).parent / fname
            if path.exists():
                st.markdown(f"**{title}**")
                st.image(str(path), use_container_width=True)
                shown = True
        if not shown:
            st.info("Add the dashboard screenshots (dashboard_*.png) next to streamlit_app.py, or paste an embed URL above.")
