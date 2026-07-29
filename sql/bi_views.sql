-- Star Schema for Power BI

CREATE OR REPLACE VIEW bi_dim_department AS
SELECT department_id, name AS department_name
FROM departments;

CREATE OR REPLACE VIEW bi_dim_stage AS
SELECT DISTINCT stage_name
FROM stage_events;

CREATE OR REPLACE VIEW bi_dim_source AS
SELECT DISTINCT source
FROM candidates;

CREATE OR REPLACE VIEW bi_dim_date AS
SELECT d::date AS date_val,
       EXTRACT(year FROM d) AS year,
       EXTRACT(quarter FROM d) AS quarter,
       EXTRACT(month FROM d) AS month,
       TO_CHAR(d, 'Month') AS month_name
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day'::interval) d;

CREATE OR REPLACE VIEW bi_fact_applications AS
SELECT 
    a.application_id,
    a.req_id,
    c.candidate_id,
    r.department_id,
    c.source,
    a.apply_date,
    (SELECT stage_name FROM stage_events se WHERE se.application_id = a.application_id ORDER BY event_date DESC LIMIT 1) as current_stage,
    (SELECT (o.offer_date - a.apply_date) FROM offers o WHERE o.application_id = a.application_id LIMIT 1) as days_to_offer
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN requisitions r ON a.req_id = r.req_id;

CREATE OR REPLACE VIEW bi_fact_headcount AS
WITH actuals AS (
    SELECT 
        department_id,
        TO_CHAR(start_date, 'YYYY-MM') as join_month,
        COUNT(*) as hires
    FROM employees
    GROUP BY department_id, TO_CHAR(start_date, 'YYYY-MM')
)
SELECT 
    hp.department_id,
    hp.fiscal_period,
    hp.planned_headcount,
    hp.planned_hires,
    COALESCE(a.hires, 0) as actual_hires
FROM headcount_plan hp
LEFT JOIN actuals a ON hp.department_id = a.department_id AND hp.fiscal_period = a.join_month;
