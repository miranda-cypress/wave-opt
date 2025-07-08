#!/usr/bin/env python3
"""
Script to generate fake completed orders for the database.
This will populate the database with realistic order data for testing calculations.
"""

import random
import psycopg2
from datetime import datetime, timedelta
from decimal import Decimal
from database_service import DatabaseService

def generate_completed_orders(num_orders=10000):
    """Generate fake completed orders with realistic data."""
    
    db_service = DatabaseService()
    
    try:
        conn = db_service.get_connection()
        cursor = conn.cursor()
        
        print(f"Generating {num_orders} completed orders...")
        
        # Get existing customers, workers, and SKUs for realistic references
        cursor.execute("SELECT id, customer_code, name FROM customers WHERE warehouse_id = 1")
        customers = cursor.fetchall()
        
        cursor.execute("SELECT id, worker_code, name, hourly_rate FROM workers WHERE warehouse_id = 1 AND active = TRUE")
        workers = cursor.fetchall()
        
        cursor.execute("SELECT id, sku_code, name, pick_time_minutes, pack_time_minutes FROM skus WHERE warehouse_id = 1")
        skus = cursor.fetchall()
        
        if not customers:
            print("No customers found. Creating sample customers...")
            customers = [
                (1, 'CUST001', 'Acme Corp'),
                (2, 'CUST002', 'Tech Solutions Inc'),
                (3, 'CUST003', 'Global Retail'),
                (4, 'CUST004', 'Supply Chain Co'),
                (5, 'CUST005', 'E-commerce Plus')
            ]
            for cust_id, cust_code, cust_name in customers:
                cursor.execute("""
                    INSERT INTO customers (id, warehouse_id, customer_code, name, customer_type, priority_level)
                    VALUES (%s, 1, %s, %s, 'b2b', %s)
                    ON CONFLICT (id) DO NOTHING
                """, (cust_id, cust_code, cust_name, random.randint(1, 5)))
        
        if not workers:
            print("No workers found. Creating sample workers...")
            workers = [
                (1, 'W001', 'Sarah Johnson', 25.50),
                (2, 'W002', 'Mike Chen', 24.00),
                (3, 'W003', 'Lisa Rodriguez', 26.00),
                (4, 'W004', 'David Smith', 23.50),
                (5, 'W005', 'Emma Wilson', 25.00)
            ]
            for worker_id, worker_code, worker_name, hourly_rate in workers:
                cursor.execute("""
                    INSERT INTO workers (id, warehouse_id, worker_code, name, hourly_rate, efficiency_factor)
                    VALUES (%s, 1, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (worker_id, worker_code, worker_name, hourly_rate, random.uniform(0.8, 1.2)))
        
        if not skus:
            print("No SKUs found. Creating sample SKUs...")
            skus = [
                (1, 'SKU001', 'Widget A', 2.5, 1.5),
                (2, 'SKU002', 'Gadget B', 3.0, 2.0),
                (3, 'SKU003', 'Tool C', 4.0, 2.5),
                (4, 'SKU004', 'Part D', 1.5, 1.0),
                (5, 'SKU005', 'Component E', 2.0, 1.8)
            ]
            for sku_id, sku_code, sku_name, pick_time, pack_time in skus:
                cursor.execute("""
                    INSERT INTO skus (id, warehouse_id, sku_code, name, pick_time_minutes, pack_time_minutes)
                    VALUES (%s, 1, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (sku_id, sku_code, sku_name, pick_time, pack_time))
        
        # Generate orders over the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        orders_created = 0
        batch_size = 1000
        
        for batch_start in range(0, num_orders, batch_size):
            batch_end = min(batch_start + batch_size, num_orders)
            batch_orders = []
            
            for i in range(batch_start, batch_end):
                # Random order date within the last 6 months
                order_date = start_date + timedelta(
                    days=random.randint(0, 180),
                    hours=random.randint(8, 18),
                    minutes=random.randint(0, 59)
                )
                
                # Random shipping deadline (1-7 days after order)
                shipping_deadline = order_date + timedelta(days=random.randint(1, 7))
                
                # Random completion date (before deadline)
                completion_date = order_date + timedelta(
                    days=random.randint(0, 5),
                    hours=random.randint(1, 8)
                )
                
                # Select random customer
                customer = random.choice(customers)
                customer_id = customer[0]
                
                # Generate order items (1-5 items per order)
                num_items = random.randint(1, 5)
                total_pick_time = 0
                total_pack_time = 0
                total_volume = 0
                total_weight = 0
                
                order_items = []
                for j in range(num_items):
                    sku = random.choice(skus)
                    sku_id = sku[0]
                    quantity = random.randint(1, 10)
                    
                    # Calculate times with some variation
                    base_pick_time = float(sku[3]) * quantity
                    base_pack_time = float(sku[4]) * quantity
                    
                    # Add some realistic variation (±20%)
                    pick_time = base_pick_time * random.uniform(0.8, 1.2)
                    pack_time = base_pack_time * random.uniform(0.8, 1.2)
                    
                    total_pick_time += pick_time
                    total_pack_time += pack_time
                    total_volume += quantity * random.uniform(0.1, 2.0)
                    total_weight += quantity * random.uniform(0.5, 5.0)
                    
                    order_items.append({
                        'sku_id': sku_id,
                        'quantity': quantity,
                        'pick_time': pick_time,
                        'pack_time': pack_time,
                        'volume': quantity * random.uniform(0.1, 2.0),
                        'weight': quantity * random.uniform(0.5, 5.0)
                    })
                
                # Create order
                order_number = f"ORD{str(i+1).zfill(6)}"
                priority = random.randint(1, 5)
                
                cursor.execute("""
                    INSERT INTO orders (
                        warehouse_id, order_number, customer_id, order_date,
                        priority, shipping_deadline, total_pick_time, total_pack_time,
                        total_volume, total_weight, status, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    1, order_number, customer_id, order_date,
                    priority, shipping_deadline, total_pick_time, total_pack_time,
                    total_volume, total_weight, 'shipped', order_date, completion_date
                ))
                
                order_result = cursor.fetchone()
                if order_result:
                    order_id = order_result[0]
                else:
                    raise Exception("Failed to create order")
                
                # Create order items
                for item in order_items:
                    cursor.execute("""
                        INSERT INTO order_items (
                            order_id, sku_id, quantity, pick_time, pack_time,
                            volume, weight, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        order_id, item['sku_id'], item['quantity'], item['pick_time'],
                        item['pack_time'], item['volume'], item['weight'], order_date
                    ))
                
                orders_created += 1
                
                if orders_created % 1000 == 0:
                    print(f"Created {orders_created} orders...")
            
            # Commit batch
            conn.commit()
            print(f"Committed batch of {batch_end - batch_start} orders")
        
        print(f"✅ Successfully created {orders_created} completed orders!")
        
        # Print some statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                AVG(total_pick_time) as avg_pick_time,
                AVG(total_pack_time) as avg_pack_time,
                AVG(total_pick_time + total_pack_time) as avg_total_time,
                AVG(total_volume) as avg_volume,
                AVG(total_weight) as avg_weight
            FROM orders 
            WHERE warehouse_id = 1 AND status = 'shipped'
        """)
        
        stats = cursor.fetchone()
        if stats:
            print(f"\n📊 Order Statistics:")
            print(f"Total Orders: {stats[0]}")
            print(f"Average Pick Time: {stats[1]:.2f} minutes")
            print(f"Average Pack Time: {stats[2]:.2f} minutes")
            print(f"Average Total Time: {stats[3]:.2f} minutes")
            print(f"Average Volume: {stats[4]:.2f} cubic feet")
            print(f"Average Weight: {stats[5]:.2f} lbs")
        else:
            print("No statistics available")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating orders: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    generate_completed_orders(10000) 