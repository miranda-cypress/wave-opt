"""
Optimization result models for the wave optimization system.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from .warehouse import StageType, Worker, Equipment, Order


class StageSchedule(BaseModel):
    """Schedule for a single order stage."""
    order_id: int
    stage_type: StageType
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    assigned_worker_id: Optional[int] = None
    assigned_equipment_id: Optional[int] = None
    zone: Optional[int] = None
    
    @property
    def is_on_time(self) -> bool:
        """Check if this stage completed on time."""
        return True  # Will be calculated based on order deadline


class OrderSchedule(BaseModel):
    """Complete schedule for a single order."""
    order_id: int
    customer_id: int
    priority: int
    shipping_deadline: datetime
    stages: List[StageSchedule]
    
    # Calculated fields
    total_processing_time: float = Field(default=0.0, description="Total processing time in minutes")
    completion_time: Optional[datetime] = None
    is_on_time: bool = Field(default=True, description="Whether order meets deadline")
    deadline_violation_minutes: float = Field(default=0.0, description="Minutes past deadline")
    
    def calculate_metrics(self):
        """Calculate order completion metrics."""
        if not self.stages:
            return
            
        # Find completion time (end of last stage)
        self.completion_time = max(stage.end_time for stage in self.stages)
        
        # Calculate total processing time
        self.total_processing_time = sum(stage.duration_minutes for stage in self.stages)
        
        # Check deadline compliance
        if self.completion_time > self.shipping_deadline:
            self.is_on_time = False
            self.deadline_violation_minutes = (
                self.completion_time - self.shipping_deadline
            ).total_seconds() / 60.0


class WorkerSchedule(BaseModel):
    """Schedule for a single worker."""
    worker_id: int
    worker_name: str
    assigned_stages: List[StageSchedule]
    
    # Calculated fields
    total_work_hours: float = Field(default=0.0, description="Total hours worked")
    overtime_hours: float = Field(default=0.0, description="Overtime hours")
    labor_cost: float = Field(default=0.0, description="Total labor cost")
    
    def calculate_metrics(self, hourly_rate: float, max_hours: float = 8.0):
        """Calculate worker metrics."""
        self.total_work_hours = sum(stage.duration_minutes for stage in self.assigned_stages) / 60.0
        
        if self.total_work_hours > max_hours:
            self.overtime_hours = self.total_work_hours - max_hours
            regular_hours = max_hours
        else:
            self.overtime_hours = 0.0
            regular_hours = self.total_work_hours
            
        # Calculate labor cost (regular + overtime)
        self.labor_cost = (regular_hours * hourly_rate) + (self.overtime_hours * hourly_rate * 1.5)


class EquipmentSchedule(BaseModel):
    """Schedule for a single piece of equipment."""
    equipment_id: int
    equipment_name: str
    equipment_type: str
    assigned_stages: List[StageSchedule]
    
    # Calculated fields
    total_usage_hours: float = Field(default=0.0, description="Total usage hours")
    utilization_rate: float = Field(default=0.0, description="Equipment utilization percentage")
    equipment_cost: float = Field(default=0.0, description="Total equipment cost")
    
    def calculate_metrics(self, hourly_cost: float, total_horizon_hours: float):
        """Calculate equipment metrics."""
        self.total_usage_hours = sum(stage.duration_minutes for stage in self.assigned_stages) / 60.0
        self.utilization_rate = (self.total_usage_hours / total_horizon_hours) * 100.0
        self.equipment_cost = self.total_usage_hours * hourly_cost


class OptimizationMetrics(BaseModel):
    """Overall optimization performance metrics."""
    total_orders: int
    on_time_orders: int
    late_orders: int
    on_time_percentage: float
    
    total_labor_cost: float
    total_equipment_cost: float
    total_deadline_penalties: float
    total_cost: float
    
    average_order_processing_time: float
    total_processing_time: float
    
    optimization_runtime_seconds: float
    solver_status: str
    
    def calculate_metrics(self, order_schedules: List[OrderSchedule], 
                         worker_schedules: List[WorkerSchedule],
                         equipment_schedules: List[EquipmentSchedule],
                         deadline_penalty_per_hour: float):
        """Calculate overall optimization metrics."""
        self.total_orders = len(order_schedules)
        self.on_time_orders = sum(1 for order in order_schedules if order.is_on_time)
        self.late_orders = self.total_orders - self.on_time_orders
        self.on_time_percentage = (self.on_time_orders / self.total_orders) * 100.0
        
        # Calculate costs
        self.total_labor_cost = sum(worker.labor_cost for worker in worker_schedules)
        self.total_equipment_cost = sum(equipment.equipment_cost for equipment in equipment_schedules)
        self.total_deadline_penalties = sum(
            order.deadline_violation_minutes / 60.0 * deadline_penalty_per_hour
            for order in order_schedules if not order.is_on_time
        )
        self.total_cost = self.total_labor_cost + self.total_equipment_cost + self.total_deadline_penalties
        
        # Calculate processing times
        self.total_processing_time = sum(order.total_processing_time for order in order_schedules)
        self.average_order_processing_time = self.total_processing_time / self.total_orders


class OptimizationResult(BaseModel):
    """Complete optimization result."""
    order_schedules: List[OrderSchedule]
    worker_schedules: List[WorkerSchedule]
    equipment_schedules: List[EquipmentSchedule]
    metrics: OptimizationMetrics
    
    # Metadata
    optimization_start_time: datetime
    optimization_end_time: datetime
    input_summary: Dict[str, Any]
    
    def calculate_all_metrics(self, deadline_penalty_per_hour: float):
        """Calculate all metrics for the optimization result."""
        # Calculate order metrics
        for order_schedule in self.order_schedules:
            order_schedule.calculate_metrics()
        
        # Calculate worker metrics
        for worker_schedule in self.worker_schedules:
            worker_schedule.calculate_metrics(hourly_rate=25.0)  # Default hourly rate
        
        # Calculate equipment metrics
        total_horizon_hours = 16.0  # Default optimization horizon
        for equipment_schedule in self.equipment_schedules:
            equipment_schedule.calculate_metrics(hourly_cost=10.0, total_horizon_hours=total_horizon_hours)
        
        # Calculate overall metrics
        self.metrics.calculate_metrics(
            self.order_schedules,
            self.worker_schedules,
            self.equipment_schedules,
            deadline_penalty_per_hour
        )
    
    def get_efficiency_improvement(self, baseline_cost: float) -> Dict[str, float]:
        """Calculate efficiency improvements compared to baseline."""
        cost_savings = baseline_cost - self.metrics.total_cost
        cost_savings_percentage = (cost_savings / baseline_cost) * 100.0
        
        return {
            "cost_savings": cost_savings,
            "cost_savings_percentage": cost_savings_percentage,
            "on_time_improvement": self.metrics.on_time_percentage,
            "processing_time_reduction": 0.0  # Would need baseline for comparison
        }
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert result to summary dictionary for API response."""
        return {
            "total_orders": self.metrics.total_orders,
            "on_time_percentage": self.metrics.on_time_percentage,
            "total_cost": self.metrics.total_cost,
            "labor_cost": self.metrics.total_labor_cost,
            "equipment_cost": self.metrics.total_equipment_cost,
            "deadline_penalties": self.metrics.total_deadline_penalties,
            "optimization_runtime": self.metrics.optimization_runtime_seconds,
            "solver_status": self.metrics.solver_status
        } 