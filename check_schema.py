#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_schema():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check orders table schema
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'orders' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("Orders table columns:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']}")
        
        print("\nChecking for ORD00376899...")
        cursor.execute("""
            SELECT * FROM orders WHERE order_number = %s
        """, ('ORD00376899',))
        
        order = cursor.fetchone()
        if order:
            print(f"Order found: {order}")
        else:
            print("Order ORD00376899 not found")
    
    conn.close()

if __name__ == "__main__":
    check_schema() 