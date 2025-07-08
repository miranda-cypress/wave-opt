#!/usr/bin/env python3
"""Check wave_assignments table schema."""

import psycopg2

def check_wave_assignments_schema():
    """Check the wave_assignments table schema."""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='warehouse_opt',
            user='wave_user',
            password='wave_password'
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'wave_assignments' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("Wave assignments table columns:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_wave_assignments_schema() 