#!/usr/bin/env python3
"""
Update Wave Assignments with New Baseline Data

This script updates the wave_assignments table to match the new baseline data
from the original_wms_plans materialized view, ensuring the frontend displays
consistent data.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_wave_assignments():
    """Update wave_assignments table with new baseline data."""
    print("🔄 Updating Wave Assignments with New Baseline Data")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='warehouse_opt',
            user='wave_user',
            password='wave_password'
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get all orders from the materialized view
            cursor.execute("""
                SELECT DISTINCT order_id 
                FROM original_wms_plans 
                ORDER BY order_id
            """)
            order_ids = [row['order_id'] for row in cursor.fetchall()]
            
            print(f"📊 Found {len(order_ids)} orders to update")
            
            updated_count = 0
            for order_id in order_ids:
                # Get the new baseline data for this order
                cursor.execute("""
                    SELECT 
                        order_id,
                        stage_name,
                        duration_minutes,
                        waiting_time_before,
                        start_time_minutes,
                        worker_id,
                        worker_name,
                        equipment_id,
                        equipment_name,
                        stage_order
                    FROM original_wms_plans 
                    WHERE order_id = %s
                    ORDER BY stage_order
                """, (order_id,))
                
                baseline_stages = cursor.fetchall()
                
                if not baseline_stages:
                    continue
                
                # Get the wave_id for this order
                cursor.execute("""
                    SELECT DISTINCT wave_id 
                    FROM wave_assignments 
                    WHERE order_id = %s
                """, (order_id,))
                
                wave_result = cursor.fetchone()
                if not wave_result:
                    print(f"⚠️  No wave assignment found for order {order_id}")
                    continue
                
                wave_id = wave_result['wave_id']
                
                # Delete existing assignments for this order
                cursor.execute("""
                    DELETE FROM wave_assignments 
                    WHERE order_id = %s
                """, (order_id,))
                
                # Insert new assignments based on baseline data
                for stage_data in baseline_stages:
                    # Check if equipment exists, otherwise use NULL
                    equipment_id = stage_data['equipment_id']
                    if equipment_id:
                        cursor.execute("SELECT id FROM equipment WHERE id = %s", (equipment_id,))
                        if not cursor.fetchone():
                            equipment_id = None
                    
                    # Check if worker exists, otherwise use NULL
                    worker_id = stage_data['worker_id']
                    if worker_id:
                        cursor.execute("SELECT id FROM workers WHERE id = %s", (worker_id,))
                        if not cursor.fetchone():
                            worker_id = None
                    
                    # Calculate start time by adding minutes to wave start time
                    cursor.execute("""
                        INSERT INTO wave_assignments 
                        (wave_id, order_id, stage, assigned_worker_id, assigned_equipment_id,
                         planned_start_time, planned_duration_minutes, sequence_order)
                        VALUES (%s, %s, %s, %s, %s, 
                                (SELECT planned_start_time + INTERVAL '%s minutes' FROM waves WHERE id = %s),
                                %s, %s)
                    """, (
                        wave_id,
                        order_id,
                        stage_data['stage_name'].lower(),  # Convert to lowercase
                        worker_id,
                        equipment_id,
                        stage_data['start_time_minutes'],
                        wave_id,
                        stage_data['duration_minutes'],
                        stage_data['stage_order']
                    ))
                
                updated_count += 1
                if updated_count % 100 == 0:
                    print(f"✅ Updated {updated_count} orders...")
            
            conn.commit()
            print(f"🎉 Successfully updated {updated_count} orders!")
            print("   The frontend should now show consistent baseline data.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating wave assignments: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    update_wave_assignments() 