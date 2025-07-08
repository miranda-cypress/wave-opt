-- Enhanced Original WMS Plan Generator
-- Creates materialized views and functions to generate baseline "original" plans
-- These represent how orders would be processed using basic WMS heuristics

-- Function to calculate original stage durations using realistic WMS heuristics
CREATE OR REPLACE FUNCTION calculate_original_stage_duration(
    order_id INTEGER,
    stage_name VARCHAR(20),
    total_pick_time DECIMAL,
    total_pack_time DECIMAL,
    order_priority VARCHAR(10),
    total_items INTEGER,
    total_weight DECIMAL
) RETURNS INTEGER AS $$
DECLARE
    base_duration INTEGER;
    priority_multiplier DECIMAL;
    complexity_multiplier DECIMAL;
    priority_int INTEGER;
    walking_time DECIMAL;
    item_count INTEGER;
BEGIN
    -- Convert priority string to integer
    priority_int := CASE order_priority
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN '5' THEN 5
        ELSE 3  -- Default to medium priority
    END;
    
    -- Get actual item count for this order
    SELECT get_order_item_count(order_id) INTO item_count;
    
    -- Base duration calculations based on WMS heuristics
    CASE stage_name
        WHEN 'PICK' THEN
            -- Use the order's total_pick_time if available and non-zero
            IF total_pick_time > 0 THEN
                base_duration := CEIL(total_pick_time * 1.3); -- 30% slower due to poor routing
            ELSE
                -- Use standard time per item if no pick time available
                base_duration := CEIL(item_count * 2.0); -- 2 minutes per item
            END IF;
            
            -- Add walking time for pick stage
            walking_time := calculate_order_walking_time(order_id);
            base_duration := base_duration + CEIL(walking_time);
            
            -- Priority affects picking speed (rush orders get rushed)
            IF priority_int <= 2 THEN
                base_duration := CEIL(base_duration * 0.9); -- 10% faster for high priority
            END IF;
            
            -- Weight affects picking time
            IF total_weight > 20 THEN
                base_duration := CEIL(base_duration * 1.2); -- 20% slower for heavy orders
            END IF;
            
        WHEN 'CONSOLIDATE' THEN
            -- Use standard time per item for consolidation
            base_duration := CEIL(item_count * 0.5); -- 0.5 minutes per item
            
            -- More items = more consolidation time
            IF item_count > 5 THEN
                base_duration := base_duration + (item_count - 5) * 0.2;
            END IF;
            
        WHEN 'PACK' THEN
            -- Use the order's total_pack_time if available and non-zero
            IF total_pack_time > 0 THEN
                base_duration := CEIL(total_pack_time * 1.4); -- 40% slower due to poor station assignment
            ELSE
                -- Use standard time per item if no pack time available
                base_duration := CEIL(item_count * 1.5); -- 1.5 minutes per item
            END IF;
            
            -- Heavy orders take longer to pack
            IF total_weight > 15 THEN
                base_duration := CEIL(base_duration * 1.15);
            END IF;
            
        WHEN 'LABEL' THEN
            -- Use standard time per order for labeling
            base_duration := 5; -- 5 minutes per order
            
            -- More items = more labels
            IF item_count > 3 THEN
                base_duration := base_duration + (item_count - 3) * 0.5;
            END IF;
            
        WHEN 'STAGE' THEN
            -- Use standard time per order for staging
            base_duration := 10; -- 10 minutes per order
            
            -- Heavy orders take longer to stage
            IF total_weight > 25 THEN
                base_duration := base_duration + 5;
            END IF;
            
        WHEN 'SHIP' THEN
            -- Use standard time per order for shipping
            base_duration := 8; -- 8 minutes per order
            
            -- Priority affects shipping speed
            IF priority_int <= 2 THEN
                base_duration := CEIL(base_duration * 0.8); -- 20% faster for high priority
            END IF;
            
        ELSE
            base_duration := 10;
    END CASE;
    
    RETURN base_duration;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate realistic waiting times based on WMS bottlenecks
