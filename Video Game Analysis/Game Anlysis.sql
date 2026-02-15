CREATE DATABASE IF NOT EXISTS game_analysis;
USE game_analysis;
SELECT DATABASE();

/*DROP TABLE IF EXISTS merged_game_data;
DROP TABLE IF EXISTS game_sales;
DROP TABLE IF EXISTS games_engagement;
-- Truncate TABLE games; 
-- Truncate TABLE vgsales; 
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS vgsales;
-- DESCRIBE games;*/

-- Games Engagement (METADATA) Table
CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(255) NOT NULL,
    platform VARCHAR(50),
    genres VARCHAR(200),
    rating FLOAT,
    plays INT,
    wishlist INT,
    backlogs INT,
    release_date DATE,
    release_year INT,
    summary TEXT,
    reviews TEXT
);

SELECT COUNT(*) FROM games;
ALTER TABLE games
ADD COLUMN game_id INT AUTO_INCREMENT PRIMARY KEY FIRST;

CREATE TABLE game_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(255),
    platform VARCHAR(50),
    publisher VARCHAR(100),
    year INT,
    na_sales FLOAT,
    eu_sales FLOAT,
    jp_sales FLOAT,
    other_sales FLOAT,
    global_sales FLOAT
);

SELECT COUNT(*) FROM game_sales;
describe game_sales;
ALTER TABLE game_sales
ADD COLUMN sale_id INT AUTO_INCREMENT PRIMARY KEY FIRST;

CREATE INDEX idx_games_title_platform
ON games(title);

CREATE INDEX idx_sales_name_platform
ON game_sales(title);

SELECT DATABASE();
USE game_analysis;
SHOW TABLES;

DESCRIBE games;
DESCRIBE game_sales;

UPDATE games
SET title = LOWER(TRIM(title));

UPDATE game_sales
SET name = LOWER(TRIM(name));

SELECT COUNT(*)
FROM games g
INNER JOIN game_sales s
ON g.title = s.name; -- And g.genres = s.genre;

-- DROP TABLE IF EXISTS merged_game_data;

CREATE TABLE merged_game_data (

    id INT AUTO_INCREMENT PRIMARY KEY,

    game_id INT,
    sale_id INT,
    title VARCHAR(255),
    genres VARCHAR(200),
    rating FLOAT,
    plays INT,
    wishlist INT,
    backlogs INT,
    platform VARCHAR(50),
    publisher VARCHAR(100),
    year INT,
    na_sales FLOAT,
    eu_sales FLOAT,
    jp_sales FLOAT,
    other_sales FLOAT,
    global_sales FLOAT
);
show tables;

INSERT INTO merged_game_data (

    game_id,
    sale_id,
    title,
    genres,
    rating,
    plays,
    wishlist,
    backlogs,
    platform,
    publisher,
    year,
    na_sales,
    eu_sales,
    jp_sales,
    other_sales,
    global_sales
)

SELECT
    g.game_id,
    s.sale_id,
    g.title,
    g.genres,
    g.rating,
    g.plays,
    g.wishlist,
    g.backlogs,
    s.platform,
    s.publisher,
    s.year,
    s.na_sales,
    s.eu_sales,
    s.jp_sales,
    s.other_sales,
    s.global_sales

FROM games g INNER JOIN game_sales s ON g.title = s.name;

-- Verify Merge Data
SELECT COUNT(*) FROM merged_game_data;
SELECT * FROM merged_game_data LIMIT 10;

-- Foreign Keys
ALTER TABLE merged_game_data
ADD CONSTRAINT fk_game
FOREIGN KEY (game_id) REFERENCES games(game_id);

ALTER TABLE merged_game_data
ADD CONSTRAINT fk_sale
FOREIGN KEY (sale_id) REFERENCES game_sales(sale_id);

CREATE VIEW powerbi_dashboard AS
SELECT
    title,
    genres,
    platform,
    rating,
    plays,
    wishlist,
    backlogs,
    publisher,
    year,
    global_sales
FROM merged_game_data;

SELECT COUNT(*)
FROM games g
JOIN game_sales s
ON g.title = s.name;

-- Examples :
SELECT COUNT(*) AS total_games
FROM games;
SELECT COUNT(*) AS total_sales
FROM game_sales;
SELECT COUNT(*) AS total_merged
FROM merged_game_data;

/*SELECT 
    times_listed,
    CASE 
        WHEN times_listed LIKE '%k' THEN 
            CAST(REPLACE(LOWER(times_listed), 'k', '') AS DECIMAL) * 1000
        ELSE 
            CAST(times_listed AS DECIMAL)
    END AS numeric_column
FROM games;
Select * from games;*/

