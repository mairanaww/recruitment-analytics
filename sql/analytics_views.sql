-- Time-to-fill by department
CREATE OR REPLACE VIEW v_time_to_fill AS
SELECT 
    d.name AS department,
    r.req_id,
    r.title,
    r.open_date,
    r.close_date,
    (r.close_date - r.open_date) AS days_to_fill
FROM requisitions r
JOIN departments d ON r.department_id = d.department_id
WHERE r.status = 'Closed' AND r.close_date IS NOT NULL;

-- Funnel conversion (stage-to-stage)
CREATE OR REPLACE VIEW v_funnel_conversion AS
WITH stage_counts AS (
    SELECT stage_name, COUNT(DISTINCT application_id) as num_applications
    FROM stage_events
    GROUP BY stage_name
)
SELECT * FROM stage_counts;

-- Offer acceptance rate
CREATE OR REPLACE VIEW v_offer_acceptance AS
SELECT 
    DATE_TRUNC('month', offer_date) as offer_month,
    COUNT(*) as total_offers,
    SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END) as accepted_offers,
    ROUND(SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as acceptance_rate_pct
FROM offers
GROUP BY 1;

-- Headcount actual vs plan
CREATE OR REPLACE VIEW v_headcount_vs_plan AS
WITH current_actual AS (
    SELECT 
        department_id,
        COUNT(*) as actual_headcount
    FROM employees
    WHERE status = 'Active'
    GROUP BY department_id
)
SELECT 
    d.name AS department,
    hp.fiscal_period,
    hp.planned_headcount,
    COALESCE(ca.actual_headcount, 0) as actual_headcount,
    COALESCE(ca.actual_headcount, 0) - hp.planned_headcount as variance
FROM headcount_plan hp
JOIN departments d ON hp.department_id = d.department_id
LEFT JOIN current_actual ca ON hp.department_id = ca.department_id;
