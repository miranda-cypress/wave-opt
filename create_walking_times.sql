-- Create walking_times table
CREATE TABLE IF NOT EXISTS walking_times (
    id SERIAL PRIMARY KEY,
    from_bin_id INTEGER NOT NULL,
    to_bin_id INTEGER NOT NULL,
    distance_feet DECIMAL(8,2) NOT NULL,
    walking_time_minutes DECIMAL(6,2) NOT NULL,
    path_type VARCHAR(50) DEFAULT 'weighted_manhattan',
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_walking_times_from_bin ON walking_times(from_bin_id);
CREATE INDEX IF NOT EXISTS idx_walking_times_to_bin ON walking_times(to_bin_id);
CREATE INDEX IF NOT EXISTS idx_walking_times_computed_at ON walking_times(computed_at);

-- Insert some sample walking times (using SKU IDs as bin IDs for now)
INSERT INTO walking_times (from_bin_id, to_bin_id, distance_feet, walking_time_minutes) VALUES
(1, 2, 50.0, 2.0),
(1, 3, 75.0, 3.0),
(1, 4, 100.0, 4.0),
(2, 3, 25.0, 1.0),
(2, 4, 50.0, 2.0),
(3, 4, 25.0, 1.0),
(5, 6, 30.0, 1.5),
(5, 7, 60.0, 3.0),
(6, 7, 30.0, 1.5)
ON CONFLICT DO NOTHING; 