#!/usr/bin/env python3
"""
Script to check order 8 specifically and its wave assignment data.
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_order_8():
    """Check order 8 specifically."""
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
        
        # Check order 8 in orders table
        cursor.execute("""
            SELECT o.id, o.order_number, o.customer_id, c.name as customer_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.id = 8
        """)
        
        order_result = cursor.fetchone()
        if order_result:
            order_id, order_number, customer_id, customer_name = order_result
            logger.info(f"Order 8: id={order_id}, order_number={order_number}, customer_id={customer_id}, customer_name={customer_name}")
        else:
            logger.warning("Order 8 not found in orders table")
        
        # Check if order 8 is in wave_order_metrics
        cursor.execute("""
            SELECT order_id, wave_id, plan_version_id
            FROM wave_order_metrics
            WHERE order_id = 8
        """)
        
        metrics_result = cursor.fetchall()
        if metrics_result:
            logger.info(f"Order 8 found in wave_order_metrics: {metrics_result}")
        else:
            logger.warning("Order 8 not found in wave_order_metrics table")
        
        # Check wave assignments for order 8
        cursor.execute("""
            SELECT wave_id, stage, assigned_worker_id
            FROM wave_assignments
            WHERE order_id = 8
        """)
        
        assignments_result = cursor.fetchall()
        if assignments_result:
            logger.info(f"Order 8 wave assignments: {assignments_result}")
        else:
            logger.warning("Order 8 not found in wave_assignments table")
        
        # Check what waves exist
        cursor.execute("""
            SELECT id, wave_name
            FROM waves
            ORDER BY id
            LIMIT 10
        """)
        
        waves_result = cursor.fetchall()
        logger.info(f"First 10 waves: {waves_result}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking order 8: {e}")

if __name__ == "__main__":
    check_order_8() 