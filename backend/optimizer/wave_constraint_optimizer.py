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
        """Get wave data from database."""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="warehouse_opt",
                user="wave_user",
                password="wave_password"
            )
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get wave details
                cursor.execute("""
                    SELECT w.*, wa.order_id, o.order_number, o.shipping_deadline, o.priority,
                           o.customer_id, c.customer_type
                    FROM waves w
                    JOIN wave_assignments wa ON w.id = wa.wave_id
                    JOIN orders o ON wa.order_id = o.id
                    JOIN customers c ON o.customer_id = c.id
                    WHERE w.id = %s
                    ORDER BY wa.assignment_order
                """, (wave_id,))
                
                wave_data = cursor.fetchall()
                
                # Get workers and their skills
                cursor.execute("""
                    SELECT w.id, w.worker_code, w.name, w.hourly_rate,
                           ws.skill_name, ws.proficiency_level
                    FROM workers w
                    LEFT JOIN worker_skills ws ON w.id = ws.worker_id
                    WHERE w.warehouse_id = 1
                    ORDER BY w.id, ws.skill_name
                """)
                
                workers_data = cursor.fetchall()
                
                # Get equipment
                cursor.execute("""
                    SELECT id, equipment_code, equipment_type, capacity, hourly_cost
                    FROM equipment
                    WHERE warehouse_id = 1
                """)
                
                equipment_data = cursor.fetchall()
                
                return {
                    'wave_data': wave_data,
                    'workers': workers_data,
                    'equipment': equipment_data
                }
                
        except Exception as e:
            print(f"Database error: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def create_optimization_model(self, wave_data: Dict) -> bool:
        """Create the constraint programming model."""
        try:
            self.model = cp_model.CpModel()
            
            # Extract data
            orders = wave_data['wave_data']
            workers = wave_data['workers']
            equipment = wave_data['equipment']
            
            num_orders = len(orders)
            num_workers = len(set(w['id'] for w in workers))
            num_equipment = len(equipment)
            
            # Time horizon (24 hours in minutes)
            horizon = 24 * 60
            
            # Decision Variables
            # 1. Start time for each order at each stage
            start_times = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    start_times[order_idx, stage] = self.model.NewIntVar(
                        0, horizon, f'start_{order_idx}_{stage}'
                    )
            
            # 2. Worker assignment for each order at each stage
            worker_assignments = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    worker_assignments[order_idx, stage] = self.model.NewIntVar(
                        0, num_workers - 1, f'worker_{order_idx}_{stage}'
                    )
            
            # 3. Equipment usage for each order at each stage
            equipment_usage = {}
            for order_idx in range(num_orders):
                for stage in self.stages:
                    equipment_usage[order_idx, stage] = self.model.NewIntVar(
                        0, num_equipment - 1, f'equipment_{order_idx}_{stage}'
                    )
            
            # Constraints
            
            # 1. Stage precedence constraints
            for order_idx in range(num_orders):
                for stage in self.stages:
                    for prereq_stage in self.stage_precedence[stage]:
                        # Current stage must start after prerequisite stage ends
                        prereq_end = start_times[order_idx, prereq_stage] + self.stage_durations[prereq_stage]
                        self.model.Add(start_times[order_idx, stage] >= prereq_end)
            
            # 2. Worker capacity constraints (one worker can only work on one order at a time)
            for worker_id in range(num_workers):
                for stage in self.stages:
                    # Create intervals for each order that could be assigned to this worker
                    intervals = []
                    for order_idx in range(num_orders):
                        # Check if worker has the required skill for this stage
                        worker_has_skill = False
                        for w in workers:
                            if w['id'] == worker_id and w['skill_name'] == stage:
                                worker_has_skill = True
                                break
                        
                        if worker_has_skill:
                            interval = self.model.NewIntervalVar(
                                start_times[order_idx, stage],
                                self.stage_durations[stage],
                                start_times[order_idx, stage] + self.stage_durations[stage],
                                f'interval_{order_idx}_{stage}_{worker_id}'
                            )
                            intervals.append(interval)
                    
                    # No overlap constraint for this worker at this stage
                    if len(intervals) > 1:
                        self.model.AddNoOverlap(intervals)
            
            # 3. Equipment capacity constraints
            for equip_id in range(num_equipment):
                for stage in self.stages:
                    intervals = []
                    for order_idx in range(num_orders):
                        interval = self.model.NewIntervalVar(
                            start_times[order_idx, stage],
                            self.stage_durations[stage],
                            start_times[order_idx, stage] + self.stage_durations[stage],
                            f'equip_interval_{order_idx}_{stage}_{equip_id}'
                        )
                        intervals.append(interval)
                    
                    if len(intervals) > 1:
                        self.model.AddNoOverlap(intervals)
            
            # 4. Shipping deadline constraints
            deadline_penalties = []
            for order_idx, order in enumerate(orders):
                if order['shipping_deadline']:
                    deadline_time = order['shipping_deadline'].timestamp() / 60  # Convert to minutes
                    ship_end_time = start_times[order_idx, 'ship'] + self.stage_durations['ship']
                    
                    # Penalty for missing deadline
                    missed_deadline = self.model.NewBoolVar(f'missed_deadline_{order_idx}')
                    self.model.Add(ship_end_time > deadline_time).OnlyEnforceIf(missed_deadline)
                    self.model.Add(ship_end_time <= deadline_time).OnlyEnforceIf(missed_deadline.Not())
                    
                    # Penalty based on priority and customer type
                    penalty_weight = 1
                    if order['priority'] == 'high':
                        penalty_weight = 3
                    elif order['priority'] == 'medium':
                        penalty_weight = 2
                    
                    if order['customer_type'] == 'premium':
                        penalty_weight *= 2
                    
                    deadline_penalties.append(missed_deadline * penalty_weight * 100)
            
            # 5. Worker assignment constraints (worker must have required skill)
            for order_idx in range(num_orders):
                for stage in self.stages:
                    # Get workers with this skill
                    skilled_workers = []
                    for w in workers:
                        if w['skill_name'] == stage:
                            skilled_workers.append(w['id'])
                    
                    if skilled_workers:
                        # Worker assignment must be one of the skilled workers
                        self.model.AddAllowedAssignments(
                            [worker_assignments[order_idx, stage]], 
                            [skilled_workers]
                        )
            
            # Objective Function: Multi-objective optimization
            # 1. Minimize total completion time
            completion_times = []
            for order_idx in range(num_orders):
                completion_time = start_times[order_idx, 'ship'] + self.stage_durations['ship']
                completion_times.append(completion_time)
            
            max_completion_time = self.model.NewIntVar(0, horizon, 'max_completion')
            self.model.AddMaxEquality(max_completion_time, completion_times)
            
            # 2. Minimize labor cost
            labor_costs = []
            for order_idx in range(num_orders):
                for stage in self.stages:
                    # Get worker hourly rate
                    worker_rate = 25  # Default rate
                    for w in workers:
                        if w['id'] == worker_assignments[order_idx, stage]:
                            worker_rate = w['hourly_rate']
                            break
                    
                    stage_cost = (self.stage_durations[stage] / 60) * worker_rate
                    labor_costs.append(stage_cost)
            
            total_labor_cost = self.model.NewIntVar(0, 10000, 'total_labor_cost')
            self.model.Add(total_labor_cost == sum(labor_costs))
            
            # 3. Minimize equipment cost
            equipment_costs = []
            for order_idx in range(num_orders):
                for stage in self.stages:
                    # Get equipment hourly cost
                    equip_cost = 10  # Default cost
                    for e in equipment:
                        if e['id'] == equipment_usage[order_idx, stage]:
                            equip_cost = e['hourly_cost']
                            break
                    
                    stage_equip_cost = (self.stage_durations[stage] / 60) * equip_cost
                    equipment_costs.append(stage_equip_cost)
            
            total_equipment_cost = self.model.NewIntVar(0, 5000, 'total_equipment_cost')
            self.model.Add(total_equipment_cost == sum(equipment_costs))
            
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
            
            return True
            
        except Exception as e:
            print(f"Error creating model: {e}")
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
        try:
            # Get wave data
            wave_data = self.get_wave_data(wave_id)
            if not wave_data:
                return {"error": "Failed to get wave data"}
            
            # Create optimization model
            if not self.create_optimization_model(wave_data):
                return {"error": "Failed to create optimization model"}
            
            # Solve optimization
            result = self.solve_optimization(time_limit)
            
            # Add wave information
            result["wave_id"] = wave_id
            result["num_orders"] = len(wave_data['wave_data'])
            result["num_workers"] = len(set(w['id'] for w in wave_data['workers']))
            result["num_equipment"] = len(wave_data['equipment'])
            
            return result
            
        except Exception as e:
            return {"error": f"Optimization error: {e}"}

# Example usage
if __name__ == "__main__":
    optimizer = WaveConstraintOptimizer()
    result = optimizer.optimize_wave(1)
    print(result) 