#!/usr/bin/env python3
"""
Test script for the new constraint programming optimization engine.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from models.warehouse import (
    Worker, Equipment, SKU, Order, OrderItem, WarehouseConfig,
    SkillType, EquipmentType, StageType
)
from optimizer.wave_optimizer import MultiStageOptimizer, OptimizationConstraints, OptimizationRequirements

def create_test_data():
    """Create test data for optimization."""
    
    # Create workers
    workers = [
        Worker(
            id=1,
            name="Sarah Johnson",
            skills={SkillType.PICKING, SkillType.PACKING},
            hourly_rate=25.0,
            efficiency_factor=1.2,
            max_hours_per_day=8.0
        ),
        Worker(
            id=2,
            name="Mike Chen",
            skills={SkillType.PICKING, SkillType.SHIPPING},
            hourly_rate=22.0,
            efficiency_factor=1.0,
            max_hours_per_day=8.0
        ),
        Worker(
            id=3,
            name="Lisa Rodriguez",
            skills={SkillType.PACKING, SkillType.LABELING},
            hourly_rate=24.0,
            efficiency_factor=0.9,
            max_hours_per_day=8.0
        )
    ]
    
    # Create equipment
    equipment = [
        Equipment(
            id=1,
            name="Packing Station 1",
            equipment_type=EquipmentType.PACKING_STATION,
            capacity=1,
            hourly_cost=5.0
        ),
        Equipment(
            id=2,
            name="Dock Door 1",
            equipment_type=EquipmentType.DOCK_DOOR,
            capacity=2,
            hourly_cost=3.0
        ),
        Equipment(
            id=3,
            name="Pick Cart 1",
            equipment_type=EquipmentType.PICK_CART,
            capacity=3,
            hourly_cost=2.0
        )
    ]
    
    # Create SKUs
    skus = [
        SKU(
            id=1,
            name="Widget A",
            zone=1,
            pick_time_minutes=2.0,
            pack_time_minutes=1.5,
            volume_cubic_feet=0.5,
            weight_lbs=2.0
        ),
        SKU(
            id=2,
            name="Widget B",
            zone=2,
            pick_time_minutes=3.0,
            pack_time_minutes=2.0,
            volume_cubic_feet=1.0,
            weight_lbs=5.0
        )
    ]
    
    # Create orders
    now = datetime.now()
    orders = []
    
    for i in range(5):
        order = Order(
            id=i+1,
            customer_id=i+1,
            priority=1,
            created_at=now,
            shipping_deadline=now + timedelta(hours=8),
            items=[
                OrderItem(sku_id=1, quantity=2),
                OrderItem(sku_id=2, quantity=1)
            ]
        )
        # Calculate times
        sku_dict = {sku.id: sku for sku in skus}
        order.calculate_times(sku_dict)
        orders.append(order)
    
    # Create warehouse config
    warehouse_config = WarehouseConfig(
        name="Test Warehouse",
        workers=workers,
        equipment=equipment,
        skus=skus
    )
    
    return warehouse_config, orders, workers, equipment

def test_optimization():
    """Test the optimization engine."""
    print("Testing Constraint Programming Optimization Engine")
    print("=" * 50)
    
    # Create test data
    warehouse_config, orders, workers, equipment = create_test_data()
    
    print(f"Created test data:")
    print(f"- {len(workers)} workers")
    print(f"- {len(equipment)} equipment")
    print(f"- {len(orders)} orders")
    print()
    
    # Test constraints
    constraints = OptimizationConstraints()
    print("Optimization Constraints:")
    for key, constraint in constraints.get_constraint_descriptions().items():
        print(f"- {constraint['name']}: {constraint['description']}")
    print()
    
    # Test requirements
    requirements = OptimizationRequirements()
    print("Optimization Requirements:")
    print(f"- Max solve time: {requirements.max_solve_time_seconds}s")
    print(f"- Max orders per wave: {requirements.max_orders_per_wave}")
    print(f"- Max workers: {requirements.max_workers}")
    print(f"- Time granularity: {requirements.time_granularity_minutes} minutes")
    print()
    
    # Create optimizer
    optimizer = MultiStageOptimizer(warehouse_config)
    
    # Create deadlines dictionary
    deadlines = {order.id: order.shipping_deadline for order in orders}
    
    print("Running optimization...")
    try:
        # Run optimization
        result = optimizer.optimize_workflow(orders, workers, equipment, deadlines)
        
        print("Optimization completed successfully!")
        print()
        print("Results:")
        print(f"- Total orders: {result.metrics.total_orders}")
        print(f"- On-time orders: {result.metrics.on_time_orders}")
        print(f"- On-time percentage: {result.metrics.on_time_percentage:.1f}%")
        print(f"- Total cost: ${result.metrics.total_cost:.2f}")
        print(f"- Optimization time: {result.metrics.optimization_runtime_seconds:.2f}s")
        print(f"- Solver status: {result.metrics.solver_status}")
        
        # Generate explanation
        explanation = optimizer.generate_explanation(result)
        print()
        print("Optimization Explanation:")
        print(explanation)
        
        return True
        
    except Exception as e:
        print(f"Optimization failed: {e}")
        return False

if __name__ == "__main__":
    success = test_optimization()
    sys.exit(0 if success else 1) 