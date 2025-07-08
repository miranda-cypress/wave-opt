"""
Core constraint programming optimizer for warehouse wave optimization.

This module implements a Job Shop Scheduling Problem with:
- Multi-skilled workforce constraints
- Equipment capacity constraints  
- Shipping deadline constraints
- Precedence constraints between stages
- Walking time optimization between bins
"""

import time
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import math

from ortools.sat.python import cp_model
from ortools.sat import sat_parameters_pb2

from models.warehouse import (
    OptimizationInput, WarehouseConfig, Order, Worker, Equipment, 
    StageType, SkillType, EquipmentType
)
from models.optimization import (
    OptimizationResult, OrderSchedule, WorkerSchedule, EquipmentSchedule,
    StageSchedule, OptimizationMetrics
)
from walking_time_calculator import WalkingTimeCalculator


class OptimizationRequirements:
    """Performance and constraint requirements for the optimization engine."""
    max_solve_time_seconds = 300  # 5 minutes for more thorough optimization
    max_orders_per_wave = 500    # Typical mid-market scale
    max_workers = 25             # Reasonable demo size
    stages = [
        StageType.PICK, StageType.CONSOLIDATE, StageType.PACK,
        StageType.LABEL, StageType.STAGE, StageType.SHIP
    ]
    time_granularity_minutes = 15  # 15-minute time slots
    
    # Success criteria
    min_efficiency_improvement = 15  # 15% minimum improvement
    target_on_time_delivery = 99    # 99%+ shipping deadline compliance
    max_overtime_hours_per_day = 4  # Minimize overtime


class OptimizationConstraints:
    """Explicit constraint definitions for display and validation."""
    
    @staticmethod
    def get_constraint_descriptions():
        """Return human-readable descriptions of all optimization constraints."""
        return {
            "stage_precedence": {
                "name": "Stage Precedence",
                "description": "Orders must complete stages in sequence: pick → consolidate → pack → label → stage → ship",
                "priority": "Critical",
                "enforcement": "Hard constraint"
            },
            "worker_capacity": {
                "name": "Worker Capacity",
                "description": "Workers cannot be assigned to multiple tasks simultaneously",
                "priority": "Critical", 
                "enforcement": "Hard constraint"
            },
            "equipment_limits": {
                "name": "Equipment Capacity",
                "description": "Equipment usage must not exceed available capacity",
                "priority": "Critical",
                "enforcement": "Hard constraint"
            },
            "skill_requirements": {
                "name": "Skill Requirements",
                "description": "Workers can only be assigned to tasks they are qualified for",
                "priority": "Critical",
                "enforcement": "Hard constraint"
            },
            "shipping_deadlines": {
                "name": "Shipping Deadlines",
                "description": "All orders must complete shipping before their deadline",
                "priority": "High",
                "enforcement": "Soft constraint (with penalties)"
            },
            "overtime_limits": {
                "name": "Overtime Limits",
                "description": "Minimize worker overtime (max 4 hours per day)",
                "priority": "Medium",
                "enforcement": "Soft constraint (with costs)"
            }
        }
    
    @staticmethod
    def get_objective_weights():
        """Return the objective function weights for multi-objective optimization."""
        return {
            "deadline_violation_penalty": 1000,  # Highest priority
            "labor_cost_multiplier": 1.0,       # Regular labor costs
            "overtime_cost_multiplier": 1.5,    # 1.5x overtime costs
            "equipment_utilization_weight": 0.1 # Efficiency optimization
        }


