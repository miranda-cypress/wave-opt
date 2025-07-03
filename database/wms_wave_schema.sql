-- WMS Wave Optimization Database Schema
-- Realistic warehouse management system with wave planning capabilities

-- Drop existing tables if they exist
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS wave_assignments CASCADE;
DROP TABLE IF EXISTS waves CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS worker_skills CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS skus CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS optimization_plans CASCADE;
DROP TABLE IF EXISTS optimization_runs CASCADE;

-- Warehouse configuration
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    timezone VARCHAR(50) DEFAULT 'UTC',
    operating_hours JSONB, -- {"start": "08:00", "end": "18:00", "days": ["mon", "tue", "wed", "thu", "fri"]}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(10) DEFAULT 'b2b', -- 'b2b', 'b2c'
    priority_level INTEGER DEFAULT 3 CHECK (priority_level BETWEEN 1 AND 5),
    service_level VARCHAR(20) DEFAULT 'standard', -- 'standard', 'premium', 'rush'
    shipping_address JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SKUs (Stock Keeping Units)
CREATE TABLE skus (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    sku_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    zone VARCHAR(20) NOT NULL, -- 'A', 'B', 'C', 'D', 'E'
    pick_time_minutes DECIMAL(5,2) DEFAULT 2.0,
    pack_time_minutes DECIMAL(5,2) DEFAULT 1.5,
    volume_cubic_feet DECIMAL(8,3),
    weight_lbs DECIMAL(8,2),
    demand_pattern VARCHAR(20) DEFAULT 'stable', -- 'stable', 'seasonal', 'trending'
    velocity_class CHAR(1) DEFAULT 'B', -- 'A', 'B', 'C' (fast, medium, slow movers)
    shelf_life_days INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workers
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    worker_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    hourly_rate DECIMAL(6,2) NOT NULL,
    efficiency_factor DECIMAL(3,2) DEFAULT 1.0, -- 0.5 to 1.5
    max_hours_per_day DECIMAL(4,2) DEFAULT 8.0,
    reliability_score DECIMAL(3,2) DEFAULT 0.95, -- 0.0 to 1.0
    shift VARCHAR(20) DEFAULT 'first', -- 'first', 'second', 'third'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Worker skills (many-to-many relationship)
CREATE TABLE worker_skills (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES workers(id) ON DELETE CASCADE,
    skill VARCHAR(50) NOT NULL, -- 'picking', 'packing', 'shipping', 'receiving', 'inventory'
    proficiency_level INTEGER DEFAULT 3 CHECK (proficiency_level BETWEEN 1 AND 5),
    certified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(worker_id, skill)
);

-- Equipment
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    equipment_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL, -- 'packing_station', 'dock_door', 'forklift', 'scanner', 'conveyor'
    capacity INTEGER DEFAULT 1, -- simultaneous operations
    hourly_cost DECIMAL(8,2) DEFAULT 0.0,
    efficiency_factor DECIMAL(3,2) DEFAULT 1.0,
    maintenance_frequency INTEGER DEFAULT 30, -- days between maintenance
    current_utilization DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    order_number VARCHAR(30) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMPTZ NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(10) DEFAULT 'b2b',
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    shipping_deadline TIMESTAMPTZ NOT NULL,
    total_pick_time DECIMAL(8,2) DEFAULT 0.0,
    total_pack_time DECIMAL(8,2) DEFAULT 0.0,
    total_volume DECIMAL(10,3) DEFAULT 0.0,
    total_weight DECIMAL(10,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'assigned', 'in_progress', 'completed', 'shipped'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Order items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    sku_id INTEGER REFERENCES skus(id),
    quantity INTEGER NOT NULL,
    pick_time DECIMAL(8,2) DEFAULT 0.0,
    pack_time DECIMAL(8,2) DEFAULT 0.0,
    volume DECIMAL(8,3) DEFAULT 0.0,
    weight DECIMAL(8,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Waves (wave planning)
CREATE TABLE waves (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    wave_name VARCHAR(50) NOT NULL,
    wave_type VARCHAR(20) DEFAULT 'manual', -- 'manual', 'ai_optimized', 'priority_based'
    planned_start_time TIMESTAMPTZ,
    actual_start_time TIMESTAMPTZ,
    planned_completion_time TIMESTAMPTZ,
    actual_completion_time TIMESTAMPTZ,
    total_orders INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    assigned_workers TEXT[], -- Array of worker codes
    efficiency_score DECIMAL(5,2), -- 0-100
    travel_time_minutes INTEGER DEFAULT 0,
    labor_cost DECIMAL(10,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'cancelled'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wave assignments (orders assigned to waves)
CREATE TABLE wave_assignments (
    id SERIAL PRIMARY KEY,
    wave_id INTEGER REFERENCES waves(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL, -- 'pick', 'consolidate', 'pack', 'label', 'stage', 'ship'
    assigned_worker_id INTEGER REFERENCES workers(id),
    assigned_equipment_id INTEGER REFERENCES equipment(id),
    planned_start_time TIMESTAMPTZ,
    planned_duration_minutes INTEGER,
    actual_start_time TIMESTAMPTZ,
    actual_duration_minutes INTEGER,
    sequence_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    wave_id INTEGER REFERENCES waves(id) ON DELETE CASCADE,
    metric_type VARCHAR(30) NOT NULL, -- 'efficiency', 'travel_time', 'labor_cost', 'on_time_delivery'
    metric_value DECIMAL(10,2) NOT NULL,
    measurement_time TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optimization runs
CREATE TABLE optimization_runs (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    scenario_type VARCHAR(50) NOT NULL, -- 'wave_optimization', 'cross_wave', 'bottleneck', 'deadline'
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    total_orders INTEGER NOT NULL,
    total_workers INTEGER NOT NULL,
    total_equipment INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    objective_value DECIMAL(12,2), -- Cost savings or efficiency improvement
    solver_status VARCHAR(20), -- 'optimal', 'feasible', 'infeasible'
    solve_time_seconds DECIMAL(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optimization plans (detailed results)
CREATE TABLE optimization_plans (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES optimization_runs(id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL, -- 'wave_optimization', 'cross_wave', 'worker_assignment'
    optimization_result JSONB NOT NULL, -- Detailed optimization results
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_orders_warehouse_status ON orders(warehouse_id, status);
CREATE INDEX idx_orders_deadline ON orders(shipping_deadline);
CREATE INDEX idx_orders_priority ON orders(priority);
CREATE INDEX idx_skus_warehouse_zone ON skus(warehouse_id, zone);
CREATE INDEX idx_skus_velocity ON skus(velocity_class);
CREATE INDEX idx_workers_warehouse_active ON workers(warehouse_id, active);
CREATE INDEX idx_worker_skills_worker ON worker_skills(worker_id);
CREATE INDEX idx_equipment_warehouse_type ON equipment(warehouse_id, equipment_type);
CREATE INDEX idx_wave_assignments_wave_stage ON wave_assignments(wave_id, stage);
CREATE INDEX idx_wave_assignments_worker ON wave_assignments(assigned_worker_id);
CREATE INDEX idx_wave_assignments_equipment ON wave_assignments(assigned_equipment_id);
CREATE INDEX idx_performance_metrics_wave_type ON performance_metrics(wave_id, metric_type);
CREATE INDEX idx_optimization_runs_warehouse_scenario ON optimization_runs(warehouse_id, scenario_type);
CREATE INDEX idx_optimization_plans_run_type ON optimization_plans(run_id, plan_type);

-- Insert default warehouse
INSERT INTO warehouses (id, name, location, timezone, operating_hours) VALUES 
(1, 'MidWest Distribution Center', 'Chicago, IL', 'America/Chicago', 
 '{"start": "08:00", "end": "18:00", "days": ["mon", "tue", "wed", "thu", "fri"]}');

-- Insert sample customers
INSERT INTO customers (warehouse_id, customer_code, name, customer_type, priority_level, service_level) VALUES
(1, 'CUST001', 'Acme Corporation', 'b2b', 1, 'premium'),
(1, 'CUST002', 'Global Retail Chain', 'b2b', 2, 'premium'),
(1, 'CUST003', 'Local Store Network', 'b2b', 3, 'standard'),
(1, 'CUST004', 'Online Marketplace', 'b2c', 4, 'standard'),
(1, 'CUST005', 'Direct Consumer', 'b2c', 5, 'standard');

-- Insert sample SKUs
INSERT INTO skus (warehouse_id, sku_code, name, category, zone, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs, velocity_class) VALUES
(1, 'SKU001', 'Premium Widget A', 'Electronics', 'A', 1.5, 1.0, 0.5, 2.0, 'A'),
(1, 'SKU002', 'Standard Widget B', 'Electronics', 'A', 2.0, 1.5, 1.0, 3.5, 'A'),
(1, 'SKU003', 'Heavy Component C', 'Industrial', 'B', 3.0, 2.0, 2.5, 15.0, 'B'),
(1, 'SKU004', 'Light Accessory D', 'Accessories', 'A', 1.0, 0.5, 0.1, 0.5, 'A'),
(1, 'SKU005', 'Bulk Item E', 'Bulk', 'C', 5.0, 3.0, 5.0, 25.0, 'C'),
(1, 'SKU006', 'Fragile Item F', 'Fragile', 'A', 2.5, 2.5, 0.3, 1.0, 'B'),
(1, 'SKU007', 'Fast Moving G', 'Fast Moving', 'A', 1.0, 0.8, 0.2, 0.8, 'A'),
(1, 'SKU008', 'Slow Moving H', 'Slow Moving', 'C', 4.0, 2.0, 3.0, 12.0, 'C'),
(1, 'SKU009', 'Medium Item I', 'Medium', 'B', 2.5, 1.5, 1.5, 5.0, 'B'),
(1, 'SKU010', 'Large Item J', 'Large', 'C', 6.0, 4.0, 8.0, 40.0, 'C');

-- Insert sample workers
INSERT INTO workers (warehouse_id, worker_code, name, hourly_rate, efficiency_factor, max_hours_per_day, reliability_score, shift) VALUES
(1, 'W001', 'John Smith', 18.50, 1.1, 8.0, 0.98, 'first'),
(1, 'W002', 'Sarah Johnson', 17.75, 1.05, 8.0, 0.95, 'first'),
(1, 'W003', 'Mike Davis', 19.00, 1.15, 8.0, 0.99, 'first'),
(1, 'W004', 'Lisa Wilson', 16.50, 0.95, 8.0, 0.92, 'first'),
(1, 'W005', 'Tom Brown', 18.00, 1.0, 8.0, 0.96, 'first'),
(1, 'W006', 'Amy Garcia', 17.25, 1.08, 8.0, 0.94, 'second'),
(1, 'W007', 'Chris Martinez', 18.75, 1.12, 8.0, 0.97, 'second'),
(1, 'W008', 'Jennifer Lee', 16.75, 0.98, 8.0, 0.93, 'second');

-- Insert worker skills
INSERT INTO worker_skills (worker_id, skill, proficiency_level) VALUES
(1, 'picking', 5), (1, 'packing', 4), (1, 'shipping', 3),
(2, 'picking', 4), (2, 'packing', 5), (2, 'receiving', 3),
(3, 'picking', 5), (3, 'packing', 4), (3, 'inventory', 4),
(4, 'picking', 3), (4, 'packing', 4), (4, 'shipping', 4),
(5, 'picking', 4), (5, 'packing', 3), (5, 'receiving', 5),
(6, 'picking', 4), (6, 'packing', 4), (6, 'shipping', 4),
(7, 'picking', 5), (7, 'packing', 5), (7, 'inventory', 3),
(8, 'picking', 3), (8, 'packing', 4), (8, 'receiving', 4);

-- Insert equipment
INSERT INTO equipment (warehouse_id, equipment_code, name, equipment_type, capacity, hourly_cost, efficiency_factor) VALUES
(1, 'EQ001', 'Packing Station 1', 'packing_station', 1, 5.00, 1.0),
(1, 'EQ002', 'Packing Station 2', 'packing_station', 1, 5.00, 1.0),
(1, 'EQ003', 'Packing Station 3', 'packing_station', 1, 5.00, 1.0),
(1, 'EQ004', 'Dock Door 1', 'dock_door', 1, 2.00, 1.0),
(1, 'EQ005', 'Dock Door 2', 'dock_door', 1, 2.00, 1.0),
(1, 'EQ006', 'Forklift 1', 'forklift', 1, 8.00, 1.0),
(1, 'EQ007', 'Forklift 2', 'forklift', 1, 8.00, 1.0),
(1, 'EQ008', 'Scanner 1', 'scanner', 1, 1.00, 1.0),
(1, 'EQ009', 'Scanner 2', 'scanner', 1, 1.00, 1.0),
(1, 'EQ010', 'Conveyor Line 1', 'conveyor', 5, 3.00, 1.0);

-- Insert sample orders
INSERT INTO orders (warehouse_id, order_number, customer_id, order_date, customer_name, customer_type, priority, shipping_deadline, total_pick_time, total_pack_time, total_volume, total_weight, status) VALUES
(1, 'ORD001', 1, '2024-01-15 08:00:00', 'Acme Corporation', 'b2b', 1, '2024-01-15 17:00:00', 45.0, 30.0, 15.5, 45.0, 'pending'),
(1, 'ORD002', 2, '2024-01-15 08:15:00', 'Global Retail Chain', 'b2b', 2, '2024-01-15 18:00:00', 60.0, 40.0, 25.0, 75.0, 'pending'),
(1, 'ORD003', 3, '2024-01-15 08:30:00', 'Local Store Network', 'b2b', 3, '2024-01-16 12:00:00', 30.0, 20.0, 8.0, 25.0, 'pending'),
(1, 'ORD004', 4, '2024-01-15 08:45:00', 'Online Marketplace', 'b2c', 4, '2024-01-16 17:00:00', 20.0, 15.0, 5.0, 12.0, 'pending'),
(1, 'ORD005', 5, '2024-01-15 09:00:00', 'Direct Consumer', 'b2c', 5, '2024-01-17 12:00:00', 15.0, 10.0, 3.0, 8.0, 'pending'),
(1, 'ORD006', 1, '2024-01-15 09:15:00', 'Acme Corporation', 'b2b', 1, '2024-01-15 16:00:00', 35.0, 25.0, 12.0, 35.0, 'pending'),
(1, 'ORD007', 2, '2024-01-15 09:30:00', 'Global Retail Chain', 'b2b', 2, '2024-01-15 19:00:00', 50.0, 35.0, 20.0, 60.0, 'pending'),
(1, 'ORD008', 3, '2024-01-15 09:45:00', 'Local Store Network', 'b2b', 3, '2024-01-16 14:00:00', 25.0, 18.0, 7.0, 22.0, 'pending'),
(1, 'ORD009', 4, '2024-01-15 10:00:00', 'Online Marketplace', 'b2c', 4, '2024-01-16 18:00:00', 18.0, 12.0, 4.5, 10.0, 'pending'),
(1, 'ORD010', 5, '2024-01-15 10:15:00', 'Direct Consumer', 'b2c', 5, '2024-01-17 14:00:00', 12.0, 8.0, 2.5, 6.0, 'pending');

-- Insert order items
INSERT INTO order_items (order_id, sku_id, quantity, pick_time, pack_time, volume, weight) VALUES
(1, 1, 5, 7.5, 5.0, 2.5, 10.0),
(1, 2, 3, 6.0, 4.5, 3.0, 10.5),
(1, 4, 10, 10.0, 5.0, 1.0, 5.0),
(2, 3, 2, 6.0, 4.0, 5.0, 30.0),
(2, 5, 1, 5.0, 3.0, 5.0, 25.0),
(2, 7, 8, 8.0, 6.4, 1.6, 6.4),
(3, 1, 2, 3.0, 2.0, 1.0, 4.0),
(3, 6, 1, 2.5, 2.5, 0.3, 1.0),
(3, 9, 3, 7.5, 4.5, 4.5, 15.0),
(4, 4, 5, 5.0, 2.5, 0.5, 2.5),
(4, 7, 3, 3.0, 2.4, 0.6, 2.4),
(5, 2, 1, 2.0, 1.5, 1.0, 3.5),
(5, 8, 1, 4.0, 2.0, 3.0, 12.0),
(6, 1, 3, 4.5, 3.0, 1.5, 6.0),
(6, 3, 1, 3.0, 2.0, 2.5, 15.0),
(6, 10, 1, 6.0, 4.0, 8.0, 40.0),
(7, 2, 4, 8.0, 6.0, 4.0, 14.0),
(7, 5, 2, 10.0, 6.0, 10.0, 50.0),
(8, 4, 3, 3.0, 1.5, 0.3, 1.5),
(8, 9, 2, 5.0, 3.0, 3.0, 10.0),
(9, 1, 1, 1.5, 1.0, 0.5, 2.0),
(9, 6, 2, 5.0, 5.0, 0.6, 2.0),
(10, 2, 1, 2.0, 1.5, 1.0, 3.5),
(10, 7, 2, 2.0, 1.6, 0.4, 1.6);

-- Insert sample waves
INSERT INTO waves (warehouse_id, wave_name, wave_type, planned_start_time, planned_completion_time, total_orders, total_items, assigned_workers, efficiency_score, labor_cost, status) VALUES
(1, 'Morning Wave 1', 'manual', '2024-01-15 08:00:00', '2024-01-15 10:00:00', 3, 15, ARRAY['W001', 'W002', 'W003'], 75.0, 285.0, 'planned'),
(1, 'Morning Wave 2', 'manual', '2024-01-15 10:00:00', '2024-01-15 12:00:00', 3, 12, ARRAY['W001', 'W002', 'W004'], 72.0, 270.0, 'planned'),
(1, 'Afternoon Wave 1', 'manual', '2024-01-15 13:00:00', '2024-01-15 15:00:00', 2, 8, ARRAY['W005', 'W006'], 78.0, 180.0, 'planned'),
(1, 'Afternoon Wave 2', 'manual', '2024-01-15 15:00:00', '2024-01-15 17:00:00', 2, 6, ARRAY['W007', 'W008'], 70.0, 160.0, 'planned');

-- Insert wave assignments
INSERT INTO wave_assignments (wave_id, order_id, stage, assigned_worker_id, assigned_equipment_id, planned_start_time, planned_duration_minutes, sequence_order) VALUES
(1, 1, 'pick', 1, 8, '2024-01-15 08:00:00', 45, 1),
(1, 1, 'pack', 2, 1, '2024-01-15 08:45:00', 30, 2),
(1, 2, 'pick', 3, 9, '2024-01-15 08:15:00', 60, 3),
(1, 2, 'pack', 1, 2, '2024-01-15 09:15:00', 40, 4),
(1, 6, 'pick', 2, 8, '2024-01-15 09:15:00', 35, 5),
(1, 6, 'pack', 3, 3, '2024-01-15 09:50:00', 25, 6),
(2, 3, 'pick', 1, 9, '2024-01-15 10:00:00', 30, 1),
(2, 3, 'pack', 2, 1, '2024-01-15 10:30:00', 20, 2),
(2, 7, 'pick', 4, 8, '2024-01-15 10:15:00', 50, 3),
(2, 7, 'pack', 1, 2, '2024-01-15 11:05:00', 35, 4),
(2, 8, 'pick', 2, 9, '2024-01-15 10:30:00', 25, 5),
(2, 8, 'pack', 4, 3, '2024-01-15 10:55:00', 18, 6),
(3, 4, 'pick', 5, 8, '2024-01-15 13:00:00', 20, 1),
(3, 4, 'pack', 6, 1, '2024-01-15 13:20:00', 15, 2),
(3, 9, 'pick', 5, 9, '2024-01-15 13:15:00', 18, 3),
(3, 9, 'pack', 6, 2, '2024-01-15 13:33:00', 12, 4),
(4, 5, 'pick', 7, 8, '2024-01-15 15:00:00', 15, 1),
(4, 5, 'pack', 8, 1, '2024-01-15 15:15:00', 10, 2),
(4, 10, 'pick', 7, 9, '2024-01-15 15:10:00', 12, 3),
(4, 10, 'pack', 8, 2, '2024-01-15 15:22:00', 8, 4); 