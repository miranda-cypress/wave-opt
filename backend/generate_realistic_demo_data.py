#!/usr/bin/env python3
"""
Generate realistic demo data for warehouse optimization system.

This script creates:
- 5000 SKUs distributed across zones
- 10000 orders with deadlines across 4 days
- 16 waves (4 per day)
- Simple scheduling assignments for baseline comparison
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import random
from datetime import datetime, timedelta
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealisticDataGenerator:
    def __init__(self, db_config=None):
        """Initialize with database connection."""
        if db_config is None:
            # Default connection parameters
            self.db_config = {
                'host': 'localhost',
                'port': 5433,
                'database': 'warehouse_opt',
                'user': 'wave_user',
                'password': 'wave_password'
            }
        else:
            self.db_config = db_config
        
        self.conn = None
        self.cursor = None
    
    def to_pg_array(self, pylist):
        """Convert Python list to PostgreSQL array string."""
        if not pylist:
            return '{}'
        return '{' + ','.join(str(x) for x in pylist) + '}'
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def clear_existing_data(self):
        """Clear existing demo data."""
        logger.info("Clearing existing demo data...")
        
        # Clear in reverse dependency order
        self.cursor.execute("DELETE FROM wave_assignments")
        self.cursor.execute("DELETE FROM waves")
        self.cursor.execute("DELETE FROM order_items")
        self.cursor.execute("DELETE FROM orders")
        self.cursor.execute("DELETE FROM customers")
        self.cursor.execute("DELETE FROM skus WHERE id > 15")  # Keep original SKUs
        self.cursor.execute("DELETE FROM bins WHERE id > 50")  # Keep original bins
        
        self.conn.commit()
        logger.info("Existing demo data cleared")
    
    def generate_skus(self, target_count=5000):
        """Generate additional SKUs to reach target count."""
        logger.info(f"Generating SKUs to reach {target_count} total...")
        
        # Get current SKU count
        self.cursor.execute("SELECT COUNT(*) as count FROM skus")
        current_count = self.cursor.fetchone()['count']
        
        if current_count >= target_count:
            logger.info(f"Already have {current_count} SKUs, no need to generate more")
            return
        
        # Get existing zones
        self.cursor.execute("SELECT DISTINCT zone FROM skus")
        zones = [row['zone'] for row in self.cursor.fetchall()]
        
        # Generate new SKUs
        skus_to_add = target_count - current_count
        new_skus = []
        
        for i in range(skus_to_add):
            sku_id = current_count + i + 1
            zone = random.choice(zones)
            weight = random.uniform(0.1, 110.0)  # 0.1 to 110 lbs
            volume = random.uniform(0.001, 18.0)  # 0.001 to 18 cubic feet
            pick_time = random.uniform(0.5, 3.0)  # 0.5 to 3 minutes
            
            new_skus.append({
                'id': sku_id,
                'sku_code': f'SKU{sku_id:06d}',
                'name': f'Product {sku_id}',
                'zone': zone,
                'weight_lbs': round(weight, 2),
                'volume_cubic_feet': round(volume, 3),
                'pick_time_minutes': round(pick_time, 1),
                'warehouse_id': 1
            })
        
        # Insert new SKUs in batches
        batch_size = 1000
        for i in range(0, len(new_skus), batch_size):
            batch = new_skus[i:i + batch_size]
            values = [(sku['id'], sku['sku_code'], sku['name'], sku['zone'], 
                      sku['weight_lbs'], sku['volume_cubic_feet'], 
                      sku['pick_time_minutes'], sku['warehouse_id']) for sku in batch]
            
            self.cursor.executemany("""
                INSERT INTO skus (id, sku_code, name, zone, weight_lbs, 
                                volume_cubic_feet, pick_time_minutes, warehouse_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, values)
        
        self.conn.commit()
        logger.info(f"Generated {len(new_skus)} new SKUs")
    
    def generate_customers(self, target_count=6000):
        """Generate realistic customer names."""
        logger.info(f"Generating {target_count} customers...")
        
        # Clear existing customers
        self.cursor.execute("DELETE FROM customers")
        
        # Realistic company name components
        prefixes = ['Global', 'Premier', 'Elite', 'Advanced', 'Innovative', 'Strategic', 'Dynamic', 'Progressive', 'Excellence', 'Quality']
        industries = ['Tech', 'Solutions', 'Systems', 'Services', 'Industries', 'Corporation', 'Enterprises', 'Partners', 'Group', 'International']
        suffixes = ['Inc', 'LLC', 'Corp', 'Ltd', 'Co', 'Company', 'Associates', 'Partners', 'Group', 'Enterprises']
        
        # Generate customer names
        customers = []
        for i in range(target_count):
            customer_id = i + 1
            
            # Generate realistic company name
            if random.random() < 0.7:  # 70% chance of prefix + industry + suffix
                name = f"{random.choice(prefixes)} {random.choice(industries)} {random.choice(suffixes)}"
            elif random.random() < 0.5:  # 15% chance of industry + suffix
                name = f"{random.choice(industries)} {random.choice(suffixes)}"
            else:  # 15% chance of simple name
                name = f"Customer {customer_id}"
            
            customers.append({
                'id': customer_id,
                'warehouse_id': 1,
                'customer_code': f'CUST{customer_id:06d}',
                'name': name,
                'customer_type': 'b2b',
                'priority_level': random.randint(1, 5),
                'service_level': 'standard'
            })
        
        # Insert customers
        values = [(customer['id'], customer['warehouse_id'], customer['customer_code'], 
                  customer['name'], customer['customer_type'], customer['priority_level'], 
                  customer['service_level']) for customer in customers]
        
        self.cursor.executemany("""
            INSERT INTO customers (id, warehouse_id, customer_code, name, customer_type, priority_level, service_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)
        
        self.conn.commit()
        logger.info(f"Generated {len(customers)} customers")
        return customers

    def generate_orders(self, target_count=10000):
        """Generate orders with deadlines across next 4 days."""
        logger.info(f"Generating {target_count} orders...")
        
        # Clear existing orders
        self.cursor.execute("DELETE FROM order_items")
        self.cursor.execute("DELETE FROM orders")
        
        # Get customer IDs
        self.cursor.execute("SELECT id FROM customers")
        customer_ids = [row['id'] for row in self.cursor.fetchall()]
        
        # Generate deadlines across next 4 days
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        deadlines = []
        
        for day in range(4):
            for hour in range(8, 20):  # 8 AM to 8 PM
                for minute in [0, 30]:  # Every 30 minutes
                    deadline = tomorrow + timedelta(days=day, hours=hour, minutes=minute)
                    deadlines.append(deadline)
        
        # Distribute orders across deadlines
        orders = []
        start_order_number = 376892
        for i in range(target_count):
            order_id = i + 1
            shipping_deadline = random.choice(deadlines)
            customer_id = random.choice(customer_ids)
            priority = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]  # 1=low, 2=medium, 3=high
            order_number = f'ORD{start_order_number + i:08d}'
            order_date = datetime.now()
            
            orders.append({
                'id': order_id,
                'customer_id': customer_id,
                'shipping_deadline': shipping_deadline,
                'priority': priority,
                'warehouse_id': 1,
                'status': 'pending',
                'order_number': order_number,
                'order_date': order_date
            })
        
        # Insert orders
        values = [(order['id'], order['customer_id'], order['shipping_deadline'], 
                  order['priority'], order['warehouse_id'], order['status'], 
                  order['order_number'], order['order_date']) for order in orders]
        
        self.cursor.executemany("""
            INSERT INTO orders (id, customer_id, shipping_deadline, priority, warehouse_id, status, order_number, order_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, values)
        
        self.conn.commit()
        logger.info(f"Generated {len(orders)} orders")
        
        # Generate order items
        self.generate_order_items()
    
    def generate_order_items(self):
        """Generate order items for all orders."""
        logger.info("Generating order items...")
        
        # Get all SKUs
        self.cursor.execute("SELECT id FROM skus")
        sku_ids = [row['id'] for row in self.cursor.fetchall()]
        
        # Get all orders
        self.cursor.execute("SELECT id FROM orders")
        order_ids = [row['id'] for row in self.cursor.fetchall()]
        
        order_items = []
        item_id = 1
        
        for order_id in order_ids:
            # Each order has 1-12 items
            num_items = random.randint(1, 12)
            
            for _ in range(num_items):
                sku_id = random.choice(sku_ids)
                quantity = random.randint(1, 10)
                
                order_items.append({
                    'id': item_id,
                    'order_id': order_id,
                    'sku_id': sku_id,
                    'quantity': quantity
                })
                item_id += 1
        
        # Insert order items in batches
        batch_size = 1000
        for i in range(0, len(order_items), batch_size):
            batch = order_items[i:i + batch_size]
            values = [(item['id'], item['order_id'], item['sku_id'], item['quantity']) 
                     for item in batch]
            
            self.cursor.executemany("""
                INSERT INTO order_items (id, order_id, sku_id, quantity)
                VALUES (%s, %s, %s, %s)
            """, values)
        
        self.conn.commit()
        logger.info(f"Generated {len(order_items)} order items")
    
    def generate_waves(self):
        """Generate 16 waves (4 per day for 4 days)."""
        logger.info("Generating 16 waves...")
        
        # Clear existing waves
        self.cursor.execute("DELETE FROM wave_assignments")
        self.cursor.execute("DELETE FROM waves")
        
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        waves = []
        
        # Cross-platform date formatting helper
        def format_date(dt):
            if sys.platform == "win32":
                return dt.strftime("%B %#d")
            else:
                return dt.strftime("%B %-d")
        
        for day in range(4):
            for wave_num in range(4):
                wave_id = day * 4 + wave_num + 1
                
                # Wave start times: 8AM, 10AM, 1PM, 3PM
                start_hours = [8, 10, 13, 15]
                start_time = tomorrow + timedelta(days=day, hours=start_hours[wave_num])
                completion_time = start_time + timedelta(hours=2)  # 2-hour waves
                
                # Generate wave name with date and wave type
                date_str = format_date(start_time)
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
                
                waves.append({
                    'id': wave_id,
                    'warehouse_id': 1,
                    'wave_name': wave_name,
                    'wave_type': 'manual',
                    'planned_start_time': start_time,
                    'actual_start_time': None,
                    'planned_completion_time': completion_time,
                    'actual_completion_time': None,
                    'total_orders': 0,  # Will be updated after assignment
                    'assigned_workers': [],  # Will be populated
                    'labor_cost': 0,  # Will be calculated
                    'status': 'planned',
                    'external_wave_id': f'EXT_WAVE_{wave_id:03d}',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
        
        # Insert waves
        values = [(
            wave['id'], wave['warehouse_id'], wave['wave_name'], wave['wave_type'],
            wave['planned_start_time'], wave['actual_start_time'],
            wave['planned_completion_time'], wave['actual_completion_time'],
            wave['total_orders'], self.to_pg_array(wave['assigned_workers']),
            wave['labor_cost'], wave['status'], wave['external_wave_id'],
            wave['created_at'], wave['updated_at']
        ) for wave in waves]
        self.cursor.executemany("""
            INSERT INTO waves (
                id, warehouse_id, wave_name, wave_type,
                planned_start_time, actual_start_time, planned_completion_time,
                actual_completion_time, total_orders, assigned_workers,
                labor_cost, status, external_wave_id,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)
        
        self.conn.commit()
        logger.info(f"Generated {len(waves)} waves")
        
        return waves
    
    def assign_orders_to_waves(self):
        """Assign orders to waves based on deadlines."""
        logger.info("Assigning orders to waves...")
        
        # Get all orders sorted by deadline
        self.cursor.execute("""
            SELECT id, shipping_deadline FROM orders 
            ORDER BY shipping_deadline
        """)
        orders = self.cursor.fetchall()
        
        # Get all waves
        self.cursor.execute("SELECT id, planned_start_time, planned_completion_time FROM waves ORDER BY planned_start_time")
        waves = self.cursor.fetchall()
        
        # Assign orders to waves (500-700 per wave)
        orders_per_wave = len(orders) // len(waves)
        min_orders = 500
        max_orders = 700
        
        wave_assignments = []
        order_idx = 0
        
        for wave in waves:
            # Determine number of orders for this wave
            num_orders = random.randint(min_orders, max_orders)
            if order_idx + num_orders > len(orders):
                num_orders = len(orders) - order_idx
            
            if num_orders <= 0:
                break
            
            # Assign orders to this wave
            for i in range(num_orders):
                if order_idx >= len(orders):
                    break
                
                order = orders[order_idx]
                wave_assignments.append({
                    'wave_id': wave['id'],
                    'order_id': order['id'],
                    'source_id': 1,  # WMS source
                    'stage': 'pick'  # Initial stage, can be changed later
                })
                order_idx += 1
        
        # Insert wave assignments
        values = [(assignment['wave_id'], assignment['order_id'], assignment['source_id'], assignment['stage']) 
                 for assignment in wave_assignments]
        
        self.cursor.executemany("""
            INSERT INTO wave_assignments (wave_id, order_id, source_id, stage)
            VALUES (%s, %s, %s, %s)
        """, values)
        
        self.conn.commit()
        logger.info(f"Assigned {len(wave_assignments)} orders to waves")
    
    def apply_simple_scheduling(self):
        """Apply simple scheduling heuristics to create baseline assignments."""
        logger.info("Applying simple scheduling heuristics...")
        
        # Get all waves
        self.cursor.execute("SELECT id, planned_start_time, planned_completion_time FROM waves ORDER BY id")
        waves = self.cursor.fetchall()
        
        # Get workers
        self.cursor.execute("SELECT id, hourly_rate FROM workers")
        workers = self.cursor.fetchall()
        
        if not workers:
            logger.warning("No workers found, creating default workers")
            self.create_default_workers()
            self.cursor.execute("SELECT id, hourly_rate FROM workers")
            workers = self.cursor.fetchall()
        
        for wave in waves:
            self.schedule_wave_simple(wave, workers)
    
    def create_default_workers(self):
        """Create default workers if none exist."""
        workers = []
        for i in range(10):  # 10 workers
            worker_id = i + 1
            workers.append({
                'id': worker_id,
                'worker_code': f'W{worker_id:03d}',
                'name': f'Worker {worker_id}',
                'hourly_rate': random.uniform(20, 35),
                'max_hours_per_day': 8,
                'skills': ['pick', 'pack'],
                'warehouse_id': 1
            })
        
        values = [(w['id'], w['worker_code'], w['name'], w['hourly_rate'],
                  w['max_hours_per_day'], w['skills'], w['warehouse_id']) for w in workers]
        
        self.cursor.executemany("""
            INSERT INTO workers (id, worker_code, name, hourly_rate, max_hours_per_day, skills, warehouse_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)
        
        self.conn.commit()
        logger.info(f"Created {len(workers)} default workers")
    
    def schedule_wave_simple(self, wave, workers):
        """Apply simple scheduling to a single wave."""
        logger.info(f"Scheduling wave {wave['id']}...")
        
        # Get orders in this wave
        self.cursor.execute("""
            SELECT wa.order_id, o.shipping_deadline
            FROM wave_assignments wa
            JOIN orders o ON wa.order_id = o.id
            WHERE wa.wave_id = %s
            ORDER BY o.shipping_deadline
        """, (wave['id'],))
        
        wave_orders = self.cursor.fetchall()
        
        if not wave_orders:
            logger.warning(f"No orders found for wave {wave['id']}")
            return
        
        # Simple scheduling: assign orders to workers round-robin
        # Calculate estimated duration per order (5-15 minutes)
        base_duration = 10  # minutes per order
        current_time = wave['planned_start_time']
        
        # Assign workers to orders
        assignments = []
        worker_idx = 0
        
        for i, order in enumerate(wave_orders):
            worker = workers[worker_idx % len(workers)]
            
            # Calculate order duration based on items
            self.cursor.execute("""
                SELECT COUNT(*) as item_count, SUM(oi.quantity * s.pick_time_minutes) as total_pick_time
                FROM order_items oi
                JOIN skus s ON oi.sku_id = s.id
                WHERE oi.order_id = %s
            """, (order['order_id'],))
            
            result = self.cursor.fetchone()
            item_count = result['item_count'] or 1
            total_pick_time = float(result['total_pick_time'] or base_duration)
            
            # Add some buffer time
            duration = max(total_pick_time * 1.2, float(base_duration))
            
            assignments.append({
                'wave_id': wave['id'],
                'order_id': order['order_id'],
                'assigned_worker_id': worker['id'],
                'planned_start_time': current_time,
                'planned_duration_minutes': int(duration),
                'stage': 'pick',
                'sequence_order': i + 1
            })
            
            # Move to next worker
            worker_idx += 1
            
            # Advance time (simple: just add duration)
            current_time += timedelta(minutes=duration)
        
        # Insert assignments
        values = [(a['wave_id'], a['order_id'], a['assigned_worker_id'],
                  a['planned_start_time'], a['planned_duration_minutes'],
                  a['stage'], a['sequence_order']) for a in assignments]
        
        self.cursor.executemany("""
            UPDATE wave_assignments 
            SET assigned_worker_id = %s, planned_start_time = %s, 
                planned_duration_minutes = %s, stage = %s, sequence_order = %s
            WHERE wave_id = %s AND order_id = %s
        """, [(a['assigned_worker_id'], a['planned_start_time'], a['planned_duration_minutes'],
               a['stage'], a['sequence_order'], a['wave_id'], a['order_id']) for a in assignments])
        
        # Update wave with order count and worker codes
        self.cursor.execute("""
            SELECT COUNT(DISTINCT order_id) as count FROM wave_assignments WHERE wave_id = %s
        """, (wave['id'],))
        unique_orders = self.cursor.fetchone()['count']
        unique_worker_ids = list(set(a['assigned_worker_id'] for a in assignments))
        # Fetch worker codes for these IDs
        if unique_worker_ids:
            format_strings = ','.join(['%s'] * len(unique_worker_ids))
            self.cursor.execute(f"SELECT worker_code FROM workers WHERE id IN ({format_strings})", tuple(unique_worker_ids))
            worker_codes = [row['worker_code'] for row in self.cursor.fetchall()]
        else:
            worker_codes = []
        total_labor_cost = sum(a['planned_duration_minutes'] / 60 * 25 for a in assignments)  # $25/hour
        
        self.cursor.execute("""
            UPDATE waves 
            SET total_orders = %s, assigned_workers = %s, labor_cost = %s
            WHERE id = %s
        """, (unique_orders, self.to_pg_array(worker_codes), total_labor_cost, wave['id']))
        
        self.conn.commit()
        logger.info(f"Scheduled {unique_orders} unique orders for wave {wave['id']} with {len(worker_codes)} workers")
    
    def generate_daily_update_script(self):
        """Generate SQL script to update deadlines daily."""
        script_content = """
-- Daily deadline update script
-- Run this script daily to keep order deadlines in the future

UPDATE orders 
SET shipping_deadline = shipping_deadline + INTERVAL '1 day'
WHERE shipping_deadline < NOW() + INTERVAL '1 day';

-- Optional: Add some randomness to deadlines within the day
UPDATE orders 
SET shipping_deadline = shipping_deadline + (RANDOM() * INTERVAL '12 hours')
WHERE shipping_deadline::date = CURRENT_DATE + INTERVAL '1 day';
"""
        
        with open('daily_deadline_update.sql', 'w') as f:
            f.write(script_content)
        
        logger.info("Generated daily_deadline_update.sql script")
    
    def run_full_generation(self):
        """Run the complete data generation process."""
        try:
            self.connect()
            
            logger.info("Starting realistic demo data generation...")
            
            # Clear existing data
            self.clear_existing_data()
            
            # Generate data in order
            self.generate_skus(5000)
            self.generate_customers(6000)
            self.generate_orders(10000)
            self.generate_waves()
            self.assign_orders_to_waves()
            self.apply_simple_scheduling()
            self.generate_daily_update_script()
            
            logger.info("Realistic demo data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during data generation: {e}")
            raise
        finally:
            self.close()


if __name__ == "__main__":
    generator = RealisticDataGenerator()
    generator.run_full_generation() 