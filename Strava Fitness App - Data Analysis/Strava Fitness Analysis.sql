-- Ensure you are using the correct database

USE strava_fitness_analysis;
SELECT DATABASE();

-- Create the table structure

CREATE TABLE daily_activity (
    Id BIGINT,
    ActivityDate DATE,
    TotalSteps INT,
    TotalDistance FLOAT,
    TrackerDistance FLOAT,
    LoggedActivitiesDistance FLOAT,
    VeryActiveDistance FLOAT,
    ModeratelyActiveDistance FLOAT,
    LightActiveDistance FLOAT,
    SedentaryActiveDistance FLOAT,
    VeryActiveMinutes INT,
    FairlyActiveMinutes INT,
    LightlyActiveMinutes INT,
    SedentaryMinutes INT,
    Calories INT
);
SELECT COUNT(*) FROM daily_activity;

CREATE TABLE sleep_day (
    Id BIGINT,
    SleepDay DATETIME,
    TotalSleepRecords INT,
    TotalMinutesAsleep INT,
    TotalTimeInBed INT
);
SELECT COUNT(*) FROM sleep_day;

CREATE TABLE weight_log (
    Id BIGINT,
    Date DATETIME,
    WeightKg FLOAT,
    WeightPounds FLOAT,
    Fat FLOAT,
    BMI FLOAT,
    IsManualReport BOOLEAN,
    LogId BIGINT
);
SELECT COUNT(*) FROM weight_log;

CREATE TABLE hourly_intensity (
    Id BIGINT,
    ActivityHour DATETIME,
    TotalIntensity INT,
    AverageIntensity FLOAT
);
SELECT COUNT(*) FROM hourly_intensity;

CREATE TABLE heartrate_daily (
    Id BIGINT,
    date DATE,
    avg_heartrate FLOAT,
    max_heartrate INT,
    min_heartrate INT
);

/*SET unique_checks = 0;
SET foreign_key_checks = 0;
SET sql_log_bin = 0; -- Disables binary logging (improves write speed)
SET autocommit = 0;
-- [Run your LOAD DATA command here]
COMMIT;
SET autocommit = 1;*/

LOAD DATA LOCAL INFILE 'E:/analytics PDF/Strava Fitness/cleaned_heartrate_seconds.csv'
INTO TABLE heartrate_daily
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' -- Handles quotes if they exist
LINES TERMINATED BY '\r\n' -- Standard for Windows
IGNORE 1 ROWS;            -- Skips the header to avoid Row 1 errors

select count(*) from heartrate_daily;
-- TRUNCATE TABLE heartrate_daily;

-- Master Table for Power BI

SELECT
    Id,
    DATE(Time) AS date,
    AVG(Value) AS avg_heartrate,
    MAX(Value) AS max_heartrate,
    MIN(Value) AS min_heartrate
FROM heartrate_daily
GROUP BY Id, DATE(Time);

CREATE TABLE heartrate_summary AS
SELECT 
    Id,
    DATE(Time) AS date,
    AVG(Value) AS avg_heartrate,
    MAX(Value) AS max_heartrate,
    MIN(Value) AS min_heartrate
FROM heartrate_daily
GROUP BY Id, DATE(Time);
SHOW COLUMNS FROM heartrate_summary;

CREATE TABLE fitness_master AS
SELECT
a.Id,
a.ActivityDate,

-- Activity
a.TotalSteps,
a.TotalDistance,
a.Calories,
a.VeryActiveMinutes,
a.FairlyActiveMinutes,
a.LightlyActiveMinutes,
a.SedentaryMinutes,

-- Sleep
s.TotalMinutesAsleep,
s.TotalTimeInBed,

-- Heart Rate
h.avg_heartrate,
h.max_heartrate,
h.min_heartrate,

-- Weight
w.WeightKg,
w.BMI,
w.Fat

FROM daily_activity a

LEFT JOIN sleep_day s
ON a.Id = s.Id
AND DATE(a.ActivityDate) = DATE(s.SleepDay)

LEFT JOIN heartrate_summary h
ON a.Id = h.Id
AND DATE(a.ActivityDate) = h.date

LEFT JOIN weight_log w
ON a.Id = w.Id
AND DATE(a.ActivityDate) = DATE(w.Date);

SHOW TABLES;
SELECT * 
FROM fitness_master
LIMIT 10;
select count(*) from fitness_master;

/*------------------------------------------------------------------------------*/

--                      Cleaning And EDA(Queries) Analysis 

/*------------------------------------------------------------------------------*/

--  SECTION 1: DATA QUALITY CHECKS

