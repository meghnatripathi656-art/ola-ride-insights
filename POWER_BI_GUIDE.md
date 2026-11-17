# Power BI guide - Ola Ride Insights

## 1. Connect data
**Option A (MySQL):** Get Data > MySQL database > Server `localhost`, Database `ola` > Import > table `ola_rides`.
(Power BI may ask for the MySQL connector: install "MySQL Connector/NET" from dev.mysql.com.)
**Option B (easy):** Get Data > Text/CSV > `ola_clean.csv` > Load.

In Power Query set types: `Date` = Date/Time, `Booking_Value`, `Ride_Distance` = Whole number, `Driver_Ratings`, `Customer_Rating` = Decimal.
Do NOT replace blank ratings with 0.

## 2. Page setup
Page size: 16:9. Page background: insert the matching slide from `docs/Ola-Slides-filled.pptx` as image
(File > Export > PDF/PNG), then Format page > Canvas background > Image. Create 5 pages named:
Overall, Vehicle Type, Revenue, Cancellation, Ratings.
Add the same 3 slicers on every page: **Vehicle_Type**, **Date**, **Booking_Status**.

## 3. DAX measures (Modeling > New measure)
```DAX
Total Bookings = COUNTROWS(ola_rides)
Successful Bookings = CALCULATE(COUNTROWS(ola_rides), ola_rides[Booking_Status] = "Success")
Success Rate % = DIVIDE([Successful Bookings], [Total Bookings])
Cancelled by Customer = CALCULATE(COUNTROWS(ola_rides), ola_rides[Booking_Status] = "Canceled by Customer")
Cancelled by Driver = CALCULATE(COUNTROWS(ola_rides), ola_rides[Booking_Status] = "Canceled by Driver")
Driver Not Found = CALCULATE(COUNTROWS(ola_rides), ola_rides[Booking_Status] = "Driver Not Found")
Total Booking Value = SUM(ola_rides[Booking_Value])
Success Booking Value = CALCULATE(SUM(ola_rides[Booking_Value]), ola_rides[Booking_Status] = "Success")
Avg Distance (Success) = CALCULATE(AVERAGE(ola_rides[Ride_Distance]), ola_rides[Booking_Status] = "Success")
Total Distance = SUM(ola_rides[Ride_Distance])
Avg Driver Rating = AVERAGE(ola_rides[Driver_Ratings])
Avg Customer Rating = AVERAGE(ola_rides[Customer_Rating])
```
`AVERAGE` ignores blanks, so ratings of cancelled rides do not distort the average.

## 4. Visuals per page
| Page | Visual | Fields |
|---|---|---|
| Overall | Line chart: Ride volume over time | Axis `Date` (day), Values `Total Bookings` |
| Overall | Donut: Booking status breakdown | Legend `Booking_Status`, Values `Total Bookings` |
| Overall | Cards | Total Bookings, Success Rate %, Success Booking Value |
| Vehicle Type | Table / matrix (matches slide 2) | `Vehicle_Type`, Total Booking Value, Success Booking Value, Avg Distance (Success), Total Distance |
| Vehicle Type | Bar: Top 5 vehicle types by ride distance | Axis `Vehicle_Type`, Values `Total Distance`, Filter: Top N = 5 by Total Distance |
| Revenue | Column: Revenue by payment method | Axis `Payment_Method`, Values `Success Booking Value`; **filter `Payment_Method` is not "Not Applicable"** |
| Revenue | Bar: Top 5 customers by booking value | Axis `Customer_ID`, Values `Success Booking Value`, Top N = 5 |
| Revenue | Column: Ride distance per day | Axis `Date`, Values `Total Distance` |
| Cancellation | Bar: Reasons (Customer) | Axis `Canceled_Rides_by_Customer`, Values `Total Bookings`; **filter not "Not Applicable"** |
| Cancellation | Bar: Reasons (Driver) | Axis `Canceled_Rides_by_Driver`, Values `Total Bookings`; **filter not "Not Applicable"** |
| Ratings | Matrix (matches slide 5) | Columns `Vehicle_Type`, Values `Avg Driver Rating`, `Avg Customer Rating` |
| Ratings | Histogram-style column | Axis `Driver_Ratings` (as category), Values `Total Bookings`; same for `Customer_Rating` |
| Ratings | Scatter: Customer vs Driver ratings | X `Avg Customer Rating`, Y `Avg Driver Rating`, Details `Vehicle_Type` |

## 5. Publish and embed in Streamlit
Home > Publish to Power BI service (free work/school account needed). In the service: File > Embed report >
Publish to web (public) and copy the iframe URL, then paste it in the **Power BI** tab of the Streamlit app.
If your account cannot publish to web, add screenshots of each dashboard page to the Streamlit app instead.
