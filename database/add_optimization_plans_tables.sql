-- Add Optimization Plans Tables to Existing Database
-- Run this script to add the new tables for storing optimization plans

-- Optimization Plans Table
-- Stores detailed optimized plans for easy access from frontend
CREATE TABLE IF NOT EXISTS optimization_plans (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL,
    stage VARCHAR(20) NOT NULL, -- 'PICK', 'CONSOLIDATE', 'PACK', 'LABEL', 'STAGE', 'SHIP'
    worker_id INTEGER REFERENCES workers(id),
    equipment_id INTEGER REFERENCES equipment(id),
    start_time_minutes INTEGER NOT NULL, -- Minutes from start of shift
    duration_minutes INTEGER NOT NULL,
    waiting_time_before INTEGER DEFAULT 0, -- Minutes of waiting before this stage
    sequence_order INTEGER NOT NULL, -- Order within the stage
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_optimization_plans_run_id ON optimization_plans(optimization_run_id);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_order_id ON optimization_plans(order_id);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_stage ON optimization_plans(stage);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_worker_id ON optimization_plans(worker_id);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_equipment_id ON optimization_plans(equipment_id);

-- Table to store plan metadata and summary metrics
CREATE TABLE IF NOT EXISTS optimization_plan_summaries (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id) ON DELETE CASCADE,
    total_orders INTEGER NOT NULL,
    total_processing_time_original INTEGER NOT NULL, -- Minutes
    total_processing_time_optimized INTEGER NOT NULL, -- Minutes
    total_waiting_time_original INTEGER NOT NULL, -- Minutes
    total_waiting_time_optimized INTEGER NOT NULL, -- Minutes
    time_savings INTEGER NOT NULL, -- Minutes saved
    waiting_time_reduction INTEGER NOT NULL, -- Minutes of waiting time reduced
    worker_utilization_improvement DECIMAL(5,2), -- Percentage improvement
    equipment_utilization_improvement DECIMAL(5,2), -- Percentage improvement
    on_time_percentage_original DECIMAL(5,2), -- Percentage of orders on time
    on_time_percentage_optimized DECIMAL(5,2), -- Percentage of orders on time
    total_cost_original DECIMAL(10,2), -- Total cost in dollars
    total_cost_optimized DECIMAL(10,2), -- Total cost in dollars
    cost_savings DECIMAL(10,2), -- Cost savings in dollars
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_optimization_plan_summaries_run_id ON optimization_plan_summaries(optimization_run_id);

-- Table to store individual order timeline data for frontend display
CREATE TABLE IF NOT EXISTS order_timelines (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL,
    customer_name VARCHAR(100),
    priority INTEGER,
    shipping_deadline TIMESTAMPTZ,
    -- Original plan data (JSON for flexibility)
    original_timeline JSONB, -- Array of stage objects with timing and worker info
    optimized_timeline JSONB, -- Array of stage objects with timing and worker info
    -- Summary metrics
    total_processing_time_original INTEGER NOT NULL,
    total_processing_time_optimized INTEGER NOT NULL,
    total_waiting_time_original INTEGER NOT NULL,
    total_waiting_time_optimized INTEGER NOT NULL,
    time_savings INTEGER NOT NULL,
    waiting_time_reduction INTEGER NOT NULL,
    on_time_original BOOLEAN,
    on_time_optimized BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_order_timelines_run_id ON order_timelines(optimization_run_id);
CREATE INDEX IF NOT EXISTS idx_order_timelines_order_id ON order_timelines(order_id);
CREATE INDEX IF NOT EXISTS idx_order_timelines_customer ON order_timelines(customer_name);

-- Comments for documentation
COMMENT ON TABLE optimization_plans IS 'Detailed stage-by-stage optimization plans for each order';
COMMENT ON TABLE optimization_plan_summaries IS 'Summary metrics and improvements for optimization runs';
COMMENT ON TABLE order_timelines IS 'Individual order timeline data for frontend comparison display';

-- Success message
SELECT 'Optimization plans tables created successfully!' as status; 