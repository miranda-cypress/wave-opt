#!/usr/bin/env python3
"""
Synthetic Data Generator for AI Wave Optimization Demo
MidWest Distribution Co. - Complete Dataset Generation
"""

import json
import random
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class MidWestDistributionDataGenerator:
    """Generate comprehensive synthetic data for MidWest Distribution Co demo."""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        
    def connect(self):
        """Connect to PostgreSQL database."""
        self.conn = psycopg2.connect(**self.db_config)
        return self.conn
    
    def generate_complete_dataset(self):
        """Generate complete MidWest Distribution Co dataset."""
        print("🚀 Generating MidWest Distribution Co. Complete Dataset...")
        
        # Generate core data
        self.generate_products()
        self.generate_workers()
        self.generate_equipment()
        self.generate_orders()
        self.generate_waves()
        self.generate_performance_metrics()
        
        print("✅ Complete dataset generated successfully!")
    
    def generate_products(self):
        """Generate 250 products with realistic attributes."""
        print("📦 Generating product catalog...")
        
        # Product categories and names
        categories = {
            'electronics': ['Laptop', 'Tablet', 'Phone', 'Monitor', 'Keyboard', 'Mouse', 'Speaker', 'Headphones'],
            'clothing': ['T-Shirt', 'Jeans', 'Sweater', 'Jacket', 'Shoes', 'Hat', 'Socks', 'Belt'],
            'home': ['Lamp', 'Chair', 'Table', 'Bed', 'Sofa', 'Mirror', 'Rug', 'Curtain'],
            'sports': ['Basketball', 'Soccer Ball', 'Tennis Racket', 'Golf Club', 'Bike', 'Helmet', 'Gloves'],
            'books': ['Novel', 'Textbook', 'Magazine', 'Journal', 'Manual', 'Guide', 'Dictionary'],
            'food': ['Cereal', 'Snacks', 'Beverages', 'Candy', 'Nuts', 'Chips', 'Cookies']
        }
        
        # Velocity classes with distribution
        velocity_distribution = {'A': 0.2, 'B': 0.3, 'C': 0.5}  # 20% A, 30% B, 50% C
        
        products = []
        for i in range(250):
            category = random.choice(list(categories.keys()))
            base_name = random.choice(categories[category])
            sku = f"{category[:3].upper()}{i+1:03d}"
            
            # Determine velocity class
            velocity_class = np.random.choice(['A', 'B', 'C'], p=[0.2, 0.3, 0.5])
            
            # Generate realistic attributes based on velocity class
            if velocity_class == 'A':
                avg_daily_demand = random.uniform(50, 200)
                pick_complexity = random.randint(1, 2)
                unit_cost = random.uniform(10, 100)
            elif velocity_class == 'B':
                avg_daily_demand = random.uniform(10, 50)
                pick_complexity = random.randint(2, 4)
                unit_cost = random.uniform(5, 50)
            else:  # C items
                avg_daily_demand = random.uniform(1, 10)
                pick_complexity = random.randint(3, 5)
                unit_cost = random.uniform(1, 25)
            
            # Zone assignment based on velocity
            if velocity_class == 'A':
                primary_zone_id = 2  # Zone A - Fast Movers
            elif velocity_class == 'B':
                primary_zone_id = 3  # Zone B - Medium Movers
            else:
                primary_zone_id = 4  # Zone C - Slow Movers
            
            product = {
                'sku': sku,
                'name': f"{base_name} {random.choice(['Pro', 'Elite', 'Basic', 'Premium', 'Standard'])}",
                'description': f"High-quality {base_name.lower()} for {category} category",
                'velocity_class': velocity_class,
                'weight_lbs': round(random.uniform(0.1, 50), 2),
                'length_in': round(random.uniform(1, 24), 1),
                'width_in': round(random.uniform(1, 18), 1),
                'height_in': round(random.uniform(1, 12), 1),
                'primary_zone_id': primary_zone_id,
                'pick_complexity': pick_complexity,
                'handling_requirements': random.sample(['fragile', 'hazmat', 'refrigerated'], random.randint(0, 1)),
                'unit_cost': round(unit_cost, 2),
                'avg_daily_demand': round(avg_daily_demand, 2)
            }
            products.append(product)
        
        # Insert products
        cursor = self.conn.cursor()
        for product in products:
            cursor.execute("""
                INSERT INTO products (sku, name, description, velocity_class, weight_lbs, 
                                    length_in, width_in, height_in, primary_zone_id, 
                                    pick_complexity, handling_requirements, unit_cost, avg_daily_demand)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (product['sku'], product['name'], product['description'], product['velocity_class'],
                  product['weight_lbs'], product['length_in'], product['width_in'], product['height_in'],
                  product['primary_zone_id'], product['pick_complexity'], product['handling_requirements'],
                  product['unit_cost'], product['avg_daily_demand']))
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Generated {len(products)} products")
    
    def generate_workers(self):
        """Generate 15 multi-skilled workers."""
        print("👥 Generating worker profiles...")
        
        worker_names = [
            "Sarah Johnson", "Mike Chen", "Lisa Rodriguez", "David Thompson", "Emma Wilson",
            "James Brown", "Maria Garcia", "Robert Davis", "Jennifer Lee", "Christopher Miller",
            "Amanda Taylor", "Daniel Anderson", "Jessica Martinez", "Kevin White", "Nicole Clark"
        ]
        
        # Skill combinations
        skill_combinations = [
            ['picking', 'packing'],
            ['picking', 'receiving'],
            ['packing', 'shipping'],
            ['picking', 'packing', 'shipping'],
            ['receiving', 'inventory'],
            ['picking', 'inventory'],
            ['packing', 'inventory'],
            ['shipping', 'inventory'],
            ['picking', 'packing', 'receiving'],
            ['packing', 'shipping', 'inventory'],
            ['picking', 'receiving', 'inventory'],
            ['picking', 'packing', 'shipping', 'inventory'],
            ['receiving', 'shipping'],
            ['picking', 'shipping'],
            ['packing', 'receiving']
        ]
        
        workers = []
        for i, name in enumerate(worker_names):
            worker_id = f"W{i+1:02d}"
            skills = skill_combinations[i]
            experience_years = random.randint(1, 15)
            
            # Performance rates based on experience
            base_pick_rate = 60 + (experience_years * 2) + random.randint(-10, 10)
            base_pack_rate = 20 + (experience_years * 1.5) + random.randint(-5, 5)
            
            # Hourly rate based on experience and skills
            base_rate = 15 + (experience_years * 1.2) + (len(skills) * 0.5)
            
            worker = {
                'id': worker_id,
                'name': name,
                'skills': skills,
                'experience_years': experience_years,
                'hourly_rate': round(base_rate, 2),
                'pick_rate_items_per_hour': max(30, base_pick_rate),
                'pack_rate_orders_per_hour': max(10, base_pack_rate),
                'max_hours_per_day': 8.0,
                'shift': random.choice(['first', 'second', 'third']),
                'is_cross_trained': len(skills) > 2,
                'active': True
            }
            workers.append(worker)
        
        # Insert workers
        cursor = self.conn.cursor()
        for worker in workers:
            cursor.execute("""
                INSERT INTO workers (id, name, skills, experience_years, hourly_rate,
                                   pick_rate_items_per_hour, pack_rate_orders_per_hour,
                                   max_hours_per_day, shift, is_cross_trained, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (worker['id'], worker['name'], worker['skills'], worker['experience_years'],
                  worker['hourly_rate'], worker['pick_rate_items_per_hour'], worker['pack_rate_orders_per_hour'],
                  worker['max_hours_per_day'], worker['shift'], worker['is_cross_trained'], worker['active']))
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Generated {len(workers)} workers")
    
    def generate_equipment(self):
        """Generate equipment with capacity constraints."""
        print("🔧 Generating equipment inventory...")
        
        equipment_data = [
            # Packing stations
            {'name': 'Packing Station 1', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            {'name': 'Packing Station 2', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            {'name': 'Packing Station 3', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            {'name': 'Packing Station 4', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            {'name': 'Packing Station 5', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            {'name': 'Packing Station 6', 'equipment_type': 'packing_station', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 5.0, 'required_skills': ['packing']},
            
            # Dock doors
            {'name': 'Dock Door 1', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 2', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 3', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 4', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 5', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 6', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 7', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            {'name': 'Dock Door 8', 'equipment_type': 'dock_door', 'zone_id': 6, 'capacity': 1, 'hourly_cost': 2.0, 'required_skills': ['shipping']},
            
            # Forklifts
            {'name': 'Forklift 1', 'equipment_type': 'forklift', 'zone_id': 1, 'capacity': 1, 'hourly_cost': 8.0, 'required_skills': ['receiving', 'shipping']},
            {'name': 'Forklift 2', 'equipment_type': 'forklift', 'zone_id': 1, 'capacity': 1, 'hourly_cost': 8.0, 'required_skills': ['receiving', 'shipping']},
            
            # Scanners
            {'name': 'Scanner 1', 'equipment_type': 'scanner', 'zone_id': 2, 'capacity': 1, 'hourly_cost': 1.0, 'required_skills': ['picking', 'packing']},
            {'name': 'Scanner 2', 'equipment_type': 'scanner', 'zone_id': 3, 'capacity': 1, 'hourly_cost': 1.0, 'required_skills': ['picking', 'packing']},
            {'name': 'Scanner 3', 'equipment_type': 'scanner', 'zone_id': 4, 'capacity': 1, 'hourly_cost': 1.0, 'required_skills': ['picking', 'packing']},
            {'name': 'Scanner 4', 'equipment_type': 'scanner', 'zone_id': 5, 'capacity': 1, 'hourly_cost': 1.0, 'required_skills': ['picking', 'packing']},
        ]
        
        # Insert equipment
        cursor = self.conn.cursor()
        for equipment in equipment_data:
            cursor.execute("""
                INSERT INTO equipment (name, equipment_type, zone_id, capacity, hourly_cost, required_skills, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (equipment['name'], equipment['equipment_type'], equipment['zone_id'],
                  equipment['capacity'], equipment['hourly_cost'], equipment['required_skills'], True))
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Generated {len(equipment_data)} equipment items")
    
    def generate_orders(self):
        """Generate 2500 orders with realistic patterns."""
        print("📋 Generating order history...")
        
        # Customer types and patterns
        customer_types = ['b2b', 'b2c']
        order_types = ['standard', 'rush', 'expedited']
        
        # Generate orders over the last 30 days
        start_date = datetime.now() - timedelta(days=30)
        
        orders = []
        for i in range(2500):
            order_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(6, 22),  # Operating hours
                minutes=random.randint(0, 59)
            )
            
            # Order characteristics
            customer_type = random.choice(customer_types)
            order_type = random.choice(order_types)
            
            # Priority based on order type
            if order_type == 'rush':
                priority = random.choice([1, 2])
            elif order_type == 'expedited':
                priority = random.choice([2, 3])
            else:
                priority = random.choice([3, 4, 5])
            
            # Shipping deadline based on priority and order type
            if priority == 1:  # Rush
                deadline_hours = random.randint(2, 6)
            elif priority == 2:  # Expedited
                deadline_hours = random.randint(6, 24)
            else:  # Standard
                deadline_hours = random.randint(24, 72)
            
            shipping_deadline = order_date + timedelta(hours=deadline_hours)
            
            # Generate order items
            num_items = random.randint(1, 8)
            total_items = 0
            total_weight = 0.0
            
            order = {
                'id': f"ORD{order_date.strftime('%Y%m%d')}{i+1:04d}",
                'order_date': order_date,
                'customer_id': f"CUST{random.randint(1, 120):03d}",
                'customer_type': customer_type,
                'order_type': order_type,
                'priority': priority,
                'shipping_deadline': shipping_deadline,
                'total_items': total_items,
                'total_weight': total_weight,
                'status': 'pending'
            }
            orders.append(order)
        
        # Insert orders
        cursor = self.conn.cursor()
        for order in orders:
            cursor.execute("""
                INSERT INTO orders (id, order_date, customer_id, customer_type, order_type,
                                  priority, shipping_deadline, total_items, total_weight, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (order['id'], order['order_date'], order['customer_id'], order['customer_type'],
                  order['order_type'], order['priority'], order['shipping_deadline'],
                  order['total_items'], order['total_weight'], order['status']))
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Generated {len(orders)} orders")
        
        # Generate order items
        self.generate_order_items()
    
    def generate_order_items(self):
        """Generate order line items."""
        print("📦 Generating order line items...")
        
        cursor = self.conn.cursor()
        
        # Get all orders and products
        cursor.execute("SELECT id FROM orders")
        order_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT sku, weight_lbs FROM products")
        products = cursor.fetchall()
        
        order_items = []
        for order_id in order_ids:
            # 1-8 items per order
            num_items = random.randint(1, 8)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for i, (sku, weight) in enumerate(selected_products):
                quantity = random.randint(1, 5)
                order_items.append({
                    'order_id': order_id,
                    'sku': sku,
                    'quantity': quantity,
                    'line_priority': i + 1
                })
        
        # Insert order items
        for item in order_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, sku, quantity, line_priority)
                VALUES (%s, %s, %s, %s)
            """, (item['order_id'], item['sku'], item['quantity'], item['line_priority']))
        
        # Update order totals
        cursor.execute("""
            UPDATE orders 
            SET total_items = (
                SELECT SUM(oi.quantity) 
                FROM order_items oi 
                WHERE oi.order_id = orders.id
            ),
            total_weight = (
                SELECT SUM(oi.quantity * p.weight_lbs) 
                FROM order_items oi 
                JOIN products p ON oi.sku = p.sku 
                WHERE oi.order_id = orders.id
            )
        """)
        
        self.conn.commit()
        cursor.close()
        print(f"✅ Generated {len(order_items)} order items")
    
    def generate_waves(self):
        """Generate wave planning data."""
        print("🌊 Generating wave planning data...")
        
        # Generate some baseline (inefficient) waves
        cursor = self.conn.cursor()
        
        # Get recent orders
        cursor.execute("SELECT id FROM orders WHERE status = 'pending' ORDER BY order_date DESC LIMIT 100")
        recent_orders = [row[0] for row in cursor.fetchall()]
        
        # Create baseline waves
        baseline_waves = [
            {
                'name': 'Baseline Wave 1',
                'wave_type': 'manual',
                'planned_start_time': datetime.now() + timedelta(hours=1),
                'total_orders': 25,
                'assigned_workers': ['W01', 'W02', 'W03'],
                'efficiency_score': 72.0,
                'labor_cost': 2850.0,
                'status': 'planned'
            },
            {
                'name': 'Baseline Wave 2',
                'wave_type': 'manual',
                'planned_start_time': datetime.now() + timedelta(hours=3),
                'total_orders': 30,
                'assigned_workers': ['W04', 'W05', 'W06'],
                'efficiency_score': 68.0,
                'labor_cost': 3200.0,
                'status': 'planned'
            }
        ]
        
        for wave in baseline_waves:
            cursor.execute("""
                INSERT INTO waves (name, wave_type, planned_start_time, total_orders,
                                 assigned_workers, efficiency_score, labor_cost, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (wave['name'], wave['wave_type'], wave['planned_start_time'],
                  wave['total_orders'], wave['assigned_workers'], wave['efficiency_score'],
                  wave['labor_cost'], wave['status']))
        
        self.conn.commit()
        cursor.close()
        print("✅ Generated baseline waves")
    
    def generate_performance_metrics(self):
        """Generate performance metrics for demo scenarios."""
        print("📊 Generating performance metrics...")
        
        cursor = self.conn.cursor()
        
        # Baseline metrics (inefficient)
        baseline_metrics = [
            {'metric_type': 'efficiency', 'metric_value': 72.0},
            {'metric_type': 'on_time_delivery', 'metric_value': 87.0},
            {'metric_type': 'labor_cost', 'metric_value': 2850.0},
            {'metric_type': 'overtime_hours', 'metric_value': 12.0},
            {'metric_type': 'travel_time', 'metric_value': 45.0},
        ]
        
        # Optimized metrics
        optimized_metrics = [
            {'metric_type': 'efficiency', 'metric_value': 89.0},
            {'metric_type': 'on_time_delivery', 'metric_value': 99.2},
            {'metric_type': 'labor_cost', 'metric_value': 2280.0},
            {'metric_type': 'overtime_hours', 'metric_value': 2.0},
            {'metric_type': 'travel_time', 'metric_value': 28.0},
        ]
        
        # Get wave IDs
        cursor.execute("SELECT id FROM waves")
        wave_ids = [row[0] for row in cursor.fetchall()]
        
        if wave_ids:
            # Insert baseline metrics
            for metric in baseline_metrics:
                cursor.execute("""
                    INSERT INTO performance_metrics (wave_id, metric_type, metric_value, notes)
                    VALUES (%s, %s, %s, %s)
                """, (wave_ids[0], metric['metric_type'], metric['metric_value'], 'Baseline performance'))
            
            # Insert optimized metrics
            for metric in optimized_metrics:
                cursor.execute("""
                    INSERT INTO performance_metrics (wave_id, metric_type, metric_value, notes)
                    VALUES (%s, %s, %s, %s)
                """, (wave_ids[1], metric['metric_type'], metric['metric_value'], 'AI optimized performance'))
        
        self.conn.commit()
        cursor.close()
        print("✅ Generated performance metrics")

def main():
    """Main function to generate complete dataset."""
    db_config = {
        'host': 'localhost',
        'database': 'wave_opt',
        'user': 'postgres',
        'password': 'password'
    }
    
    generator = MidWestDistributionDataGenerator(db_config)
    generator.connect()
    generator.generate_complete_dataset()
    generator.conn.close()

if __name__ == "__main__":
    main() 