-- Hottest and coldest day per city
WITH ranked AS (
    SELECT
        c.name AS city,
        w.date,
        w.temp_max,
        w.temp_min,
        ROW_NUMBER() OVER (PARTITION BY c.city_id ORDER BY w.temp_max DESC) AS hot_rank,
        ROW_NUMBER() OVER (PARTITION BY c.city_id ORDER BY w.temp_min ASC)  AS cold_rank
    FROM daily_weather w
    JOIN cities c ON c.city_id = w.city_id
)
SELECT
    city,
    MAX(CASE WHEN hot_rank = 1 THEN temp_max END)  AS hottest_day_temp,
    MAX(CASE WHEN hot_rank = 1 THEN date END)      AS hottest_date,
    MIN(CASE WHEN cold_rank = 1 THEN temp_min END) AS coldest_day_temp,
    MIN(CASE WHEN cold_rank = 1 THEN date END)     AS coldest_date
FROM ranked
GROUP BY city
ORDER BY city;