SELECT *
FROM daily_activity
WHERE Id IS NULL
   OR ActivityDate IS NULL;
   
-- Remove Duplicate Records
SELECT Id, ActivityDate, COUNT(*)
FROM daily_activity
GROUP BY Id, ActivityDate
HAVING COUNT(*) > 1;

DELETE t1
FROM daily_activity t1
JOIN daily_activity t2
ON t1.Id = t2.Id
AND t1.ActivityDate = t2.ActivityDate
AND t1.Calories > t2.Calories;

-- |Check Invalid Values Steps cannot be negative|
/*SELECT *
FROM daily_activity
WHERE TotalSteps < 0;

SELECT *
FROM daily_activity
WHERE Calories < 0;*/

-- |Remove Unrealistic Heart Rate Values|
-- Normal human heart rate range: 30 – 220 bpm
   
DELETE FROM heartrate_daily
WHERE Value < 30 OR Value > 220;

-- Check Sleep Data Issues: Sleep cannot exceed 1440 minutes per day.
SELECT *
FROM sleep_day
WHERE TotalMinutesAsleep > 1440;
/*    -- Remove if necessary:
DELETE FROM sleep_day
WHERE TotalMinutesAsleep > 1440;*/

UPDATE sleep_day
SET SleepDay = DATE(SleepDay);

UPDATE weight_log
SET Date = DATE(Date);

-- Create Date Column for Heart Rate (if needed)
UPDATE heartrate_daily
SET date = DATE(Time);

-- Validate User IDs: Check if any invalid IDs exist.
SELECT *
FROM daily_activity
WHERE Id <= 0;

-- Quick Data Quality Summary: Check ranges of important metrics.
SELECT
MIN(TotalSteps),
MAX(TotalSteps),
AVG(TotalSteps)
FROM daily_activity;

SELECT
MIN(Calories),
MAX(Calories),
AVG(Calories)
FROM daily_activity;

-- Check for negative values in activity columns
SELECT 
    MIN(TotalDistance), MAX(TotalDistance),
    MIN(TotalSteps), MAX(TotalSteps),
    MIN(LoggedActivitiesDistance), MAX(LoggedActivitiesDistance),
    MIN(SedentaryActiveDistance), MAX(SedentaryActiveDistance),
    MIN(SedentaryMinutes), MAX(SedentaryMinutes),
    MIN(Calories), MAX(Calories)
FROM daily_activity;

-- Find unrealistic logs with 1440 sedentary minutes (entire day)
SELECT 
    Id, SedentaryMinutes,
    COUNT(*) AS 'Sedentary Days (1440 mins)'
FROM daily_activity
WHERE SedentaryMinutes = 1440
GROUP BY Id, SedentaryMinutes; 

/* ---------------------------- Business Queries Analysis ---------------------------------------*/
/* ----------------------------------------------------------------------------------------------*/

-- SECTION 2: ACTIVITY PATTERN ANALYSIS

