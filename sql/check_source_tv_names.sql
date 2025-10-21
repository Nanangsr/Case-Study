-- Kueri untuk melihat semua nama TV unik dari data sumber
SELECT DISTINCT tv_name
FROM (
    SELECT 'iq' AS tv_name FROM profiles_psych WHERE iq IS NOT NULL
    UNION ALL
    SELECT 'pauli' AS tv_name FROM profiles_psych WHERE pauli IS NOT NULL
    UNION ALL
    SELECT pillar_code AS tv_name FROM competencies_yearly
    UNION ALL
    SELECT scale_code AS tv_name FROM papi_scores
) AS all_source_tv_names
ORDER BY tv_name;