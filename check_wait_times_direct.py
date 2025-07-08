#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_wait_times_direct():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check wait times directly from materialized view
        cursor.execute("""
            SELECT stage_name, waiting_time_before 
            FROM original_wms_plans 
            WHERE order_id = 8 
            ORDER BY stage_order, stage_name
            LIMIT 20
        """)
        
        results = cursor.fetchall()
        print("Wait times from materialized view for order 8:")
        print("=" * 50)
        for row in results:
            print(f"  {row['stage_name']}: {row['waiting_time_before']} min")
        
        # Check if there are any 60-minute values
        cursor.execute("""
            SELECT COUNT(*) as count_60
            FROM original_wms_plans 
            WHERE order_id = 8 AND waiting_time_before = 60
        """)
        
        result = cursor.fetchone()
        print(f"\nCount of 60-minute wait times: {result['count_60']}")
        
        # Check the range of wait times
        cursor.execute("""
            SELECT 
                MIN(waiting_time_before) as min_wait,
                MAX(waiting_time_before) as max_wait,
                AVG(waiting_time_before) as avg_wait
            FROM original_wms_plans 
            WHERE order_id = 8
        """)
        
        result = cursor.fetchone()
        print(f"Wait time range: {result['min_wait']} - {result['max_wait']} min (avg: {result['avg_wait']:.1f})")
        
    conn.close()

if __name__ == "__main__":
    check_wait_times_direct() 