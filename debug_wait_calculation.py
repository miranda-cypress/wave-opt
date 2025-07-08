#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def debug_wait_calculation():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check the actual wait time calculation for order 8
        cursor.execute("""
            SELECT 
                order_id,
                stage_name,
                stage_order,
                waiting_time_before,
                duration_minutes,
                start_time_minutes
            FROM original_wms_plans 
            WHERE order_id = 8 
            ORDER BY stage_order
        """)
        
        results = cursor.fetchall()
        print("Order 8 from original_wms_plans:")
        print("=" * 50)
        for row in results:
            print(f"  {row['stage_name']} (order {row['stage_order']}): {row['waiting_time_before']} min wait, {row['duration_minutes']} min duration")
        
        # Check if the wave_assignments calculation is working
        cursor.execute("""
            WITH stage_mapping AS (
                SELECT 
                    order_id,
                    stage,
                    planned_start_time,
                    planned_duration_minutes,
                    CASE stage
                        WHEN 'pick' THEN 1
                        WHEN 'consolidate' THEN 2
                        WHEN 'pack' THEN 3
                        WHEN 'label' THEN 4
                        WHEN 'stage' THEN 5
                        WHEN 'ship' THEN 6
                        ELSE 1
                    END as stage_order
                FROM wave_assignments 
                WHERE order_id = 8
            ),
            wait_calc AS (
                SELECT 
                    s1.order_id,
                    s1.stage,
                    s1.stage_order,
                    s1.planned_start_time as current_start,
                    s1.planned_duration_minutes as current_duration,
                    s2.planned_start_time as next_start,
                    CASE 
                        WHEN s1.stage_order = 1 THEN 0
                        ELSE EXTRACT(EPOCH FROM (s2.planned_start_time - (s1.planned_start_time + INTERVAL '1 minute' * s1.planned_duration_minutes))) / 60
                    END as calculated_wait
                FROM stage_mapping s1
                LEFT JOIN stage_mapping s2 ON s2.order_id = s1.order_id AND s2.stage_order = s1.stage_order + 1
                ORDER BY s1.stage_order
            )
            SELECT * FROM wait_calc
        """)
        
        results = cursor.fetchall()
        print("\nCalculated wait times from wave_assignments:")
        print("=" * 50)
        for row in results:
            print(f"  {row['stage']} (order {row['stage_order']}): {row['calculated_wait']:.1f} min wait")
            print(f"    Current: {row['current_start']} ({row['current_duration']} min)")
            if row['next_start']:
                print(f"    Next: {row['next_start']}")
            print()
        
    conn.close()

if __name__ == "__main__":
    debug_wait_calculation() 