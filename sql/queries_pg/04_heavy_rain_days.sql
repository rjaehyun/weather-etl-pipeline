-- Days with rainfall above 10mm (heavy rain threshold)
SELECT 
    c.name AS city,
    w.date,
    ROUND(w.rainfall::numeric, 2) AS rainfall_mm,
    ROUND(w.temp_max::numeric, 2) AS temp_max
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
WHERE w.rainfall > 10
ORDER BY c.name, w.date;