-- Compare cities side by side for the most recent date
WITH latest_date AS (
    SELECT MAX(date) AS max_date FROM daily_weather
)
SELECT 
    c.name AS city,
    w.date,
    ROUND(w.temp_max::numeric, 1) AS temp_max,
    ROUND(w.temp_min::numeric, 1) AS temp_min,
    ROUND(w.rainfall::numeric, 2) AS rainfall
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
CROSS JOIN latest_date
WHERE w.date = latest_date.max_date
ORDER BY c.name;