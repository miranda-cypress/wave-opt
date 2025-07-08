#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_waiting_times():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check waiting times for order 8
        cursor.execute("""
            SELECT stage_name, waiting_time_before, duration_minutes
            FROM original_wms_plans 
            WHERE order_id = 8 
            ORDER BY stage_order
        """)
        
        results = cursor.fetchall()
        print("Order 8 Waiting Times:")
        print("=" * 50)
        for row in results:
            print(f"  {row['stage_name']}: {row['waiting_time_before']} min wait, {row['duration_minutes']} min duration")
        
        # Check the waiting time calculation function
        print("\nTesting waiting time calculation function:")
        print("=" * 50)
        cursor.execute("""
            SELECT 
                'PICK' as stage,
                calculate_original_waiting_time('PICK', '1', 100) as wait_time
            UNION ALL
            SELECT 
                'CONSOLIDATE' as stage,
                calculate_original_waiting_time('CONSOLIDATE', '1', 100) as wait_time
            UNION ALL
            SELECT 
                'PACK' as stage,
                calculate_original_waiting_time('PACK', '1', 100) as wait_time
            UNION ALL
            SELECT 
                'LABEL' as stage,
                calculate_original_waiting_time('LABEL', '1', 100) as wait_time
            UNION ALL
            SELECT 
                'STAGE' as stage,
                calculate_original_waiting_time('STAGE', '1', 100) as wait_time
            UNION ALL
            SELECT 
                'SHIP' as stage,
                calculate_original_waiting_time('SHIP', '1', 100) as wait_time
        """)
        
        function_results = cursor.fetchall()
        for row in function_results:
            print(f"  {row['stage']}: {row['wait_time']} min")
        
        # Check total orders in queue
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders WHERE status = 'pending'")
        total_orders = cursor.fetchone()['total_orders']
        print(f"\nTotal pending orders: {total_orders}")
    
    conn.close()

if __name__ == "__main__":
    check_waiting_times() 