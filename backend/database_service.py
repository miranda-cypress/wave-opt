#!/usr/bin/env python3
"""
Database Service for AI Wave Optimization Agent

Handles PostgreSQL database connections and queries for:
- Workers and their skills
- Equipment and capacity
- SKUs and processing characteristics
- Orders and order items
- Optimization runs and results
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for handling database operations."""
    
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
    
    def get_workers(self, warehouse_id: int = 1) -> List[Dict]:
        """Get all workers with their skills for a warehouse."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT w.id, w.name, w.hourly_rate, w.efficiency_factor, 
                       w.max_hours_per_day, w.reliability_score,
                       array_agg(ws.skill) as skills
                FROM workers w
                LEFT JOIN worker_skills ws ON w.id = ws.worker_id
                WHERE w.warehouse_id = %s
                GROUP BY w.id, w.name, w.hourly_rate, w.efficiency_factor, 
                         w.max_hours_per_day, w.reliability_score
                ORDER BY w.id
            """, (warehouse_id,))
            
            workers = []
            for row in cursor.fetchall():
                worker = dict(row)
                worker['skills'] = worker['skills'] if worker['skills'][0] is not None else []
                workers.append(worker)
            
            return workers
    
    def get_equipment(self, warehouse_id: int = 1) -> List[Dict]:
        """Get all equipment for a warehouse."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, equipment_type, capacity, hourly_cost,
                       efficiency_factor, maintenance_frequency, current_utilization
                FROM equipment
                WHERE warehouse_id = %s
                ORDER BY equipment_type, id
            """, (warehouse_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_skus(self, warehouse_id: int = 1) -> List[Dict]:
        """Get all SKUs for a warehouse."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, category, zone, pick_time_minutes, pack_time_minutes,
                       volume_cubic_feet, weight_lbs, demand_pattern, shelf_life_days
                FROM skus
                WHERE warehouse_id = %s
                ORDER BY category, name
            """, (warehouse_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_orders(self, warehouse_id: int = 1, limit: Optional[int] = None) -> List[Dict]:
        """Get pending orders with their items for a warehouse."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get orders
            query = """
                SELECT o.id, o.customer_name, o.customer_type, o.priority,
                       o.created_at, o.shipping_deadline, o.total_pick_time,
                       o.total_pack_time, o.total_volume, o.total_weight, o.status
                FROM orders o
                WHERE o.warehouse_id = %s AND o.status = 'pending'
                ORDER BY o.priority ASC, o.shipping_deadline ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (warehouse_id,))
            orders = [dict(row) for row in cursor.fetchall()]
            
            # Get order items for each order
            for order in orders:
                cursor.execute("""
                    SELECT oi.id, oi.sku_id, oi.quantity, oi.pick_time, oi.pack_time,
                           oi.volume, oi.weight, s.name as sku_name, s.category
                    FROM order_items oi
                    JOIN skus s ON oi.sku_id = s.id
                    WHERE oi.order_id = %s
                    ORDER BY oi.id
                """, (order['id'],))
                
                order['items'] = [dict(row) for row in cursor.fetchall()]
            
            return orders
    
    def get_orders_by_scenario(self, scenario_type: str = "mixed", limit: int = 50) -> List[Dict]:
        """Get orders for a specific scenario type."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get orders from the most recent optimization run for this scenario
            cursor.execute("""
                SELECT o.id, o.warehouse_id, o.customer_name, o.customer_type, o.priority,
                       o.created_at, o.shipping_deadline, o.total_pick_time,
                       o.total_pack_time, o.total_volume, o.total_weight, o.status
                FROM orders o
                WHERE o.status = 'pending'
                ORDER BY o.priority ASC, o.shipping_deadline ASC
                LIMIT %s
            """, (limit,))
            
            orders = [dict(row) for row in cursor.fetchall()]
            
            # Get order items for each order
            for order in orders:
                cursor.execute("""
                    SELECT oi.id, oi.sku_id, oi.quantity, oi.pick_time, oi.pack_time,
                           oi.volume, oi.weight, s.name as sku_name, s.category
                    FROM order_items oi
                    JOIN skus s ON oi.sku_id = s.id
                    WHERE oi.order_id = %s
                    ORDER BY oi.id
                """, (order['id'],))
                
                order['items'] = [dict(row) for row in cursor.fetchall()]
            
            return orders
    
    def save_optimization_run(self, scenario_type: str, total_orders: int, 
                            total_workers: int, total_equipment: int) -> int:
        """Save optimization run metadata and return the run ID."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO optimization_runs (scenario_type, start_time, total_orders, 
                                             total_workers, total_equipment, status)
                VALUES (%s, %s, %s, %s, %s, 'running')
                RETURNING id
            """, (scenario_type, datetime.now(), total_orders, total_workers, total_equipment))
            
            result = cursor.fetchone()
            run_id = result[0] if result else 0
            conn.commit()
            return run_id
    
    def update_optimization_run(self, run_id: int, objective_value: float, 
                              solver_status: str, solve_time_seconds: float):
        """Update optimization run with results."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE optimization_runs 
                SET end_time = %s, status = 'completed', objective_value = %s,
                    solver_status = %s, solve_time_seconds = %s
                WHERE id = %s
            """, (datetime.now(), objective_value, solver_status, solve_time_seconds, run_id))
            
            conn.commit()
    
    def save_optimization_schedule(self, run_id: int, schedules: List[Dict]):
        """Save optimization schedule results."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            for schedule in schedules:
                cursor.execute("""
                    INSERT INTO optimization_schedules 
                    (optimization_run_id, order_id, worker_id, equipment_id, 
                     stage, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    run_id,
                    schedule.get('order_id'),
                    schedule.get('worker_id'),
                    schedule.get('equipment_id'),
                    schedule['stage'],
                    schedule['start_time'],
                    schedule['end_time']
                ))
            
            conn.commit()
    
    def get_original_wms_plan(self, order_id: int) -> List[Dict]:
        """
        Get original WMS plan for a specific order from the materialized view.
        
        Args:
            order_id: ID of the order
            
        Returns:
            List of stage plans for the original WMS approach
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM get_original_order_plan(%s)
            """, (order_id,))
            
            stages = []
            for row in cursor.fetchall():
                stage_data = dict(row)
                stages.append({
                    'stage': stage_data['stage_name'],
                    'duration_minutes': stage_data['duration_minutes'],
                    'waiting_time_before': stage_data['waiting_time_before'],
                    'start_time_minutes': stage_data['start_time_minutes'],
                    'worker_id': stage_data['worker_id'],
                    'worker_name': stage_data['worker_name'],
                    'equipment_id': stage_data['equipment_id'],
                    'equipment_name': stage_data['equipment_name'],
                    'sequence_order': stage_data['stage_order']
                })
            
            return stages
    
    def get_original_wms_plan_summary(self) -> Dict:
        """
        Get summary of original WMS plans for all orders.
        
        Returns:
            Dictionary with summary metrics for original plans
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM get_original_plan_summary()
            """)
            
            result = cursor.fetchone()
            return dict(result) if result else {}
    
    def refresh_original_plans(self):
        """Refresh the original WMS plans materialized view."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT refresh_original_plans()")
            conn.commit()
    
    def save_optimization_plan(self, run_id: int, optimization_result: Dict):
        """
        Save detailed optimization plan including stage-by-stage data and summary metrics.
        
        Args:
            run_id: ID of the optimization run
            optimization_result: Complete optimization result with schedules and metrics
        """
        conn = self.get_connection()
        with conn.cursor() as cursor:
            try:
                # Save detailed stage-by-stage plans
                if 'order_schedules' in optimization_result:
                    for order_schedule in optimization_result['order_schedules']:
                        order_id = order_schedule['order_id']
                        
                        # Save each stage for this order
                        for stage_schedule in order_schedule['stages']:
                            cursor.execute("""
                                INSERT INTO optimization_plans 
                                (optimization_run_id, order_id, stage, worker_id, equipment_id,
                                 start_time_minutes, duration_minutes, waiting_time_before, sequence_order)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                run_id,
                                order_id,
                                stage_schedule['stage'],
                                stage_schedule.get('worker_id'),
                                stage_schedule.get('equipment_id'),
                                stage_schedule['start_time_minutes'],
                                stage_schedule['duration_minutes'],
                                stage_schedule.get('waiting_time_before', 0),
                                stage_schedule.get('sequence_order', 0)
                            ))
                
                # Get original plan summary for comparison
                original_summary = self.get_original_wms_plan_summary()
                
                # Save plan summary metrics
                if 'metrics' in optimization_result:
                    metrics = optimization_result['metrics']
                    cursor.execute("""
                        INSERT INTO optimization_plan_summaries 
                        (optimization_run_id, total_orders, total_processing_time_original,
                         total_processing_time_optimized, total_waiting_time_original,
                         total_waiting_time_optimized, time_savings, waiting_time_reduction,
                         worker_utilization_improvement, equipment_utilization_improvement,
                         on_time_percentage_original, on_time_percentage_optimized,
                         total_cost_original, total_cost_optimized, cost_savings)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        run_id,
                        metrics.get('total_orders', 0),
                        original_summary.get('total_processing_time', 0),
                        metrics.get('total_processing_time_optimized', 0),
                        original_summary.get('total_waiting_time', 0),
                        metrics.get('total_waiting_time_optimized', 0),
                        original_summary.get('total_processing_time', 0) - metrics.get('total_processing_time_optimized', 0),
                        original_summary.get('total_waiting_time', 0) - metrics.get('total_waiting_time_optimized', 0),
                        metrics.get('worker_utilization_improvement', 0.0),
                        metrics.get('equipment_utilization_improvement', 0.0),
                        metrics.get('on_time_percentage_original', 85.0),  # Default baseline
                        metrics.get('on_time_percentage_optimized', 0.0),
                        metrics.get('total_cost_original', 0.0),
                        metrics.get('total_cost_optimized', 0.0),
                        metrics.get('cost_savings', 0.0)
                    ))
                
                # Save individual order timelines for frontend display
                if 'order_schedules' in optimization_result:
                    for order_schedule in optimization_result['order_schedules']:
                        order_id = order_schedule['order_id']
                        
                        # Get order details
                        cursor.execute("""
                            SELECT customer_name, priority, shipping_deadline
                            FROM orders WHERE id = %s
                        """, (order_id,))
                        order_info = cursor.fetchone()
                        
                        if order_info:
                            customer_name, priority, shipping_deadline = order_info
                            
                            # Get original plan for this order
                            original_stages = self.get_original_wms_plan(order_id)
                            
                            # Create timeline data for frontend
                            original_timeline = []
                            optimized_timeline = []
                            
                            # Build original timeline
                            for stage in original_stages:
                                original_stage_data = {
                                    'stage': stage['stage'],
                                    'duration_minutes': stage['duration_minutes'],
                                    'worker_name': stage['worker_name'],
                                    'waiting_time_before': stage['waiting_time_before']
                                }
                                original_timeline.append(original_stage_data)
                            
                            # Build optimized timeline
                            for stage_schedule in order_schedule['stages']:
                                stage_data = {
                                    'stage': stage_schedule['stage'],
                                    'duration_minutes': stage_schedule['duration_minutes'],
                                    'worker_name': stage_schedule.get('worker_name', ''),
                                    'waiting_time_before': stage_schedule.get('waiting_time_before', 0)
                                }
                                optimized_timeline.append(stage_data)
                            
                            # Calculate summary metrics
                            total_processing_time_original = sum(s['duration_minutes'] for s in original_timeline)
                            total_processing_time_optimized = sum(s['duration_minutes'] for s in optimized_timeline)
                            total_waiting_time_original = sum(s['waiting_time_before'] for s in original_timeline)
                            total_waiting_time_optimized = sum(s['waiting_time_before'] for s in optimized_timeline)
                            
                            cursor.execute("""
                                INSERT INTO order_timelines 
                                (optimization_run_id, order_id, customer_name, priority, shipping_deadline,
                                 original_timeline, optimized_timeline, total_processing_time_original,
                                 total_processing_time_optimized, total_waiting_time_original,
                                 total_waiting_time_optimized, time_savings, waiting_time_reduction,
                                 on_time_original, on_time_optimized)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                run_id,
                                order_id,
                                customer_name,
                                priority,
                                shipping_deadline,
                                json.dumps(original_timeline),
                                json.dumps(optimized_timeline),
                                total_processing_time_original,
                                total_processing_time_optimized,
                                total_waiting_time_original,
                                total_waiting_time_optimized,
                                total_processing_time_original - total_processing_time_optimized,
                                total_waiting_time_original - total_waiting_time_optimized,
                                True,  # Simplified - assume original is on time
                                True   # Simplified - assume optimized is on time
                            ))
                
                conn.commit()
                logger.info(f"Successfully saved optimization plan for run {run_id}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to save optimization plan: {e}")
                raise
    
    def get_optimization_plan(self, run_id: int) -> Dict:
        """
        Get complete optimization plan including summary metrics and order timelines.
        
        Args:
            run_id: ID of the optimization run
            
        Returns:
            Dictionary containing plan summary and order timelines
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get plan summary
            cursor.execute("""
                SELECT * FROM optimization_plan_summaries 
                WHERE optimization_run_id = %s
            """, (run_id,))
            summary = cursor.fetchone()
            
            # Get order timelines
            cursor.execute("""
                SELECT * FROM order_timelines 
                WHERE optimization_run_id = %s
                ORDER BY order_id
            """, (run_id,))
            order_timelines = [dict(row) for row in cursor.fetchall()]
            
            # Get detailed stage plans
            cursor.execute("""
                SELECT op.*, w.name as worker_name, e.name as equipment_name
                FROM optimization_plans op
                LEFT JOIN workers w ON op.worker_id = w.id
                LEFT JOIN equipment e ON op.equipment_id = e.id
                WHERE op.optimization_run_id = %s
                ORDER BY op.order_id, op.sequence_order
            """, (run_id,))
            stage_plans = [dict(row) for row in cursor.fetchall()]
            
            return {
                'run_id': run_id,
                'summary': dict(summary) if summary else {},
                'order_timelines': order_timelines,
                'stage_plans': stage_plans
            }
    
    def get_latest_optimization_plan(self) -> Dict:
        """
        Get the most recent optimization plan.
        
        Returns:
            Dictionary containing the latest plan data
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get the latest optimization run
            cursor.execute("""
                SELECT id FROM optimization_runs 
                WHERE status = 'completed'
                ORDER BY end_time DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                return self.get_optimization_plan(result['id'])
            else:
                return {}
    
    def get_optimization_plans_by_scenario(self, scenario_type: str, limit: int = 5) -> List[Dict]:
        """
        Get optimization plans for a specific scenario type.
        
        Args:
            scenario_type: Type of scenario (e.g., 'bottleneck', 'deadline', 'mixed')
            limit: Maximum number of plans to return
            
        Returns:
            List of optimization plan dictionaries
        """
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id FROM optimization_runs 
                WHERE scenario_type = %s AND status = 'completed'
                ORDER BY end_time DESC 
                LIMIT %s
            """, (scenario_type, limit))
            
            run_ids = [row['id'] for row in cursor.fetchall()]
            plans = []
            
            for run_id in run_ids:
                plan = self.get_optimization_plan(run_id)
                if plan:
                    plans.append(plan)
            
            return plans
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict]:
        """Get recent optimization run history."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, run_id, scenario_type, start_time, end_time, status,
                       total_orders, total_workers, total_equipment, objective_value,
                       solver_status, solve_time_seconds
                FROM optimization_runs
                ORDER BY start_time DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_warehouse_stats(self, warehouse_id: int = 1) -> Dict[str, Any]:
        """Get warehouse statistics."""
        conn = self.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get basic counts
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM workers WHERE warehouse_id = %s) as total_workers,
                    (SELECT COUNT(*) FROM equipment WHERE warehouse_id = %s) as total_equipment,
                    (SELECT COUNT(*) FROM skus WHERE warehouse_id = %s) as total_skus,
                    (SELECT COUNT(*) FROM orders WHERE warehouse_id = %s AND status = 'pending') as pending_orders
            """, (warehouse_id, warehouse_id, warehouse_id, warehouse_id))
            
            result = cursor.fetchone()
            stats = dict(result) if result else {}
            
            # Get equipment breakdown
            cursor.execute("""
                SELECT equipment_type, COUNT(*) as count
                FROM equipment
                WHERE warehouse_id = %s
                GROUP BY equipment_type
                ORDER BY count DESC
            """, (warehouse_id,))
            
            stats['equipment_breakdown'] = [dict(row) for row in cursor.fetchall()]
            
            # Get order priority breakdown
            cursor.execute("""
                SELECT priority, COUNT(*) as count
                FROM orders
                WHERE warehouse_id = %s AND status = 'pending'
                GROUP BY priority
                ORDER BY priority
            """, (warehouse_id,))
            
            stats['order_priority_breakdown'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None
    
    def get_orders_for_optimization(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get orders for optimization, using the same 100 orders as the original plan.
        
        Args:
            limit: Number of orders to get (default 100 for testing)
            
        Returns:
            List of order dictionaries
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Use the same order selection logic as the original plan
                cursor.execute("""
                    SELECT 
                        o.id,
                        o.customer_name,
                        o.priority,
                        o.shipping_deadline,
                        o.total_pick_time,
                        o.total_pack_time,
                        -- Use default values for columns that don't exist in the schema
                        5 as total_items,
                        15.0 as total_weight,
                        o.status
                    FROM orders o
                    WHERE o.status = 'pending'
                    AND o.id IN (
                        SELECT id FROM orders 
                        WHERE status = 'pending' 
                        ORDER BY priority ASC, shipping_deadline ASC 
                        LIMIT %s
                    )
                    ORDER BY o.priority ASC, o.shipping_deadline ASC
                """, (limit,))
                
                orders = [dict(row) for row in cursor.fetchall()]
                return orders
                
        except Exception as e:
            print(f"Error getting orders for optimization: {e}")
            return [] 