-- Average daily steps by weekday
SELECT 
DAYNAME(ActivityDate) AS weekday,
AVG(TotalSteps) AS avg_steps
FROM daily_activity
GROUP BY weekday
ORDER BY FIELD(weekday,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

/*SELECT 
    strftime('%w', ActivityDate) AS Weekday, 
    AVG(TotalSteps) AS AvgSteps
FROM daily_activity
GROUP BY Weekday
ORDER BY Weekday;*/  -- Use it if we had Date with Time in Activity Colunm.

-- Average active minutes vs calories burned
SELECT
DAYNAME(ActivityDate) AS weekday,
AVG(LightlyActiveMinutes) AS avg_light_activity,
AVG(FairlyActiveMinutes) AS avg_fair_activity,
AVG(VeryActiveMinutes) AS avg_very_active
FROM daily_activity
GROUP BY weekday
ORDER BY FIELD(weekday,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

-- Total Avg Activity Minutes Daily
SELECT 
    AVG(VeryActiveMinutes + LightlyActiveMinutes + FairlyActiveMinutes) AS TotalActiveMinutes,
    AVG(Calories) AS AvgCalories
FROM daily_activity;

--  Active Minutes vs Calories Burned
SELECT
DAYNAME(ActivityDate) AS weekday,
AVG(LightlyActiveMinutes + FairlyActiveMinutes + VeryActiveMinutes) AS avg_total_active_minutes,
AVG(Calories) AS avg_calories
FROM daily_activity
GROUP BY weekday
ORDER BY FIELD(weekday,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');

-- Average Steps by Participant and Weekday
SELECT
Id,
DAYNAME(ActivityDate) AS weekday,
AVG(TotalSteps) AS avg_steps
FROM daily_activity
GROUP BY Id, weekday
ORDER BY Id;

-- Sedentary Time Analysis: 
-- Sedentary Minutes by Participant
SELECT
Id,
DAYNAME(ActivityDate) AS weekday,
AVG(SedentaryMinutes) AS avg_sedentary_minutes
FROM daily_activity
GROUP BY Id, weekday
ORDER BY Id;

-- How much time do users spend being sedentary?
SELECT
AVG(SedentaryMinutes) AS avg_sedentary_minutes
FROM daily_activity;

-- Steps Distribution: daily step distributed among users.
SELECT
TotalSteps,
COUNT(*) AS frequency
FROM daily_activity
GROUP BY TotalSteps
ORDER BY TotalSteps;

-- Steps vs Calories: users burn more calories when they take more steps.
SELECT
TotalSteps,
Calories
FROM daily_activity
ORDER BY TotalSteps DESC;

-- User Activity Comparison: Which users are the most active overall.
SELECT
Id,
AVG(TotalSteps) AS avg_steps
FROM daily_activity
GROUP BY Id
ORDER BY avg_steps DESC;

/*--------------------------------------------------------*/

--  SECTION 3: SLEEP PATTERNS

SELECT *
FROM sleep_day
WHERE TotalMinutesAsleep IS NULL;

-- User Activity Comparison: Which users are the most active overall?
SELECT
AVG(TotalMinutesAsleep)/60 AS avg_sleep_hours
FROM sleep_day;

-- Average sleep minutes by weekday
SELECT 
    DAYNAME(SleepDay) AS Weekday, 
    AVG(TotalMinutesAsleep) AS AvgSleepMinutes
FROM sleep_day
GROUP BY Weekday;

-- Users with < 6 hours sleep
SELECT *
FROM sleep_day
WHERE TotalMinutesAsleep < 360;

-- Sleep vs Activity: Do users who walk more also sleep more.
SELECT
a.TotalSteps,
s.TotalMinutesAsleep
FROM daily_activity a
JOIN sleep_day s
ON a.Id = s.Id
AND DATE(a.ActivityDate) = DATE(s.SleepDay);

/*--------------------------------------------------------*/

--  SECTION 4: HEART RATE ANALYSIS

SELECT *
FROM heartrate_daily
WHERE Value IS NULL;

-- Heart Rate Trend: average heart rate change over time (Average heart rate per day).

SELECT
date,
AVG(Value) AS avg_heart_rate
FROM heartrate_daily
GROUP BY date
ORDER BY date;

-- Average heart rate by hour of day : At what time of day is heart rate highest?
SELECT
HOUR(Time) AS hour_of_day,
AVG(Value) AS avg_heart_rate
FROM heartrate_daily
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Heart Rate Distribution: What is the distribution of heart rate values?
SELECT
Value AS heart_rate,
COUNT(*) AS frequency
FROM heartrate_daily
GROUP BY heart_rate
ORDER BY heart_rate;

/*--------------------------------------------------------*/

--  SECTION 5: BMI & WEIGHT ANALYSIS


-- Weight vs Activity: Users with different weight levels have different activity levels.
SELECT
w.WeightKg,
AVG(a.TotalSteps) AS avg_steps
FROM weight_log w
JOIN daily_activity a
ON w.Id = a.Id
GROUP BY w.WeightKg
ORDER BY w.WeightKg;

-- Categorize each BMI record
SELECT 
    BMI,
    CASE 
        WHEN BMI < 18.5 THEN 'Underweight'
        WHEN BMI >= 18.5 AND BMI < 25 THEN 'Normal'
        WHEN BMI >= 25 AND BMI < 30 THEN 'Overweight'
        ELSE 'Obese'
    END AS BMI_Category
FROM weight_Log;

-- Count number of users in each BMI category
SELECT 
    BMI_Category, 
    COUNT(*) AS Count
FROM (
    SELECT 
        CASE 
            WHEN BMI < 18.5 THEN 'Underweight'
            WHEN BMI >= 18.5 AND BMI < 25 THEN 'Normal'
            WHEN BMI >= 25 AND BMI < 30 THEN 'Overweight'
            ELSE 'Obese'
        END AS BMI_Category
    FROM weight_log
) AS bmi_data
GROUP BY BMI_Category;

-- Peak Workout Hours: At what hour are users most active?
SELECT
HOUR(ActivityHour) AS hour,
AVG(TotalIntensity) AS avg_intensity
FROM hourly_intensity
GROUP BY hour
ORDER BY hour;


/*--------------------------------------------------------END-------------------------------------------------*/

