-- Create walking_times table to store precomputed walking times between bins
CREATE TABLE IF NOT EXISTS walking_times (
    id SERIAL PRIMARY KEY,
    from_bin_id INTEGER REFERENCES bins(id) ON DELETE CASCADE,
    to_bin_id INTEGER REFERENCES bins(id) ON DELETE CASCADE,
    distance_feet DECIMAL(8,2) NOT NULL,
    walking_time_minutes DECIMAL(6,2) NOT NULL,
    path_type VARCHAR(20) DEFAULT 'weighted_manhattan', -- 'euclidean', 'manhattan', 'weighted_manhattan', 'graph'
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(from_bin_id, to_bin_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_walking_times_from_bin ON walking_times(from_bin_id);
CREATE INDEX IF NOT EXISTS idx_walking_times_to_bin ON walking_times(to_bin_id);
CREATE INDEX IF NOT EXISTS idx_walking_times_computed_at ON walking_times(computed_at);

-- Create a view for easy querying of walking times
CREATE OR REPLACE VIEW walking_times_matrix AS
SELECT 
    wt.from_bin_id,
    wt.to_bin_id,
    b1.bin_id as from_bin_code,
    b2.bin_id as to_bin_code,
    b1.zone as from_zone,
    b2.zone as to_zone,
    wt.distance_feet,
    wt.walking_time_minutes,
    wt.path_type,
    wt.computed_at
FROM walking_times wt
JOIN bins b1 ON wt.from_bin_id = b1.id
JOIN bins b2 ON wt.to_bin_id = b2.id
ORDER BY b1.bin_id, b2.bin_id; 