-- Ola Ride Insights - 10 SQL queries (MySQL)
-- Table: ola_rides (import ola_clean.csv)
-- CREATE DATABASE ola; USE ola;

-- 1. All successful bookings
SELECT * FROM ola_rides
WHERE Booking_Status = 'Success';

-- 2. Average ride distance per vehicle type (successful rides only;
--    cancelled rides have distance 0 and would pull the average down)
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY avg_distance DESC;

-- 3. Total rides cancelled by customers  (expected: 10499)
SELECT COUNT(*) AS cancelled_by_customer
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';

-- 4. Top 5 customers by number of rides
--    (CID954071 = 5 rides; the next four have 4 each, so ties are broken by Customer_ID)
SELECT Customer_ID, COUNT(Booking_ID) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC, Customer_ID
LIMIT 5;

-- 5. Rides cancelled by drivers for personal & car related issues  (expected: 6542)
SELECT COUNT(*) AS driver_personal_car_issue
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- 6. Max and min driver rating for Prime Sedan  (expected: 5.0 / 3.0)
SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';

-- 7. Rides paid via UPI  (expected: 25881 rows)
SELECT * FROM ola_rides
WHERE Payment_Method = 'UPI';

-- 8. Average customer rating per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

-- 9. Total booking value of successful rides  (expected: 35080467)
SELECT SUM(Booking_Value) AS total_success_booking_value
FROM ola_rides
WHERE Booking_Status = 'Success';

-- 10. Incomplete rides with reason  (expected: 3926 rows)
SELECT Booking_ID, Customer_ID, Vehicle_Type, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';
