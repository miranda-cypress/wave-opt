#!/usr/bin/env python3
"""
WMS Wave Planner

This script generates realistic WMS-style wave planning data including:
- Detailed stage scheduling for each order (pick, consolidate, pack, label, stage, ship)
- Worker assignments based on skills and availability
- Equipment assignments (packing stations, dock doors, etc.)
- Realistic timing calculations
- Resource capacity constraints
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


class WMSWavePlanner:
    """Generates realistic WMS-style wave planning data."""
    
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
        
        # Stage definitions with typical durations (minutes)
        self.stages = {
            'pick': {'duration_base': 15, 'worker_skill': 'picking', 'equipment_type': None},
            'consolidate': {'duration_base': 5, 'worker_skill': 'picking', 'equipment_type': None},
            'pack': {'duration_base': 10, 'worker_skill': 'packing', 'equipment_type': 'packing_station'},
            'label': {'duration_base': 3, 'worker_skill': 'packing', 'equipment_type': 'scanner'},
            'stage': {'duration_base': 8, 'worker_skill': 'shipping', 'equipment_type': None},
            'ship': {'duration_base': 5, 'worker_skill': 'shipping', 'equipment_type': 'dock_door'}
        }
        
        # Resource capacity limits
        self.max_workers_per_shift = 20
        self.max_packing_stations = 8
        self.max_dock_doors = 4
        self.max_scanners = 4
        
        # Time constants
        self.shift_start_hour = 8
        self.shift_end_hour = 18
        self.worker_efficiency = 0.85
        
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
    
    def get_available_resources(self, wave_start_time: datetime):
        """Get available workers and equipment for a specific wave."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get workers with their skills
            cursor.execute("""
                SELECT w.id, w.worker_code, w.efficiency_factor, ws.skill, ws.proficiency_level
                FROM workers w
                LEFT JOIN worker_skills ws ON w.id = ws.worker_id
                WHERE w.active = TRUE AND w.warehouse_id = 1
                ORDER BY w.id, ws.skill
            """)
            workers_data = cursor.fetchall()
            
            # Get equipment
            cursor.execute("""
                SELECT id, equipment_code, equipment_type, capacity, efficiency_factor
                FROM equipment 
                WHERE warehouse_id = 1
                ORDER BY equipment_type, id
            """)
            equipment_data = cursor.fetchall()
            
            # Organize workers by skill
            workers_by_skill = {}
            for worker_id, worker_code, efficiency, skill, proficiency in workers_data:
                if skill not in workers_by_skill:
                    workers_by_skill[skill] = []
                workers_by_skill[skill].append({
                    'id': worker_id,
                    'code': worker_code,
                    'efficiency': efficiency,
                    'proficiency': proficiency or 3
                })
            
            # Organize equipment by type
            equipment_by_type = {}
            for eq_id, eq_code, eq_type, capacity, efficiency in equipment_data:
                if eq_type not in equipment_by_type:
                    equipment_by_type[eq_type] = []
                equipment_by_type[eq_type].append({
                    'id': eq_id,
                    'code': eq_code,
                    'capacity': capacity,
                    'efficiency': efficiency
                })
            
            return workers_by_skill, equipment_by_type
    
    def calculate_order_stages(self, order_id: int, wave_start_time: datetime) -> List[Dict]:
        """Calculate detailed stage scheduling for an order."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get order details
            cursor.execute("""
                SELECT o.id, o.total_pick_time, o.total_pack_time, o.total_volume, o.total_weight,
                       COUNT(oi.id) as num_items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = %s
                GROUP BY o.id
            """, (order_id,))
            order_data = cursor.fetchone()
            
            if not order_data:
                return []
            
            order_id, total_pick_time, total_pack_time, total_volume, total_weight, num_items = order_data
            
            # Calculate stage durations based on order characteristics
            stages = []
            current_time = wave_start_time
            
            for stage_name, stage_config in self.stages.items():
                # Calculate duration based on order characteristics
                base_duration = stage_config['duration_base']
                
                if stage_name == 'pick':
                    duration = max(base_duration, total_pick_time or 10)
                elif stage_name == 'pack':
                    duration = max(base_duration, total_pack_time or 8)
                elif stage_name == 'consolidate':
                    duration = base_duration + (num_items * 0.5)  # More items = more time
                elif stage_name == 'label':
                    duration = base_duration + (num_items * 0.3)  # More items = more labels
                elif stage_name == 'stage':
                    duration = base_duration + (float(total_volume or 0) * 0.5)  # More volume = more staging time
                elif stage_name == 'ship':
                    duration = base_duration + (float(total_weight or 0) * 0.1)  # More weight = more shipping time
                else:
                    duration = base_duration
                
                # Add some variability
                duration = duration * random.uniform(0.8, 1.2)
                
                stages.append({
                    'stage': stage_name,
                    'planned_start_time': current_time,
                    'planned_duration_minutes': round(duration, 2),
                    'worker_skill': stage_config['worker_skill'],
                    'equipment_type': stage_config['equipment_type']
                })
                
                current_time += timedelta(minutes=duration)
            
            return stages
    
    def assign_resources_to_stages(self, stages: List[Dict], workers_by_skill: Dict, 
                                 equipment_by_type: Dict) -> List[Dict]:
        """Assign workers and equipment to each stage."""
        assigned_stages = []
        
        for stage in stages:
            # Assign worker based on skill
            worker_id = None
            if stage['worker_skill'] in workers_by_skill:
                available_workers = workers_by_skill[stage['worker_skill']]
                if available_workers:
                    # Select worker based on proficiency and efficiency
                    selected_worker = max(available_workers, 
                                       key=lambda w: w['proficiency'] * w['efficiency'])
                    worker_id = selected_worker['id']
            
            # Assign equipment if needed
            equipment_id = None
            if stage['equipment_type'] and stage['equipment_type'] in equipment_by_type:
                available_equipment = equipment_by_type[stage['equipment_type']]
                if available_equipment:
                    # Simple round-robin assignment
                    equipment_id = available_equipment[0]['id']
            
            stage['assigned_worker_id'] = worker_id
            stage['assigned_equipment_id'] = equipment_id
            assigned_stages.append(stage)
        
        return assigned_stages
    
    def create_wms_wave_plan(self):
        """Create detailed WMS-style wave planning for all existing waves."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Creating WMS-style wave planning...")
            
            # Get all waves
            cursor.execute("""
                SELECT id, wave_name, planned_start_time, total_orders
                FROM waves 
                WHERE warehouse_id = 1
                ORDER BY planned_start_time, id
            """)
            waves = cursor.fetchall()
            
            for wave_id, wave_name, planned_start_time, total_orders in waves:
                logger.info(f"Planning wave {wave_name} with {total_orders} orders")
                
                # Get orders for this wave
                cursor.execute("""
                    SELECT wa.order_id, wa.sequence_order
                    FROM wave_assignments wa
                    WHERE wa.wave_id = %s
                    ORDER BY wa.sequence_order
                """, (wave_id,))
                wave_orders = cursor.fetchall()
                
                # Get available resources for this wave
                workers_by_skill, equipment_by_type = self.get_available_resources(planned_start_time)
                
                # Calculate wave start time (8 AM on the planned date)
                wave_start_time = planned_start_time.replace(hour=8, minute=0, second=0, microsecond=0)
                
                # Process each order in the wave
                for order_id, sequence_order in wave_orders:
                    # Calculate detailed stages for this order
                    order_stages = self.calculate_order_stages(order_id, wave_start_time)
                    
                    # Assign resources to stages
                    assigned_stages = self.assign_resources_to_stages(
                        order_stages, workers_by_skill, equipment_by_type
                    )
                    
                    # Update wave assignments with detailed planning
                    for stage_idx, stage in enumerate(assigned_stages):
                        cursor.execute("""
                            UPDATE wave_assignments 
                            SET assigned_worker_id = %s,
                                assigned_equipment_id = %s,
                                planned_start_time = %s,
                                planned_duration_minutes = %s
                            WHERE wave_id = %s AND order_id = %s AND stage = %s
                        """, (
                            stage['assigned_worker_id'],
                            stage['assigned_equipment_id'],
                            stage['planned_start_time'],
                            stage['planned_duration_minutes'],
                            wave_id,
                            order_id,
                            stage['stage']
                        ))
                    
                    # Move start time forward for next order
                    if assigned_stages:
                        last_stage = assigned_stages[-1]
                        wave_start_time = (last_stage['planned_start_time'] + 
                                         timedelta(minutes=last_stage['planned_duration_minutes']))
                
                # Update wave with completion time
                if wave_orders:
                    cursor.execute("""
                        SELECT MAX(planned_start_time + INTERVAL '1 minute' * planned_duration_minutes)
                        FROM wave_assignments 
                        WHERE wave_id = %s
                    """, (wave_id,))
                    completion_result = cursor.fetchone()
                    completion_time = completion_result[0] if completion_result else None
                    
                    if completion_time:
                        cursor.execute("""
                            UPDATE waves 
                            SET planned_completion_time = %s
                            WHERE id = %s
                        """, (completion_time, wave_id))
            
            conn.commit()
            logger.info("WMS wave planning completed successfully!")
    
    def calculate_wave_metrics(self):
        """Calculate and store performance metrics for each wave."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Calculating wave performance metrics...")
            
            # Get all waves
            cursor.execute("""
                SELECT id, wave_name, total_orders, planned_start_time, planned_completion_time
                FROM waves 
                WHERE warehouse_id = 1
            """)
            waves = cursor.fetchall()
            
            for wave_id, wave_name, total_orders, start_time, completion_time in waves:
                if not start_time or not completion_time:
                    continue
                
                # Calculate metrics
                duration_hours = (completion_time - start_time).total_seconds() / 3600
                orders_per_hour = total_orders / duration_hours if duration_hours > 0 else 0
                
                # Calculate labor cost (assume $18.50/hour per worker)
                estimated_workers = max(1, math.ceil(total_orders / 50))  # Rough estimate
                labor_cost = duration_hours * estimated_workers * 18.50
                
                # Calculate efficiency score (0-100)
                efficiency_score = min(100, max(0, 85 + random.uniform(-10, 10)))
                
                # Store metrics
                metrics = [
                    ('efficiency', efficiency_score),
                    ('labor_cost', round(labor_cost, 2)),
                    ('orders_per_hour', round(orders_per_hour, 2)),
                    ('duration_hours', round(duration_hours, 2)),
                    ('worker_count', estimated_workers)
                ]
                
                for metric_type, metric_value in metrics:
                    cursor.execute("""
                        INSERT INTO performance_metrics (wave_id, metric_type, metric_value, source_id)
                        VALUES (%s, %s, %s, 1)
                        ON CONFLICT DO NOTHING
                    """, (wave_id, metric_type, metric_value))
            
            conn.commit()
            logger.info("Wave performance metrics calculated and stored!")


def main():
    """Main function to run the WMS wave planner."""
    planner = WMSWavePlanner()
    planner.create_wms_wave_plan()
    planner.calculate_wave_metrics()


if __name__ == "__main__":
    main() 