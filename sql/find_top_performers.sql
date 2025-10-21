-- Kueri untuk mencari ID Top Performer (Rating 5 di tahun terakhir)
SELECT
    employee_id
FROM
    performance_yearly
WHERE
    rating = 5
    AND year = (SELECT MAX(year) FROM performance_yearly)
ORDER BY
    employee_id
LIMIT 20; 