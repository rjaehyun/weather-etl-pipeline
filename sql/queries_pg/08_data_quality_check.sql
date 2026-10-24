-- Check for missing or null data
SELECT 
    c.name AS city,
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN w.temp_max IS NULL THEN 1 END) AS null_temp_max,
    COUNT(CASE WHEN w.temp_min IS NULL THEN 1 END) AS null_temp_min,
    COUNT(CASE WHEN w.rainfall IS NULL THEN 1 END) AS null_rainfall,
    COUNT(CASE WHEN w.temp_max < w.temp_min THEN 1 END) AS invalid_temp_range
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
GROUP BY c.name;