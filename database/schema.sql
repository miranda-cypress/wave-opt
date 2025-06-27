-- AI Wave Optimization Demo - Complete Database Schema
-- MidWest Distribution Co. Warehouse Management System

-- Drop existing tables if they exist
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS wave_assignments CASCADE;
DROP TABLE IF EXISTS waves CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS zones CASCADE;
DROP TABLE IF EXISTS demo_scenarios CASCADE;

-- Warehouse layout and zones
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    zone_type VARCHAR(20) NOT NULL, -- 'receiving', 'picking', 'packing', 'shipping'
    x_coordinate INTEGER,
    y_coordinate INTEGER,
    size_sqft INTEGER,
    capacity_limit INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product catalog with AI-enrichable attributes
CREATE TABLE products (
    sku VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    velocity_class CHAR(1) NOT NULL, -- 'A', 'B', 'C' 
    weight_lbs DECIMAL(8,2),
    length_in DECIMAL(6,2),
    width_in DECIMAL(6,2),
    height_in DECIMAL(6,2),
    primary_zone_id INTEGER REFERENCES zones(id),
    pick_complexity INTEGER CHECK (pick_complexity BETWEEN 1 AND 5), -- 1-5 scale
    handling_requirements TEXT[], -- 'fragile', 'hazmat', 'refrigerated'
    unit_cost DECIMAL(10,2),
    avg_daily_demand DECIMAL(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Multi-skilled workers
CREATE TABLE workers (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    skills TEXT[] NOT NULL, -- 'picking', 'packing', 'receiving', 'shipping', 'inventory'
    experience_years INTEGER,
    hourly_rate DECIMAL(6,2) NOT NULL,
    pick_rate_items_per_hour INTEGER,
    pack_rate_orders_per_hour INTEGER,
    max_hours_per_day DECIMAL(4,2) DEFAULT 8.0,
    shift VARCHAR(20) DEFAULT 'first', -- 'first', 'second', 'third'
    is_cross_trained BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Equipment and capacity constraints
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL, -- 'packing_station', 'dock_door', 'forklift', 'scanner'
    zone_id INTEGER REFERENCES zones(id),
    capacity INTEGER DEFAULT 1, -- simultaneous operations
    hourly_cost DECIMAL(8,2) DEFAULT 0.0,
    required_skills TEXT[], -- skills needed to operate
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders with shipping deadlines
CREATE TABLE orders (
    id VARCHAR(30) PRIMARY KEY,
    order_date TIMESTAMPTZ NOT NULL,
    customer_id VARCHAR(20),
    customer_type VARCHAR(10) DEFAULT 'b2b', -- 'b2b', 'b2c'
    order_type VARCHAR(20) DEFAULT 'standard', -- 'standard', 'rush', 'expedited'
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5), -- 1-5, higher = more urgent
    shipping_deadline TIMESTAMPTZ NOT NULL,
    total_items INTEGER DEFAULT 0,
    total_weight DECIMAL(10,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order line items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(30) REFERENCES orders(id) ON DELETE CASCADE,
    sku VARCHAR(20) REFERENCES products(sku),
    quantity INTEGER NOT NULL,
    line_priority INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wave planning and execution
CREATE TABLE waves (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    wave_type VARCHAR(20) DEFAULT 'manual', -- 'manual', 'ai_optimized'
    planned_start_time TIMESTAMPTZ,
    actual_start_time TIMESTAMPTZ,
    planned_completion_time TIMESTAMPTZ,
    actual_completion_time TIMESTAMPTZ,
    total_orders INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    assigned_workers TEXT[], -- worker IDs
    efficiency_score DECIMAL(5,2), -- 0-100
    travel_time_minutes INTEGER DEFAULT 0,
    labor_cost DECIMAL(10,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'planned',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wave assignments (orders to waves)
CREATE TABLE wave_assignments (
    id SERIAL PRIMARY KEY,
    wave_id INTEGER REFERENCES waves(id) ON DELETE CASCADE,
    order_id VARCHAR(30) REFERENCES orders(id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL, -- 'pick', 'consolidate', 'pack', 'label', 'stage', 'ship'
    assigned_worker_id VARCHAR(20) REFERENCES workers(id),
    assigned_equipment_id INTEGER REFERENCES equipment(id),
    planned_start_time TIMESTAMPTZ,
    planned_duration_minutes INTEGER,
    actual_start_time TIMESTAMPTZ,
    actual_duration_minutes INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics and KPIs
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    wave_id INTEGER REFERENCES waves(id) ON DELETE CASCADE,
    metric_type VARCHAR(30) NOT NULL, -- 'efficiency', 'travel_time', 'labor_cost', 'on_time_delivery'
    metric_value DECIMAL(10,2) NOT NULL,
    measurement_time TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Demo scenarios for different presentations
CREATE TABLE demo_scenarios (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(50) NOT NULL,
    description TEXT,
    baseline_efficiency DECIMAL(5,2),
    optimized_efficiency DECIMAL(5,2),
    improvement_percentage DECIMAL(5,2),
    annual_savings_estimate DECIMAL(12,2),
    scenario_data JSONB, -- Flexible storage for scenario parameters
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_orders_deadline ON orders(shipping_deadline);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_priority ON orders(priority);
CREATE INDEX idx_products_velocity ON products(velocity_class);
CREATE INDEX idx_products_zone ON products(primary_zone_id);
CREATE INDEX idx_workers_skills ON workers USING GIN(skills);
CREATE INDEX idx_workers_active ON workers(active);
CREATE INDEX idx_equipment_zone ON equipment(zone_id);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_wave_assignments_wave_stage ON wave_assignments(wave_id, stage);
CREATE INDEX idx_wave_assignments_worker ON wave_assignments(assigned_worker_id);
CREATE INDEX idx_wave_assignments_equipment ON wave_assignments(assigned_equipment_id);
CREATE INDEX idx_performance_metrics_wave_type ON performance_metrics(wave_id, metric_type);
CREATE INDEX idx_performance_metrics_time ON performance_metrics(measurement_time);

-- Insert demo scenarios
INSERT INTO demo_scenarios (scenario_name, description, baseline_efficiency, optimized_efficiency, improvement_percentage, annual_savings_estimate, scenario_data) VALUES
('Baseline Inefficient', 'Manual wave planning with poor sequencing and bottlenecks', 72.0, 89.0, 17.0, 285000.00, '{"problems": ["manual_waves", "poor_sequencing", "bottlenecks"], "daily_labor_cost": 2850, "overtime_hours": 12, "on_time_delivery": 87}'),
('AI Optimized', 'AI-driven optimization with synchronized flow and skill optimization', 89.0, 95.0, 6.0, 150000.00, '{"improvements": ["synchronized_flow", "skill_optimization", "deadline_focus"], "daily_labor_cost": 2280, "overtime_hours": 2, "on_time_delivery": 99.2}'),
('Rush Order Handling', 'System adaptation to urgent orders without disrupting existing schedule', 85.0, 92.0, 7.0, 75000.00, '{"scenario": "rush_order", "rush_orders_per_day": 50, "impact_reduction": 60}'),
('Seasonal Surge', 'Peak season handling with 40% order volume increase', 68.0, 82.0, 14.0, 200000.00, '{"scenario": "seasonal_surge", "volume_increase": 40, "worker_scaling": 25}');

-- Insert warehouse zones
INSERT INTO zones (name, zone_type, x_coordinate, y_coordinate, size_sqft, capacity_limit) VALUES
('Receiving Dock', 'receiving', 0, 0, 5000, 4),
('Zone A - Fast Movers', 'picking', 100, 0, 15000, 8),
('Zone B - Medium Movers', 'picking', 200, 0, 12000, 6),
('Zone C - Slow Movers', 'picking', 300, 0, 8000, 4),
('Packing Area', 'packing', 100, 100, 10000, 6),
('Shipping Dock', 'shipping', 0, 100, 8000, 8); 