-- EDA QUESTIONS & SQL ANSWERS – VIDEO GAME PROJECT:

/* PART A: games TABLE (Metadata)
-- Top-rated games */
SELECT title, rating FROM games ORDER BY rating DESC LIMIT 10;

-- Developers with highest average rating
SELECT team, AVG(rating) AS avg_rating FROM games GROUP BY team ORDER BY avg_rating DESC;

-- Most common genres
SELECT genres, COUNT(*) AS total_games FROM games GROUP BY genres ORDER BY total_games DESC;

-- Highest backlog vs wishlist
SELECT title, (backlogs - wishlist) AS diff FROM games ORDER BY diff DESC LIMIT 10;

-- Release trend by year
SELECT release_year, COUNT(*) AS total_games FROM games GROUP BY release_year ORDER BY release_year;

-- Rating distribution
SELECT rating, COUNT(*) AS count FROM games GROUP BY rating ORDER BY rating;

-- Top wishlisted games
SELECT title, wishlist FROM games ORDER BY wishlist DESC LIMIT 10;

-- Avg plays per genre
SELECT genres, AVG(plays) AS avg_plays FROM games GROUP BY genres ORDER BY avg_plays DESC;

-- Most productive developers
SELECT team,
       COUNT(*) AS total_games,
       AVG(rating) AS avg_rating FROM games GROUP BY team ORDER BY total_games DESC;

/*-- PART B: game_sales TABLE (Sales)
-- Best region by sales*/
SELECT
   SUM(na_sales) AS na,
   SUM(eu_sales) AS eu,
   SUM(jp_sales) AS jp,
   SUM(other_sales) AS other_region FROM game_sales;
   
-- Best-selling platforms
SELECT platform, SUM(global_sales) AS total_sales FROM game_sales GROUP BY platform ORDER BY total_sales DESC;

-- Sales trend by year
SELECT year, SUM(global_sales) AS total_sales FROM game_sales GROUP BY year ORDER BY year;

-- Top publishers
SELECT publisher, SUM(global_sales) AS total_sales FROM game_sales GROUP BY publisher ORDER BY total_sales DESC;

-- Top 10 global games
SELECT name, global_sales FROM game_sales ORDER BY global_sales DESC LIMIT 10;

-- Platform evolution over time
SELECT year, platform, SUM(global_sales) AS sales FROM game_sales GROUP BY year, platform ORDER BY year;

-- Regional sales by platform
SELECT platform,
       SUM(na_sales) AS na,
       SUM(eu_sales) AS eu,
       SUM(jp_sales) AS jp
FROM game_sales GROUP BY platform;

-- Regional genre preference
SELECT genres,
       SUM(na_sales) AS na,
       SUM(eu_sales) AS eu,
       SUM(jp_sales) AS jp
FROM merged_game_data GROUP BY genres;

-- Yearly sales change
SELECT year, SUM(global_sales) AS total_sales FROM game_sales GROUP BY year ORDER BY year;

-- Avg sales per publisher
SELECT publisher, AVG(global_sales) AS avg_sales FROM game_sales GROUP BY publisher;

-- Top 5 per platform
SELECT platform, name, global_sales FROM game_sales ORDER BY platform, global_sales DESC;

/* PART C: merged_game_data (Merged Table)
-- Best-selling genres */
SELECT genres, SUM(global_sales) AS sales FROM merged_game_data GROUP BY genres ORDER BY sales DESC;

-- Rating vs Sales
SELECT rating, AVG(global_sales) AS avg_sales FROM merged_game_data GROUP BY rating;

-- High-rated platforms
SELECT platform, COUNT(*) AS high_rated FROM merged_game_data WHERE rating >= 4 GROUP BY platform;

-- Release & sales trend
SELECT year, SUM(global_sales) AS total_sales FROM merged_game_data GROUP BY year ORDER BY year;

-- Wishlist vs sales
SELECT wishlist, global_sales FROM merged_game_data;

-- High engagement, low sales
SELECT title, plays, global_sales FROM merged_game_data WHERE plays > 3000 AND global_sales < 1;

-- Wishlist/backlog vs rating
SELECT wishlist, backlogs, rating FROM merged_game_data;

-- Engagement by genre
SELECT genres,
       AVG(plays) AS plays,
       AVG(wishlist) AS wishlist,
       AVG(backlogs) AS backlogs
FROM merged_game_data GROUP BY genres;

-- Best Genre + Platform combo
SELECT genres, platform, SUM(global_sales) AS sales FROM merged_game_data GROUP BY genres, platform ORDER BY sales DESC;


