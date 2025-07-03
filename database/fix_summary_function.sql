-- Fix the get_original_plan_summary function
DROP FUNCTION IF EXISTS get_original_plan_summary();

CREATE OR REPLACE FUNCTION get_original_plan_summary()
RETURNS TABLE (
    total_orders INTEGER,
    total_processing_time INTEGER,
    total_waiting_time INTEGER,
    avg_processing_time_per_order DECIMAL,
    avg_waiting_time_per_order DECIMAL,
    total_time INTEGER,
    avg_time_per_order DECIMAL,
    high_priority_orders INTEGER,
    low_priority_orders INTEGER,
    bottleneck_stage VARCHAR(20),
    max_waiting_time INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT owp.order_id)::INTEGER as total_orders,
        SUM(owp.proc_time)::INTEGER as total_processing_time,
        SUM(owp.wait_time)::INTEGER as total_waiting_time,
        AVG(owp.proc_time) as avg_processing_time_per_order,
        AVG(owp.wait_time) as avg_waiting_time_per_order,
        SUM(owp.total_time)::INTEGER as total_time,
        AVG(owp.total_time) as avg_time_per_order,
        COUNT(DISTINCT CASE WHEN owp.priority IN ('1', '2') THEN owp.order_id END)::INTEGER as high_priority_orders,
        COUNT(DISTINCT CASE WHEN owp.priority IN ('4', '5') THEN owp.order_id END)::INTEGER as low_priority_orders,
        'PICK'::VARCHAR(20) as bottleneck_stage,
        MAX(owp.wait_time)::INTEGER as max_waiting_time
    FROM (
        SELECT DISTINCT 
            order_id, 
            original_wms_plans.total_processing_time as proc_time, 
            original_wms_plans.total_waiting_time as wait_time, 
            original_wms_plans.total_time, 
            priority
        FROM original_wms_plans
    ) owp;
END;
$$ LANGUAGE plpgsql; 