CREATE OR REPLACE FUNCTION calculate_original_waiting_time(
    stage_name VARCHAR(20),
    order_priority VARCHAR(10),
    total_orders_in_queue INTEGER
) RETURNS INTEGER AS $$
DECLARE
    base_waiting_time INTEGER;
    queue_multiplier DECIMAL;
    priority_discount DECIMAL;
    priority_int INTEGER;
    max_waiting_time INTEGER := 60; -- Cap waiting time at 60 minutes
BEGIN
    -- Convert priority string to integer
    priority_int := CASE order_priority
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN '5' THEN 5
        ELSE 3  -- Default to medium priority
    END;
    
    -- Base waiting times based on typical WMS bottlenecks
    CASE stage_name
        WHEN 'PICK' THEN
            -- Wait after picking due to consolidation bottleneck
            base_waiting_time := 10;
        WHEN 'CONSOLIDATE' THEN
            -- Wait after consolidation due to packing bottleneck (most common)
            base_waiting_time := 15;
        WHEN 'PACK' THEN
            -- Wait after packing due to labeling bottleneck
            base_waiting_time := 8;
        WHEN 'LABEL' THEN
            -- Wait after labeling due to staging bottleneck
            base_waiting_time := 6;
        WHEN 'STAGE' THEN
            -- Wait after staging due to shipping bottleneck
            base_waiting_time := 12;
        ELSE
            base_waiting_time := 5;
    END CASE;
    
    -- Queue length affects waiting time (basic WMS doesn't optimize for this)
    IF total_orders_in_queue > 10 THEN
        queue_multiplier := 1.0 + (total_orders_in_queue - 10) * 0.1;
        base_waiting_time := CEIL(base_waiting_time * queue_multiplier);
    END IF;
    
    -- Priority orders get priority in queues (basic WMS feature)
    IF priority_int <= 2 THEN
        priority_discount := 0.7; -- 30% less waiting for high priority
        base_waiting_time := CEIL(base_waiting_time * priority_discount);
    END IF;
    
    -- Cap the waiting time at a reasonable maximum
    IF base_waiting_time > max_waiting_time THEN
        base_waiting_time := max_waiting_time;
    END IF;
    
    RETURN base_waiting_time;
END;
$$ LANGUAGE plpgsql;

-- Function to assign workers using basic WMS heuristics (first available, round-robin)
CREATE OR REPLACE FUNCTION get_original_worker_assignment(
    order_id INTEGER,
    stage_name VARCHAR(20),
    order_priority VARCHAR(10)
) RETURNS INTEGER AS $$
DECLARE
    worker_id INTEGER;
    available_workers INTEGER[];
    priority_int INTEGER;
BEGIN
    -- Convert priority string to integer
    priority_int := CASE order_priority
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN '5' THEN 5
        ELSE 3  -- Default to medium priority
    END;
    
    -- Basic WMS: Simple worker assignment based on availability and basic skills
    CASE stage_name
        WHEN 'PICK' THEN
            -- Pickers: workers 1-8 (basic WMS assigns to first available picker)
            worker_id := 1 + ((order_id + priority_int) % 8);
        WHEN 'PACK' THEN
            -- Packers: workers 9-12 (basic WMS assigns to first available packer)
            worker_id := 9 + ((order_id + priority_int) % 4);
        WHEN 'SHIP' THEN
            -- Shippers: workers 13-15 (basic WMS assigns to first available shipper)
            worker_id := 13 + ((order_id + priority_int) % 3);
        WHEN 'CONSOLIDATE' THEN
            -- General workers: workers 1-5 (basic WMS uses general workers)
            worker_id := 1 + ((order_id + priority_int) % 5);
        WHEN 'LABEL' THEN
            -- Label specialists: workers 6-8 (basic WMS assigns to label workers)
            worker_id := 6 + ((order_id + priority_int) % 3);
        WHEN 'STAGE' THEN
            -- Staging workers: workers 10-12 (basic WMS assigns to staging workers)
            worker_id := 10 + ((order_id + priority_int) % 3);
        ELSE
            -- Default: round-robin assignment
            worker_id := 1 + (order_id % 15);
    END CASE;
    
    RETURN worker_id;
END;
$$ LANGUAGE plpgsql;

-- Function to assign equipment using basic WMS heuristics (first available)
CREATE OR REPLACE FUNCTION get_original_equipment_assignment(
    stage_name VARCHAR(20),
    order_id INTEGER,
    order_priority VARCHAR(10)
) RETURNS INTEGER AS $$
DECLARE
    priority_int INTEGER;
BEGIN
    -- Convert priority string to integer
    priority_int := CASE order_priority
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN '5' THEN 5
        ELSE 3  -- Default to medium priority
    END;
    
    -- Basic WMS: Simple equipment assignment (first available)
    CASE stage_name
        WHEN 'PACK' THEN
            -- Packing stations: equipment 1-8 (basic WMS assigns to first available)
            RETURN 1 + ((order_id + priority_int) % 8);
        WHEN 'SHIP' THEN
            -- Dock doors: equipment 9-14 (basic WMS assigns to first available)
            RETURN 9 + ((order_id + priority_int) % 6);
        WHEN 'PICK' THEN
            -- Pick carts: equipment 15-34 (basic WMS assigns to first available)
            RETURN 15 + ((order_id + priority_int) % 20);
        WHEN 'LABEL' THEN
            -- Label printers: equipment 35-38 (basic WMS assigns to first available)
            RETURN 35 + ((order_id + priority_int) % 4);
        ELSE
            RETURN NULL;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate order sequence using basic WMS heuristics
CREATE OR REPLACE FUNCTION calculate_original_order_sequence(
    order_priority VARCHAR(10),
    shipping_deadline TIMESTAMPTZ,
    order_id INTEGER
) RETURNS INTEGER AS $$
DECLARE
    sequence_base INTEGER;
    deadline_factor INTEGER;
    priority_int INTEGER;
BEGIN
    -- Convert priority string to integer
    priority_int := CASE order_priority
        WHEN '1' THEN 1
        WHEN '2' THEN 2
        WHEN '3' THEN 3
        WHEN '4' THEN 4
        WHEN '5' THEN 5
        ELSE 3  -- Default to medium priority
    END;
    
    -- Basic WMS: Simple priority-based sequencing
    sequence_base := order_id; -- Start with order ID
    
    -- Priority orders get earlier sequence
    IF priority_int <= 2 THEN
        sequence_base := sequence_base - 1000; -- High priority orders go first
    ELSIF priority_int >= 4 THEN
        sequence_base := sequence_base + 1000; -- Low priority orders go last
    END IF;
    
    -- Deadline factor (basic WMS considers deadlines)
    deadline_factor := EXTRACT(EPOCH FROM (shipping_deadline - NOW())) / 3600; -- Hours until deadline
    IF deadline_factor < 4 THEN
        sequence_base := sequence_base - 500; -- Urgent orders get priority
    END IF;
    
    RETURN sequence_base;
END;
$$ LANGUAGE plpgsql;

-- Enhanced materialized view for original WMS plans using wave_order_metrics
CREATE MATERIALIZED VIEW original_wms_plans AS
WITH original_plan_version AS (
    SELECT id AS plan_version_id
    FROM wave_plan_versions
    WHERE version_type = 'original'
    ORDER BY id LIMIT 1
),
order_stages AS (
    SELECT 
        wa.order_id,
        c.name as customer_name,
        o.priority,
        o.shipping_deadline,
        wom.pick_time_minutes,
        wom.pack_time_minutes,
        wom.walking_time_minutes,
        wom.consolidate_time_minutes,
        wom.label_time_minutes,
        wom.stage_time_minutes,
        wom.ship_time_minutes,
        unnest(ARRAY['PICK', 'CONSOLIDATE', 'PACK', 'LABEL', 'STAGE', 'SHIP'])::VARCHAR(20) as stage_name,
        generate_series(1, 6) as stage_order,
        wa.wave_id,
        -- Calculate order sequence using basic WMS heuristics
        calculate_original_order_sequence(o.priority, o.shipping_deadline, o.id) as order_sequence
    FROM wave_assignments wa
    JOIN orders o ON wa.order_id = o.id
    LEFT JOIN customers c ON o.customer_id = c.id
    JOIN original_plan_version opv ON TRUE
    LEFT JOIN wave_order_metrics wom ON wom.order_id = wa.order_id AND wom.wave_id = wa.wave_id AND wom.plan_version_id = opv.plan_version_id
    WHERE o.status = 'pending'
),
stage_calculations AS (
    SELECT 
        os.*,
        -- Use times from wave_order_metrics for each stage
        CASE WHEN os.stage_name = 'PICK' THEN COALESCE(os.pick_time_minutes, 0)
             WHEN os.stage_name = 'CONSOLIDATE' THEN COALESCE(os.consolidate_time_minutes, 0)
             WHEN os.stage_name = 'PACK' THEN COALESCE(os.pack_time_minutes, 0)
             WHEN os.stage_name = 'LABEL' THEN COALESCE(os.label_time_minutes, 0)
             WHEN os.stage_name = 'STAGE' THEN COALESCE(os.stage_time_minutes, 0)
             WHEN os.stage_name = 'SHIP' THEN COALESCE(os.ship_time_minutes, 0)
             ELSE 0 END as duration_minutes,
        -- Calculate waiting time using queue-based heuristics (can be improved later)
        calculate_original_waiting_time(
            os.stage_name::VARCHAR(20), os.priority::VARCHAR, 
            (SELECT COUNT(*) FROM orders WHERE status = 'pending')::INTEGER
        ) as waiting_time_before,
        -- Assign workers using basic WMS heuristics
        get_original_worker_assignment(os.order_id, os.stage_name::VARCHAR(20), os.priority)::INTEGER as worker_id,
        -- Assign equipment using basic WMS heuristics
        get_original_equipment_assignment(os.stage_name::VARCHAR(20), os.order_id, os.priority) as equipment_id
    FROM order_stages os
)
SELECT 
    sc.*,
    w.name as worker_name,
    e.name as equipment_name,
    -- Calculate cumulative time (start time for each stage)
    (SUM(sc.duration_minutes + sc.waiting_time_before) OVER (
        PARTITION BY sc.order_id 
        ORDER BY sc.stage_order 
        ROWS UNBOUNDED PRECEDING
    ) - sc.waiting_time_before)::INTEGER as start_time_minutes,
    -- Calculate total processing time for the order
    SUM(sc.duration_minutes) OVER (PARTITION BY sc.order_id)::INTEGER as total_processing_time,
    -- Calculate total waiting time for the order
    SUM(sc.waiting_time_before) OVER (PARTITION BY sc.order_id)::INTEGER as total_waiting_time,
    -- Calculate completion time
    SUM(sc.duration_minutes + sc.waiting_time_before) OVER (PARTITION BY sc.order_id)::INTEGER as total_time
FROM stage_calculations sc
LEFT JOIN workers w ON sc.worker_id = w.id
LEFT JOIN equipment e ON sc.equipment_id = e.id
ORDER BY sc.order_sequence, sc.order_id, sc.stage_order;

-- Create indexes for performance
CREATE INDEX idx_original_wms_plans_order_id ON original_wms_plans(order_id);
CREATE INDEX idx_original_wms_plans_stage ON original_wms_plans(stage_name);
CREATE INDEX idx_original_wms_plans_worker_id ON original_wms_plans(worker_id);
CREATE INDEX idx_original_wms_plans_sequence ON original_wms_plans(order_sequence);

-- Function to refresh the materialized view
CREATE OR REPLACE FUNCTION refresh_original_plans() RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW original_wms_plans;
END;
$$ LANGUAGE plpgsql;

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

-- Enhanced function to get original plan summary with WMS-specific metrics
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
        SUM(owp.total_processing_time)::INTEGER as total_processing_time,
        SUM(owp.total_waiting_time)::INTEGER as total_waiting_time,
        AVG(owp.total_processing_time) as avg_processing_time_per_order,
        AVG(owp.total_waiting_time) as avg_waiting_time_per_order,
        SUM(owp.total_time)::INTEGER as total_time,
        AVG(owp.total_time) as avg_time_per_order,
        COUNT(DISTINCT CASE WHEN owp.priority IN ('1', '2') THEN owp.order_id END)::INTEGER as high_priority_orders,
        COUNT(DISTINCT CASE WHEN owp.priority IN ('4', '5') THEN owp.order_id END)::INTEGER as low_priority_orders,
        (SELECT stage_name FROM (
            SELECT stage_name, AVG(waiting_time_before) as avg_wait
            FROM original_wms_plans 
            GROUP BY stage_name 
            ORDER BY avg_wait DESC 
            LIMIT 1
        ) bottleneck) as bottleneck_stage,
        MAX(owp.waiting_time_before)::INTEGER as max_waiting_time
    FROM (
        SELECT DISTINCT order_id, total_processing_time, total_waiting_time, total_time, priority
        FROM original_wms_plans
    ) owp;
END;
$$ LANGUAGE plpgsql;

-- Function to analyze WMS inefficiencies
CREATE OR REPLACE FUNCTION analyze_wms_inefficiencies()
RETURNS TABLE (
    inefficiency_type VARCHAR(50),
    description TEXT,
    impact_level VARCHAR(20),
    affected_orders INTEGER,
    time_waste_minutes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Poor Routing'::VARCHAR(50) as inefficiency_type,
        'Basic WMS uses simple zone-based picking without route optimization'::TEXT as description,
        'High'::VARCHAR(20) as impact_level,
        COUNT(DISTINCT order_id)::INTEGER as affected_orders,
        SUM(duration_minutes * 0.3)::INTEGER as time_waste_minutes
    FROM original_wms_plans 
    WHERE stage_name = 'PICK'
    
    UNION ALL
    
    SELECT 
        'Equipment Bottlenecks'::VARCHAR(50),
        'Basic WMS assigns to first available equipment without optimization'::TEXT,
        'Medium'::VARCHAR(20),
        COUNT(DISTINCT order_id)::INTEGER,
        SUM(waiting_time_before)::INTEGER
    FROM original_wms_plans 
    WHERE stage_name IN ('PACK', 'SHIP')
    
    UNION ALL
    
    SELECT 
        'Worker Assignment'::VARCHAR(50),
        'Basic WMS uses simple round-robin assignment without skill matching'::TEXT,
        'Medium'::VARCHAR(20),
        COUNT(DISTINCT order_id)::INTEGER,
        SUM(duration_minutes * 0.2)::INTEGER
    FROM original_wms_plans 
    WHERE stage_name IN ('PACK', 'LABEL', 'STAGE')
    
    UNION ALL
    
    SELECT 
        'Queue Management'::VARCHAR(50),
        'Basic WMS does not optimize for queue lengths and bottlenecks'::TEXT,
        'High'::VARCHAR(20),
        COUNT(DISTINCT order_id)::INTEGER,
        SUM(waiting_time_before)::INTEGER
    FROM original_wms_plans 
    WHERE waiting_time_before > 10;
END;
$$ LANGUAGE plpgsql;

-- Initial refresh of the materialized view
SELECT refresh_original_plans();

-- Success message
SELECT 'Enhanced original WMS plan generator created successfully!' as status; 