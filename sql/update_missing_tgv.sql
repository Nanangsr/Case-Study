-- Kueri untuk mengisi TGV yang kosong di tabel dim_talent_mapping
UPDATE dim_talent_mapping
SET "Talent Group Variable (TGV)" =
    CASE "Sub-test"
        -- CliftonStrengths
        WHEN 'Activator' THEN 'Motivation & Drive'
        WHEN 'Competition' THEN 'Motivation & Drive'
        WHEN 'Consistency' THEN 'Conscientiousness & Reliability'
        WHEN 'Context' THEN 'Cognitive & Problem-Solving'
        WHEN 'Empathy' THEN 'Social Orientation & Collaboration'
        WHEN 'Focus' THEN 'Conscientiousness & Reliability'
        WHEN 'Harmony' THEN 'Social Orientation & Collaboration'
        WHEN 'Individualization' THEN 'Social Orientation & Collaboration'
        WHEN 'Input' THEN 'Cognitive & Problem-Solving'
        WHEN 'Positivity' THEN 'Social Orientation & Collaboration'
        WHEN 'Responsibility' THEN 'Conscientiousness & Reliability'
        WHEN 'Restorative' THEN 'Cognitive & Problem-Solving'
        WHEN 'Significance' THEN 'Leadership & Influence'

        -- MBTI
        WHEN 'Feeling' THEN 'Social Orientation & Collaboration'
        WHEN 'Judging' THEN 'Conscientiousness & Reliability'
        WHEN 'Perceiving' THEN 'Adaptability & Stress Tolerance'
        WHEN 'Sensing' THEN 'Conscientiousness & Reliability'
        WHEN 'Thinking' THEN 'Cognitive & Problem-Solving'

        -- PAPI Kostick
        WHEN 'Papi_B' THEN 'Social Orientation & Collaboration'
        WHEN 'Papi_F' THEN 'Conscientiousness & Reliability'
        WHEN 'Papi_G' THEN 'Motivation & Drive'
        WHEN 'Papi_K' THEN 'Leadership & Influence'
        WHEN 'Papi_N' THEN 'Conscientiousness & Reliability'
        WHEN 'Papi_O' THEN 'Social Orientation & Collaboration'
        WHEN 'Papi_R' THEN 'Cognitive & Problem-Solving'
        WHEN 'Papi_V' THEN 'Motivation & Drive'
        WHEN 'Papi_W' THEN 'Conscientiousness & Reliability'
        WHEN 'Papi_X' THEN 'Leadership & Influence'

        -- Pilar Kompetensi
        WHEN 'iq' THEN 'Cognitive & Problem-Solving'
        WHEN 'pauli' THEN 'Cognitive & Problem-Solving' 
        WHEN 'QDD' THEN 'Conscientiousness & Reliability'
        WHEN 'STO' THEN 'Social Orientation & Collaboration'
        WHEN 'FTC' THEN 'Creativity & Innovation Orientation'
        WHEN 'VCU' THEN 'Commercial Savvy & Impact'
        WHEN 'CEX' THEN 'Creativity & Innovation Orientation'
        WHEN 'CSI' THEN 'Commercial Savvy & Impact'
        WHEN 'GDR' THEN 'Motivation & Drive'
        WHEN 'IDS' THEN 'Cognitive & Problem-Solving'
        WHEN 'LIE' THEN 'Leadership & Influence'
        WHEN 'SEA' THEN 'Social Orientation & Collaboration'

        ELSE "Talent Group Variable (TGV)" 
    END
WHERE
    "Talent Group Variable (TGV)" IS NULL OR "Talent Group Variable (TGV)" = ''; 