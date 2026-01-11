SELECT * FROM `ola ride insight analysis`.ola_dataset;

-- Dataset Has Been Cleaned In Excel Sheet : Numeric Conversion, Duplicate and Null conversion,etc.

select * from ola_dataset;

-- 1. Retrieve all successful bookings
SELECT * FROM ola_dataset WHERE Booking_Status = 'Success';

-- 2. Average ride distance per vehicle type
SELECT 
    Vehicle_Type, ROUND(AVG(Ride_Distance),2) AS Avg_Ride_Distance FROM ola_dataset 
    WHERE Ride_Distance > 0 GROUP BY Vehicle_Type ORDER BY Avg_Ride_Distance DESC;

-- 3. Total cancelled rides by customers
SELECT COUNT(*) AS Total_Customer_Cancellations FROM ola_dataset WHERE Booking_Status = 'Canceled by Customer';

-- 4. Top 5 customers by number of rides
SELECT 
    Customer_ID, COUNT(*) AS Total_Rides FROM ola_dataset GROUP BY Customer_ID ORDER BY Total_Rides DESC LIMIT 5;
    
-- 5. Rides cancelled by drivers (personal/car issues)
SELECT 
    Incomplete_Rides_Reason, COUNT(*) AS Total FROM ola_dataset
WHERE Booking_Status = 'Canceled by Driver' 
AND Incomplete_Rides_Reason LIKE '%Customer Demand%' OR Incomplete_Rides_Reason LIKE '%Vehicle Breakdown%' 
OR Incomplete_Rides_Reason LIKE '%Other Issue%' OR  Incomplete_Rides_Reason LIKE '%Customer Demand%' GROUP BY Incomplete_Rides_Reason;

-- 6. Max & Min driver ratings for Prime Sedan
SELECT 
    MAX(Driver_Ratings) AS Max_Rating,MIN(Driver_Ratings) AS Min_Rating FROM ola_dataset WHERE Vehicle_Type = 'Prime Sedan';

-- 7. Rides paid via UPI
SELECT * FROM ola_dataset WHERE Payment_Method = 'UPI';

-- 8. Average customer rating per vehicle type
SELECT 
    Vehicle_Type, ROUND(AVG(Customer_Rating),2) AS Avg_Customer_Rating FROM ola_dataset GROUP BY Vehicle_Type;
    
-- 9. Total booking value of successful rides
SELECT 
    SUM(Booking_Value) AS Total_Revenue FROM ola_dataset WHERE Booking_Status = 'Success';
    
-- 10. List all Incomplete rides with reason
SELECT 
    Booking_ID, Booking_Status, Incomplete_Rides_Reason FROM ola_dataset WHERE Booking_Status <> 'Success';








