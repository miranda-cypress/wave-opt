#!/usr/bin/env python3
"""
Enhanced Demo Data Generator

This script generates comprehensive demo data for the wave optimization system:
- 5000 SKUs across multiple zones
- 10000 orders with deadlines across 4 days
- 16 waves (4 per day) with 500-700 orders each
- Wave assignments with pick orders from WMS
- Labor calculations and completion time estimates
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDemoDataGenerator:
    """Generates comprehensive demo data for wave optimization testing."""
    
    def __init__(self, host: str = "localhost", port: int = 5433, 
                 database: str = "warehouse_opt", user: str = "wave_user", 
                 password: str = "wave_password"):
        """Initialize database connection parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        
        # Configuration
        self.num_skus = 5000
        self.num_orders = 10000
        self.num_days = 4
        self.waves_per_day = 4
        self.orders_per_wave_min = 500
        self.orders_per_wave_max = 700
        
        # Time constants (in minutes)
        self.pick_time_base = 2.0
        self.pack_time_base = 1.5
        self.walking_time_per_zone = 3.0
        self.setup_time_per_order = 1.0
        
        # Labor constants
        self.worker_efficiency = 0.85
        self.max_workers_per_wave = 20
        self.worker_hourly_rate = 18.50
    
    def get_connection(self):
        """Get a database connection."""
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_enhanced_skus(self):
        """Create 5000 SKUs with realistic distribution across zones."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Creating 5000 SKUs...")
            
            # Zone distribution: A (fast) = 40%, B (medium) = 35%, C (slow) = 25%
            zone_distribution = {
                'A': int(self.num_skus * 0.40),
                'B': int(self.num_skus * 0.35), 
                'C': int(self.num_skus * 0.25)
            }
            
            categories = [
                'Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Automotive',
                'Books', 'Toys', 'Health & Beauty', 'Tools', 'Kitchen',
                'Office Supplies', 'Pet Supplies', 'Baby Products', 'Jewelry', 'Art'
            ]
            
            velocity_classes = ['A', 'B', 'C']
            
            sku_counter = 1
            for zone, count in zone_distribution.items():
                for i in range(count):
                    # Determine velocity class based on zone
                    if zone == 'A':
                        velocity = random.choices(['A', 'B'], weights=[0.7, 0.3])[0]
                    elif zone == 'B':
                        velocity = random.choices(['B', 'C'], weights=[0.6, 0.4])[0]
                    else:
                        velocity = 'C'
                    
                    # Generate realistic pick/pack times based on zone and velocity
                    if zone == 'A':
                        pick_time = random.uniform(1.0, 2.5)
                        pack_time = random.uniform(0.8, 1.5)
                    elif zone == 'B':
                        pick_time = random.uniform(2.0, 4.0)
                        pack_time = random.uniform(1.5, 2.5)
                    else:
                        pick_time = random.uniform(3.0, 6.0)
                        pack_time = random.uniform(2.0, 4.0)
                    
                    category = random.choice(categories)
                    volume = random.uniform(0.1, 10.0)
                    weight = random.uniform(0.5, 50.0)
                    
                    cursor.execute("""
                        INSERT INTO skus (warehouse_id, sku_code, name, category, zone, 
                                        pick_time_minutes, pack_time_minutes, volume_cubic_feet, 
                                        weight_lbs, velocity_class, external_sku_id, source_id)
                        VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                        ON CONFLICT (sku_code) DO NOTHING
                    """, (
                        f'SKU{sku_counter:04d}',
                        f'Product {sku_counter} - {category}',
                        category,
                        zone,
                        round(pick_time, 2),
                        round(pack_time, 2),
                        round(volume, 3),
                        round(weight, 2),
                        velocity,
                        f'EXT_SKU_{sku_counter:04d}'
                    ))
                    sku_counter += 1
            
            conn.commit()
            logger.info(f"Created {sku_counter - 1} SKUs")
    
    def create_enhanced_orders(self):
        """Create 10000 orders with deadlines across 4 days."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Creating 10000 orders...")
            
            # Get all customer IDs
            cursor.execute("SELECT id FROM customers WHERE warehouse_id = 1")
            customer_ids = [row[0] for row in cursor.fetchall()]
            
            # Get all SKU IDs
            cursor.execute("SELECT id, zone FROM skus WHERE warehouse_id = 1")
            sku_data = cursor.fetchall()
            sku_ids = [row[0] for row in sku_data]
            sku_zones = {row[0]: row[1] for row in sku_data}
            
            # Create orders with deadlines across 4 days starting tomorrow
            start_date = datetime.now() + timedelta(days=1)
            
            for order_num in range(1, self.num_orders + 1):
                # Distribute orders across 4 days
                day_offset = (order_num - 1) % self.num_days
                deadline = start_date + timedelta(days=day_offset)
                
                # Add some time variation within each day
                hour_offset = random.randint(8, 17)  # 8 AM to 5 PM
                minute_offset = random.randint(0, 59)
                deadline = deadline.replace(hour=hour_offset, minute=minute_offset)
                
                # Random order details
                customer_id = random.choice(customer_ids)
                priority = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.2, 0.1])[0]
                num_items = random.randint(1, 12)
                
                # Fetch customer name and type
                cursor.execute("SELECT customer_type FROM customers WHERE id = %s", (customer_id,))
                customer_row = cursor.fetchone()
                if customer_row is None:
                    logger.warning(f"Customer not found for id={customer_id}, skipping order_num={order_num}")
                    continue
                customer_type = customer_row[0]
                # Create order
                order_date = deadline.replace(hour=0, minute=0, second=0, microsecond=0)
                cursor.execute("""
                    INSERT INTO orders (warehouse_id, customer_id, order_number, 
                                      order_date, customer_type, 
                                      shipping_deadline, priority, status, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, 'pending', 2)
                    RETURNING id
                """, (
                    customer_id,
                    f'ORD{order_num:06d}',
                    order_date,
                    customer_type,
                    deadline,
                    priority
                ))
                order_row = cursor.fetchone()
                if order_row is None:
                    logger.warning(f"Order insert failed for order_num={order_num}")
                    continue
                order_id = order_row[0]
                
                # Create order items
                order_skus = random.sample(sku_ids, min(num_items, len(sku_ids)))
                for item_num, sku_id in enumerate(order_skus, 1):
                    quantity = random.randint(1, 5)
                    cursor.execute("""
                        INSERT INTO order_items (order_id, sku_id, quantity, source_id)
                        VALUES (%s, %s, %s, 2)
                    """, (order_id, sku_id, quantity))
            
            conn.commit()
            logger.info(f"Created {self.num_orders} orders")
    
    def create_wave_plan_versions(self):
        """Create wave plan versions for original WMS and optimized plans."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Create original WMS plan version
            cursor.execute("""
                INSERT INTO wave_plan_versions (warehouse_id, version_name, version_description, 
                                              version_type, created_by, is_active)
                VALUES (1, 'Original WMS Plan', 'Initial wave plan from WMS system', 
                       'original', 'system', TRUE)
                RETURNING id
            """)
            orig_row = cursor.fetchone()
            if orig_row is None:
                logger.error("Failed to insert original wave plan version.")
                return None, None
            original_version_id = orig_row[0]
            
            # Create optimized plan version
            cursor.execute("""
                INSERT INTO wave_plan_versions (warehouse_id, version_name, version_description, 
                                              version_type, created_by, is_active)
                VALUES (1, 'Optimized Wave Plan', 'AI-optimized wave plan', 
                       'optimized', 'system', TRUE)
                RETURNING id
            """)
            opt_row = cursor.fetchone()
            if opt_row is None:
                logger.error("Failed to insert optimized wave plan version.")
                return original_version_id, None
            optimized_version_id = opt_row[0]
            
            conn.commit()
            logger.info(f"Created wave plan versions: Original={original_version_id}, Optimized={optimized_version_id}")
            return original_version_id, optimized_version_id
    
    def create_waves_and_assignments(self, original_version_id: int, optimized_version_id: int):
        """Create waves and assign orders to them."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Creating waves and assignments...")
            
            # Get all orders grouped by deadline day
            cursor.execute("""
                SELECT id, shipping_deadline, priority 
                FROM orders 
                WHERE warehouse_id = 1 AND status = 'pending'
                ORDER BY shipping_deadline
            """)
            orders = cursor.fetchall()
            
            # Group orders by day
            orders_by_day = {}
            for order_id, deadline, priority in orders:
                day_key = deadline.date()
                if day_key not in orders_by_day:
                    orders_by_day[day_key] = []
                orders_by_day[day_key].append((order_id, deadline, priority))
            
            wave_counter = 1
            
            for day, day_orders in orders_by_day.items():
                # Sort orders by deadline and priority
                day_orders.sort(key=lambda x: (x[1], x[2]))
                
                # Split into 4 waves per day
                orders_per_wave = len(day_orders) // self.waves_per_day
                remainder = len(day_orders) % self.waves_per_day
                
                start_idx = 0
                for wave_num in range(self.waves_per_day):
                    # Calculate wave size (distribute remainder)
                    wave_size = orders_per_wave + (1 if wave_num < remainder else 0)
                    end_idx = start_idx + wave_size
                    wave_orders = day_orders[start_idx:end_idx]
                    
                    if not wave_orders:
                        continue
                    
                    # Create wave for both original and optimized versions
                    for version_id, version_type in [(original_version_id, 'original'), (optimized_version_id, 'optimized')]:
                        # Generate wave name with date and wave type
                        wave_date = day  # day is already a date object
                        wave_num = wave_num + 1  # 1-4 for the day
                        
                        date_str = wave_date.strftime("%B %-d")
                        if wave_num == 1:
                            wave_type = "Morning Wave 1"
                        elif wave_num == 2:
                            wave_type = "Morning Wave 2"
                        elif wave_num == 3:
                            wave_type = "Afternoon Wave 1"
                        elif wave_num == 4:
                            wave_type = "Afternoon Wave 2"
                        else:
                            wave_type = f"Wave {wave_num}"
                        
                        wave_name = f"{date_str} - {wave_type}"
                        
                        # Calculate wave statistics
                        total_orders = len(wave_orders)
                        total_items = 0
                        total_pick_time = 0
                        total_pack_time = 0
                        
                        # Get order details for calculations
                        order_ids = [order[0] for order in wave_orders]
                        cursor.execute("""
                            SELECT oi.order_id, oi.quantity, s.pick_time_minutes, s.pack_time_minutes, s.zone
                            FROM order_items oi
                            JOIN skus s ON oi.sku_id = s.id
                            WHERE oi.order_id = ANY(%s)
                        """, (order_ids,))
                        
                        item_details = cursor.fetchall()
                        for order_id, quantity, pick_time, pack_time, zone in item_details:
                            total_items += quantity
                            total_pick_time += pick_time * quantity
                            total_pack_time += pack_time * quantity
                        
                        # Calculate labor requirements
                        total_work_time = total_pick_time + total_pack_time + (len(wave_orders) * self.setup_time_per_order)
                        estimated_workers = max(1, math.ceil(total_work_time / (8 * 60 * self.worker_efficiency)))  # 8-hour shift
                        estimated_workers = min(estimated_workers, self.max_workers_per_wave)
                        
                        # Calculate completion time
                        completion_time_minutes = total_work_time / (estimated_workers * self.worker_efficiency)
                        completion_time_hours = completion_time_minutes / 60
                        
                        # Calculate labor cost
                        labor_cost = (completion_time_hours * estimated_workers * self.worker_hourly_rate)
                        
                        # Create wave
                        cursor.execute("""
                            INSERT INTO waves (warehouse_id, wave_name, wave_type, version_id,
                                             total_orders, total_items, efficiency_score,
                                             travel_time_minutes, labor_cost, status)
                            VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, 'planned')
                            RETURNING id
                        """, (
                            wave_name,
                            version_type,
                            version_id,
                            total_orders,
                            total_items,
                            round(random.uniform(75, 95), 2),  # Efficiency score
                            round(total_work_time * 0.1, 2),  # Travel time estimate
                            round(labor_cost, 2)
                        ))
                        wave_id_row = cursor.fetchone()
                        if wave_id_row is None:
                            logger.warning(f"Wave insert failed for wave_name={wave_name}")
                            continue
                        wave_id = wave_id_row[0]
                        
                        # Create wave assignments with pick order
                        for seq_num, (order_id, deadline, priority) in enumerate(wave_orders, 1):
                            # Calculate pick sequence based on zone efficiency
                            cursor.execute("""
                                SELECT DISTINCT s.zone, COUNT(*) as zone_count
                                FROM order_items oi
                                JOIN skus s ON oi.sku_id = s.id
                                WHERE oi.order_id = %s
                                GROUP BY s.zone
                                ORDER BY s.zone
                            """, (order_id,))
                            zones = cursor.fetchall()
                            
                            # Simple pick sequence: A -> B -> C
                            pick_sequence = []
                            for zone, count in zones:
                                if zone == 'A':
                                    pick_sequence.extend(['A'] * count)
                                elif zone == 'B':
                                    pick_sequence.extend(['B'] * count)
                                elif zone == 'C':
                                    pick_sequence.extend(['C'] * count)
                            
                            # Create assignment
                            cursor.execute("""
                                INSERT INTO wave_assignments (wave_id, order_id, stage, sequence_order,
                                                           planned_duration_minutes, external_assignment_id)
                                VALUES (%s, %s, 'pick', %s, %s, %s)
                            """, (
                                wave_id,
                                order_id,
                                seq_num,
                                round(total_work_time / len(wave_orders), 2),
                                f'EXT_ASSIGN_{wave_id}_{order_id}'
                            ))
                    
                    wave_counter += 1
                    start_idx = end_idx
            
            conn.commit()
            logger.info(f"Created {wave_counter - 1} waves with assignments")
    
    def create_performance_metrics(self):
        """Create performance metrics for wave comparison."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Creating performance metrics...")
            
            # Get all waves
            cursor.execute("""
                SELECT id, wave_name, total_orders, total_items, labor_cost, efficiency_score
                FROM waves
                ORDER BY wave_name
            """)
            waves = cursor.fetchall()
            
            for wave_id, wave_name, total_orders, total_items, labor_cost, efficiency in waves:
                # Create various performance metrics
                metrics = [
                    ('efficiency', efficiency),
                    ('labor_cost', labor_cost),
                    ('orders_per_hour', round(total_orders / 8, 2)),  # Assuming 8-hour shift
                    ('items_per_hour', round(total_items / 8, 2)),
                    ('cost_per_order', round(labor_cost / total_orders, 2) if total_orders > 0 else 0),
                    ('on_time_delivery', round(random.uniform(85, 98), 2))
                ]
                
                for metric_type, metric_value in metrics:
                    cursor.execute("""
                        INSERT INTO performance_metrics (wave_id, metric_type, metric_value, source_id)
                        VALUES (%s, %s, %s, 1)
                    """, (wave_id, metric_type, metric_value))
            
            conn.commit()
            logger.info("Created performance metrics")
    
    def create_daily_deadline_update_script(self):
        """Create SQL script to update order deadlines daily."""
        script_content = """
