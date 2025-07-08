#!/usr/bin/env python3
"""
Test script to check order 8 data from the materialized view
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_order_8():
    """Test what data is returned for order 8 from the materialized view."""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='warehouse_opt',
            user='wave_user',
            password='wave_password'
        )
        
        print("🔍 Testing Order 8 Data")
        print("=" * 40)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test 1: Check if order 8 exists in orders table
            cursor.execute("""
                SELECT id, order_number, priority, shipping_deadline, total_pick_time, total_pack_time
                FROM orders 
                WHERE id = 8
            """)
            order_data = cursor.fetchone()
            if order_data:
                print(f"✅ Order 8 found in orders table:")
                print(f"   Order Number: {order_data['order_number']}")
                print(f"   Priority: {order_data['priority']}")
                print(f"   Pick Time: {order_data['total_pick_time']}")
                print(f"   Pack Time: {order_data['total_pack_time']}")
            else:
                print("❌ Order 8 not found in orders table")
                return
            
            # Test 2: Check the materialized view directly
            print("\n📊 Checking original_wms_plans materialized view:")
            cursor.execute("""
                SELECT order_id, stage_name, duration_minutes, waiting_time_before, 
                       start_time_minutes, worker_id, worker_name, equipment_id, equipment_name
                FROM original_wms_plans 
                WHERE order_id = 8
                ORDER BY stage_order
            """)
            
            mv_results = cursor.fetchall()
            if mv_results:
                print(f"✅ Found {len(mv_results)} stages for order 8 in materialized view:")
                for stage in mv_results:
                    print(f"   {stage['stage_name']}: {stage['duration_minutes']} min, Worker: {stage['worker_name']}")
            else:
                print("❌ No data found for order 8 in materialized view")
            
            # Test 3: Test the function that the API uses
            print("\n🔧 Testing get_original_order_plan function:")
            cursor.execute("SELECT * FROM get_original_order_plan(8)")
            
            function_results = cursor.fetchall()
            if function_results:
                print(f"✅ Function returned {len(function_results)} stages:")
                for stage in function_results:
                    print(f"   {stage['stage_name']}: {stage['duration_minutes']} min, Worker: {stage['worker_name']}")
            else:
                print("❌ Function returned no data for order 8")
            
            # Test 4: Check if there are any wave assignments for order 8
            print("\n🌊 Checking wave assignments for order 8:")
            cursor.execute("""
                SELECT wave_id, stage, assigned_worker_id, planned_duration_minutes
                FROM wave_assignments 
                WHERE order_id = 8
                ORDER BY sequence_order
            """)
            
            wave_results = cursor.fetchall()
            if wave_results:
                print(f"✅ Found {len(wave_results)} wave assignments for order 8:")
                for assignment in wave_results:
                    print(f"   Wave {assignment['wave_id']}, Stage: {assignment['stage']}, Duration: {assignment['planned_duration_minutes']}")
            else:
                print("❌ No wave assignments found for order 8")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_order_8() 