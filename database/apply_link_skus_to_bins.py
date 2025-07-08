#!/usr/bin/env python3
"""
Script to link SKUs to bins by adding a bin_id foreign key to the skus table.
"""

import sys
import os

# Add the backend directory to the path so we can import database_service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database_service import DatabaseService

def apply_link_skus_to_bins():
    try:
        db = DatabaseService()
        conn = db.get_connection()
        cursor = conn.cursor()

        print("Adding bin_id column to skus table if not exists...")
        cursor.execute("ALTER TABLE skus ADD COLUMN IF NOT EXISTS bin_id INTEGER REFERENCES bins(id)")

        print("Linking sample SKUs to bins...")
        for i in range(1, 11):
            sku_code = f'SKU{i:03d}'
            bin_code = f'BIN{i:03d}'
            cursor.execute("UPDATE skus SET bin_id = (SELECT id FROM bins WHERE bin_id = %s) WHERE sku_code = %s", (bin_code, sku_code))

        print("Creating index for bin_id foreign key...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skus_bin_id ON skus(bin_id)")

        conn.commit()
        print("✓ Migration completed successfully!")

        # Verify
        cursor.execute("SELECT sku_code, bin_id FROM skus ORDER BY sku_code")
        for row in cursor.fetchall():
            print(row)

        conn.close()
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    apply_link_skus_to_bins() 