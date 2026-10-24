-- Total rainfall per city, with a count of rainy days
SELECT 
    c.name AS city,
    ROUND(SUM(w.rainfall)::numeric, 2) AS total_rainfall_mm,
    COUNT(CASE WHEN w.rainfall > 0 THEN 1 END) AS rainy_days,
    ROUND(AVG(w.rainfall)::numeric, 2) AS avg_daily_rainfall
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
GROUP BY c.name
ORDER BY total_rainfall_mm DESC;