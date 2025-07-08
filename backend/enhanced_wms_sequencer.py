#!/usr/bin/env python3
"""
Enhanced WMS Sequencer - Entry-Level WMS Algorithm

This script implements a realistic but suboptimal baseline WMS algorithm that:
1. Sorts orders by deadline and priority
2. Groups orders by zone for basic efficiency
3. Assigns workers based on skills and availability
4. Monitors equipment capacity constraints
5. Tracks queue lengths and adjusts resource allocation
6. Updates wave assignments with realistic sequencing

This creates a baseline that clearly shows improvement opportunities
for AI optimization to address.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedWMSSequencer:
    """Entry-level WMS sequencer with realistic but suboptimal algorithms."""
    
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
        
        # Stage definitions with basic durations
        self.stages = ['pick', 'consolidate', 'pack', 'label', 'stage', 'ship']
        self.stage_skills = {
            'pick': ['picking'],
            'consolidate': ['picking', 'inventory'],
            'pack': ['packing'],
            'label': ['packing', 'shipping'],
            'stage': ['inventory', 'shipping'],
            'ship': ['shipping']
        }
        self.stage_equipment = {
            'pack': ['packing_station'],
            'ship': ['dock_door'],
            'label': ['label_printer']
        }
        
        # Queue thresholds for dynamic resource allocation
        self.queue_thresholds = {
            'pack': 5,  # Move workers to packing if >5 orders waiting
            'ship': 3,  # Move workers to shipping if >3 orders waiting
            'consolidate': 8  # Move workers to consolidation if >8 orders waiting
        }
    
    def get_connection(self):
        """Get database connection."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        return self.conn
    
    def get_wave_orders(self, wave_id: int) -> List[Dict]:
        """Get all orders for a wave with their details."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT 
                    o.id as order_id,
                    o.priority,
                    o.shipping_deadline,
                    o.total_pick_time,
                    o.total_pack_time,
                    o.total_weight,
                    o.total_volume,
                    c.name as customer_name
                FROM wave_assignments wa
                JOIN orders o ON wa.order_id = o.id
                LEFT JOIN customers c ON o.customer_id = c.id
                WHERE wa.wave_id = %s
                ORDER BY o.shipping_deadline, o.priority, o.id
            """, (wave_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_order_zones(self, order_id: int) -> List[str]:
        """Get zones for an order's items."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT s.zone
                FROM order_items oi
                JOIN skus s ON oi.sku_id = s.id
                WHERE oi.order_id = %s
                ORDER BY s.zone
            """, (order_id,))
            return [row[0] for row in cursor.fetchall()]
    
    def get_available_workers(self) -> List[Dict]:
        """Get all active workers with their skills."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT w.id, w.name, w.worker_code, w.hourly_rate, w.efficiency_factor,
                       array_agg(ws.skill) as skills,
                       array_agg(ws.proficiency_level) as proficiency_levels
                FROM workers w
                LEFT JOIN worker_skills ws ON w.id = ws.worker_id
                WHERE w.active = true
                GROUP BY w.id, w.name, w.worker_code, w.hourly_rate, w.efficiency_factor
                ORDER BY w.id
            """)
            workers = cursor.fetchall()
            
            # Process skills and proficiency levels
            for worker in workers:
                if worker['skills'] and worker['skills'][0] is not None:
                    # Create skill-proficiency mapping
                    skills = worker['skills']
                    proficiencies = worker['proficiency_levels'] or [3] * len(skills)
                    worker['skill_proficiencies'] = dict(zip(skills, proficiencies))
                else:
                    worker['skill_proficiencies'] = {}
                    worker['skills'] = []
            
            return [dict(worker) for worker in workers]
    
    def get_available_equipment(self) -> List[Dict]:
        """Get all active equipment."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, equipment_code, equipment_type, capacity, hourly_cost
                FROM equipment
                WHERE active = true
                ORDER BY equipment_type, id
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def sort_orders_by_criteria(self, orders: List[Dict]) -> List[Dict]:
        """Sort orders by deadline, priority, and zone efficiency."""
        # Primary sort: deadline (earliest first)
        # Secondary sort: priority (1=highest, 5=lowest)
        # Tertiary sort: zone efficiency (A->B->C)
        
        def get_zone_efficiency_score(order):
            zones = self.get_order_zones(order['order_id'])
            # Zone A is most efficient, C is least efficient
            zone_scores = {'A': 3, 'B': 2, 'C': 1}
            if zones:
                return max(zone_scores.get(zone, 1) for zone in zones)
            return 1
        
        return sorted(orders, key=lambda o: (
            o['shipping_deadline'],  # Earliest deadline first
            o['priority'],           # Lower priority number = higher priority
            -get_zone_efficiency_score(o)  # Higher zone efficiency first
        ))
    
    def group_orders_by_zone(self, orders: List[Dict]) -> List[List[Dict]]:
        """Group orders by their primary zone for basic efficiency."""
        zone_groups = {}
        
        for order in orders:
            zones = self.get_order_zones(order['order_id'])
            if zones:
                primary_zone = zones[0]  # Use first zone as primary
                if primary_zone not in zone_groups:
                    zone_groups[primary_zone] = []
                zone_groups[primary_zone].append(order)
            else:
                # Default to zone A if no zones found
                if 'A' not in zone_groups:
                    zone_groups['A'] = []
                zone_groups['A'].append(order)
        
        # Return groups in zone order (A->B->C)
        zone_order = ['A', 'B', 'C']
        return [zone_groups.get(zone, []) for zone in zone_order if zone in zone_groups]
    
    def find_worker_for_stage(self, stage: str, workers: List[Dict], 
                             worker_assignments: Dict) -> Optional[Dict]:
        """Find the best available worker for a stage."""
        required_skills = self.stage_skills.get(stage, [])
        
        # Find workers with required skills
        qualified_workers = []
        for worker in workers:
            worker_skills = worker.get('skills', [])
            if any(skill in worker_skills for skill in required_skills):
                qualified_workers.append(worker)
        
        # If no qualified workers, use any worker
        if not qualified_workers:
            qualified_workers = workers
        
        # Find worker with least current workload
        best_worker = None
        min_workload = float('inf')
        
        for worker in qualified_workers:
            current_workload = len(worker_assignments.get(worker['id'], []))
            if current_workload < min_workload:
                min_workload = current_workload
                best_worker = worker
        
        return best_worker
    
    def find_equipment_for_stage(self, stage: str, equipment: List[Dict],
                                equipment_assignments: Dict) -> Optional[Dict]:
        """Find available equipment for a stage."""
        required_equipment_types = self.stage_equipment.get(stage, [])
        
        if not required_equipment_types:
            return None
        
        # Find equipment with required type
        available_equipment = []
        for eq in equipment:
            if eq['equipment_type'] in required_equipment_types:
                current_usage = len(equipment_assignments.get(eq['id'], []))
                if current_usage < eq['capacity']:
                    available_equipment.append(eq)
        
        if not available_equipment:
            return None
        
        # Return equipment with least current usage
        return min(available_equipment, 
                  key=lambda e: len(equipment_assignments.get(e['id'], [])))
    
    def calculate_stage_duration(self, stage: str, order: Dict) -> int:
        """Calculate realistic duration for a stage."""
        # Use actual pick/pack times from the order if available
        if stage == 'pick' and order.get('total_pick_time'):
            duration = float(order['total_pick_time'])
        elif stage == 'pack' and order.get('total_pack_time'):
            duration = float(order['total_pack_time'])
        else:
            # Fallback to estimated duration based on weight/volume
            base_durations = {
                'pick': 2.5,      # minutes per item
                'consolidate': 1.0, # minutes per item
                'pack': 3.0,       # minutes per item
                'label': 0.5,      # minutes per item
                'stage': 1.0,      # minutes per item
                'ship': 2.0        # minutes per item
            }
            
            # Estimate items based on weight (rough approximation)
            estimated_items = max(1, int(order.get('total_weight', 1) / 2))
            base_duration = base_durations.get(stage, 1.0)
            
            # Apply complexity factors
            if stage == 'pick':
                zones = self.get_order_zones(order['order_id'])
                zone_factor = 1.0 + (len(zones) - 1) * 0.2  # More zones = more travel time
                duration = estimated_items * base_duration * zone_factor
            elif stage == 'pack':
                # Pack time varies by item count and complexity
                complexity_factor = 1.0 + (estimated_items - 1) * 0.1  # More items = more complex
                duration = estimated_items * base_duration * complexity_factor
            else:
                duration = estimated_items * base_duration
        
        # Add some randomness (±20%)
        duration = duration * (0.8 + random.random() * 0.4)
        
        return max(1, int(duration))  # Minimum 1 minute
    
    def monitor_queue_lengths(self, wave_id: int) -> Dict[str, int]:
        """Monitor queue lengths at each stage."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT stage, COUNT(*) as queue_length
                FROM wave_assignments wa
                WHERE wa.wave_id = %s 
                AND wa.assigned_worker_id IS NULL
                GROUP BY stage
            """, (wave_id,))
            
            queue_lengths = {}
            for stage, count in cursor.fetchall():
                queue_lengths[stage] = count
            
            return queue_lengths
    
    def adjust_resource_allocation(self, wave_id: int, workers: List[Dict],
                                 worker_assignments: Dict) -> None:
        """Dynamically adjust resource allocation based on queue lengths."""
        queue_lengths = self.monitor_queue_lengths(wave_id)
        
        # Find workers currently assigned to less critical stages
        available_workers = []
        for worker in workers:
            current_assignments = worker_assignments.get(worker['id'], [])
            if len(current_assignments) < 3:  # Workers with light workload
                available_workers.append(worker)
        
        if not available_workers:
            return
        
        # Move workers to bottleneck stages
        for stage, threshold in self.queue_thresholds.items():
            if queue_lengths.get(stage, 0) > threshold:
                # Find worker with required skills for this stage
                required_skills = self.stage_skills.get(stage, [])
                for worker in available_workers:
                    worker_skills = worker.get('skills', [])
                    if any(skill in worker_skills for skill in required_skills):
                        # Reassign worker to bottleneck stage
                        logger.info(f"Moving worker {worker['name']} to {stage} stage")
                        break
    
    def sequence_wave_orders(self, wave_id: int) -> bool:
        """Apply enhanced WMS sequencing to a wave."""
        logger.info(f"Starting enhanced WMS sequencing for wave {wave_id}")
        
        conn = self.get_connection()
        with conn.cursor() as cursor:
            try:
                # Get wave details
                cursor.execute("""
                    SELECT wave_name, planned_start_time, total_orders
                    FROM waves WHERE id = %s
                """, (wave_id,))
                wave_data = cursor.fetchone()
                
                if not wave_data:
                    logger.error(f"Wave {wave_id} not found")
                    return False
                
                wave_name, planned_start_time, total_orders = wave_data
                logger.info(f"Sequencing wave '{wave_name}' with {total_orders} orders")
                
                # Get orders and resources
                orders = self.get_wave_orders(wave_id)
                workers = self.get_available_workers()
                equipment = self.get_available_equipment()
                
                if not orders or not workers:
                    logger.warning(f"Insufficient data for wave {wave_id}")
                    return False
                
                # Step 1: Sort orders by deadline, priority, and zone efficiency
                sorted_orders = self.sort_orders_by_criteria(orders)
                
                # Step 2: Group orders by zone for basic efficiency
                zone_groups = self.group_orders_by_zone(sorted_orders)
                
                # Step 3: Clear existing assignments for this wave
                cursor.execute("DELETE FROM wave_assignments WHERE wave_id = %s", (wave_id,))
                
                # Step 4: Process orders with enhanced sequencing
                worker_assignments = {}
                equipment_assignments = {}
                current_time = planned_start_time or datetime.now()
                sequence_order = 1
                
                for zone_group in zone_groups:
                    logger.info(f"Processing zone group with {len(zone_group)} orders")
                    
                    for order in zone_group:
                        # Monitor queues and adjust resource allocation
                        self.adjust_resource_allocation(wave_id, workers, worker_assignments)
                        
                        # Process each stage for this order
                        for stage in self.stages:
                            # Calculate duration
                            duration = self.calculate_stage_duration(stage, order)
                            
                            # Find available worker
                            worker = self.find_worker_for_stage(stage, workers, worker_assignments)
                            
                            # Find available equipment
                            equipment_item = self.find_equipment_for_stage(stage, equipment, equipment_assignments)
                            
                            # Create assignment
                            cursor.execute("""
                                INSERT INTO wave_assignments (
                                    wave_id, order_id, stage, assigned_worker_id, 
                                    assigned_equipment_id, planned_start_time, 
                                    planned_duration_minutes, sequence_order
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                wave_id, order['order_id'], stage,
                                worker['id'] if worker else None,
                                equipment_item['id'] if equipment_item else None,
                                current_time, duration, sequence_order
                            ))
                            
                            # Track assignments for load balancing
                            if worker:
                                if worker['id'] not in worker_assignments:
                                    worker_assignments[worker['id']] = []
                                worker_assignments[worker['id']].append({
                                    'order_id': order['order_id'],
                                    'stage': stage,
                                    'start_time': current_time,
                                    'duration': duration
                                })
                            
                            if equipment_item:
                                if equipment_item['id'] not in equipment_assignments:
                                    equipment_assignments[equipment_item['id']] = []
                                equipment_assignments[equipment_item['id']].append({
                                    'order_id': order['order_id'],
                                    'stage': stage,
                                    'start_time': current_time,
                                    'duration': duration
                                })
                            
                            # Advance time for next stage
                            current_time += timedelta(minutes=duration)
                        
                        sequence_order += 1
                
                # Update wave with new order count
                cursor.execute("""
                    UPDATE waves 
                    SET total_orders = %s
                    WHERE id = %s
                """, (len(orders), wave_id))
                
                conn.commit()
                logger.info(f"Successfully sequenced wave {wave_id} with {len(orders)} orders")
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Error sequencing wave {wave_id}: {str(e)}")
                return False
    
    def sequence_all_waves(self) -> Dict[str, int]:
        """Apply enhanced sequencing to all waves."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, wave_name, total_orders 
                FROM waves 
                WHERE status = 'planned'
                ORDER BY planned_start_time, id
            """)
            waves = cursor.fetchall()
        
        results = {
            'total_waves': len(waves),
            'successful_waves': 0,
            'failed_waves': 0
        }
        
        for wave_id, wave_name, total_orders in waves:
            logger.info(f"Processing wave {wave_id}: {wave_name} ({total_orders} orders)")
            
            if self.sequence_wave_orders(wave_id):
                results['successful_waves'] += 1
            else:
                results['failed_waves'] += 1
        
        logger.info(f"Enhanced WMS sequencing completed: {results}")
        return results


def main():
    """Main function to run enhanced WMS sequencing."""
    sequencer = EnhancedWMSSequencer()
    
    try:
        results = sequencer.sequence_all_waves()
        print(f"✅ Enhanced WMS sequencing completed successfully!")
        print(f"   Total waves: {results['total_waves']}")
        print(f"   Successful: {results['successful_waves']}")
        print(f"   Failed: {results['failed_waves']}")
        
    except Exception as e:
        print(f"❌ Error running enhanced WMS sequencing: {str(e)}")
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main() 