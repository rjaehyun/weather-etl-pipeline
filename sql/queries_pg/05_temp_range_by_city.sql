-- Daily temperature range per city
SELECT
    c.name AS city,
    w.date,
    ROUND(w.temp_max::numeric, 1) AS high,
    ROUND(w.temp_min::numeric, 1) AS low,
    ROUND((w.temp_max - w.temp_min)::numeric, 1) AS temp_range
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
ORDER BY c.name, w.date DESC;