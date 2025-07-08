-- Add bins table to existing database
-- This script adds the bins table without dropping existing data

-- Create bins table
CREATE TABLE IF NOT EXISTS bins (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    bin_id VARCHAR(20) UNIQUE NOT NULL,
    bin_type VARCHAR(50) NOT NULL, -- 'shelf', 'pallet', 'rack', 'floor', 'mezzanine', 'conveyor'
    x_coordinate DECIMAL(8,2) NOT NULL,
    y_coordinate DECIMAL(8,2) NOT NULL,
    z_coordinate DECIMAL(8,2) NOT NULL,
    zone VARCHAR(20), -- 'A', 'B', 'C', 'D', 'E'
    aisle VARCHAR(20), -- Aisle identifier
    level INTEGER, -- Shelf level or floor level
    capacity_cubic_feet DECIMAL(8,3),
    max_weight_lbs DECIMAL(8,2),
    current_utilization DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    active BOOLEAN DEFAULT TRUE,
    external_bin_id VARCHAR(50), -- ID in external WMS system
    source_id INTEGER REFERENCES data_sources(id),
    import_id INTEGER REFERENCES data_imports(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for bins table
CREATE INDEX IF NOT EXISTS idx_bins_warehouse_type ON bins(warehouse_id, bin_type);
CREATE INDEX IF NOT EXISTS idx_bins_coordinates ON bins(x_coordinate, y_coordinate, z_coordinate);
CREATE INDEX IF NOT EXISTS idx_bins_zone_aisle ON bins(zone, aisle);
CREATE INDEX IF NOT EXISTS idx_bins_external_id ON bins(external_bin_id);

-- Insert sample bins data
INSERT INTO bins (warehouse_id, bin_id, bin_type, x_coordinate, y_coordinate, z_coordinate, zone, aisle, level, capacity_cubic_feet, max_weight_lbs, current_utilization, external_bin_id, source_id) VALUES
(1, 'BIN001', 'shelf', 10.0, 20.0, 5.0, 'A', 'A1', 1, 50.0, 100.0, 0.3, 'EXT_BIN_001', 1),
(1, 'BIN002', 'shelf', 10.0, 20.0, 6.0, 'A', 'A1', 2, 50.0, 100.0, 0.4, 'EXT_BIN_002', 1),
(1, 'BIN003', 'shelf', 10.0, 20.0, 7.0, 'A', 'A1', 3, 50.0, 100.0, 0.2, 'EXT_BIN_003', 1),
(1, 'BIN004', 'shelf', 15.0, 20.0, 5.0, 'A', 'A2', 1, 50.0, 100.0, 0.5, 'EXT_BIN_004', 1),
(1, 'BIN005', 'shelf', 15.0, 20.0, 6.0, 'A', 'A2', 2, 50.0, 100.0, 0.6, 'EXT_BIN_005', 1),
(1, 'BIN006', 'pallet', 25.0, 30.0, 0.0, 'B', 'B1', 1, 200.0, 500.0, 0.7, 'EXT_BIN_006', 1),
(1, 'BIN007', 'pallet', 30.0, 30.0, 0.0, 'B', 'B1', 1, 200.0, 500.0, 0.8, 'EXT_BIN_007', 1),
(1, 'BIN008', 'rack', 40.0, 40.0, 5.0, 'B', 'B2', 1, 150.0, 300.0, 0.4, 'EXT_BIN_008', 1),
(1, 'BIN009', 'rack', 40.0, 40.0, 6.0, 'B', 'B2', 2, 150.0, 300.0, 0.3, 'EXT_BIN_009', 1),
(1, 'BIN010', 'floor', 50.0, 50.0, 0.0, 'C', 'C1', 1, 500.0, 1000.0, 0.9, 'EXT_BIN_010', 1),
(1, 'BIN011', 'mezzanine', 60.0, 60.0, 10.0, 'C', 'C2', 1, 300.0, 600.0, 0.2, 'EXT_BIN_011', 1),
(1, 'BIN012', 'conveyor', 70.0, 70.0, 3.0, 'A', 'A3', 1, 100.0, 200.0, 0.1, 'EXT_BIN_012', 1)
ON CONFLICT (bin_id) DO NOTHING; 