#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_warehouse_ids():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT DISTINCT warehouse_id FROM waves ORDER BY warehouse_id")
            warehouse_ids = [row['warehouse_id'] for row in cursor.fetchall()]
            print(f"Warehouse IDs in waves table: {warehouse_ids}")
            
            # Check waves for each warehouse_id
            for warehouse_id in warehouse_ids:
                cursor.execute("""
                    SELECT id, wave_name, total_orders, warehouse_id 
                    FROM waves 
                    WHERE warehouse_id = %s 
                    ORDER BY id
                """, (warehouse_id,))
                waves = cursor.fetchall()
                print(f"\nWaves for warehouse_id {warehouse_id}:")
                for wave in waves:
                    print(f"  ID: {wave['id']}, Name: {wave['wave_name']}, Orders: {wave['total_orders']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_warehouse_ids() 