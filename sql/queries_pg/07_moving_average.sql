-- 7-day moving average of max temperature per city
-- Window functions like AVG(...) OVER (...) are very powerful
SELECT 
    c.name AS city,
    w.date,
    ROUND(w.temp_max::numeric, 1) AS temp_max,
    ROUND(
        AVG(w.temp_max) OVER (
            PARTITION BY c.city_id 
            ORDER BY w.date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::numeric, 
        1
    ) AS moving_avg_7d
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
ORDER BY c.name, w.date;