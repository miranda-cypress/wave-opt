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
from psycopg2.extras import RealDictCursor
import time

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
        
        # Save optimization plan to database
        try:
            # Convert result to dictionary format for database storage
            result_dict = result.to_summary_dict() if hasattr(result, 'to_summary_dict') else {
                "total_orders": len(orders),
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "metrics": {
                    "total_cost": result.metrics.total_cost if result.metrics else 0.0,
                    "solver_status": result.metrics.solver_status if result.metrics else "UNKNOWN",
                    "solve_time_seconds": solve_time
                }
            }
            
            # Add order schedules if available
            if hasattr(result, 'order_schedules') and result.order_schedules:
                result_dict['order_schedules'] = []
                for order_schedule in result.order_schedules:
                    schedule_dict = {
                        'order_id': order_schedule.order_id,
                        'stages': []
                    }
                    for stage in order_schedule.stages:
                        stage_dict = {
                            'stage': stage.stage_type.value if hasattr(stage.stage_type, 'value') else str(stage.stage_type),
                            'start_time_minutes': int((stage.start_time - datetime.now()).total_seconds() / 60) if stage.start_time else 0,
                            'duration_minutes': stage.duration_minutes,
                            'worker_id': stage.assigned_worker_id,
                            'equipment_id': stage.assigned_equipment_id,
                            'worker_name': '',  # Will be populated from worker lookup
                            'waiting_time_before': 0,  # Will be calculated
                            'sequence_order': 0  # Will be set based on order
                        }
                        schedule_dict['stages'].append(stage_dict)
                    result_dict['order_schedules'].append(schedule_dict)
            
            # Save the complete optimization plan
            db_service.save_optimization_plan(run_id, result_dict)
            
        except Exception as e:
            # Log error but don't fail the optimization
            print(f"Warning: Failed to save optimization plan: {e}")
        
        return {
            "status": "success",
            "run_id": run_id,
            "warehouse_id": warehouse_id,
            "result": result.to_summary_dict() if hasattr(result, 'to_summary_dict') else {
                "total_orders": len(orders),
                "total_workers": len(workers),
                "total_equipment": len(equipment),
                "solve_time_seconds": solve_time
            }
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
    """Get optimization constraints and requirements."""
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
            "time_granularity_minutes": requirements.time_granularity_minutes
        }
    }


