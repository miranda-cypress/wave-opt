"""
Simple Wave Optimizer - Fallback optimizer when constraint programming fails.

This provides a basic scheduling algorithm that can be used as a backup
when the more complex OR-Tools optimizer encounters issues.
"""

import logging
import time
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

class SimpleWaveOptimizer:
    """Simple wave optimizer using basic scheduling algorithms."""
    
    def __init__(self):
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
    
    def optimize_wave(self, wave_data: Dict) -> Dict:
        """Simple optimization using earliest deadline first scheduling."""
        logger = logging.getLogger("SimpleWaveOptimizer")
        
        try:
            orders = wave_data.get('wave_data', [])
            workers = wave_data.get('workers', [])
            equipment = wave_data.get('equipment', [])
            
            if not orders or not workers or not equipment:
                return {"error": "Missing required data"}
            
            logger.info(f"Simple optimizer: {len(orders)} orders, {len(workers)} workers, {len(equipment)} equipment")
            
            # Sort orders by priority and deadline
            sorted_orders = sorted(orders, key=lambda x: (
                {'high': 1, 'medium': 2, 'low': 3}.get(x.get('priority', 'medium'), 2),
                x.get('shipping_deadline', datetime.now() + timedelta(hours=24))
            ))
            
            # Simple scheduling: assign orders to available workers
            schedule = []
            worker_availability = {w.get('id', i): 0 for i, w in enumerate(workers)}
            equipment_availability = {e.get('id', i): 0 for i, e in enumerate(equipment)}
            
            total_cost = 0
            total_time = 0
            on_time_orders = 0
            
            for order_idx, order in enumerate(sorted_orders):
                order_schedule = {
                    'order_id': order.get('order_id'),
                    'stages': [],
                    'total_time': 0,
                    'is_on_time': True
                }
                
                current_time = 0
                
                for stage in self.stages:
                    # Find available worker for this stage
                    available_worker = None
                    for worker in workers:
                        if worker_availability[worker.get('id', 0)] <= current_time:
                            # Check if worker has skill (simplified)
                            if self._worker_can_do_stage(worker, stage):
                                available_worker = worker
                                break
                    
                    if not available_worker:
                        # Assign to first available worker
                        available_worker = min(workers, key=lambda w: worker_availability[w.get('id', 0)])
                    
                    # Find available equipment
                    available_equipment = min(equipment, key=lambda e: equipment_availability[e.get('id', 0)])
                    
                    # Calculate start time (after worker and equipment are available)
                    start_time = max(
                        current_time,
                        worker_availability[available_worker.get('id', 0)],
                        equipment_availability[available_equipment.get('id', 0)]
                    )
                    
                    duration = self.stage_durations[stage]
                    end_time = start_time + duration
                    
                    # Update availability
                    worker_availability[available_worker.get('id', 0)] = end_time
                    equipment_availability[available_equipment.get('id', 0)] = end_time
                    
                    # Add stage to schedule
                    stage_schedule = {
                        'stage': stage,
                        'worker_id': available_worker.get('id', 0),
                        'equipment_id': available_equipment.get('id', 0),
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration
                    }
                    order_schedule['stages'].append(stage_schedule)
                    
                    current_time = end_time
                
                order_schedule['total_time'] = current_time
                total_time = max(total_time, current_time)
                
                # Check if order is on time
                deadline = order.get('shipping_deadline')
                if deadline:
                    if isinstance(deadline, str):
                        try:
                            deadline = datetime.fromisoformat(deadline)
                        except:
                            deadline = datetime.now() + timedelta(hours=24)
                    elif isinstance(deadline, datetime):
                        # Ensure timezone-naive
                        if deadline.tzinfo is not None:
                            deadline = deadline.replace(tzinfo=None)
                    else:
                        deadline = datetime.now() + timedelta(hours=24)
                    
                    # Ensure both dates are timezone-naive for comparison
                    if hasattr(deadline, 'tzinfo') and deadline.tzinfo is not None:
                        deadline = deadline.replace(tzinfo=None)
                    
                    now = datetime.now()
                    if hasattr(now, 'tzinfo') and now.tzinfo is not None:
                        now = now.replace(tzinfo=None)
                    
                    if current_time <= (deadline - now).total_seconds() / 60:
                        on_time_orders += 1
                    else:
                        order_schedule['is_on_time'] = False
                
                # Calculate cost
                order_cost = sum(
                    (stage['duration'] / 60) * 25  # $25/hour default rate
                    for stage in order_schedule['stages']
                )
                total_cost += order_cost
                
                schedule.append(order_schedule)
            
            # Calculate metrics
            total_orders = len(orders)
            on_time_percentage = (on_time_orders / total_orders * 100) if total_orders > 0 else 0
            
            result = {
                "status": "success",
                "solve_time": 0.1,  # Simple algorithm is very fast
                "objective_value": total_cost + total_time * 0.1,  # Simple objective
                "solution": {
                    "schedule": schedule,
                    "total_cost": total_cost,
                    "total_time": total_time,
                    "on_time_orders": on_time_orders,
                    "on_time_percentage": on_time_percentage
                },
                "num_orders": total_orders,
                "num_workers": len(workers),
                "num_equipment": len(equipment),
                "optimization_type": "simple_fallback"
            }
            
            logger.info(f"Simple optimization completed: {on_time_percentage:.1f}% on-time, cost: ${total_cost:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Simple optimizer error: {e}")
            return {"error": f"Simple optimization failed: {e}"}
    
    def _worker_can_do_stage(self, worker: Dict, stage: str) -> bool:
        """Check if worker can perform a stage (simplified logic)."""
        skill = worker.get('skill_name', 'general')
        
        # Direct skill match
        if skill == stage:
            return True
        
        # Skill mapping
        skill_mapping = {
            'pick': 'picking',
            'pack': 'packing', 
            'ship': 'shipping',
            'consolidate': 'consolidation',
            'label': 'labeling',
            'stage': 'staging'
        }
        
        if skill == skill_mapping.get(stage, stage):
            return True
        
        # General workers can do anything
        if skill == 'general':
            return True
        
        return False 