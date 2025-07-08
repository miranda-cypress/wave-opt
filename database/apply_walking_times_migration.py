#!/usr/bin/env python3
"""
Script to create the walking_times table for storing precomputed walking times between bins.
"""

import sys
import os

# Add the backend directory to the path so we can import database_service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database_service import DatabaseService

def apply_walking_times_migration():
    """Apply the walking_times table migration."""
    try:
        db = DatabaseService()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("Creating walking_times table...")
        
        # Create walking_times table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS walking_times (
                id SERIAL PRIMARY KEY,
                from_bin_id INTEGER REFERENCES bins(id) ON DELETE CASCADE,
                to_bin_id INTEGER REFERENCES bins(id) ON DELETE CASCADE,
                distance_feet DECIMAL(8,2) NOT NULL,
                walking_time_minutes DECIMAL(6,2) NOT NULL,
                path_type VARCHAR(20) DEFAULT 'weighted_manhattan',
                computed_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(from_bin_id, to_bin_id)
            )
        """)
        
        print("✓ Created walking_times table")
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walking_times_from_bin ON walking_times(from_bin_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walking_times_to_bin ON walking_times(to_bin_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_walking_times_computed_at ON walking_times(computed_at)")
        
        print("✓ Created indexes")
        
        # Create view
        print("Creating walking_times_matrix view...")
        cursor.execute("""
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
            ORDER BY b1.bin_id, b2.bin_id
        """)
        
        print("✓ Created walking_times_matrix view")
        
        # Commit the changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    apply_walking_times_migration() 