@app.get("/optimization/plans/{run_id}")
async def get_optimization_plan(run_id: int):
    """
    Get detailed optimization plan for a specific run.
    
    Args:
        run_id: ID of the optimization run
        
    Returns:
        Complete optimization plan with summary and order timelines
    """
    try:
        plan = db_service.get_optimization_plan(run_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Optimization plan not found for run {run_id}")
        
        return {
            "status": "success",
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization plan: {str(e)}")


@app.get("/optimization/plans/latest")
async def get_latest_optimization_plan():
    """
    Get the most recent optimization plan.
    
    Returns:
        Latest optimization plan with summary and order timelines
    """
    try:
        plan = db_service.get_latest_optimization_plan()
        if not plan:
            raise HTTPException(status_code=404, detail="No optimization plans found")
        
        return {
            "status": "success",
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest optimization plan: {str(e)}")


@app.get("/optimization/plans/scenario/{scenario_type}")
async def get_optimization_plans_by_scenario(scenario_type: str, limit: int = 5):
    """
    Get optimization plans for a specific scenario type.
    
    Args:
        scenario_type: Type of scenario (e.g., 'bottleneck', 'deadline', 'mixed')
        limit: Maximum number of plans to return
        
    Returns:
        List of optimization plans for the scenario
    """
    try:
        plans = db_service.get_optimization_plans_by_scenario(scenario_type, limit)
        
        return {
            "status": "success",
            "scenario_type": scenario_type,
            "plans": plans
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization plans: {str(e)}")


@app.get("/optimization/original/order/{order_id}")
async def get_original_wms_plan(order_id: int):
    """
    Get original WMS plan for a specific order.
    
    Args:
        order_id: ID of the order
        
    Returns:
        Original WMS plan with stage-by-stage breakdown
    """
    try:
        original_plan = db_service.get_original_wms_plan(order_id)
        if not original_plan:
            raise HTTPException(status_code=404, detail=f"Original plan not found for order {order_id}")
        
        return {
            "status": "success",
            "order_id": order_id,
            "original_plan": original_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get original plan: {str(e)}")


@app.get("/optimization/original/summary")
async def get_original_wms_plan_summary():
    """
    Get summary of original WMS plans for all orders.
    
    Returns:
        Summary metrics for original plans
    """
    try:
        summary = db_service.get_original_wms_plan_summary()
        
        return {
            "status": "success",
            "original_plan_summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get original plan summary: {str(e)}")


@app.post("/optimization/original/refresh")
async def refresh_original_plans():
    """
    Refresh the original WMS plans materialized view.
    
    Returns:
        Success message
    """
    try:
        db_service.refresh_original_plans()
        
        return {
            "status": "success",
            "message": "Original WMS plans refreshed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh original plans: {str(e)}")


@app.get("/optimization/original/inefficiencies")
async def get_wms_inefficiencies():
    """
    Analyze inefficiencies in the original WMS approach.
    
    Returns:
        Analysis of WMS inefficiencies and their impact
    """
    try:
        conn = db_service.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM analyze_wms_inefficiencies()")
            inefficiencies = [dict(row) for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "wms_inefficiencies": inefficiencies,
            "analysis": {
                "description": "Analysis of common inefficiencies in basic WMS systems",
                "total_inefficiencies": len(inefficiencies),
                "high_impact_count": len([i for i in inefficiencies if i['impact_level'] == 'High']),
                "medium_impact_count": len([i for i in inefficiencies if i['impact_level'] == 'Medium'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze WMS inefficiencies: {str(e)}")


@app.post("/optimization/run")
async def run_optimization():
    """
    Run optimization on the same 100 orders used in the original plan.
    
    Returns:
        Optimization results with plan details
    """
    try:
        # Get the same 100 orders used in the original plan
        orders = db_service.get_orders_for_optimization(100)
        
        if not orders:
            raise HTTPException(status_code=400, detail="No orders available for optimization")
        
        print(f"Running optimization on {len(orders)} orders")
        
        # Get workers and equipment
        workers = db_service.get_workers()
        equipment = db_service.get_equipment()
        skus = db_service.get_skus()
        
        # Create warehouse config
        from models.warehouse import WarehouseConfig, Worker, Equipment, SKU, Order, OrderItem
        from datetime import datetime
        
        # Convert workers to Worker objects
        worker_objects = []
        for w in workers:
            worker = Worker(
                id=w['id'],
                name=w['name'],
                skills=set(w['skills']),
                hourly_rate=w['hourly_rate'],
                efficiency_factor=w['efficiency_factor'],
                max_hours_per_day=w['max_hours_per_day']
            )
            worker_objects.append(worker)
        
        # Convert equipment to Equipment objects
        equipment_objects = []
        for e in equipment:
            equipment_obj = Equipment(
                id=e['id'],
                name=e['name'],
                equipment_type=e['equipment_type'],
                capacity=e['capacity'],
                hourly_cost=e['hourly_cost'],
                efficiency_factor=e['efficiency_factor']
            )
            equipment_objects.append(equipment_obj)
        
        # Convert SKUs to SKU objects
        sku_objects = []
        for s in skus:
            sku = SKU(
                id=s['id'],
                name=s['name'],
                zone=s['zone'],
                pick_time_minutes=s['pick_time_minutes'],
                pack_time_minutes=s['pack_time_minutes'],
                volume_cubic_feet=s['volume_cubic_feet'],
                weight_lbs=s['weight_lbs']
            )
            sku_objects.append(sku)
        
        warehouse_config = WarehouseConfig(
            name="MidWest Distribution Co",
            total_sqft=85000,
            zones=5,
            workers=worker_objects,
            equipment=equipment_objects,
            skus=sku_objects
        )
        
        # Create optimizer
        optimizer = MultiStageOptimizer(warehouse_config)
        
        # Convert orders to Order objects and create deadlines dict
        order_objects = []
        deadlines = {}
        
        for order_data in orders:
            # Create dummy order items for now (we'll use the calculated times)
            items = [OrderItem(sku_id=1, quantity=order_data['total_items'])]
            
            order = Order(
                id=order_data['id'],
                customer_id=1,  # Default customer ID
                priority=order_data['priority'],
                created_at=datetime.now(),
                shipping_deadline=order_data['shipping_deadline'],
                items=items,
                total_pick_time=order_data['total_pick_time'],
                total_pack_time=order_data['total_pack_time'],
                total_weight=order_data['total_weight']
            )
            order_objects.append(order)
            deadlines[order.id] = order.shipping_deadline
        
        # Create optimization run record
        run_id = db_service.save_optimization_run(
            scenario_type="100_order_test",
            total_orders=len(orders),
            total_workers=len(workers),
            total_equipment=len(equipment)
        )
        
        # Run optimization
        start_time = time.time()
        optimized_plan = optimizer.optimize_workflow(order_objects, worker_objects, equipment_objects, deadlines)
        optimization_time = time.time() - start_time
        
        if not optimized_plan:
            raise HTTPException(status_code=500, detail="Optimization failed to generate a plan")
        
        # Update optimization run with results
        db_service.update_optimization_run(
            run_id=run_id,
            objective_value=optimized_plan.metrics.total_cost,
            solver_status=optimized_plan.metrics.solver_status,
            solve_time_seconds=optimization_time
        )
        
        # Convert OptimizationResult to dict for saving
        optimization_dict = {
            'order_schedules': [
                {
                    'order_id': schedule.order_id,
                    'customer_id': schedule.customer_id,
                    'priority': schedule.priority,
                    'shipping_deadline': schedule.shipping_deadline,
                    'stages': [
                        {
                            'stage': stage.stage_type.value,
                            'start_time': stage.start_time,
                            'end_time': stage.end_time,
                            'duration_minutes': stage.duration_minutes,
                            'assigned_worker_id': stage.assigned_worker_id,
                            'assigned_equipment_id': stage.assigned_equipment_id
                        }
                        for stage in schedule.stages
                    ]
                }
                for schedule in optimized_plan.order_schedules
            ],
            'metrics': {
                'total_orders': optimized_plan.metrics.total_orders,
                'on_time_orders': optimized_plan.metrics.on_time_orders,
                'late_orders': optimized_plan.metrics.late_orders,
                'on_time_percentage_optimized': optimized_plan.metrics.on_time_percentage,
                'total_labor_cost': optimized_plan.metrics.total_labor_cost,
                'total_equipment_cost': optimized_plan.metrics.total_equipment_cost,
                'total_deadline_penalties': optimized_plan.metrics.total_deadline_penalties,
                'total_cost_optimized': optimized_plan.metrics.total_cost,
                'average_order_processing_time': optimized_plan.metrics.average_order_processing_time,
                'total_processing_time_optimized': optimized_plan.metrics.total_processing_time,
                'optimization_runtime_seconds': optimized_plan.metrics.optimization_runtime_seconds,
                'solver_status': optimized_plan.metrics.solver_status
            }
        }
        
        # Save the optimized plan
        db_service.save_optimization_plan(run_id, optimization_dict)
        
        # Get the saved plan
        summary = db_service.get_optimization_plan(run_id)
        
        return {
            "status": "success",
            "message": f"Optimization completed successfully on {len(orders)} orders",
            "plan_id": run_id,
            "optimization_time_seconds": round(optimization_time, 2),
            "orders_processed": len(orders),
            "summary": summary
        }
        
    except Exception as e:
        print(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 