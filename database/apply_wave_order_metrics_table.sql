-- Migration: Create wave_order_metrics table for per-order, per-wave, per-plan metrics

CREATE TABLE IF NOT EXISTS wave_order_metrics (
    id SERIAL PRIMARY KEY,
    wave_id INTEGER REFERENCES waves(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    plan_version_id INTEGER REFERENCES wave_plan_versions(id),
    pick_time_minutes DECIMAL(8,2),
    pack_time_minutes DECIMAL(8,2),
    walking_time_minutes DECIMAL(8,2),
    consolidate_time_minutes DECIMAL(8,2),
    label_time_minutes DECIMAL(8,2),
    stage_time_minutes DECIMAL(8,2),
    ship_time_minutes DECIMAL(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(wave_id, order_id, plan_version_id)
);

-- Index for fast lookup by wave and plan version
CREATE INDEX IF NOT EXISTS idx_wave_order_metrics_wave_plan ON wave_order_metrics(wave_id, plan_version_id); 