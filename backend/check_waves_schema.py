#!/usr/bin/env python3
"""Check waves table schema."""

import psycopg2

def check_waves_schema():
    """Check the waves table schema."""
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
            WHERE table_name = 'waves' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("Waves table columns:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        # Also check a sample row
        cursor.execute("SELECT * FROM waves LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\nSample wave row: {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_waves_schema() 