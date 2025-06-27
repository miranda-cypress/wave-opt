"""
Warehouse data models for the optimization system.
"""

from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta


class StageType(str, Enum):
    """Warehouse workflow stages."""
    PICK = "pick"
    CONSOLIDATE = "consolidate"
    PACK = "pack"
    LABEL = "label"
    STAGE = "stage"
    SHIP = "ship"


class SkillType(str, Enum):
    """Worker skill types."""
    PICKING = "picking"
    PACKING = "packing"
    SHIPPING = "shipping"
    LABELING = "labeling"
    CONSOLIDATION = "consolidation"
    STAGING = "staging"


class EquipmentType(str, Enum):
    """Equipment types in the warehouse."""
    PACKING_STATION = "packing_station"
    DOCK_DOOR = "dock_door"
    PICK_CART = "pick_cart"
    CONVEYOR = "conveyor"
    LABEL_PRINTER = "label_printer"


class Worker(BaseModel):
    """Worker model with skills and availability."""
    id: int
    name: str
    skills: Set[SkillType] = Field(description="Worker's skill set")
    hourly_rate: float = Field(description="Hourly labor cost")
    efficiency_factor: float = Field(default=1.0, description="Worker efficiency multiplier")
    max_hours_per_day: float = Field(default=8.0, description="Maximum working hours per day")
    
    class Config:
        json_encoders = {
            set: list
        }


class Equipment(BaseModel):
    """Equipment model with capacity and availability."""
    id: int
    name: str
    equipment_type: EquipmentType
    capacity: int = Field(description="Maximum concurrent usage")
    hourly_cost: float = Field(default=0.0, description="Hourly equipment cost")
    efficiency_factor: float = Field(default=1.0, description="Equipment efficiency multiplier")


class SKU(BaseModel):
    """Stock Keeping Unit model."""
    id: int
    name: str
    zone: int = Field(description="Warehouse zone (1-5)")
    pick_time_minutes: float = Field(description="Average pick time in minutes")
    pack_time_minutes: float = Field(description="Average pack time in minutes")
    volume_cubic_feet: float = Field(description="Item volume for space planning")
    weight_lbs: float = Field(description="Item weight for shipping calculations")


class OrderItem(BaseModel):
    """Individual item in an order."""
    sku_id: int
    quantity: int
    sku: Optional[SKU] = None


class Order(BaseModel):
    """Customer order with multiple items."""
    id: int
    customer_id: int
    priority: int = Field(description="Order priority (1=highest, 5=lowest)")
    created_at: datetime
    shipping_deadline: datetime
    items: List[OrderItem]
    
    # Calculated fields
    total_pick_time: float = Field(default=0.0, description="Total pick time in minutes")
    total_pack_time: float = Field(default=0.0, description="Total pack time in minutes")
    total_volume: float = Field(default=0.0, description="Total volume in cubic feet")
    total_weight: float = Field(default=0.0, description="Total weight in pounds")
    
    def calculate_times(self, skus: Dict[int, SKU]):
        """Calculate processing times based on SKU data."""
        self.total_pick_time = sum(
            item.quantity * skus[item.sku_id].pick_time_minutes 
            for item in self.items
        )
        self.total_pack_time = sum(
            item.quantity * skus[item.sku_id].pack_time_minutes 
            for item in self.items
        )
        self.total_volume = sum(
            item.quantity * skus[item.sku_id].volume_cubic_feet 
            for item in self.items
        )
        self.total_weight = sum(
            item.quantity * skus[item.sku_id].weight_lbs 
            for item in self.items
        )


class WarehouseConfig(BaseModel):
    """Warehouse configuration and constraints."""
    name: str = "MidWest Distribution Co"
    total_sqft: int = 85000
    zones: int = 5
    workers: List[Worker]
    equipment: List[Equipment]
    skus: List[SKU]
    
    # Operational constraints
    shift_start_hour: int = 6  # 6 AM
    shift_end_hour: int = 22   # 10 PM
    max_orders_per_day: int = 2500
    
    # Cost parameters
    deadline_penalty_per_hour: float = 100.0  # Penalty for missing deadline
    overtime_multiplier: float = 1.5  # Overtime pay multiplier
    
    def get_workers_by_skill(self, skill: SkillType) -> List[Worker]:
        """Get all workers with a specific skill."""
        return [w for w in self.workers if skill in w.skills]
    
    def get_equipment_by_type(self, equipment_type: EquipmentType) -> List[Equipment]:
        """Get all equipment of a specific type."""
        return [e for e in self.equipment if e.equipment_type == equipment_type]


class OptimizationInput(BaseModel):
    """Input data for the optimization model."""
    warehouse_config: WarehouseConfig
    orders: List[Order]
    optimization_horizon_hours: int = Field(default=16, description="Optimization time horizon")
    
    def validate(self) -> List[str]:
        """Validate the optimization input and return any errors."""
        errors = []
        
        # Validate orders have calculated times
        sku_dict = {sku.id: sku for sku in self.warehouse_config.skus}
        for order in self.orders:
            if order.total_pick_time == 0:
                order.calculate_times(sku_dict)
        
        # Check for deadline violations
        horizon_end = datetime.now() + timedelta(hours=self.optimization_horizon_hours)
        for order in self.orders:
            if order.shipping_deadline > horizon_end:
                errors.append(f"Order {order.id} deadline {order.shipping_deadline} exceeds optimization horizon")
        
        return errors 