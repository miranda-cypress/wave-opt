#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_waves_detailed():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, wave_name, wave_type, total_orders, warehouse_id, 
                       created_at, status
                FROM waves 
                WHERE warehouse_id = 1
                ORDER BY created_at DESC
                LIMIT 10
            """)
            waves = cursor.fetchall()
            
            print(f"Waves ordered by created_at DESC (limit 10):")
            for wave in waves:
                print(f"  ID: {wave['id']}, Name: {wave['wave_name']}, Orders: {wave['total_orders']}, Created: {wave['created_at']}, Status: {wave['status']}")
            
            print(f"\nTotal waves found: {len(waves)}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_waves_detailed() 