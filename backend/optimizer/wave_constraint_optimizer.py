"""
OR-Tools Constraint Programming Optimizer for Wave Optimization

Implements a comprehensive constraint programming model for warehouse wave optimization
with 6 stages: pick, consolidate, pack, label, stage, ship

Features:
- Multi-skilled workers with proficiency levels
- Equipment capacity constraints
- Shipping deadline penalties
- Stage precedence constraints
- Multi-objective optimization
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Optional
import time
from datetime import datetime, timedelta
import math
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import traceback
import sys

class WaveConstraintOptimizer:
    """OR-Tools Constraint Programming optimizer for wave optimization."""
    
    def __init__(self):
        self.model = None
        self.solver = None
        self.stages = ['pick', 'consolidate', 'pack', 'label', 'stage', 'ship']
        self.stage_durations = {
            'pick': 15,      # minutes per order
            'consolidate': 10,
            'pack': 20,
            'label': 5,
            'stage': 8,
            'ship': 12
        }
        self.stage_precedence = {
            'pick': [],
            'consolidate': ['pick'],
            'pack': ['consolidate'],
            'label': ['pack'],
            'stage': ['label'],
            'ship': ['stage']
        }
        
    def get_wave_data(self, wave_id: int) -> Dict:
        """Get wave data from database with diagnostics."""
        logger = logging.getLogger("WaveConstraintOptimizer")
        conn = None
        try:
            # Try multiple database connection configurations
            connection_configs = [
                {
                    "host": "localhost",
                    "port": 5432,  # Standard PostgreSQL port
                    "database": "warehouse_opt",
                    "user": "wave_user",
                    "password": "wave_password"
                },
                {
                    "host": "localhost", 
                    "port": 5433,  # Alternative port
                    "database": "warehouse_opt",
                    "user": "wave_user",
                    "password": "wave_password"
                }
            ]
            
            for config in connection_configs:
                try:
                    logger.info(f"Attempting database connection with config: {config}")
                    conn = psycopg2.connect(**config)
                    logger.info(f"Successfully connected to database for wave_id={wave_id}")
                    break
                except Exception as conn_error:
                    logger.warning(f"Failed to connect with config {config}: {conn_error}")
                    continue
            
            if not conn:
                logger.error("Failed to connect to database with any configuration")
                return {"error": "Database connection failed"}
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get wave details with better error handling
                try:
                    cursor.execute("""
                        SELECT w.*, wa.order_id, o.order_number, o.shipping_deadline, 
                               CASE 
                                   WHEN o.priority = 1 THEN 'high'
                                   WHEN o.priority = 2 THEN 'high'
                                   WHEN o.priority = 3 THEN 'medium'
                                   WHEN o.priority = 4 THEN 'low'
                                   WHEN o.priority = 5 THEN 'low'
                                   ELSE 'medium'
                               END as priority,
                               o.customer_id, c.customer_type,
                               COALESCE(w.planned_start_time, NOW()) as planned_start_time
                        FROM waves w
                        JOIN wave_assignments wa ON w.id = wa.wave_id
                        JOIN orders o ON wa.order_id = o.id
                        JOIN customers c ON o.customer_id = c.id
                        WHERE w.id = %s
                        ORDER BY wa.sequence_order
                    """, (wave_id,))
                    wave_data = cursor.fetchall()
                    if not wave_data:
                        logger.error(f"No orders found for wave_id={wave_id}")
                        return {"error": f"No orders found for wave_id={wave_id}"}
                except Exception as e:
                    logger.error(f"Error fetching wave data: {e}")
                    return {"error": f"Error fetching wave data: {e}"}
                
                # Get workers and their skills
                try:
                    cursor.execute("""
                        SELECT w.id, w.worker_code, w.name, w.hourly_rate,
                               COALESCE(ws.skill, 'general') as skill_name, 
                               COALESCE(ws.proficiency_level, 1) as proficiency_level
                        FROM workers w
                        LEFT JOIN worker_skills ws ON w.id = ws.worker_id
                        WHERE w.warehouse_id = 1
                        ORDER BY w.id, ws.skill
                    """)
                    workers_data = cursor.fetchall()
                    if not workers_data:
                        logger.error("No workers found for warehouse_id=1")
                        return {"error": "No workers found for warehouse_id=1"}
                except Exception as e:
                    logger.error(f"Error fetching workers: {e}")
                    return {"error": f"Error fetching workers: {e}"}
                
                # Get equipment
                try:
                    cursor.execute("""
                        SELECT id, equipment_code, equipment_type, capacity, hourly_cost
                        FROM equipment
                        WHERE warehouse_id = 1
                    """)
                    equipment_data = cursor.fetchall()
                    if not equipment_data:
                        logger.error("No equipment found for warehouse_id=1")
                        return {"error": "No equipment found for warehouse_id=1"}
                except Exception as e:
                    logger.error(f"Error fetching equipment: {e}")
                    return {"error": f"Error fetching equipment: {e}"}
                
                # Validate and clean required fields in orders
                cleaned_wave_data = []
                for order in wave_data:
                    cleaned_order = dict(order)
                    # Ensure required fields have default values
                    if cleaned_order.get('shipping_deadline') is None:
                        cleaned_order['shipping_deadline'] = datetime.now() + timedelta(hours=24)
                    if cleaned_order.get('priority') is None:
                        cleaned_order['priority'] = 'medium'
                    if cleaned_order.get('customer_type') is None:
                        cleaned_order['customer_type'] = 'standard'
                    if cleaned_order.get('planned_start_time') is None:
                        cleaned_order['planned_start_time'] = datetime.now()
                    
                    cleaned_wave_data.append(cleaned_order)
                
                logger.info(f"Fetched {len(cleaned_wave_data)} orders, {len(workers_data)} workers, {len(equipment_data)} equipment for wave_id={wave_id}")
                return {
                    'wave_data': cleaned_wave_data,
                    'workers': workers_data,
                    'equipment': equipment_data
                }
        except Exception as e:
            logger.error(f"Database error for wave_id={wave_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Database error: {e}"}
        finally:
            if conn:
                conn.close()
    
    def create_optimization_model(self, wave_data: Dict) -> bool:
        """Create the constraint programming model with diagnostics."""
        logger = logging.getLogger("WaveConstraintOptimizer")
        try:
            logger.info("Starting model creation...")
            self.model = cp_model.CpModel()
            logger.info("Created CP model instance")
            
            # Extract data
            orders = wave_data.get('wave_data', [])
            workers = wave_data.get('workers', [])
            equipment = wave_data.get('equipment', [])
            logger.info(f"Model creation input: {len(orders)} orders, {len(workers)} workers, {len(equipment)} equipment.")
            logger.info(f"Orders type: {type(orders)}, Workers type: {type(workers)}, Equipment type: {type(equipment)}")
            
            # Validate data
            if not orders:
                logger.error("No orders provided to model.")
                return False
            if not workers:
                logger.error("No workers provided to model.")
                return False
            if not equipment:
                logger.error("No equipment provided to model.")
                return False
            
            # Ensure we have valid data structures
            if not isinstance(orders, list) or not isinstance(workers, list) or not isinstance(equipment, list):
                logger.error("Invalid data types - expected lists for orders, workers, and equipment")
                return False
            
            num_orders = len(orders)
            num_workers = len(set(w.get('id', 0) for w in workers if w.get('id') is not None))
            num_equipment = len(equipment)
            
            # Safety checks for model size
            if num_orders > 100:
                logger.warning(f"Large number of orders ({num_orders}), this may cause performance issues")
            if num_workers > 50:
                logger.warning(f"Large number of workers ({num_workers}), this may cause performance issues")
            
            logger.info(f"Model parameters: num_orders={num_orders}, num_workers={num_workers}, num_equipment={num_equipment}")
            
            # Time horizon (24 hours in minutes)
            horizon = 24 * 60
            logger.info(f"Time horizon set to {horizon} minutes")
            
            # Use planned_start_time from the first order as the base
            planned_start_time = orders[0].get('planned_start_time')
            if planned_start_time is None:
                logger.warning("No planned_start_time found in orders, using current time")
                base_time = datetime.now()
            else:
                if isinstance(planned_start_time, datetime):
                    base_time = planned_start_time.replace(tzinfo=None)
                else:
                    try:
                        base_time = datetime.fromisoformat(str(planned_start_time))
                    except:
                        logger.warning("Invalid planned_start_time format, using current time")
                        base_time = datetime.now()
            
            logger.info(f"Base time set to: {base_time}")
            
            # Decision Variables
            logger.info("Creating decision variables...")
            # 1. Start time for each order at each stage
            start_times = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    start_times[order_idx, stage] = self.model.NewIntVar(
                        0, horizon, f'start_{order_idx}_{stage}'
                    )
            logger.info(f"Created {len(start_times)} start time variables")
            
            # 2. Worker assignment for each order at each stage
            worker_assignments = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    worker_assignments[order_idx, stage] = self.model.NewIntVar(
                        0, num_workers - 1, f'worker_{order_idx}_{stage}'
                    )
            logger.info(f"Created {len(worker_assignments)} worker assignment variables")
            
            # 3. Equipment usage for each order at each stage
            equipment_usage = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    equipment_usage[order_idx, stage] = self.model.NewIntVar(
                        0, num_equipment - 1, f'equipment_{order_idx}_{stage}'
                    )
            logger.info(f"Created {len(equipment_usage)} equipment usage variables")
            
            # Constraints
            logger.info("Creating constraints...")
            
            # 1. Stage precedence constraints
            logger.info("Creating stage precedence constraints...")
            for order_idx in range(num_orders):
                for stage in self.stages:
                    for prereq_stage in self.stage_precedence[stage]:
                        # Current stage must start after prerequisite stage ends
                        prereq_end = start_times[order_idx, prereq_stage] + self.stage_durations[prereq_stage]
                        self.model.Add(start_times[order_idx, stage] >= prereq_end)
            logger.info("Stage precedence constraints created")
            
            # 2. Worker capacity constraints (one worker can only work on one order at a time)
            logger.info("Creating worker capacity constraints...")
            try:
                for worker_id in range(num_workers):
                    for stage in self.stages:
                        # Create intervals for each order that could be assigned to this worker
                        intervals = []
                        for order_idx in range(num_orders):
                            # Check if worker has the required skill for this stage
                            worker_has_skill = False
                            for w in workers:
                                if w.get('id') == worker_id and w.get('skill_name') == stage:
                                    worker_has_skill = True
                                    break
                            # Also check for skill mappings (e.g., 'picking' -> 'pick')
                            if not worker_has_skill:
                                skill_mapping = {
                                    'pick': 'picking',
                                    'pack': 'packing',
                                    'ship': 'shipping',
                                    'consolidate': 'consolidation',
                                    'label': 'labeling',
                                    'stage': 'staging'
                                }
                                mapped_skill = skill_mapping.get(stage, stage)
                                for w in workers:
                                    if w.get('id') == worker_id and w.get('skill_name') == mapped_skill:
                                        worker_has_skill = True
                                        break
                            
                            # If no specific skill found, assume general worker can do any task
                            if not worker_has_skill:
                                worker_has_skill = True
                            
                            if worker_has_skill:
                                try:
                                    interval = self.model.NewIntervalVar(
                                        start_times[order_idx, stage],
                                        self.stage_durations[stage],
                                        start_times[order_idx, stage] + self.stage_durations[stage],
                                        f'interval_{order_idx}_{stage}_{worker_id}'
                                    )
                                    intervals.append(interval)
                                except Exception as interval_error:
                                    logger.warning(f"Failed to create interval for order {order_idx}, stage {stage}, worker {worker_id}: {interval_error}")
                                    continue
                        
                        # No overlap constraint for this worker at this stage
                        if len(intervals) > 1:
                            try:
                                self.model.AddNoOverlap(intervals)
                            except Exception as overlap_error:
                                logger.warning(f"Failed to add no-overlap constraint for worker {worker_id}, stage {stage}: {overlap_error}")
                logger.info("Worker capacity constraints created")
            except Exception as e:
                logger.error(f"Error creating worker capacity constraints: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            # 3. Equipment capacity constraints
            logger.info("Creating equipment capacity constraints...")
            try:
                for equip_id in range(num_equipment):
                    for stage in self.stages:
                        intervals = []
                        for order_idx in range(num_orders):
                            try:
                                interval = self.model.NewIntervalVar(
                                    start_times[order_idx, stage],
                                    self.stage_durations[stage],
                                    start_times[order_idx, stage] + self.stage_durations[stage],
                                    f'equip_interval_{order_idx}_{stage}_{equip_id}'
                                )
                                intervals.append(interval)
                            except Exception as interval_error:
                                logger.warning(f"Failed to create equipment interval for order {order_idx}, stage {stage}, equipment {equip_id}: {interval_error}")
                                continue
                        
                        if len(intervals) > 1:
                            try:
                                self.model.AddNoOverlap(intervals)
                            except Exception as overlap_error:
                                logger.warning(f"Failed to add equipment no-overlap constraint for equipment {equip_id}, stage {stage}: {overlap_error}")
                logger.info("Equipment capacity constraints created")
            except Exception as e:
                logger.error(f"Error creating equipment capacity constraints: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            # 4. Shipping deadline constraints
            logger.info("Creating shipping deadline constraints...")
            deadline_penalties = []
            try:
                for order_idx, order in enumerate(orders):
                    shipping_deadline = order.get('shipping_deadline')
                    if shipping_deadline:
                        try:
                            # Convert to minutes relative to planned_start_time
                            if isinstance(shipping_deadline, datetime):
                                deadline_time = int((shipping_deadline - base_time).total_seconds() // 60)
                            else:
                                # Try to parse string deadline
                                try:
                                    deadline_dt = datetime.fromisoformat(str(shipping_deadline))
                                    deadline_time = int((deadline_dt - base_time).total_seconds() // 60)
                                except:
                                    logger.warning(f"Invalid deadline format for order {order_idx}, skipping deadline constraint")
                                    continue
                            
                            ship_end_time = start_times[order_idx, 'ship'] + self.stage_durations['ship']
                            
                            # Penalty for missing deadline
                            missed_deadline = self.model.NewBoolVar(f'missed_deadline_{order_idx}')
                            self.model.Add(ship_end_time > deadline_time).OnlyEnforceIf(missed_deadline)
                            self.model.Add(ship_end_time <= deadline_time).OnlyEnforceIf(missed_deadline.Not())
                            
                            # Penalty based on priority and customer type
                            penalty_weight = 1
                            priority = order.get('priority', 'medium')
                            if priority == 'high':
                                penalty_weight = 3
                            elif priority == 'medium':
                                penalty_weight = 2
                            
                            customer_type = order.get('customer_type', 'standard')
                            if customer_type == 'premium':
                                penalty_weight *= 2
                            
                            deadline_penalties.append(missed_deadline * penalty_weight * 100)
                        except Exception as deadline_error:
                            logger.warning(f"Failed to create deadline constraint for order {order_idx}: {deadline_error}")
                            continue
                logger.info("Shipping deadline constraints created")
            except Exception as e:
                logger.error(f"Error creating deadline constraints: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            # 5. Worker assignment constraints (worker must have required skill)
            logger.info("Creating worker assignment constraints...")
            try:
                for order_idx in range(num_orders):
                    for stage in self.stages:
                        # Get workers with this skill
                        skilled_workers = []
                        for w in workers:
                            if w.get('skill_name') == stage:
                                skilled_workers.append(w.get('id', 0))
                        # Also check for skill mappings
                        if not skilled_workers:
                            skill_mapping = {
                                'pick': 'picking',
                                'pack': 'packing',
                                'ship': 'shipping',
                                'consolidate': 'consolidation',
                                'label': 'labeling',
                                'stage': 'staging'
                            }
                            mapped_skill = skill_mapping.get(stage, stage)
                            for w in workers:
                                if w.get('skill_name') == mapped_skill:
                                    skilled_workers.append(w.get('id', 0))
                        
                        # If no skilled workers found, allow any worker (fallback)
                        if not skilled_workers:
                            skilled_workers = list(range(num_workers))
                        
                        if skilled_workers:
                            try:
                                # Worker assignment must be one of the skilled workers
                                self.model.AddAllowedAssignments(
                                    [worker_assignments[order_idx, stage]], 
                                    [skilled_workers]
                                )
                            except Exception as assignment_error:
                                logger.warning(f"Failed to add worker assignment constraint for order {order_idx}, stage {stage}: {assignment_error}")
                                continue
                logger.info("Worker assignment constraints created")
            except Exception as e:
                logger.error(f"Error creating worker assignment constraints: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            # Objective Function: Multi-objective optimization
            logger.info("Creating objective function...")
            try:
                # 1. Minimize total completion time
                completion_times = []
                for order_idx in range(num_orders):
                    completion_time = start_times[order_idx, 'ship'] + self.stage_durations['ship']
                    completion_times.append(completion_time)
                
                max_completion_time = self.model.NewIntVar(0, horizon, 'max_completion')
                self.model.AddMaxEquality(max_completion_time, completion_times)
                
                # 2. Minimize labor cost (simplified)
                total_labor_cost = self.model.NewIntVar(0, 10000, 'total_labor_cost')
                # Use a simplified labor cost calculation
                labor_cost_terms = []
                for order_idx in range(num_orders):
                    for stage in self.stages:
                        # Default hourly rate of 25
                        stage_cost = int((self.stage_durations[stage] / 60) * 25)
                        labor_cost_terms.append(stage_cost)
                
                self.model.Add(total_labor_cost == sum(labor_cost_terms))
                
                # 3. Minimize equipment cost (simplified)
                total_equipment_cost = self.model.NewIntVar(0, 5000, 'total_equipment_cost')
                # Use a simplified equipment cost calculation
                equipment_cost_terms = []
                for order_idx in range(num_orders):
                    for stage in self.stages:
                        # Default hourly cost of 10
                        stage_equip_cost = int((self.stage_durations[stage] / 60) * 10)
                        equipment_cost_terms.append(stage_equip_cost)
                
                self.model.Add(total_equipment_cost == sum(equipment_cost_terms))
                
                # Combined objective with weights
                deadline_penalty = sum(deadline_penalties) if deadline_penalties else 0
                
                # Multi-objective function
                objective = (
                    max_completion_time * 1 +           # Minimize makespan
                    total_labor_cost * 0.1 +            # Minimize labor cost
                    total_equipment_cost * 0.05 +       # Minimize equipment cost
                    deadline_penalty                    # Minimize deadline violations
                )
                
                self.model.Minimize(objective)
                logger.info("Objective function created successfully")
            except Exception as e:
                logger.error(f"Error creating objective function: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            logger.info("Model creation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Exception during model creation: {e}\n{traceback.format_exc()}")
            logger.error(f"Orders snapshot: {orders}")
            logger.error(f"Workers snapshot: {workers}")
            logger.error(f"Equipment snapshot: {equipment}")
            return False
    
    def solve_optimization(self, time_limit: int = 300) -> Dict:
        """Solve the optimization problem."""
        if not self.model:
            return {"error": "Model not created"}
        
        try:
            self.solver = cp_model.CpSolver()
            self.solver.parameters.max_time_in_seconds = time_limit
            
            start_time = time.time()
            status = self.solver.Solve(self.model)
            solve_time = time.time() - start_time
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return {
                    "status": "success",
                    "solve_time": solve_time,
                    "objective_value": self.solver.ObjectiveValue(),
                    "solution": self.extract_solution()
                }
            else:
                return {
                    "status": "no_solution",
                    "solve_time": solve_time,
                    "error": f"Solver status: {status}"
                }
                
        except Exception as e:
            return {"error": f"Solve error: {e}"}
    
    def extract_solution(self) -> Dict:
        """Extract the solution from the solver."""
        if not self.solver:
            return {}
        
        solution = {
            "orders": [],
            "workers": [],
            "equipment": [],
            "schedule": []
        }
        
        # Extract order assignments and timing
        # This would need to be implemented based on the actual variable structure
        
        return solution
    
    def optimize_wave(self, wave_id: int, time_limit: int = 300) -> Dict:
        """Main optimization method for a wave."""
        logger = logging.getLogger("WaveConstraintOptimizer")
        
        try:
            # Get wave data
            wave_data = self.get_wave_data(wave_id)
            if not wave_data:
                return {"error": "Failed to get wave data"}
            
            # Try constraint programming optimization first
            logger.info(f"Attempting constraint programming optimization for wave {wave_id}")
            
            if self.create_optimization_model(wave_data):
                result = self.solve_optimization(time_limit)
                
                if not result.get("error"):
                    # Add wave information
                    result["wave_id"] = wave_id
                    result["num_orders"] = len(wave_data['wave_data'])
                    result["num_workers"] = len(set(w.get('id', 0) for w in wave_data['workers']))
                    result["num_equipment"] = len(wave_data['equipment'])
                    result["optimization_type"] = "constraint_programming"
                    
                    logger.info(f"Constraint programming optimization successful for wave {wave_id}")
                    return result
                else:
                    logger.warning(f"Constraint programming solver failed: {result.get('error')}")
            else:
                logger.warning("Failed to create constraint programming model")
            
            # Fallback to simple optimizer
            logger.info(f"Falling back to simple optimizer for wave {wave_id}")
            try:
                from .simple_wave_optimizer import SimpleWaveOptimizer
                simple_optimizer = SimpleWaveOptimizer()
                fallback_result = simple_optimizer.optimize_wave(wave_data)
                
                if not fallback_result.get("error"):
                    fallback_result["wave_id"] = wave_id
                    fallback_result["optimization_type"] = "simple_fallback"
                    logger.info(f"Simple optimizer fallback successful for wave {wave_id}")
                    return fallback_result
                else:
                    logger.error(f"Simple optimizer fallback also failed: {fallback_result.get('error')}")
                    return fallback_result
                    
            except ImportError as e:
                logger.error(f"Failed to import simple optimizer: {e}")
                return {"error": "Both constraint programming and simple optimizer failed"}
            except Exception as e:
                logger.error(f"Simple optimizer error: {e}")
                return {"error": f"Simple optimizer failed: {e}"}
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Optimization error: {e}"}

# Example usage
if __name__ == "__main__":
    optimizer = WaveConstraintOptimizer()
    result = optimizer.optimize_wave(1)
    print(result) 