-- Daily Deadline Update Script
-- Run this script daily to keep order deadlines in the future

UPDATE orders 
SET shipping_deadline = shipping_deadline + INTERVAL '1 day'
WHERE warehouse_id = 1 
  AND status = 'pending' 
  AND shipping_deadline < CURRENT_TIMESTAMP + INTERVAL '1 day';

-- Log the update
INSERT INTO data_imports (source_id, import_type, import_status, records_processed, import_metadata)
VALUES (1, 'deadline_update', 'completed', 
        (SELECT COUNT(*) FROM orders WHERE warehouse_id = 1 AND status = 'pending'),
        '{"update_type": "daily_deadline_shift", "shift_days": 1}');
"""
        
        with open('database/daily_deadline_update.sql', 'w') as f:
            f.write(script_content)
        
        logger.info("Created daily deadline update script: database/daily_deadline_update.sql")
    
    def generate_all_data(self):
        """Generate all demo data."""
        logger.info("Starting enhanced demo data generation...")
        
        try:
            # Create enhanced SKUs
            self.create_enhanced_skus()
            
            # Create enhanced orders
            self.create_enhanced_orders()
            
            # Create wave plan versions
            original_version_id, optimized_version_id = self.create_wave_plan_versions()
            
            # Only proceed if both version IDs are valid
            if original_version_id is not None and optimized_version_id is not None:
                # Create waves and assignments
                self.create_waves_and_assignments(original_version_id, optimized_version_id)
            else:
                logger.error("Wave plan version creation failed. Skipping wave/assignment generation.")
                return
            
            # Create performance metrics
            self.create_performance_metrics()
            
            # Create daily update script
            self.create_daily_deadline_update_script()
            
            logger.info("Enhanced demo data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error generating demo data: {e}")
            raise

    def clear_waves_and_assignments(self):
        """Delete all waves and wave assignments from the database."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM wave_assignments;")
            cursor.execute("DELETE FROM waves;")
            conn.commit()
            logger.info("Cleared all waves and wave assignments.")

    def create_16_new_waves(self):
        """Create 16 new waves (4 per day for the next 4 days) and assign orders evenly."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get all order IDs, sorted by deadline
            cursor.execute("SELECT id FROM orders WHERE warehouse_id = 1 AND status = 'pending' ORDER BY shipping_deadline, priority")
            order_ids = [row[0] for row in cursor.fetchall()]
            total_orders = len(order_ids)
            num_waves = 16
            orders_per_wave = total_orders // num_waves
            remainder = total_orders % num_waves
            
            start_date = datetime.now() + timedelta(days=1)
            wave_counter = 1
            start_idx = 0
            for day in range(4):
                for wave_num in range(4):
                    wave_size = orders_per_wave + (1 if (wave_counter-1) < remainder else 0)
                    end_idx = start_idx + wave_size
                    wave_orders = order_ids[start_idx:end_idx]
                    planned_start_time = (start_date + timedelta(days=day)).replace(hour=8+wave_num*2, minute=0, second=0, microsecond=0)
                    
                    # Generate wave name with date and wave type
                    date_str = planned_start_time.strftime("%B %-d")
                    if wave_num == 0:
                        wave_type = "Morning Wave 1"
                    elif wave_num == 1:
                        wave_type = "Morning Wave 2"
                    elif wave_num == 2:
                        wave_type = "Afternoon Wave 1"
                    elif wave_num == 3:
                        wave_type = "Afternoon Wave 2"
                    else:
                        wave_type = f"Wave {wave_num + 1}"
                    
                    wave_name = f"{date_str} - {wave_type}"
                    # Insert wave
                    cursor.execute("""
                        INSERT INTO waves (warehouse_id, wave_name, wave_type, planned_start_time, total_orders, status)
                        VALUES (1, %s, 'manual', %s, %s, 'planned') RETURNING id
                    """, (wave_name, planned_start_time, len(wave_orders)))
                    wave_id_row = cursor.fetchone()
                    if wave_id_row is None:
                        logger.warning(f"Wave insert failed for wave_name={wave_name}")
                        continue
                    wave_id = wave_id_row[0]
                    # Assign orders to wave
                    for seq, order_id in enumerate(wave_orders, 1):
                        cursor.execute("""
                            INSERT INTO wave_assignments (wave_id, order_id, stage, sequence_order)
                            VALUES (%s, %s, 'pick', %s)
                        """, (wave_id, order_id, seq))
                    logger.info(f"Created wave {wave_name} with {len(wave_orders)} orders.")
                    wave_counter += 1
                    start_idx = end_idx
            conn.commit()
            logger.info("Created 16 new waves and assignments.")


def main():
    """Main function to run the enhanced demo data generator."""
    generator = EnhancedDemoDataGenerator()
    generator.clear_waves_and_assignments()
    generator.create_16_new_waves()


if __name__ == "__main__":
    main() 