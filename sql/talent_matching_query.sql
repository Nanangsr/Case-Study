WITH
all_employee_scores AS MATERIALIZED (
  SELECT employee_id, 'iq' AS tv_name, iq AS tv_value FROM profiles_psych WHERE iq IS NOT NULL
  UNION ALL
  SELECT employee_id, 'pauli' AS tv_name, pauli AS tv_value FROM profiles_psych WHERE pauli IS NOT NULL
  UNION ALL
  SELECT employee_id, pillar_code AS tv_name, score AS tv_value
  FROM competencies_yearly
  WHERE year = (SELECT MAX(year) FROM competencies_yearly)
  UNION ALL
  SELECT employee_id, scale_code AS tv_name, score AS tv_value FROM papi_scores
),

scores_with_details AS MATERIALIZED (
    SELECT
        s.employee_id, s.tv_name, s.tv_value,
        m."Talent Group Variable (TGV)" AS tgv_name,
        m."Meaning" AS meaning, m."Behavior Example" AS behavior_example,
        m."Sub-test" AS sub_test_original
    FROM all_employee_scores s
    INNER JOIN dim_talent_mapping m ON s.tv_name = m."Sub-test"
),

benchmark_baseline AS (
    SELECT
        tv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tv_value) AS baseline_score
    FROM scores_with_details
    WHERE employee_id IN ('EMP100010', 'EMP100011', 'EMP100012') 
    GROUP BY tv_name
),

tv_match_rates AS MATERIALIZED (
    SELECT
        s.employee_id, s.tv_name, s.tv_value AS user_score, b.baseline_score,
        s.tgv_name, s.meaning, s.behavior_example, s.sub_test_original,
        CASE
            WHEN b.baseline_score IS NULL THEN 0
            WHEN b.baseline_score = 0 AND COALESCE(s.tv_value, 0) = 0 THEN 100.0
            WHEN b.baseline_score = 0 AND COALESCE(s.tv_value, 0) <> 0 THEN 0
            ELSE (COALESCE(s.tv_value, 0) / b.baseline_score) * 100.0
        END AS tv_match_rate
    FROM scores_with_details s
    LEFT JOIN benchmark_baseline b ON s.tv_name = b.tv_name
),

tgv_match_rates AS MATERIALIZED (
    SELECT
        employee_id, tgv_name, AVG(tv_match_rate) AS tgv_match_rate
    FROM tv_match_rates
    GROUP BY employee_id, tgv_name
),

final_match_rates AS (
    SELECT
        employee_id, AVG(tgv_match_rate) AS final_match_rate
    FROM tgv_match_rates
    GROUP BY employee_id
)

-- Kueri Final
SELECT
    tvr.employee_id,
    emp.fullname,
    dir.name AS directorate,
    pos.name AS role,
    grd.name AS grade,
    tvr.tgv_name,
    tvr.sub_test_original AS tv_name,
    tvr.meaning,
    tvr.behavior_example,
    tvr.baseline_score,
    tvr.user_score,
    tvr.tv_match_rate,
    tgvr.tgv_match_rate,
    fmr.final_match_rate
FROM tv_match_rates tvr
JOIN tgv_match_rates tgvr ON tvr.employee_id = tgvr.employee_id AND tvr.tgv_name = tgvr.tgv_name
JOIN employees emp ON tvr.employee_id = emp.employee_id
LEFT JOIN final_match_rates fmr ON fmr.employee_id = tvr.employee_id
LEFT JOIN dim_directorates dir ON emp.directorate_id = dir.directorate_id
LEFT JOIN dim_positions pos ON emp.position_id = pos.position_id
LEFT JOIN dim_grades grd ON emp.grade_id = grd.grade_id
ORDER BY
    fmr.final_match_rate DESC NULLS LAST,
    tvr.employee_id,
    tvr.tgv_name;