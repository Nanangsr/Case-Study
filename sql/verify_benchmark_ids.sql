-- Kueri untuk verifikasi ID Benchmark
SELECT
    e.employee_id,
    e.fullname,
    py.rating,
    py.year
FROM
    employees e
LEFT JOIN
    performance_yearly py ON e.employee_id = py.employee_id
WHERE
    e.employee_id IN ('EMP100010', 'EMP100011', 'EMP100012')
    AND
    py.year = (SELECT MAX(year) FROM performance_yearly);