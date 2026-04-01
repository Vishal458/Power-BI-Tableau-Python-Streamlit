--SELECT datname FROM pg_database;

CREATE TABLE bird_data (
    Admin_Unit_Code TEXT,
    Sub_Unit_Code TEXT,
    Site_Name TEXT,
    Plot_Name TEXT,
    Location_Type TEXT,
    Year INT,
    Date TIMESTAMP,
    Start_Time TIMESTAMP,
    End_Time TIMESTAMP,
    Observer TEXT,
    Visit INT,
    Interval_Length TEXT,
    ID_Method TEXT,
    Distance TEXT,
    Flyover_Observed TEXT,
    Sex TEXT,
    Common_Name TEXT,
    Scientific_Name TEXT,
    AcceptedTSN TEXT,
    NPSTaxonCode TEXT,
    AOU_Code TEXT,
    PIF_Watchlist_Status TEXT,
    Regional_Stewardship_Status TEXT,
    Temperature FLOAT,
    Humidity FLOAT,
    Sky TEXT,
    Wind TEXT,
    Disturbance TEXT,
    Initial_Three_Min_Cnt TEXT,
    Admin_Unit TEXT,
    Habitat_Type TEXT,
    TaxonCode TEXT,
    Previously_Obs TEXT,
    Hour INT,
    Time_Period TEXT,
    Month INT
);

-- DROP TABLE bird_data;


copy bird_data 
FROM 'E:/Analytics PDF/Bird Species Observation Analysis/cleaned_bird_data.csv' 
DELIMITER ',' 
CSV HEADER 
QUOTE '"' 
ESCAPE '"';

SELECT COUNT(*) FROM bird_data;

SELECT * FROM bird_data LIMIT 10;

ALTER TABLE bird_data
ALTER COLUMN Temperature TYPE FLOAT USING Temperature::FLOAT;


-- Business Queries Analysis 

-- Forest vs Grassland comparison: Which habitat has more birds?

SELECT Habitat_Type, COUNT(*) AS total_birds
FROM bird_data
GROUP BY Habitat_Type
ORDER BY total_birds DESC;

-- Biodiversity comparison: Which habitat has more species diversity?
SELECT Habitat_Type, COUNT(DISTINCT Scientific_Name) AS species_count
FROM bird_data
GROUP BY Habitat_Type
ORDER BY species_count DESC;

-- Best locations for conservation / tourism: Which locations are biodiversity hotspots?
SELECT Admin_Unit, COUNT(*) AS total_birds
FROM bird_data
GROUP BY Admin_Unit
ORDER BY total_birds DESC;

-- Dominant species: Which species are most common?
SELECT Common_Name, COUNT(*) AS count
FROM bird_data
GROUP BY Common_Name
ORDER BY count DESC
LIMIT 10;

-- Habitat preference: Which species prefer which habitat?
SELECT Habitat_Type, Common_Name, COUNT(*) AS count
FROM bird_data
GROUP BY Habitat_Type, Common_Name
ORDER BY Habitat_Type, count DESC;

-- WEATHER IMPACT : 

--How does temperature affect bird activity?
SELECT Temperature, COUNT(*) AS bird_count
FROM bird_data
GROUP BY Temperature
ORDER BY Temperature;

-- How does humidity affect bird activity?
SELECT Humidity, COUNT(*) AS bird_count
FROM bird_data
GROUP BY Humidity
ORDER BY Humidity;

-- Weather conditions vs activity
SELECT Sky, COUNT(*) AS bird_count
FROM bird_data
GROUP BY Sky
ORDER BY bird_count DESC;

-- TIME ANALYSIS:

-- Peak bird activity hour
SELECT Hour, COUNT(*) AS activity
FROM bird_data
WHERE Hour IS NOT NULL
GROUP BY Hour
ORDER BY activity DESC
LIMIT 5;

-- Activity by time period
SELECT Time_Period, COUNT(*) AS activity
FROM bird_data
GROUP BY Time_Period
ORDER BY activity DESC;

-- Monthly trend (seasonality)
SELECT Month, COUNT(*) AS total_birds
FROM bird_data
GROUP BY Month
ORDER BY Month;

-- Yearly trend
SELECT Year, COUNT(*) AS total_birds
FROM bird_data
GROUP BY Year
ORDER BY Year;

-- SPECIES ANALYSIS:

-- Total unique species
SELECT COUNT(DISTINCT Scientific_Name) AS total_species
FROM bird_data;

-- Species richness per location
SELECT Admin_Unit, COUNT(DISTINCT Scientific_Name) AS species_count
FROM bird_data
GROUP BY Admin_Unit
ORDER BY species_count DESC;

-- Species distribution (Top 10)
SELECT Common_Name, COUNT(*) AS count
FROM bird_data
GROUP BY Common_Name
ORDER BY count DESC
LIMIT 10;

-- Sex ratio
SELECT Sex, COUNT(*) AS count
FROM bird_data
GROUP BY Sex;

-- BEHAVIOR ANALYSIS:

-- Bird behavior (Identification method)
SELECT ID_Method, COUNT(*) AS count
FROM bird_data
GROUP BY ID_Method
ORDER BY count DESC;

-- Flyover behavior
SELECT Flyover_Observed, COUNT(*) AS count
FROM bird_data
GROUP BY Flyover_Observed;

-- Distance analysis
SELECT Distance, COUNT(*) AS count
FROM bird_data
GROUP BY Distance
ORDER BY count DESC;

-- Observation interval
SELECT Interval_Length, COUNT(*) AS count
FROM bird_data
GROUP BY Interval_Length
ORDER BY count DESC;

-- CONSERVATION ANALYSIS:

-- Watchlist species (at-risk)
SELECT PIF_Watchlist_Status, COUNT(*) AS count
FROM bird_data
GROUP BY PIF_Watchlist_Status;

-- Regional stewardship
SELECT Regional_Stewardship_Status, COUNT(*) AS count
FROM bird_data
GROUP BY Regional_Stewardship_Status;

-- At-risk species list
SELECT DISTINCT Common_Name
FROM bird_data
WHERE PIF_Watchlist_Status = 'TRUE';


-- Extended Business Insights :

-- Most active location
SELECT Admin_Unit, COUNT(*) AS total
FROM bird_data
GROUP BY Admin_Unit
ORDER BY total DESC
LIMIT 1;

-- Peak observation condition
SELECT Sky, COUNT(*) AS total
FROM bird_data
GROUP BY Sky
ORDER BY total DESC
LIMIT 1;

-- Best time + location combo
SELECT Admin_Unit, Time_Period, COUNT(*) AS total
FROM bird_data
GROUP BY Admin_Unit, Time_Period
ORDER BY total DESC
LIMIT 5;


