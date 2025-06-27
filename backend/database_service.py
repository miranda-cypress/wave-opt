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