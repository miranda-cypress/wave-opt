#!/usr/bin/env python3
"""
Simulated WMS Data Generator

This script generates realistic warehouse management system data that can be easily
replaced with real WMS data later. The structure supports:

1. Data import tracking (source_id, external_*_id fields)
2. Data augmentation tracking (augmentation_id fields)
3. Wave plan versioning
4. Audit trails

The generated data simulates:
- Multiple warehouses
- Realistic customer profiles
- SKU catalog with zones and velocity classes
- Workers with skills and efficiency factors
- Equipment with capacity and costs
- Orders with realistic patterns
- Wave plans with assignments
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimulatedWMSDataGenerator:
    """Generates realistic WMS data for testing and development."""
    
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
    
    def create_data_sources(self):
        """Create data sources for tracking imports."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Insert data sources
            cursor.execute("""
                INSERT INTO data_sources (source_name, source_type, connection_config, sync_frequency_minutes) 
                VALUES 
                ('WMS_Production', 'wms', '{"host": "wms.company.com", "port": 8080, "api_key": "demo_key"}', 30),
                ('OMS_Production', 'oms', '{"host": "oms.company.com", "port": 8080, "api_key": "demo_key"}', 15),
                ('Manual_Entry', 'manual', '{}', NULL),
                ('API_Integration', 'api', '{"endpoint": "https://api.company.com/v1", "auth_token": "demo_token"}', 60)
                ON CONFLICT (source_name) DO NOTHING
            """)
            conn.commit()
            logger.info("Created data sources")
    
    def create_warehouses(self):
        """Create multiple warehouses with realistic configurations."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            warehouses = [
                {
                    'name': 'MidWest Distribution Center',
                    'location': 'Chicago, IL',
                    'timezone': 'America/Chicago',
                    'external_id': 'WH001',
                    'source_id': 1
                },
                {
                    'name': 'East Coast Fulfillment Center',
                    'location': 'Newark, NJ',
                    'timezone': 'America/New_York',
                    'external_id': 'WH002',
                    'source_id': 1
                },
                {
                    'name': 'West Coast Logistics Hub',
                    'location': 'Los Angeles, CA',
                    'timezone': 'America/Los_Angeles',
                    'external_id': 'WH003',
                    'source_id': 1
                }
            ]
            
            for warehouse in warehouses:
                cursor.execute("""
                    INSERT INTO warehouses (name, location, timezone, operating_hours, external_warehouse_id, source_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (external_warehouse_id) DO NOTHING
                """, (
                    warehouse['name'],
                    warehouse['location'],
                    warehouse['timezone'],
                    json.dumps({"start": "08:00", "end": "18:00", "days": ["mon", "tue", "wed", "thu", "fri"]}),
                    warehouse['external_id'],
                    warehouse['source_id']
                ))
            
            conn.commit()
            logger.info(f"Created {len(warehouses)} warehouses")
    
    def create_customers(self):
        """Create realistic customer profiles."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            customers = [
                # B2B Customers
                {'code': 'CUST001', 'name': 'Acme Corporation', 'type': 'b2b', 'priority': 1, 'service': 'premium', 'external_id': 'EXT_CUST_001'},
                {'code': 'CUST002', 'name': 'Global Retail Chain', 'type': 'b2b', 'priority': 2, 'service': 'premium', 'external_id': 'EXT_CUST_002'},
                {'code': 'CUST003', 'name': 'Local Store Network', 'type': 'b2b', 'priority': 3, 'service': 'standard', 'external_id': 'EXT_CUST_003'},
                {'code': 'CUST004', 'name': 'Manufacturing Partners', 'type': 'b2b', 'priority': 2, 'service': 'premium', 'external_id': 'EXT_CUST_004'},
                {'code': 'CUST005', 'name': 'Regional Distributors', 'type': 'b2b', 'priority': 3, 'service': 'standard', 'external_id': 'EXT_CUST_005'},
                
                # B2C Customers
                {'code': 'CUST006', 'name': 'Online Marketplace', 'type': 'b2c', 'priority': 4, 'service': 'standard', 'external_id': 'EXT_CUST_006'},
                {'code': 'CUST007', 'name': 'Direct Consumer', 'type': 'b2c', 'priority': 5, 'service': 'standard', 'external_id': 'EXT_CUST_007'},
                {'code': 'CUST008', 'name': 'E-commerce Platform', 'type': 'b2c', 'priority': 4, 'service': 'standard', 'external_id': 'EXT_CUST_008'},
                {'code': 'CUST009', 'name': 'Subscription Service', 'type': 'b2c', 'priority': 3, 'service': 'premium', 'external_id': 'EXT_CUST_009'},
                {'code': 'CUST010', 'name': 'Flash Sale Retailer', 'type': 'b2c', 'priority': 5, 'service': 'rush', 'external_id': 'EXT_CUST_010'}
            ]
            
            for customer in customers:
                cursor.execute("""
                    INSERT INTO customers (warehouse_id, customer_code, name, customer_type, priority_level, service_level, external_customer_id, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, 2)
                    ON CONFLICT (customer_code) DO NOTHING
                """, (
                    customer['code'],
                    customer['name'],
                    customer['type'],
                    customer['priority'],
                    customer['service'],
                    customer['external_id']
                ))
            
            conn.commit()
            logger.info(f"Created {len(customers)} customers")
    
    def create_skus(self):
        """Create realistic SKU catalog with zones and velocity classes."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            skus = [
                # Fast Movers (A Zone)
                {'code': 'SKU001', 'name': 'Premium Widget A', 'category': 'Electronics', 'zone': 'A', 'pick_time': 1.5, 'pack_time': 1.0, 'volume': 0.5, 'weight': 2.0, 'velocity': 'A', 'external_id': 'EXT_SKU_001'},
                {'code': 'SKU002', 'name': 'Standard Widget B', 'category': 'Electronics', 'zone': 'A', 'pick_time': 2.0, 'pack_time': 1.5, 'volume': 1.0, 'weight': 3.5, 'velocity': 'A', 'external_id': 'EXT_SKU_002'},
                {'code': 'SKU003', 'name': 'Light Accessory D', 'category': 'Accessories', 'zone': 'A', 'pick_time': 1.0, 'pack_time': 0.5, 'volume': 0.1, 'weight': 0.5, 'velocity': 'A', 'external_id': 'EXT_SKU_003'},
                {'code': 'SKU004', 'name': 'Fast Moving G', 'category': 'Fast Moving', 'zone': 'A', 'pick_time': 1.0, 'pack_time': 0.8, 'volume': 0.2, 'weight': 0.8, 'velocity': 'A', 'external_id': 'EXT_SKU_004'},
                {'code': 'SKU005', 'name': 'Fragile Item F', 'category': 'Fragile', 'zone': 'A', 'pick_time': 2.5, 'pack_time': 2.5, 'volume': 0.3, 'weight': 1.0, 'velocity': 'B', 'external_id': 'EXT_SKU_005'},
                
                # Medium Movers (B Zone)
                {'code': 'SKU006', 'name': 'Heavy Component C', 'category': 'Industrial', 'zone': 'B', 'pick_time': 3.0, 'pack_time': 2.0, 'volume': 2.5, 'weight': 15.0, 'velocity': 'B', 'external_id': 'EXT_SKU_006'},
                {'code': 'SKU007', 'name': 'Medium Item I', 'category': 'Medium', 'zone': 'B', 'pick_time': 2.5, 'pack_time': 1.5, 'volume': 1.5, 'weight': 5.0, 'velocity': 'B', 'external_id': 'EXT_SKU_007'},
                {'code': 'SKU008', 'name': 'Assembly Kit K', 'category': 'Assembly', 'zone': 'B', 'pick_time': 4.0, 'pack_time': 3.0, 'volume': 3.0, 'weight': 8.0, 'velocity': 'B', 'external_id': 'EXT_SKU_008'},
                {'code': 'SKU009', 'name': 'Tool Set L', 'category': 'Tools', 'zone': 'B', 'pick_time': 3.5, 'pack_time': 2.5, 'volume': 2.0, 'weight': 12.0, 'velocity': 'B', 'external_id': 'EXT_SKU_009'},
                
                # Slow Movers (C Zone)
                {'code': 'SKU010', 'name': 'Bulk Item E', 'category': 'Bulk', 'zone': 'C', 'pick_time': 5.0, 'pack_time': 3.0, 'volume': 5.0, 'weight': 25.0, 'velocity': 'C', 'external_id': 'EXT_SKU_010'},
                {'code': 'SKU011', 'name': 'Slow Moving H', 'category': 'Slow Moving', 'zone': 'C', 'pick_time': 4.0, 'pack_time': 2.0, 'volume': 3.0, 'weight': 12.0, 'velocity': 'C', 'external_id': 'EXT_SKU_011'},
                {'code': 'SKU012', 'name': 'Large Item J', 'category': 'Large', 'zone': 'C', 'pick_time': 6.0, 'pack_time': 4.0, 'volume': 8.0, 'weight': 40.0, 'velocity': 'C', 'external_id': 'EXT_SKU_012'},
                {'code': 'SKU013', 'name': 'Seasonal Product M', 'category': 'Seasonal', 'zone': 'C', 'pick_time': 4.5, 'pack_time': 3.5, 'volume': 4.0, 'weight': 18.0, 'velocity': 'C', 'external_id': 'EXT_SKU_013'},
                {'code': 'SKU014', 'name': 'Specialty Item N', 'category': 'Specialty', 'zone': 'C', 'pick_time': 5.5, 'pack_time': 4.5, 'volume': 6.0, 'weight': 30.0, 'velocity': 'C', 'external_id': 'EXT_SKU_014'},
                {'code': 'SKU015', 'name': 'Oversized Product O', 'category': 'Oversized', 'zone': 'C', 'pick_time': 7.0, 'pack_time': 5.0, 'volume': 10.0, 'weight': 50.0, 'velocity': 'C', 'external_id': 'EXT_SKU_015'}
            ]
            
            for sku in skus:
                cursor.execute("""
                    INSERT INTO skus (warehouse_id, sku_code, name, category, zone, pick_time_minutes, pack_time_minutes, 
                                    volume_cubic_feet, weight_lbs, velocity_class, external_sku_id, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                    ON CONFLICT (sku_code) DO NOTHING
                """, (
                    sku['code'],
                    sku['name'],
                    sku['category'],
                    sku['zone'],
                    sku['pick_time'],
                    sku['pack_time'],
                    sku['volume'],
                    sku['weight'],
                    sku['velocity'],
                    sku['external_id']
                ))
            
            conn.commit()
            logger.info(f"Created {len(skus)} SKUs")
    
    def create_workers(self):
        """Create workers with realistic skills and efficiency factors."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            workers = [
                # First Shift Workers
                {'code': 'W001', 'name': 'John Smith', 'rate': 18.50, 'efficiency': 1.1, 'reliability': 0.98, 'shift': 'first', 'external_id': 'EXT_WORKER_001'},
                {'code': 'W002', 'name': 'Sarah Johnson', 'rate': 17.75, 'efficiency': 1.05, 'reliability': 0.95, 'shift': 'first', 'external_id': 'EXT_WORKER_002'},
                {'code': 'W003', 'name': 'Mike Davis', 'rate': 19.00, 'efficiency': 1.15, 'reliability': 0.99, 'shift': 'first', 'external_id': 'EXT_WORKER_003'},
                {'code': 'W004', 'name': 'Lisa Wilson', 'rate': 16.50, 'efficiency': 0.95, 'reliability': 0.92, 'shift': 'first', 'external_id': 'EXT_WORKER_004'},
                {'code': 'W005', 'name': 'Tom Brown', 'rate': 18.00, 'efficiency': 1.0, 'reliability': 0.96, 'shift': 'first', 'external_id': 'EXT_WORKER_005'},
                
                # Second Shift Workers
                {'code': 'W006', 'name': 'Amy Garcia', 'rate': 17.25, 'efficiency': 1.08, 'reliability': 0.94, 'shift': 'second', 'external_id': 'EXT_WORKER_006'},
                {'code': 'W007', 'name': 'Chris Martinez', 'rate': 18.75, 'efficiency': 1.12, 'reliability': 0.97, 'shift': 'second', 'external_id': 'EXT_WORKER_007'},
                {'code': 'W008', 'name': 'Jennifer Lee', 'rate': 16.75, 'efficiency': 0.98, 'reliability': 0.93, 'shift': 'second', 'external_id': 'EXT_WORKER_008'},
                {'code': 'W009', 'name': 'David Rodriguez', 'rate': 17.50, 'efficiency': 1.03, 'reliability': 0.95, 'shift': 'second', 'external_id': 'EXT_WORKER_009'},
                {'code': 'W010', 'name': 'Maria Gonzalez', 'rate': 16.25, 'efficiency': 0.97, 'reliability': 0.91, 'shift': 'second', 'external_id': 'EXT_WORKER_010'},
                
                # Third Shift Workers
                {'code': 'W011', 'name': 'James Wilson', 'rate': 19.50, 'efficiency': 1.05, 'reliability': 0.96, 'shift': 'third', 'external_id': 'EXT_WORKER_011'},
                {'code': 'W012', 'name': 'Patricia Anderson', 'rate': 18.25, 'efficiency': 1.02, 'reliability': 0.94, 'shift': 'third', 'external_id': 'EXT_WORKER_012'}
            ]
            
            for worker in workers:
                cursor.execute("""
                    INSERT INTO workers (warehouse_id, worker_code, name, hourly_rate, efficiency_factor, 
                                       max_hours_per_day, reliability_score, shift, external_worker_id, source_id)
                    VALUES (1, %s, %s, %s, %s, 8.0, %s, %s, %s, 1)
                    ON CONFLICT (worker_code) DO NOTHING
                """, (
                    worker['code'],
                    worker['name'],
                    worker['rate'],
                    worker['efficiency'],
                    worker['reliability'],
                    worker['shift'],
                    worker['external_id']
                ))
            
            conn.commit()
            logger.info(f"Created {len(workers)} workers")
    
    def create_worker_skills(self):
        """Assign skills to workers."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get worker IDs
            cursor.execute("SELECT id, worker_code FROM workers ORDER BY id")
            workers = cursor.fetchall()
            
            # Create skills data using actual worker IDs
            worker_skills_data = []
            for worker_id, worker_code in workers:
                # Assign skills based on worker code
                if worker_code == 'W001':  # John Smith - High skilled
                    worker_skills_data.extend([(worker_id, 'picking', 5), (worker_id, 'packing', 4)])
                elif worker_code == 'W002':  # Sarah Johnson - Packing specialist
                    worker_skills_data.extend([(worker_id, 'picking', 5), (worker_id, 'sorting', 3)])
                elif worker_code == 'W003':  # Mike Davis - Picking specialist
                    worker_skills_data.extend([(worker_id, 'packing', 5), (worker_id, 'shipping', 4)])
                elif worker_code == 'W004':  # Lisa Wilson - General
                    worker_skills_data.extend([(worker_id, 'picking', 4), (worker_id, 'inventory', 3)])
                elif worker_code == 'W005':  # Tom Brown - Receiving specialist
                    worker_skills_data.extend([(worker_id, 'packing', 5), (worker_id, 'quality', 4)])
                elif worker_code == 'W006':  # Amy Garcia - Shipping specialist
                    worker_skills_data.extend([(worker_id, 'picking', 3), (worker_id, 'sorting', 4)])
                elif worker_code == 'W007':  # Chris Martinez - High skilled
                    worker_skills_data.extend([(worker_id, 'packing', 4), (worker_id, 'shipping', 5)])
                elif worker_code == 'W008':  # Jennifer Lee - General
                    worker_skills_data.extend([(worker_id, 'picking', 5), (worker_id, 'inventory', 4)])
                elif worker_code == 'W009':  # David Rodriguez - Picking specialist
                    worker_skills_data.extend([(worker_id, 'packing', 3), (worker_id, 'quality', 5)])
                elif worker_code == 'W010':  # Maria Gonzalez - General
                    worker_skills_data.extend([(worker_id, 'picking', 4), (worker_id, 'sorting', 5)])
                elif worker_code == 'W011':  # James Wilson - Night shift specialist
                    worker_skills_data.extend([(worker_id, 'packing', 5), (worker_id, 'shipping', 3)])
                elif worker_code == 'W012':  # Patricia Anderson - Night shift general
                    worker_skills_data.extend([(worker_id, 'picking', 4), (worker_id, 'inventory', 5)])
            
            for worker_id, skill, proficiency in worker_skills_data:
                cursor.execute("""
                    INSERT INTO worker_skills (worker_id, skill, proficiency_level)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (worker_id, skill) DO NOTHING
                """, (worker_id, skill, proficiency))
            
            conn.commit()
            logger.info(f"Created {len(worker_skills_data)} worker skill assignments")
    
    def create_equipment(self):
        """Create equipment with realistic capacity and costs."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            equipment = [
                # Packing Stations
                {'code': 'EQ001', 'name': 'Packing Station 1', 'type': 'packing_station', 'capacity': 1, 'cost': 5.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_001'},
                {'code': 'EQ002', 'name': 'Packing Station 2', 'type': 'packing_station', 'capacity': 1, 'cost': 5.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_002'},
                {'code': 'EQ003', 'name': 'Packing Station 3', 'type': 'packing_station', 'capacity': 1, 'cost': 5.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_003'},
                {'code': 'EQ004', 'name': 'Packing Station 4', 'type': 'packing_station', 'capacity': 1, 'cost': 5.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_004'},
                
                # Dock Doors
                {'code': 'EQ005', 'name': 'Dock Door 1', 'type': 'dock_door', 'capacity': 1, 'cost': 2.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_005'},
                {'code': 'EQ006', 'name': 'Dock Door 2', 'type': 'dock_door', 'capacity': 1, 'cost': 2.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_006'},
                {'code': 'EQ007', 'name': 'Dock Door 3', 'type': 'dock_door', 'capacity': 1, 'cost': 2.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_007'},
                
                # Forklifts
                {'code': 'EQ008', 'name': 'Forklift 1', 'type': 'forklift', 'capacity': 1, 'cost': 8.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_008'},
                {'code': 'EQ009', 'name': 'Forklift 2', 'type': 'forklift', 'capacity': 1, 'cost': 8.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_009'},
                
                # Scanners
                {'code': 'EQ010', 'name': 'Scanner 1', 'type': 'scanner', 'capacity': 1, 'cost': 1.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_010'},
                {'code': 'EQ011', 'name': 'Scanner 2', 'type': 'scanner', 'capacity': 1, 'cost': 1.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_011'},
                {'code': 'EQ012', 'name': 'Scanner 3', 'type': 'scanner', 'capacity': 1, 'cost': 1.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_012'},
                
                # Conveyors
                {'code': 'EQ013', 'name': 'Conveyor Line 1', 'type': 'conveyor', 'capacity': 5, 'cost': 3.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_013'},
                {'code': 'EQ014', 'name': 'Conveyor Line 2', 'type': 'conveyor', 'capacity': 5, 'cost': 3.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_014'},
                
                # Label Printers
                {'code': 'EQ015', 'name': 'Label Printer 1', 'type': 'label_printer', 'capacity': 1, 'cost': 2.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_015'},
                {'code': 'EQ016', 'name': 'Label Printer 2', 'type': 'label_printer', 'capacity': 1, 'cost': 2.00, 'efficiency': 1.0, 'external_id': 'EXT_EQ_016'}
            ]
            
            for eq in equipment:
                cursor.execute("""
                    INSERT INTO equipment (warehouse_id, equipment_code, name, equipment_type, capacity, 
                                         hourly_cost, efficiency_factor, maintenance_frequency, current_utilization, 
                                         external_equipment_id, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, 30, 0.0, %s, 1)
                    ON CONFLICT (equipment_code) DO NOTHING
                """, (
                    eq['code'],
                    eq['name'],
                    eq['type'],
                    eq['capacity'],
                    eq['cost'],
                    eq['efficiency'],
                    eq['external_id']
                ))
            
            conn.commit()
            logger.info(f"Created {len(equipment)} equipment items")
    
    def create_orders(self, num_orders: int = 50):
        """Create realistic orders with varying patterns."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get customer IDs
            cursor.execute("SELECT id, customer_code, customer_type, priority_level FROM customers ORDER BY id")
            customers = cursor.fetchall()
            
            # Get SKU IDs
            cursor.execute("SELECT id, sku_code, pick_time_minutes, pack_time_minutes, volume_cubic_feet, weight_lbs FROM skus ORDER BY id")
            skus = cursor.fetchall()
            
            # Generate orders
            base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            
            for i in range(num_orders):
                # Select random customer
                customer = random.choice(customers)
                
                # Generate order time (spread across the day)
                order_hour = 8 + (i % 10)  # Spread across 10 hours
                order_minute = (i * 7) % 60  # Spread minutes
                order_time = base_time.replace(hour=order_hour, minute=order_minute)
                
                # Generate shipping deadline (1-3 days from order)
                days_to_deadline = random.randint(1, 3)
                deadline_time = order_time + timedelta(days=days_to_deadline, hours=random.randint(0, 23))
                
                # Generate order number
                order_number = f"ORD{str(i+1).zfill(3)}"
                external_order_id = f"EXT_ORD_{str(i+1).zfill(3)}"
                
                # Insert order
                cursor.execute("""
                    INSERT INTO orders (warehouse_id, order_number, customer_id, order_date, customer_name, 
                                      customer_type, priority, shipping_deadline, status, external_order_id, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, %s, 'pending', %s, 2)
                    ON CONFLICT (order_number) DO NOTHING
                    RETURNING id
                """, (
                    order_number,
                    customer[0],  # customer_id
                    order_time,
                    f"Customer {customer[1]}",  # customer_name
                    customer[2],  # customer_type
                    customer[3],  # priority
                    deadline_time,
                    external_order_id
                ))
                
                result = cursor.fetchone()
                if result is None:
                    # Order already exists, skip to next
                    continue
                    
                order_id = result[0]
                
                # Generate order items (1-5 items per order)
                num_items = random.randint(1, 5)
                total_pick_time = 0
                total_pack_time = 0
                total_volume = 0
                total_weight = 0
                
                for j in range(num_items):
                    sku = random.choice(skus)
                    quantity = random.randint(1, 10)
                    
                    pick_time = sku[2] * quantity
                    pack_time = sku[3] * quantity
                    volume = sku[4] * quantity
                    weight = sku[5] * quantity
                    
                    total_pick_time += pick_time
                    total_pack_time += pack_time
                    total_volume += volume
                    total_weight += weight
                    
                    cursor.execute("""
                        INSERT INTO order_items (order_id, sku_id, quantity, pick_time, pack_time, 
                                               volume, weight, external_line_id, source_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 2)
                    """, (
                        order_id,
                        sku[0],  # sku_id
                        quantity,
                        pick_time,
                        pack_time,
                        volume,
                        weight,
                        f"EXT_LINE_{order_id}_{j+1}"
                    ))
                
                # Update order totals
                cursor.execute("""
                    UPDATE orders 
                    SET total_pick_time = %s, total_pack_time = %s, total_volume = %s, total_weight = %s
                    WHERE id = %s
                """, (total_pick_time, total_pack_time, total_volume, total_weight, order_id))
            
            conn.commit()
            logger.info(f"Created {num_orders} orders with items")
    
    def create_wave_plan_versions(self):
        """Create wave plan versions for versioning support."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            versions = [
                {
                    'name': 'Original WMS Plan',
                    'description': 'Initial wave plan from WMS system',
                    'type': 'original',
                    'created_by': 'system',
                    'is_active': True
                },
                {
                    'name': 'Optimized Plan v1',
                    'description': 'First optimization run results',
                    'type': 'optimized',
                    'created_by': 'optimizer',
                    'is_active': False
                },
                {
                    'name': 'Manual Override Plan',
                    'description': 'Manual adjustments to optimized plan',
                    'type': 'manual',
                    'created_by': 'supervisor',
                    'is_active': False
                }
            ]
            
            for version in versions:
                cursor.execute("""
                    INSERT INTO wave_plan_versions (warehouse_id, version_name, version_description, 
                                                  version_type, created_by, is_active)
                    VALUES (1, %s, %s, %s, %s, %s)
                    ON CONFLICT (version_name) DO NOTHING
                """, (
                    version['name'],
                    version['description'],
                    version['type'],
                    version['created_by'],
                    version['is_active']
                ))
            
            conn.commit()
            logger.info(f"Created {len(versions)} wave plan versions")
    
    def create_waves(self):
        """Create realistic wave plans."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get version ID for original plan
            cursor.execute("SELECT id FROM wave_plan_versions WHERE version_name = 'Original WMS Plan'")
            version_id = cursor.fetchone()[0]
            
            # Define orders per wave (realistic for 2500 orders/day)
            # Each wave should handle 300-800 orders depending on shift length
            orders_per_wave = 400  # Realistic for 2-hour waves
            
            # Get worker codes
            cursor.execute("SELECT worker_code FROM workers WHERE shift = 'first' ORDER BY id")
            first_shift_workers = [w[0] for w in cursor.fetchall()]
            
            cursor.execute("SELECT worker_code FROM workers WHERE shift = 'second' ORDER BY id")
            second_shift_workers = [w[0] for w in cursor.fetchall()]
            
            waves = [
                {
                    'name': 'Morning Wave 1',
                    'type': 'manual',
                    'planned_start': '08:00:00',
                    'planned_end': '10:00:00',
                    'workers': first_shift_workers[:3],
                    'efficiency': 75.0,
                    'external_id': 'EXT_WAVE_001'
                },
                {
                    'name': 'Morning Wave 2',
                    'type': 'manual',
                    'planned_start': '10:00:00',
                    'planned_end': '12:00:00',
                    'workers': first_shift_workers[3:],
                    'efficiency': 72.0,
                    'external_id': 'EXT_WAVE_002'
                },
                {
                    'name': 'Afternoon Wave 1',
                    'type': 'manual',
                    'planned_start': '13:00:00',
                    'planned_end': '15:00:00',
                    'workers': second_shift_workers[:2],
                    'efficiency': 78.0,
                    'external_id': 'EXT_WAVE_003'
                },
                {
                    'name': 'Afternoon Wave 2',
                    'type': 'manual',
                    'planned_start': '15:00:00',
                    'planned_end': '17:00:00',
                    'workers': second_shift_workers[2:],
                    'efficiency': 70.0,
                    'external_id': 'EXT_WAVE_004'
                }
            ]
            
            base_date = datetime.now().date()
            
            for wave in waves:
                planned_start = datetime.combine(base_date, datetime.strptime(wave['planned_start'], '%H:%M:%S').time())
                planned_end = datetime.combine(base_date, datetime.strptime(wave['planned_end'], '%H:%M:%S').time())
                
                cursor.execute("""
                    INSERT INTO waves (warehouse_id, wave_name, wave_type, version_id, planned_start_time, 
                                     planned_completion_time, total_orders, assigned_workers, efficiency_score, status, 
                                     external_wave_id, source_id)
                    VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, 'planned', %s, 1)
                    RETURNING id
                """, (
                    wave['name'],
                    wave['type'],
                    version_id,
                    planned_start,
                    planned_end,
                    orders_per_wave,
                    wave['workers'],
                    wave['efficiency'],
                    wave['external_id']
                ))
                
                wave_id = cursor.fetchone()[0]
                
                # Assign orders to this wave (realistic assignment for 2500 orders/day)
                # Get orders to assign to this wave
                cursor.execute("""
                    SELECT id FROM orders 
                    WHERE status = 'pending' 
                    ORDER BY priority ASC, shipping_deadline ASC 
                    LIMIT %s
                """, (orders_per_wave,))
                
                order_ids = [row[0] for row in cursor.fetchall()]
                
                # Update order status
                if order_ids:
                    cursor.execute("""
                        UPDATE orders 
                        SET status = 'assigned' 
                        WHERE id = ANY(%s)
                    """, (order_ids,))
                
                # Create wave assignments for each order
                for i, order_id in enumerate(order_ids):
                    # Create assignments for each stage (pick, pack, ship)
                    stages = ['pick', 'pack', 'ship']
                    for stage_idx, stage in enumerate(stages):
                        cursor.execute("""
                            INSERT INTO wave_assignments (wave_id, order_id, stage, sequence_order)
                            VALUES (%s, %s, %s, %s)
                        """, (wave_id, order_id, stage, i * len(stages) + stage_idx + 1))
            
            conn.commit()
            logger.info(f"Created {len(waves)} waves")
    
    def create_data_import_record(self):
        """Create a record of this data import for tracking."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO data_imports (source_id, import_type, import_status, records_processed, 
                                        records_imported, records_failed, import_metadata, completed_at)
                VALUES (1, 'full_sync', 'completed', 200, 200, 0, 
                       '{"generator": "simulated_wms_data_generator", "version": "1.0"}', NOW())
                RETURNING id
            """)
            
            import_id = cursor.fetchone()[0]
            
            # Create augmentation record
            cursor.execute("""
                INSERT INTO data_augmentations (import_id, augmentation_type, table_name, records_augmented, 
                                              augmentation_rules, augmentation_status, completed_at)
                VALUES (%s, 'pick_times', 'skus', 15, 
                       '{"method": "simulated", "base_time": 2.0, "zone_multipliers": {"A": 0.8, "B": 1.0, "C": 1.5}}', 
                       'completed', NOW())
            """, (import_id,))
            
            conn.commit()
            logger.info(f"Created data import record (ID: {import_id})")
    
    def generate_all_data(self, num_orders: int = 50):
        """Generate all simulated WMS data."""
        logger.info("Starting WMS data generation...")
        
        try:
            self.create_data_sources()
            self.create_warehouses()
            self.create_customers()
            self.create_skus()
            self.create_workers()
            self.create_worker_skills()
            self.create_equipment()
            self.create_orders(num_orders)
            self.create_wave_plan_versions()
            self.create_waves()
            self.create_data_import_record()
            
            logger.info("WMS data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error generating WMS data: {e}")
            raise


def main():
    """Main function to run the data generator."""
    generator = SimulatedWMSDataGenerator()
    # Generate 2500 orders to match realistic daily warehouse throughput
    generator.generate_all_data(num_orders=2500)
    
    print("\n" + "="*60)
    print("WMS DATA GENERATION COMPLETED")
    print("="*60)
    print("Generated data includes:")
    print("- 3 Warehouses")
    print("- 10 Customers (B2B and B2C)")
    print("- 15 SKUs (Fast, Medium, Slow movers)")
    print("- 12 Workers with skills")
    print("- 16 Equipment items")
    print("- 2500 Orders with items (realistic daily throughput)")
    print("- 4 Wave plans")
    print("- Data import and augmentation tracking")
    print("\nThe data is structured to easily accept real WMS data later.")
    print("All tables include external_*_id fields for WMS integration.")
    print("="*60)


if __name__ == "__main__":
    main() 