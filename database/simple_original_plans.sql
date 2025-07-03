-- Simple original WMS plans materialized view
CREATE MATERIALIZED VIEW original_wms_plans AS 
SELECT 
    o.id as order_id,
    o.customer_name,
    o.priority,
    o.shipping_deadline,
    o.total_pick_time,
    o.total_pack_time,
    5 as total_items,
    15.0 as total_weight,
    'PICK' as stage_name,
    1 as stage_order,
    o.id as order_sequence,
    30 as duration_minutes,
    10 as waiting_time_before,
    1 as worker_id,
    NULL as equipment_id,
    0 as start_time_minutes,
    30 as total_processing_time,
    10 as total_waiting_time,
    40 as total_time
FROM orders o 
WHERE o.status = 'pending' 
AND o.id IN (
    SELECT id FROM orders 
    WHERE status = 'pending' 
    ORDER BY priority ASC, shipping_deadline ASC 
    LIMIT 100
);

-- Create indexes
CREATE INDEX idx_original_wms_plans_order_id ON original_wms_plans(order_id);
CREATE INDEX idx_original_wms_plans_stage ON original_wms_plans(stage_name);
CREATE INDEX idx_original_wms_plans_worker_id ON original_wms_plans(worker_id);
CREATE INDEX idx_original_wms_plans_sequence ON original_wms_plans(order_sequence);

-- Success message
SELECT 'Simple original WMS plans created successfully!' as status; 