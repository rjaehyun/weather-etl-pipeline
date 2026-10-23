-- Average temperature per city over the period
SELECT 
    c.name AS city,
    ROUND(AVG(w.temp_max), 2) AS avg_temp_max,
    ROUND(AVG(w.temp_min), 2) AS avg_temp_min,
    COUNT(*) AS days_recorded
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
GROUP BY c.name
ORDER BY avg_temp_max DESC;