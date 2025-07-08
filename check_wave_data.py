#!/usr/bin/env python3
"""
Script to check wave data and verify order assignments.
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_wave_data():
    """Check wave data and order assignments."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='warehouse_opt',
            user='wave_user',
            password='wave_password'
        )
        cursor = conn.cursor()
        
        # Check which wave order 8 is assigned to
        cursor.execute("""
            SELECT wa.wave_id, w.wave_name, wa.stage
            FROM wave_assignments wa
            JOIN waves w ON wa.wave_id = w.id
            WHERE wa.order_id = 8
        """)
        
        wave_assignment = cursor.fetchone()
        if wave_assignment:
            wave_id, wave_name, stage = wave_assignment
            logger.info(f"Order 8 is assigned to wave {wave_id}: {wave_name} (stage: {stage})")
        else:
            logger.warning("Order 8 has no wave assignment")
        
        # Check wave_order_metrics for order 8
        cursor.execute("""
            SELECT wom.wave_id, w.wave_name, wom.plan_version_id
            FROM wave_order_metrics wom
            JOIN waves w ON wom.wave_id = w.id
            WHERE wom.order_id = 8
        """)
        
        metrics_results = cursor.fetchall()
        if metrics_results:
            logger.info(f"Order 8 in wave_order_metrics: {metrics_results}")
        else:
            logger.warning("Order 8 not found in wave_order_metrics")
        
        # Check if order 8 appears in multiple waves
        cursor.execute("""
            SELECT wa.wave_id, w.wave_name, COUNT(*) as assignment_count
            FROM wave_assignments wa
            JOIN waves w ON wa.wave_id = w.id
            WHERE wa.order_id = 8
            GROUP BY wa.wave_id, w.wave_name
        """)
        
        multiple_assignments = cursor.fetchall()
        if len(multiple_assignments) > 1:
            logger.warning(f"Order 8 appears in multiple waves: {multiple_assignments}")
        else:
            logger.info(f"Order 8 appears in {len(multiple_assignments)} wave(s)")
        
        # Check wave 1 specifically
        cursor.execute("""
            SELECT wa.order_id, o.order_number, c.name as customer_name
            FROM wave_assignments wa
            JOIN orders o ON wa.order_id = o.id
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE wa.wave_id = 1
            ORDER BY wa.order_id
            LIMIT 10
        """)
        
        wave_1_orders = cursor.fetchall()
        logger.info(f"First 10 orders in wave 1: {wave_1_orders}")
        
        # Check if order 8 is incorrectly in wave 1
        cursor.execute("""
            SELECT wa.order_id, o.order_number, c.name as customer_name
            FROM wave_assignments wa
            JOIN orders o ON wa.order_id = o.id
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE wa.wave_id = 1 AND wa.order_id = 8
        """)
        
        order_8_in_wave_1 = cursor.fetchone()
        if order_8_in_wave_1:
            logger.warning(f"Order 8 incorrectly appears in wave 1: {order_8_in_wave_1}")
        else:
            logger.info("Order 8 correctly NOT in wave 1")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking wave data: {e}")

if __name__ == "__main__":
    check_wave_data() 