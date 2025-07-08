#!/usr/bin/env python3
"""
Check Wave Details

This script shows detailed information about wave assignments including:
- Stage scheduling (pick, consolidate, pack, label, stage, ship)
- Worker assignments
- Equipment assignments
- Timing information
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_wave_details():
    """Check detailed wave assignment information."""
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor() as cursor:
        # Check wave assignments with detailed info
        cursor.execute("""
            SELECT 
                w.wave_name,
                wa.stage,
                wa.sequence_order,
                wa.planned_start_time,
                wa.planned_duration_minutes,
                wr.worker_code as assigned_worker,
                eq.equipment_code as assigned_equipment,
                o.order_number,
                o.customer_name
            FROM wave_assignments wa
            JOIN waves w ON wa.wave_id = w.id
            LEFT JOIN workers wr ON wa.assigned_worker_id = wr.id
            LEFT JOIN equipment eq ON wa.assigned_equipment_id = eq.id
            JOIN orders o ON wa.order_id = o.id
            WHERE w.wave_name = 'DemoWave_01'
            ORDER BY wa.sequence_order, wa.stage
            LIMIT 20
        """)
        
        assignments = cursor.fetchall()
        
        print("=== Detailed Wave Assignment Information ===")
        print("Sample assignments for DemoWave_01 (first 20):")
        print()
        
        for assignment in assignments:
            wave_name, stage, seq_order, start_time, duration, worker, equipment, order_num, customer = assignment
            print(f"Order: {order_num} | Customer: {customer}")
            print(f"  Stage: {stage} | Sequence: {seq_order}")
            print(f"  Start: {start_time} | Duration: {duration} min")
            print(f"  Worker: {worker or 'None'} | Equipment: {equipment or 'None'}")
            print()
        
        # Check wave completion times
        cursor.execute("""
            SELECT 
                wave_name,
                planned_start_time,
                planned_completion_time,
                total_orders,
                CASE 
                    WHEN planned_completion_time IS NOT NULL AND planned_start_time IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (planned_completion_time - planned_start_time)) / 3600
                    ELSE NULL 
                END as duration_hours
            FROM waves 
            WHERE warehouse_id = 1
            ORDER BY planned_start_time
        """)
        
        waves = cursor.fetchall()
        
        print("=== Wave Completion Times ===")
        for wave in waves:
            wave_name, start_time, completion_time, total_orders, duration_hours = wave
            print(f"{wave_name}: {start_time} -> {completion_time} ({duration_hours:.1f} hours, {total_orders} orders)")
        
        # Check performance metrics
        cursor.execute("""
            SELECT 
                w.wave_name,
                pm.metric_type,
                pm.metric_value
            FROM performance_metrics pm
            JOIN waves w ON pm.wave_id = w.id
            WHERE w.wave_name = 'DemoWave_01'
            ORDER BY pm.metric_type
        """)
        
        metrics = cursor.fetchall()
        
        print("\n=== Performance Metrics for DemoWave_01 ===")
        for metric in metrics:
            wave_name, metric_type, metric_value = metric
            print(f"{metric_type}: {metric_value}")
    
    conn.close()


if __name__ == "__main__":
    check_wave_details() 