-- Create bin_types table and link to bins
-- This script adds the bin_types table and updates the bins table to reference it

-- Create bin_types table
CREATE TABLE IF NOT EXISTS bin_types (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(50) NOT NULL,
    description TEXT,
    default_capacity_cubic_feet DECIMAL(8,3),
    default_max_weight_lbs DECIMAL(8,2),
    access_type VARCHAR(20) DEFAULT 'manual', -- 'manual', 'automated', 'forklift', 'conveyor'
    height_restriction BOOLEAN DEFAULT FALSE,
    max_height_feet DECIMAL(5,2),
    requires_equipment BOOLEAN DEFAULT FALSE,
    equipment_type VARCHAR(50), -- 'forklift', 'scissor_lift', 'conveyor', 'robot'
    pick_efficiency_factor DECIMAL(3,2) DEFAULT 1.0, -- 0.5 to 2.0 (slower to faster than standard)
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default bin types
INSERT INTO bin_types (type_code, type_name, description, default_capacity_cubic_feet, default_max_weight_lbs, access_type, height_restriction, max_height_feet, requires_equipment, equipment_type, pick_efficiency_factor) VALUES
('SHELF', 'Shelf Storage', 'Standard shelf storage for small to medium items', 50.0, 100.0, 'manual', FALSE, NULL, FALSE, NULL, 1.0),
('PALLET', 'Pallet Storage', 'Ground-level pallet storage for bulk items', 200.0, 500.0, 'forklift', FALSE, NULL, TRUE, 'forklift', 0.8),
('RACK', 'Rack Storage', 'Multi-level rack storage for medium items', 150.0, 300.0, 'forklift', TRUE, 12.0, TRUE, 'forklift', 0.9),
('FLOOR', 'Floor Storage', 'Large floor space for oversized items', 500.0, 1000.0, 'forklift', FALSE, NULL, TRUE, 'forklift', 0.7),
('MEZZANINE', 'Mezzanine Storage', 'Elevated storage area', 300.0, 600.0, 'manual', TRUE, 15.0, FALSE, NULL, 0.6),
('CONVEYOR', 'Conveyor System', 'Automated conveyor storage', 100.0, 200.0, 'automated', FALSE, NULL, TRUE, 'conveyor', 1.5),
('COLD_STORAGE', 'Cold Storage', 'Refrigerated storage area', 75.0, 150.0, 'manual', FALSE, NULL, FALSE, NULL, 0.9),
('HAZMAT', 'Hazardous Materials', 'Specialized storage for hazardous materials', 25.0, 50.0, 'manual', TRUE, 8.0, FALSE, NULL, 0.5),
('BULK', 'Bulk Storage', 'Large volume storage for bulk materials', 1000.0, 2000.0, 'forklift', FALSE, NULL, TRUE, 'forklift', 0.6),
('PICK_MODULE', 'Pick Module', 'High-density picking area', 30.0, 75.0, 'manual', TRUE, 10.0, FALSE, NULL, 1.2)
ON CONFLICT (type_code) DO NOTHING;

-- Add bin_type_id column to bins table
ALTER TABLE bins ADD COLUMN IF NOT EXISTS bin_type_id INTEGER REFERENCES bin_types(id);

-- Update existing bins to reference bin_types
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'SHELF') WHERE bin_type = 'shelf';
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'PALLET') WHERE bin_type = 'pallet';
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'RACK') WHERE bin_type = 'rack';
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'FLOOR') WHERE bin_type = 'floor';
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'MEZZANINE') WHERE bin_type = 'mezzanine';
UPDATE bins SET bin_type_id = (SELECT id FROM bin_types WHERE type_code = 'CONVEYOR') WHERE bin_type = 'conveyor';

-- Make bin_type_id NOT NULL after updating all records
ALTER TABLE bins ALTER COLUMN bin_type_id SET NOT NULL;

-- Create index for the foreign key
CREATE INDEX IF NOT EXISTS idx_bins_bin_type_id ON bins(bin_type_id);

-- Create index for bin_types
CREATE INDEX IF NOT EXISTS idx_bin_types_active ON bin_types(active);
CREATE INDEX IF NOT EXISTS idx_bin_types_access_type ON bin_types(access_type); 