#!/usr/bin/env python3
"""
Script to check for orders with missing customer data and fix issues.
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_customer_issues():
    """Check for orders with missing customer data."""
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
        
        # Check for orders with missing customer data
        cursor.execute("""
            SELECT o.id, o.order_number, o.customer_id, c.name as customer_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE c.id IS NULL OR o.customer_id IS NULL
            ORDER BY o.id
            LIMIT 20
        """)
        
        missing_customers = cursor.fetchall()
        
        if missing_customers:
            logger.warning(f"Found {len(missing_customers)} orders with missing customer data:")
            for order_id, order_number, customer_id, customer_name in missing_customers:
                logger.warning(f"  Order {order_id} ({order_number}): customer_id={customer_id}, customer_name={customer_name}")
        else:
            logger.info("No orders with missing customer data found.")
        
        # Check total counts
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders o JOIN customers c ON o.customer_id = c.id")
        orders_with_customers = cursor.fetchone()[0]
        
        logger.info(f"Total orders: {total_orders}")
        logger.info(f"Total customers: {total_customers}")
        logger.info(f"Orders with valid customers: {orders_with_customers}")
        logger.info(f"Orders missing customers: {total_orders - orders_with_customers}")
        
        # Check customer ID range
        cursor.execute("SELECT MIN(id), MAX(id) FROM customers")
        min_customer_id, max_customer_id = cursor.fetchone()
        logger.info(f"Customer ID range: {min_customer_id} to {max_customer_id}")
        
        cursor.execute("SELECT MIN(customer_id), MAX(customer_id) FROM orders WHERE customer_id IS NOT NULL")
        min_order_customer_id, max_order_customer_id = cursor.fetchone()
        logger.info(f"Order customer_id range: {min_order_customer_id} to {max_order_customer_id}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking customer issues: {e}")

if __name__ == "__main__":
    check_customer_issues() 