-- Create tables for storing optimization results

-- Table to store optimization run metadata
CREATE TABLE IF NOT EXISTS optimization_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) UNIQUE,
    scenario_type VARCHAR(50),
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    total_orders INTEGER,
    total_workers INTEGER,
    total_equipment INTEGER,
    objective_value DECIMAL(15,2),
    solver_status VARCHAR(50),
    solve_time_seconds DECIMAL(10,3)
);

-- Table to store optimization plan summaries
CREATE TABLE IF NOT EXISTS optimization_plan_summaries (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id),
    total_orders INTEGER,
    total_processing_time_original INTEGER,
    total_processing_time_optimized INTEGER,
    total_waiting_time_original INTEGER,
    total_waiting_time_optimized INTEGER,
    time_savings INTEGER,
    waiting_time_reduction INTEGER,
    worker_utilization_improvement DECIMAL(5,2),
    equipment_utilization_improvement DECIMAL(5,2),
    on_time_percentage_original DECIMAL(5,2),
    on_time_percentage_optimized DECIMAL(5,2),
    total_cost_original DECIMAL(15,2),
    total_cost_optimized DECIMAL(15,2),
    cost_savings DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table to store detailed optimization plans
CREATE TABLE IF NOT EXISTS optimization_plans (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id),
    order_id INTEGER,
    stage VARCHAR(20),
    worker_id INTEGER,
    equipment_id INTEGER,
    start_time_minutes INTEGER,
    duration_minutes INTEGER,
    waiting_time_before INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table to store order timelines for comparison
CREATE TABLE IF NOT EXISTS order_timelines (
    id SERIAL PRIMARY KEY,
    optimization_run_id INTEGER REFERENCES optimization_runs(id),
    order_id INTEGER,
    customer_name VARCHAR(255),
    priority VARCHAR(10),
    shipping_deadline TIMESTAMP,
    original_timeline JSONB,
    optimized_timeline JSONB,
    total_processing_time_original INTEGER,
    total_processing_time_optimized INTEGER,
    total_waiting_time_original INTEGER,
    total_waiting_time_optimized INTEGER,
    time_savings INTEGER,
    waiting_time_reduction INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_optimization_runs_scenario ON optimization_runs(scenario_type);
CREATE INDEX IF NOT EXISTS idx_optimization_runs_status ON optimization_runs(status);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_run_id ON optimization_plans(optimization_run_id);
CREATE INDEX IF NOT EXISTS idx_optimization_plans_order_id ON optimization_plans(order_id);
CREATE INDEX IF NOT EXISTS idx_order_timelines_run_id ON order_timelines(optimization_run_id);
CREATE INDEX IF NOT EXISTS idx_order_timelines_order_id ON order_timelines(order_id);

-- Success message
SELECT 'Optimization tables created successfully!' as status; 