-- Hottest and coldest days per city
SELECT 
    c.name AS city,
    MAX(w.temp_max) AS hottest_day_temp,
    (SELECT w.date FROM daily_weather w 
     WHERE w.city_id = c.city_id 
     ORDER BY w.temp_max DESC LIMIT 1) AS hottest_date,
    MIN(w.temp_min) AS coldest_day_temp,
    (SELECT w.date FROM daily_weather w 
     WHERE w.city_id = c.city_id 
     ORDER BY w.temp_min ASC LIMIT 1) AS coldest_date
FROM daily_weather w
JOIN cities c ON c.city_id = w.city_id
GROUP BY c.name;