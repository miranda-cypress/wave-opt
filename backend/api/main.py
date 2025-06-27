"""
FastAPI application for the AI Wave Optimization Agent.

Provides REST API endpoints for:
- Running optimization scenarios
- Generating synthetic data
- Retrieving optimization results
- Real-time optimization status
- Database-driven optimization
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from optimizer.wave_optimizer import MultiStageOptimizer, OptimizationConstraints, OptimizationRequirements
from data_generator.generator import SyntheticDataGenerator
from models.warehouse import (
    OptimizationInput, Worker, Equipment, SKU, Order, OrderItem, WarehouseConfig,
    SkillType, EquipmentType
)
from models.optimization import OptimizationResult
from database_service import DatabaseService


# Initialize FastAPI app
app = FastAPI(
    title="AI Wave Optimization Agent",
    description="Constraint programming optimization for mid-market warehouse workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
optimizer = None  # Will be initialized with warehouse config
data_generator = SyntheticDataGenerator()
db_service = DatabaseService()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Wave Optimization Agent API",
        "version": "1.0.0",
        "description": "Constraint programming optimization for warehouse workflows",
        "endpoints": {
            "/optimize": "Run optimization with custom input",
            "/optimize/scenario/{scenario_type}": "Run optimization with demo scenario",
            "/optimize/database": "Run optimization with database data",
            "/data/warehouse/{warehouse_id}": "Get warehouse data from database",
            "/data/stats/{warehouse_id}": "Get warehouse statistics",
            "/history": "Get optimization history",
            "/generate/data": "Generate synthetic warehouse data",
            "/health": "Health check endpoint",
            "/optimization/constraints": "Get optimization constraints and requirements"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_service.get_connection()
        db_healthy = True
    except Exception as e:
        db_healthy = False
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "optimizer_ready": True,
        "data_generator_ready": True,
        "database_ready": db_healthy
    }


@app.get("/data/warehouse/{warehouse_id}")
async def get_warehouse_data(warehouse_id: int = 1):
    """Get warehouse data from database."""
    try:
        workers = db_service.get_workers(warehouse_id)
        equipment = db_service.get_equipment(warehouse_id)
        skus = db_service.get_skus(warehouse_id)
        orders = db_service.get_pending_orders(warehouse_id, limit=50)
        
        return {
            "warehouse_id": warehouse_id,
            "workers": workers,
            "equipment": equipment,
            "skus": skus,
            "orders": orders,
            "summary": {
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "total_skus": len(skus),
                "total_orders": len(orders)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get warehouse data: {str(e)}")


@app.get("/data/stats/{warehouse_id}")
async def get_warehouse_stats(warehouse_id: int = 1):
    """Get warehouse statistics."""
    try:
        stats = db_service.get_warehouse_stats(warehouse_id)
        return {
            "warehouse_id": warehouse_id,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get warehouse stats: {str(e)}")


@app.post("/optimize/database")
async def optimize_database_data(warehouse_id: int = 1, order_limit: int = 50):
    """
    Run optimization using data from the database.
    
    Args:
        warehouse_id: ID of the warehouse to optimize
        order_limit: Maximum number of orders to include in optimization
        
    Returns:
        OptimizationResult with complete schedule and metrics
    """
    try:
        # Get data from database
        workers_data = db_service.get_workers(warehouse_id)
        equipment_data = db_service.get_equipment(warehouse_id)
        skus_data = db_service.get_skus(warehouse_id)
        orders_data = db_service.get_pending_orders(warehouse_id, limit=order_limit)
        
        if not orders_data:
            raise HTTPException(status_code=400, detail="No pending orders found for optimization")
        
        # Convert database data to Pydantic models
        # (Worker, Equipment, SKU, Order, OrderItem, WarehouseConfig already imported above)
        
        # Convert workers
        workers = []
        for w in workers_data:
            # Convert string skills to SkillType enums
            skills = set()
            if w['skills']:
                skill_mapping = {
                    'picking': SkillType.PICKING,
                    'packing': SkillType.PACKING,
                    'shipping': SkillType.SHIPPING,
                    'labeling': SkillType.LABELING,
                    'consolidation': SkillType.CONSOLIDATION,
                    'staging': SkillType.STAGING
                }
                for skill_str in w['skills']:
                    if skill_str in skill_mapping:
                        skills.add(skill_mapping[skill_str])
            
            workers.append(Worker(
                id=w['id'],
                name=w['name'],
                skills=skills,
                hourly_rate=w['hourly_rate'],
                efficiency_factor=w['efficiency_factor'],
                max_hours_per_day=w['max_hours_per_day']
            ))
        
        # Convert equipment
        equipment = []
        for e in equipment_data:
            # Convert string equipment type to EquipmentType enum
            equipment_type_mapping = {
                'packing_station': EquipmentType.PACKING_STATION,
                'dock_door': EquipmentType.DOCK_DOOR,
                'pick_cart': EquipmentType.PICK_CART,
                'conveyor': EquipmentType.CONVEYOR,
                'label_printer': EquipmentType.LABEL_PRINTER
            }
            
            equipment_type = equipment_type_mapping.get(e['equipment_type'], EquipmentType.PACKING_STATION)
            
            equipment.append(Equipment(
                id=e['id'],
                name=e['name'],
                equipment_type=equipment_type,
                capacity=e['capacity'],
                hourly_cost=e['hourly_cost'],
                efficiency_factor=e['efficiency_factor']
            ))
        
        # Convert SKUs
        skus = []
        for s in skus_data:
            skus.append(SKU(
                id=s['id'],
                name=s['name'],
                zone=s['zone'],
                pick_time_minutes=s['pick_time_minutes'],
                pack_time_minutes=s['pack_time_minutes'],
                volume_cubic_feet=s['volume_cubic_feet'],
                weight_lbs=s['weight_lbs']
            ))
        
        # Convert orders
        orders = []
        for o in orders_data:
            # Convert order items
            items = []
            for item in o['items']:
                items.append(OrderItem(
                    sku_id=item['sku_id'],
                    quantity=item['quantity']
                ))
            
            # Create order
            order = Order(
                id=o['id'],
                customer_id=o.get('customer_id', 1),  # Default customer ID
                priority=int(o['priority']),
                created_at=o['created_at'],
                shipping_deadline=o['shipping_deadline'],
                items=items,
                total_pick_time=o['total_pick_time'],
                total_pack_time=o['total_pack_time'],
                total_volume=o['total_volume'],
                total_weight=o['total_weight']
            )
            orders.append(order)
        
        # Create warehouse configuration
        warehouse_config = WarehouseConfig(
            name=f"Warehouse {warehouse_id}",
            total_sqft=85000,
            zones=5,
            workers=workers,
            equipment=equipment,
            skus=skus,
            shift_start_hour=6,
            shift_end_hour=22,
            max_orders_per_day=2500,
            deadline_penalty_per_hour=100.0,
            overtime_multiplier=1.5
        )
        
        # Save optimization run
        run_id = db_service.save_optimization_run(
            scenario_type="database",
            total_orders=len(orders),
            total_workers=len(workers),
            total_equipment=len(equipment)
        )
        
        # Initialize optimizer with warehouse config
        optimizer = MultiStageOptimizer(warehouse_config)
        
        # Run optimization using new interface
        start_time = datetime.now()
        result = optimizer.optimize_workflow(orders, workers, equipment, [order.shipping_deadline for order in orders])
        end_time = datetime.now()
        
        solve_time = (end_time - start_time).total_seconds()
        
        # Update optimization run with results
        db_service.update_optimization_run(
            run_id=run_id,
            objective_value=result.metrics.total_cost if result.metrics else 0.0,
            solver_status=result.metrics.solver_status if result.metrics else "UNKNOWN",
            solve_time_seconds=solve_time
        )
        
        # Save optimization schedule (simplified for now)
        schedules = []
        # Note: This would need to be updated based on the actual result structure
        # For now, we'll save a placeholder
        db_service.save_optimization_schedule(run_id, schedules)
        
        return {
            "status": "success",
            "run_id": run_id,
            "warehouse_id": warehouse_id,
            "result": result.to_summary_dict() if hasattr(result, 'to_summary_dict') else {
                "total_orders": len(orders),
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "optimization_time": solve_time
            },
            "input_summary": {
                "total_orders": len(orders),
                "total_workers": len(workers),
                "total_equipment": len(equipment)
            },
            "optimization_time": solve_time,
            "solver_status": result.metrics.solver_status if result.metrics else "UNKNOWN"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database optimization failed: {str(e)}")


@app.get("/history")
async def get_optimization_history(limit: int = 10):
    """Get recent optimization run history."""
    try:
        history = db_service.get_optimization_history(limit)
        return {
            "status": "success",
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@app.post("/optimize")
async def optimize_workflow(optimization_input: OptimizationInput):
    """Legacy endpoint - use /optimize/database instead."""
    raise HTTPException(status_code=400, detail="Use /optimize/database endpoint for optimization")


@app.get("/optimize/scenario/{scenario_type}")
async def optimize_scenario(scenario_type: str):
    """Legacy endpoint - use /optimize/database instead."""
    raise HTTPException(status_code=400, detail="Use /optimize/database endpoint for optimization")


@app.get("/optimize/stream/{scenario_type}")
async def optimize_scenario_stream(scenario_type: str):
    """Legacy endpoint - use /optimize/database instead."""
    raise HTTPException(status_code=400, detail="Use /optimize/database endpoint for optimization")


@app.get("/generate/data")
async def generate_data(scenario_type: str = "bottleneck", num_orders: int = 100):
    """
    Generate synthetic warehouse data.
    
    Args:
        scenario_type: Type of scenario to generate
        num_orders: Number of orders to generate
        
    Returns:
        Generated warehouse configuration and orders
    """
    try:
        if scenario_type in ["bottleneck", "deadline", "inefficient"]:
            scenario_data = data_generator.generate_demo_scenario(scenario_type)
        else:
            # Generate custom data
            warehouse_config = data_generator.generate_warehouse_config()
            orders = data_generator.generate_orders(num_orders)
            scenario_data = {
                "warehouse_config": warehouse_config,
                "orders": orders,
                "scenario_type": "custom"
            }
        
        return {
            "status": "success",
            "scenario_type": scenario_data["scenario_type"],
            "warehouse_config": {
                "name": scenario_data["warehouse_config"].name,
                "total_sqft": scenario_data["warehouse_config"].total_sqft,
                "zones": scenario_data["warehouse_config"].zones,
                "workers_count": len(scenario_data["warehouse_config"].workers),
                "equipment_count": len(scenario_data["warehouse_config"].equipment),
                "skus_count": len(scenario_data["warehouse_config"].skus)
            },
            "orders_count": len(scenario_data["orders"]),
            "orders_summary": {
                "priority_distribution": {
                    "1": len([o for o in scenario_data["orders"] if o.priority == 1]),
                    "2": len([o for o in scenario_data["orders"] if o.priority == 2]),
                    "3": len([o for o in scenario_data["orders"] if o.priority == 3]),
                    "4": len([o for o in scenario_data["orders"] if o.priority == 4]),
                    "5": len([o for o in scenario_data["orders"] if o.priority == 5])
                },
                "avg_pick_time": sum(o.total_pick_time for o in scenario_data["orders"]) / len(scenario_data["orders"]),
                "avg_pack_time": sum(o.total_pack_time for o in scenario_data["orders"]) / len(scenario_data["orders"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")


@app.get("/scenarios")
async def list_scenarios():
    """List available demo scenarios."""
    return {
        "scenarios": [
            {
                "id": "bottleneck",
                "name": "Equipment Bottleneck",
                "description": "Too many orders requiring packing stations simultaneously",
                "embedded_inefficiency": "Packing station capacity constraint creates backlog"
            },
            {
                "id": "deadline",
                "name": "Deadline Pressure",
                "description": "Mix of urgent and normal orders with tight deadlines",
                "embedded_inefficiency": "Suboptimal sequencing leads to deadline violations"
            },
            {
                "id": "inefficient",
                "name": "Inefficient Worker Assignment",
                "description": "Orders requiring specific skills but workers poorly assigned",
                "embedded_inefficiency": "Workers with limited skills create bottlenecks"
            }
        ]
    }


@app.get("/metrics")
async def get_optimization_metrics():
    """Get optimization performance metrics and targets."""
    return {
        "target_improvements": {
            "labor_cost_reduction": "15-25%",
            "equipment_utilization": "85-95%",
            "on_time_performance": "98-99%",
            "processing_time_reduction": "20-30%"
        },
        "current_performance": {
            "avg_labor_cost_per_order": "$12.50",
            "avg_equipment_utilization": "72%",
            "avg_on_time_performance": "94%",
            "avg_processing_time": "45 minutes"
        }
    }


@app.get("/optimization/constraints")
async def get_optimization_constraints():
    """Get optimization constraints and requirements for display."""
    constraints = OptimizationConstraints()
    requirements = OptimizationRequirements()
    
    return {
        "constraints": constraints.get_constraint_descriptions(),
        "objective_weights": constraints.get_objective_weights(),
        "requirements": {
            "max_solve_time_seconds": requirements.max_solve_time_seconds,
            "max_orders_per_wave": requirements.max_orders_per_wave,
            "max_workers": requirements.max_workers,
            "stages": [stage.value for stage in requirements.stages],
            "time_granularity_minutes": requirements.time_granularity_minutes,
            "min_efficiency_improvement": requirements.min_efficiency_improvement,
            "target_on_time_delivery": requirements.target_on_time_delivery,
            "max_overtime_hours_per_day": requirements.max_overtime_hours_per_day
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 