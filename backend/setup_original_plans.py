#!/usr/bin/env python3
"""
Script to set up original WMS plans materialized view
"""

import psycopg2
from database_service import DatabaseService

def setup_original_plans():
    """Set up the original WMS plans materialized view."""
    try:
        # Connect to database
        db_service = DatabaseService()
        conn = db_service.get_connection()
        
        with conn.cursor() as cursor:
            # Drop the materialized view if it exists
            cursor.execute('DROP MATERIALIZED VIEW IF EXISTS original_wms_plans CASCADE;')
            conn.commit()
        
        # Read the SQL file
        with open('../database/original_plan_generator.sql', 'r') as f:
            sql_content = f.read()
        
        with conn.cursor() as cursor:
            # Execute the SQL
            cursor.execute(sql_content)
            conn.commit()
            
        print("Original WMS plans materialized view created successfully!")
        
    except Exception as e:
        print(f"Error setting up original plans: {e}")
        raise

if __name__ == "__main__":
    setup_original_plans() 