#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_sku_structure():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'skus' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("SKU table columns:")
        for col in columns:
            print(f"  {col['column_name']}")
    
    conn.close()

if __name__ == "__main__":
    check_sku_structure() 