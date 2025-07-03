#!/usr/bin/env python3
"""
Check waves in the database to understand why only 1 wave appears in the API.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_waves():
    """Check waves in the database."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check total waves
            cursor.execute("SELECT COUNT(*) as total FROM waves")
            total = cursor.fetchone()['total']
            print(f"Total waves in database: {total}")
            
            # Get all waves
            cursor.execute("""
                SELECT id, wave_name, wave_type, planned_start_time, 
                       total_orders, total_items, status, warehouse_id
                FROM waves 
                ORDER BY id
            """)
            waves = cursor.fetchall()
            
            print("\nWaves in database:")
            for wave in waves:
                print(f"  ID: {wave['id']}, Name: {wave['wave_name']}, Type: {wave['wave_type']}, Orders: {wave['total_orders']}, Status: {wave['status']}")
            
            # Check wave assignments
            cursor.execute("SELECT COUNT(*) as total FROM wave_assignments")
            assignments = cursor.fetchone()['total']
            print(f"\nTotal wave assignments: {assignments}")
            
            # Check orders
            cursor.execute("SELECT COUNT(*) as total FROM orders")
            orders = cursor.fetchone()['total']
            print(f"Total orders: {orders}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_waves() 