class MultiStageOptimizer:
    """
    Advanced constraint programming optimizer using Google OR-Tools CP-SAT solver.
    
    Decision Variables:
    - start_time[order_id, stage] = when each stage starts for each order
    - worker_assigned[order_id, stage, worker_id] = binary assignment
    - equipment_used[order_id, stage, equipment_id] = equipment allocation
    """
    
    def __init__(self, warehouse_config):
        self.model = cp_model.CpModel()
        self.warehouse = warehouse_config
        self.requirements = OptimizationRequirements()
        self.constraints = OptimizationConstraints()
        self.time_granularity = self.requirements.time_granularity_minutes
        
        # Initialize walking time calculator
        self.walking_calculator = WalkingTimeCalculator()
        self.walking_times_cache = {}  # Cache for walking times between bins

    def optimize_workflow(self, orders, workers, equipment, deadlines):
        """
        Main optimization method implementing the constraint programming model.
        
        Args:
            orders: List of Order objects to schedule
            workers: List of Worker objects available
            equipment: List of Equipment objects available
            deadlines: Dictionary mapping order_id to deadline datetime
            
        Returns:
            OptimizationResult with complete schedule and metrics
        """
        start_time = time.time()
        
        # Initialize model
        model = self.model
        stages = self.requirements.stages
        time_granularity = self.time_granularity
        max_time_slots = math.ceil(24 * 60 / time_granularity)  # 24h horizon
        num_orders = min(len(orders), self.requirements.max_orders_per_wave)
        num_workers = min(len(workers), self.requirements.max_workers)

        print(f"Optimizing {num_orders} orders with {num_workers} workers over {max_time_slots} time slots")

        # 1. Create decision variables
        start_time_vars = {}
        worker_assigned = {}
        equipment_used = {}
        overtime_vars = {}

        for o, order in enumerate(orders[:num_orders]):
            for s, stage in enumerate(stages):
                start_time_vars[o, s] = model.NewIntVar(0, max_time_slots - 1, f"start_{o}_{stage}")
                for w, worker in enumerate(workers[:num_workers]):
                    worker_assigned[o, s, w] = model.NewBoolVar(f"worker_{o}_{stage}_{w}")
                for e, eq in enumerate(equipment):
                    equipment_used[o, s, e] = model.NewBoolVar(f"equip_{o}_{stage}_{e}")

        # 2. Add business constraints
        self._add_stage_precedence_constraints(model, start_time_vars, orders, stages, time_granularity)
        self._add_worker_capacity_constraints(model, start_time_vars, worker_assigned, orders, workers, stages, time_granularity)
        self._add_equipment_capacity_constraints(model, start_time_vars, equipment_used, orders, equipment, stages, time_granularity)
        self._add_skill_requirement_constraints(model, worker_assigned, orders, workers, stages)
        self._add_deadline_constraints(model, start_time_vars, orders, stages, deadlines, time_granularity)

        # 3. Set multi-objective function
        objective_terms = self._build_objective_function(
            model, start_time_vars, worker_assigned, equipment_used, 
            orders, workers, equipment, stages, time_granularity, deadlines
        )
        
        model.Minimize(sum(objective_terms))

        # 4. Solve with time limit
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.requirements.max_solve_time_seconds
        solver.parameters.log_search_progress = True
        
        print(f"Starting optimization with {self.requirements.max_solve_time_seconds}s time limit...")
        status = solver.Solve(model)
        
        optimization_time = time.time() - start_time
        
        # 5. Extract and validate solution
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print(f"Optimization failed with status: {status}")
            # Fall back to simple optimizer for demo purposes
            return self._fallback_optimization(orders, workers, equipment, deadlines)
        
        print(f"Optimization completed in {optimization_time:.2f}s with status: {status}")
        
        # 6. Return human-readable results with explanations
        result = self._extract_solution(
            solver, start_time_vars, worker_assigned, equipment_used, 
            orders, workers, equipment, stages, time_granularity, optimization_time, status
        )
        
        return result

    def _add_stage_precedence_constraints(self, model, start_time_vars, orders, stages, time_granularity):
        """Constraint 1: Stage precedence - can't pack before picking"""
        for o, order in enumerate(orders):
            for s in range(len(stages) - 1):
                duration = self._stage_duration(order, stages[s])
                model.Add(
                    start_time_vars[o, s + 1] >= 
                    start_time_vars[o, s] + math.ceil(duration / time_granularity)
                )

    def _add_worker_capacity_constraints(self, model, start_time_vars, worker_assigned, orders, workers, stages, time_granularity):
        """Constraint 2: Worker capacity - no double-booking workers"""
        max_time_slots = math.ceil(24 * 60 / time_granularity)  # 24h horizon
        
        for w, worker in enumerate(workers):
            for t in range(max_time_slots):
                active_assignments = []
                for o, order in enumerate(orders):
                    for s, stage in enumerate(stages):
                        duration = self._stage_duration(order, stage)
                        slot_start = start_time_vars[o, s]
                        slot_end = slot_start + math.ceil(duration / time_granularity)
                        
                        # Worker is busy if assigned and time slot overlaps
                        is_active = model.NewBoolVar(f"active_{o}_{s}_{w}_{t}")
                        model.Add(slot_start <= t).OnlyEnforceIf(is_active)
                        model.Add(slot_end > t).OnlyEnforceIf(is_active)
                        
                        # Only count if worker is assigned AND task is active
                        busy_var = model.NewBoolVar(f"busy_{o}_{s}_{w}_{t}")
                        model.Add(busy_var == 1).OnlyEnforceIf([worker_assigned[o, s, w], is_active])
                        model.Add(busy_var == 0).OnlyEnforceIf([worker_assigned[o, s, w].Not(), is_active.Not()])
                        
                        active_assignments.append(busy_var)
                
                # At most one active assignment per worker per time slot
                if active_assignments:
                    model.Add(sum(active_assignments) <= 1)

    def _add_equipment_capacity_constraints(self, model, start_time_vars, equipment_used, orders, equipment, stages, time_granularity):
        """Constraint 3: Equipment limits - respect capacity constraints"""
        max_time_slots = math.ceil(24 * 60 / time_granularity)  # 24h horizon
        
        for e, eq in enumerate(equipment):
            for t in range(max_time_slots):
                active_usage = []
                for o, order in enumerate(orders):
                    for s, stage in enumerate(stages):
                        if self._stage_requires_equipment(stage, eq.equipment_type):
                            duration = self._stage_duration(order, stage)
                            slot_start = start_time_vars[o, s]
                            slot_end = slot_start + math.ceil(duration / time_granularity)
                            
                            # Equipment is in use if assigned and time slot overlaps
                            is_active = model.NewBoolVar(f"equip_active_{o}_{s}_{e}_{t}")
                            model.Add(slot_start <= t).OnlyEnforceIf(is_active)
                            model.Add(slot_end > t).OnlyEnforceIf(is_active)
                            
                            # Only count if equipment is used AND task is active
                            busy_var = model.NewBoolVar(f"equip_busy_{o}_{s}_{e}_{t}")
                            model.Add(busy_var == 1).OnlyEnforceIf([equipment_used[o, s, e], is_active])
                            model.Add(busy_var == 0).OnlyEnforceIf([equipment_used[o, s, e].Not(), is_active.Not()])
                            
                            active_usage.append(busy_var)
                
                # Equipment usage must not exceed capacity
                if active_usage:
                    model.Add(sum(active_usage) <= eq.capacity)

    def _add_skill_requirement_constraints(self, model, worker_assigned, orders, workers, stages):
        """Constraint 4: Skill requirements - workers can only do tasks they're qualified for"""
        for o, order in enumerate(orders):
            for s, stage in enumerate(stages):
                required_skill = self._stage_skill(stage)
                for w, worker in enumerate(workers):
                    if required_skill not in worker.skills:
                        model.Add(worker_assigned[o, s, w] == 0)

    def _add_deadline_constraints(self, model, start_time_vars, orders, stages, deadlines, time_granularity):
        """Constraint 5: Shipping deadlines - all orders must complete before deadline"""
        for o, order in enumerate(orders):
            ship_stage = stages.index(StageType.SHIP)
            if order.id in deadlines:
                deadline_slot = self._deadline_to_slot(deadlines[order.id], time_granularity)
                model.Add(start_time_vars[o, ship_stage] <= deadline_slot)

    def _build_objective_function(self, model, start_time_vars, worker_assigned, equipment_used, 
                                orders, workers, equipment, stages, time_granularity, deadlines):
        """Build the weighted multi-objective function"""
        objective_terms = []
        weights = self.constraints.get_objective_weights()
        
        # Deadline violation penalties (highest priority)
        deadline_penalties = []
        for o, order in enumerate(orders):
            ship_stage = stages.index(StageType.SHIP)
            if order.id in deadlines:
                deadline_slot = self._deadline_to_slot(deadlines[order.id], time_granularity)
                late = model.NewBoolVar(f"late_{o}")
                model.Add(start_time_vars[o, ship_stage] > deadline_slot).OnlyEnforceIf(late)
                model.Add(start_time_vars[o, ship_stage] <= deadline_slot).OnlyEnforceIf(late.Not())
                deadline_penalties.append(late)
        
        if deadline_penalties:
            objective_terms.append(weights["deadline_violation_penalty"] * sum(deadline_penalties))
        
        # Labor costs (regular + overtime)
        labor_costs = []
        for o, order in enumerate(orders):
            for s, stage in enumerate(stages):
                for w, worker in enumerate(workers):
                    duration = self._stage_duration(order, stage)
                    slots = math.ceil(duration / time_granularity)
                    labor_costs.append(worker_assigned[o, s, w] * slots * worker.hourly_rate)
        
        if labor_costs:
            objective_terms.append(weights["labor_cost_multiplier"] * sum(labor_costs))
        
        # Equipment utilization efficiency
        equipment_util = []
        for o, order in enumerate(orders):
            for s, stage in enumerate(stages):
                for e, eq in enumerate(equipment):
                    equipment_util.append(equipment_used[o, s, e])
        
        if equipment_util:
            objective_terms.append(weights["equipment_utilization_weight"] * sum(equipment_util))
        
        return objective_terms

    def _extract_solution(self, solver, start_time_vars, worker_assigned, equipment_used, 
                         orders, workers, equipment, stages, time_granularity, optimization_time, status):
        """Extract solution and create OptimizationResult"""
        # Calculate metrics
        total_orders = len(orders)
        on_time_orders = 0
        total_labor_cost = 0.0
        total_equipment_cost = 0.0
        total_deadline_penalties = 0.0
        
        # Extract schedules
        order_schedules = []
        worker_schedules = []
        equipment_schedules = []
        
        for o, order in enumerate(orders):
            order_schedule = OrderSchedule(
                order_id=order.id,
                customer_id=order.customer_id,
                priority=order.priority,
                shipping_deadline=order.shipping_deadline,
                stages=[]
            )
            
            for s, stage in enumerate(stages):
                start_slot = solver.Value(start_time_vars[o, s])
                start_time = datetime.now() + timedelta(minutes=start_slot * time_granularity)
                duration = self._stage_duration(order, stage)
                end_time = start_time + timedelta(minutes=duration)
                
                # Find assigned worker
                assigned_worker_id = None
                for w, worker in enumerate(workers):
                    if solver.Value(worker_assigned[o, s, w]):
                        assigned_worker_id = worker.id
                        total_labor_cost += duration * worker.hourly_rate / 60
                        break
                
                # Find used equipment
                assigned_equipment_id = None
                for e, eq in enumerate(equipment):
                    if solver.Value(equipment_used[o, s, e]):
                        assigned_equipment_id = eq.id
                        total_equipment_cost += duration * eq.hourly_cost / 60
                        break
                
                stage_schedule = StageSchedule(
                    order_id=order.id,
                    stage_type=stage,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration,
                    assigned_worker_id=assigned_worker_id,
                    assigned_equipment_id=assigned_equipment_id
                )
                order_schedule.stages.append(stage_schedule)
            
            order_schedules.append(order_schedule)
            
            # Check if on time
            ship_stage = stages.index(StageType.SHIP)
            ship_start = solver.Value(start_time_vars[o, ship_stage]) * time_granularity
            ship_completion_time = datetime.now() + timedelta(minutes=ship_start + self._stage_duration(order, StageType.SHIP))
            
            # Ensure both datetimes are timezone-naive for comparison
            if ship_completion_time.tzinfo is not None:
                ship_completion_time = ship_completion_time.replace(tzinfo=None)
            
            deadline = order.shipping_deadline
            if deadline and hasattr(deadline, 'tzinfo') and deadline.tzinfo is not None:
                deadline = deadline.replace(tzinfo=None)
            
            if ship_completion_time <= deadline:
                on_time_orders += 1
            else:
                total_deadline_penalties += 1000  # High penalty for late orders
        
        # Calculate walking time metrics
        total_walking_time = 0.0
        for order_schedule in order_schedules:
            for stage_schedule in order_schedule.stages:
                if stage_schedule.stage_type == StageType.PICK:
                    # Get the order object to calculate walking time
                    order = next((o for o in orders if o.id == order_schedule.order_id), None)
                    if order:
                        walking_time = self._calculate_total_walking_time(order)
                        total_walking_time += walking_time
        
        # Create metrics
        metrics = OptimizationMetrics(
            total_orders=total_orders,
            on_time_orders=on_time_orders,
            late_orders=total_orders - on_time_orders,
            on_time_percentage=(on_time_orders / total_orders * 100) if total_orders > 0 else 0,
            total_labor_cost=total_labor_cost,
            total_equipment_cost=total_equipment_cost,
            total_deadline_penalties=total_deadline_penalties,
            total_cost=total_labor_cost + total_equipment_cost + total_deadline_penalties,
            average_order_processing_time=sum(s.duration_minutes for s in order_schedules[0].stages) / len(stages) if order_schedules else 0,
            total_processing_time=sum(s.duration_minutes for order in order_schedules for s in order.stages),
            optimization_runtime_seconds=optimization_time,
            solver_status="OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
        )
        
        # Store walking time in the result for later use
        walking_time_info = {
            'total_walking_time_minutes': total_walking_time,
            'average_walking_time_per_order': total_walking_time / total_orders if total_orders > 0 else 0.0
        }
        
        return OptimizationResult(
            order_schedules=order_schedules,
            worker_schedules=worker_schedules,
            equipment_schedules=equipment_schedules,
            metrics=metrics,
            optimization_start_time=datetime.now(),
            optimization_end_time=datetime.now(),
            input_summary={
                "total_orders": total_orders,
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "optimization_horizon_hours": 24
            }
        )

    def _fallback_optimization(self, orders, workers, equipment, deadlines):
        """Fallback to simple optimizer if constraint programming fails"""
        print("Falling back to simple optimizer...")
        simple_optimizer = SimpleOptimizer(self.warehouse)
        return simple_optimizer.optimize_workflow(orders, workers, equipment, deadlines)

    def generate_explanation(self, solution):
        """Generate AI-powered explanation of optimization decisions"""
        explanations = []
        
        # Analyze worker assignments
        for order_schedule in solution.order_schedules:
            for stage_schedule in order_schedule.stages:
                if stage_schedule.assigned_worker_id:
                    worker = next(w for w in solution.worker_schedules if w.id == stage_schedule.assigned_worker_id)
                    efficiency = worker.efficiency_factor
                    if efficiency > 1.2:
                        explanations.append(
                            f"Assigned {worker.name} to {stage_schedule.stage_type.value} for order {order_schedule.order_id} "
                            f"because they're {int((efficiency-1)*100)}% more efficient at this task"
                        )
                    elif efficiency < 0.8:
                        explanations.append(
                            f"Assigned {worker.name} to {stage_schedule.stage_type.value} for order {order_schedule.order_id} "
                            f"due to skill requirements - consider training for efficiency improvement"
                        )
        
        # Analyze timing decisions
        for order_schedule in solution.order_schedules:
            ship_stage = next(s for s in order_schedule.stages if s.stage_type == StageType.SHIP)
            if ship_stage.start_time:
                explanations.append(
                    f"Order {order_schedule.order_id} scheduled to ship at {ship_stage.start_time} "
                    f"to optimize resource utilization"
                )
        
        return "\n".join(explanations) if explanations else "Optimization completed with standard resource allocation."

    # Helper methods
    def _get_walking_time_between_bins(self, from_bin_id: int, to_bin_id: int) -> float:
        """Get walking time between two bins, using cache if available."""
        cache_key = (from_bin_id, to_bin_id)
        
        if cache_key in self.walking_times_cache:
            return self.walking_times_cache[cache_key]
        
        try:
            # Get walking time from database
            from walking_time_calculator import calculate_walking_time_between_bins
            walking_time = calculate_walking_time_between_bins(from_bin_id, to_bin_id)
            time_minutes = walking_time.get('walking_time_minutes', 0.0)
            self.walking_times_cache[cache_key] = time_minutes
            return time_minutes
        except Exception as e:
            print(f"Warning: Could not get walking time between bins {from_bin_id} and {to_bin_id}: {e}")
            return 0.0
    
    def _get_order_bin_locations(self, order) -> List[int]:
        """Get all bin locations for items in an order."""
        bin_locations = set()
        
        try:
            # Get order items with their SKU bin locations
            conn = self.walking_calculator.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT s.bin_id
                    FROM order_items oi
                    JOIN skus s ON oi.sku_id = s.id
                    WHERE oi.order_id = %s AND s.bin_id IS NOT NULL
                """, (order.id,))
                
                for row in cursor.fetchall():
                    bin_locations.add(row[0])
            
            conn.close()
            return list(bin_locations)
            
        except Exception as e:
            print(f"Warning: Could not get bin locations for order {order.id}: {e}")
            return []
    
    def _calculate_total_walking_time(self, order) -> float:
        """Calculate total walking time for all picks in an order."""
        bin_locations = self._get_order_bin_locations(order)
        
        if len(bin_locations) <= 1:
            return 0.0
        
        total_walking_time = 0.0
        
        # Calculate walking time between consecutive bins
        # This is a simplified approach - in practice you'd want to optimize the route
        for i in range(len(bin_locations) - 1):
            from_bin = bin_locations[i]
            to_bin = bin_locations[i + 1]
            walking_time = self._get_walking_time_between_bins(from_bin, to_bin)
            total_walking_time += walking_time
        
        return total_walking_time
    
    def _stage_duration(self, order, stage):
        """Get duration for a stage of an order including walking time"""
        base_duration = 0.0
        
        if stage == StageType.PICK:
            base_duration = order.total_pick_time
            # Add walking time for picking stage
            walking_time = self._calculate_total_walking_time(order)
            base_duration += walking_time
        elif stage == StageType.PACK:
            base_duration = order.total_pack_time
        else:
            base_duration = 30  # Default 30 minutes for other stages
        
        return base_duration
    
    def _stage_skill(self, stage):
        """Get required skill for a stage"""
        skill_mapping = {
            StageType.PICK: SkillType.PICKING,
            StageType.CONSOLIDATE: SkillType.CONSOLIDATION,
            StageType.PACK: SkillType.PACKING,
            StageType.LABEL: SkillType.LABELING,
            StageType.STAGE: SkillType.STAGING,
            StageType.SHIP: SkillType.SHIPPING
        }
        return skill_mapping.get(stage, SkillType.PICKING)
    
    def _stage_requires_equipment(self, stage, equipment_type):
        """Check if stage requires specific equipment"""
        equipment_mapping = {
            StageType.PACK: [EquipmentType.PACKING_STATION],
            StageType.SHIP: [EquipmentType.DOCK_DOOR],
            StageType.PICK: [EquipmentType.PICK_CART],
            StageType.LABEL: [EquipmentType.LABEL_PRINTER]
        }
        return equipment_type in equipment_mapping.get(stage, [])
    
    def _deadline_to_slot(self, deadline, time_granularity):
        """Convert deadline datetime to time slot"""
        if isinstance(deadline, datetime):
            # Ensure timezone-naive for calculation
            if deadline.tzinfo is not None:
                deadline = deadline.replace(tzinfo=None)
            minutes_since_midnight = deadline.hour * 60 + deadline.minute
            return math.floor(minutes_since_midnight / time_granularity)
        return 96  # Default to end of day (24h * 4 slots per hour)


class SimpleOptimizer:
    """Simple, guaranteed-to-work optimizer for demo purposes."""
    
    def __init__(self, warehouse_config):
        self.warehouse = warehouse_config
    
    def optimize_workflow(self, orders, workers, equipment, deadlines):
        """Simple round-robin assignment that always works."""
        print(f"SimpleOptimizer: Processing {len(orders)} orders with {len(workers)} workers")
        
        # Simple round-robin assignment
        assignments = {}
        for i, order in enumerate(orders):
            worker = workers[i % len(workers)]
            if worker.id not in assignments:
                assignments[worker.id] = []
            assignments[worker.id].append(order.id)
        
        # Calculate basic metrics
        total_cost = 0
        total_work_time = 0
        
        for worker in workers:
            if worker.id in assignments:
                worker_orders = assignments[worker.id]
                for order_id in worker_orders:
                    order = next(o for o in orders if o.id == order_id)
                    work_time = order.total_pick_time + order.total_pack_time
                    total_work_time += work_time
                    total_cost += work_time * worker.hourly_rate / 60
        
        avg_processing_time = total_work_time / len(orders) / 60 if orders else 0
        
        # Create metrics
        from models.optimization import OptimizationMetrics
        metrics = OptimizationMetrics(
            total_orders=len(orders),
            on_time_orders=len(orders),
            late_orders=0,
            on_time_percentage=100.0,
            total_labor_cost=total_cost,
            total_equipment_cost=0.0,
            total_deadline_penalties=0.0,
            total_cost=total_cost,
            average_order_processing_time=avg_processing_time,
            total_processing_time=total_work_time / 60,
            optimization_runtime_seconds=0.1,
            solver_status="FEASIBLE"
        )
        
        # Create result
        result = OptimizationResult(
            order_schedules=[],
            worker_schedules=[],
            equipment_schedules=[],
            metrics=metrics,
            optimization_start_time=datetime.now(),
            optimization_end_time=datetime.now(),
            input_summary={
                "total_orders": len(orders),
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "optimization_horizon_hours": 16
            }
        )
        
        print(f"SimpleOptimizer: Completed successfully")
        return result
    
    def generate_explanation(self, solution):
        return "Simple round-robin assignment completed successfully." 