#!/usr/bin/env python3
"""
Clean setup for enhanced WMS schema.
Drops all tables, then runs the enhanced schema and simulated data setup.
"""

import psycopg2
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the database directory to the path
sys.path.append(str(Path(__file__).parent))

from setup_enhanced_schema import main as setup_main

def drop_all_tables():
    """Drop all tables in the warehouse_opt database."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            conn.commit()
        conn.close()
        logger.info("All tables dropped successfully.")
        return True
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        return False

def main():
    print("="*60)
    print("CLEAN SETUP FOR ENHANCED WMS SCHEMA")
    print("="*60)
    print("\nStep 1: Dropping all tables...")
    if not drop_all_tables():
        print("❌ Failed to drop tables")
        return False
    print("✅ All tables dropped.")
    print("\nStep 2: Running enhanced schema and simulated data setup...")
    if not setup_main():
        print("❌ Enhanced schema/data setup failed")
        return False
    print("✅ Enhanced schema and simulated data setup complete.")
    print("\nCLEAN SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    return True

def clean_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        with conn.cursor() as cursor:
            print("Deleting from wave_assignments...")
            cursor.execute("DELETE FROM wave_assignments")
            print("Deleting from waves...")
            cursor.execute("DELETE FROM waves")
            print("Deleting from orders...")
            cursor.execute("DELETE FROM orders")
            print("Deleting from performance_metrics...")
            cursor.execute("DELETE FROM performance_metrics")
            conn.commit()
            print("✅ Database cleaned!")
        conn.close()
    except Exception as e:
        print(f"Error cleaning database: {e}")

if __name__ == "__main__":
    success = main()
    if success:
        clean_database()
    sys.exit(0 if success else 1) 