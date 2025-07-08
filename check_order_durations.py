#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_order_durations():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # First, check if the order exists
        cursor.execute("""
            SELECT id, order_number, total_pick_time, total_pack_time, total_volume, total_weight, priority
            FROM orders WHERE order_number = %s
        """, ('ORD00376899',))
        
        order_data = cursor.fetchone()
        if not order_data:
            print("Order ORD00376899 not found in database")
            return
        
        print(f"Order found: {order_data}")
        print()
        
        # Get the original plan for this order
        cursor.execute("""
            SELECT * FROM get_original_order_plan(%s)
        """, (order_data['id'],))
        
        stages = cursor.fetchall()
        
        if not stages:
            print("No original plan found for this order")
            return
        
        print("Original WMS Plan for ORD00376899:")
        print("=" * 80)
        total_duration = 0
        total_waiting = 0
        
        for stage in stages:
            duration = stage['duration_minutes']
            waiting = stage['waiting_time_before']
            total = stage['total_time']
            total_duration += duration
            total_waiting += waiting
            
            print(f"Stage: {stage['stage_name']:<12} | Duration: {duration:>3} min | Waiting: {waiting:>3} min | Total: {total:>3} min")
        
        print("=" * 80)
        print(f"Total Processing Time: {total_duration} minutes ({total_duration/60:.1f} hours)")
        print(f"Total Waiting Time: {total_waiting} minutes ({total_waiting/60:.1f} hours)")
        print(f"Total Time: {stages[-1]['total_time']} minutes ({stages[-1]['total_time']/60:.1f} hours)")
        
        # Check wave assignments
        cursor.execute("""
            SELECT wa.*, w.wave_name, o.order_number
            FROM wave_assignments wa
            JOIN waves w ON wa.wave_id = w.id
            JOIN orders o ON wa.order_id = o.id
            WHERE o.order_number = %s
            ORDER BY wa.stage, wa.sequence_order
        """, ('ORD00376899',))
        
        wave_assignments = cursor.fetchall()
        
        if wave_assignments:
            print(f"\nWave Assignments for ORD00376899:")
            print("=" * 80)
            for assignment in wave_assignments:
                print(f"Wave: {assignment['wave_name']} | Stage: {assignment['stage']} | Duration: {assignment['planned_duration_minutes']} min")
        
        # Check if this order is in any waves
        cursor.execute("""
            SELECT w.wave_name, w.planned_start_time, w.planned_completion_time,
                   EXTRACT(EPOCH FROM (w.planned_completion_time - w.planned_start_time))/3600 as wave_duration_hours
            FROM waves w
            JOIN wave_assignments wa ON w.id = wa.wave_id
            JOIN orders o ON wa.order_id = o.id
            WHERE o.order_number = %s
        """, ('ORD00376899',))
        
        wave_info = cursor.fetchone()
        if wave_info:
            print(f"\nWave Information:")
            print(f"Wave: {wave_info['wave_name']}")
            print(f"Start: {wave_info['planned_start_time']}")
            print(f"End: {wave_info['planned_completion_time']}")
            print(f"Wave Duration: {wave_info['wave_duration_hours']:.1f} hours")
        
        # Check what happens when we calculate durations manually
        print(f"\nManual Duration Calculation:")
        print(f"Order priority: {order_data['priority']}")
        print(f"Total pick time: {order_data['total_pick_time']}")
        print(f"Total pack time: {order_data['total_pack_time']}")
        print(f"Total volume: {order_data['total_volume']}")
        print(f"Total weight: {order_data['total_weight']}")
        
        # Let's check what the duration calculation function would return
        cursor.execute("""
            SELECT 
                'PICK' as stage,
                calculate_original_stage_duration(%s, 'PICK', %s, %s, %s, 5, %s) as duration
            UNION ALL
            SELECT 
                'CONSOLIDATE' as stage,
                calculate_original_stage_duration(%s, 'CONSOLIDATE', %s, %s, %s, 5, %s) as duration
            UNION ALL
            SELECT 
                'PACK' as stage,
                calculate_original_stage_duration(%s, 'PACK', %s, %s, %s, 5, %s) as duration
            UNION ALL
            SELECT 
                'LABEL' as stage,
                calculate_original_stage_duration(%s, 'LABEL', %s, %s, %s, 5, %s) as duration
            UNION ALL
            SELECT 
                'STAGE' as stage,
                calculate_original_stage_duration(%s, 'STAGE', %s, %s, %s, 5, %s) as duration
            UNION ALL
            SELECT 
                'SHIP' as stage,
                calculate_original_stage_duration(%s, 'SHIP', %s, %s, %s, 5, %s) as duration
        """, (
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight'],
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight'],
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight'],
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight'],
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight'],
            order_data['id'], order_data['total_pick_time'], order_data['total_pack_time'], order_data['priority'], order_data['total_weight']
        ))
        
        manual_durations = cursor.fetchall()
        print(f"\nManual Duration Calculations:")
        for row in manual_durations:
            print(f"  {row['stage']}: {row['duration']} minutes")
    
    conn.close()

if __name__ == "__main__":
    check_order_durations() 