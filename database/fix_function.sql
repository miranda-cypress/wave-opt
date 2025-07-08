-- Enhanced function to get original plan for a specific order
CREATE OR REPLACE FUNCTION get_original_order_plan(order_id_param INTEGER)
RETURNS TABLE (
    order_id INTEGER,
    customer_name VARCHAR(100),
    priority INTEGER,
    shipping_deadline TIMESTAMPTZ,
    stage_name VARCHAR(20),
    stage_order INTEGER,
    duration_minutes DECIMAL,
    waiting_time_before INTEGER,
    start_time_minutes INTEGER,
    worker_id INTEGER,
    worker_name VARCHAR(100),
    equipment_id INTEGER,
    equipment_name VARCHAR(100),
    total_processing_time INTEGER,
    total_waiting_time INTEGER,
    total_time INTEGER,
    order_sequence INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        owp.order_id,
        owp.customer_name,
        owp.priority,
        owp.shipping_deadline,
        owp.stage_name,
        owp.stage_order,
        owp.duration_minutes,
        owp.waiting_time_before,
        owp.start_time_minutes,
        owp.worker_id,
        owp.worker_name,
        owp.equipment_id,
        owp.equipment_name,
        owp.total_processing_time,
        owp.total_waiting_time,
        owp.total_time,
        owp.order_sequence
    FROM original_wms_plans owp
    WHERE owp.order_id = order_id_param
    ORDER BY owp.stage_order;
END;
$$ LANGUAGE plpgsql; 