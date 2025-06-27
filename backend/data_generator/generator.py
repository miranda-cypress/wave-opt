"""
Synthetic data generator for "MidWest Distribution Co" warehouse.

Creates realistic warehouse data with embedded inefficiencies that the
optimization will dramatically improve for compelling demo scenarios.
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional

from models.warehouse import (
    WarehouseConfig, Worker, Equipment, SKU, Order, OrderItem,
    StageType, SkillType, EquipmentType
)


class SyntheticDataGenerator:
    """
    Generates synthetic warehouse data for optimization demos.
    
    Creates data with embedded inefficiencies:
    - Suboptimal worker assignments
    - Equipment bottlenecks
    - Deadline violations
    - Inefficient stage sequencing
    """
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with a random seed."""
        random.seed(seed)
        np.random.seed(seed)
        
        # Worker names for realistic data
        self.worker_names = [
            "Sarah Johnson", "Mike Chen", "Lisa Rodriguez", "David Kim", "Emma Wilson",
            "James Thompson", "Maria Garcia", "Robert Lee", "Jennifer Davis", "Christopher Brown",
            "Amanda Miller", "Daniel Martinez", "Jessica Taylor", "Kevin Anderson", "Nicole White"
        ]
        
        # SKU categories and names
        self.sku_categories = {
            "Electronics": ["Laptop", "Phone", "Tablet", "Headphones", "Charger"],
            "Clothing": ["T-Shirt", "Jeans", "Sweater", "Jacket", "Shoes"],
            "Home": ["Lamp", "Chair", "Table", "Mirror", "Rug"],
            "Sports": ["Basketball", "Tennis Racket", "Yoga Mat", "Dumbbells", "Bike"],
            "Books": ["Novel", "Textbook", "Magazine", "Cookbook", "Journal"]
        }
        
    def generate_warehouse_config(self) -> WarehouseConfig:
        """Generate complete warehouse configuration."""
        workers = self._generate_workers()
        equipment = self._generate_equipment()
        skus = self._generate_skus()
        
        return WarehouseConfig(
            name="MidWest Distribution Co",
            total_sqft=85000,
            zones=5,
            workers=workers,
            equipment=equipment,
            skus=skus
        )
    
    def _generate_workers(self) -> List[Worker]:
        """Generate 15 workers with varying skills and efficiency."""
        workers = []
        
        # Define skill combinations (some workers are more specialized)
        skill_combinations = [
            # Multi-skilled workers (efficient)
            {SkillType.PICKING, SkillType.PACKING, SkillType.SHIPPING},
            {SkillType.PICKING, SkillType.CONSOLIDATION, SkillType.STAGING},
            {SkillType.PACKING, SkillType.LABELING, SkillType.SHIPPING},
            
            # Specialized workers (less efficient)
            {SkillType.PICKING},
            {SkillType.PACKING},
            {SkillType.SHIPPING},
            {SkillType.LABELING},
            {SkillType.CONSOLIDATION},
            {SkillType.STAGING},
            
            # Mixed skill workers
            {SkillType.PICKING, SkillType.PACKING},
            {SkillType.PACKING, SkillType.LABELING},
            {SkillType.SHIPPING, SkillType.STAGING},
            {SkillType.PICKING, SkillType.CONSOLIDATION},
            {SkillType.LABELING, SkillType.SHIPPING},
            {SkillType.CONSOLIDATION, SkillType.STAGING}
        ]
        
        for i in range(15):
            skills = skill_combinations[i]
            
            # Vary efficiency (some workers are more productive)
            efficiency = random.uniform(0.8, 1.2)
            
            # Vary hourly rates based on skills
            base_rate = 20.0
            skill_bonus = len(skills) * 2.0  # More skills = higher pay
            hourly_rate = base_rate + skill_bonus + random.uniform(-2, 2)
            
            worker = Worker(
                id=i + 1,
                name=self.worker_names[i],
                skills=skills,
                hourly_rate=hourly_rate,
                efficiency_factor=efficiency,
                max_hours_per_day=8.0
            )
            workers.append(worker)
        
        return workers
    
    def _generate_equipment(self) -> List[Equipment]:
        """Generate warehouse equipment with capacity constraints."""
        equipment = []
        
        # Packing stations (bottleneck equipment)
        for i in range(8):
            equipment.append(Equipment(
                id=i + 1,
                name=f"Packing Station {i + 1}",
                equipment_type=EquipmentType.PACKING_STATION,
                capacity=1,
                hourly_cost=15.0,
                efficiency_factor=random.uniform(0.9, 1.1)
            ))
        
        # Dock doors (shipping bottleneck)
        for i in range(6):
            equipment.append(Equipment(
                id=i + 9,
                name=f"Dock Door {i + 1}",
                equipment_type=EquipmentType.DOCK_DOOR,
                capacity=1,
                hourly_cost=5.0,
                efficiency_factor=1.0
            ))
        
        # Pick carts
        for i in range(20):
            equipment.append(Equipment(
                id=i + 15,
                name=f"Pick Cart {i + 1}",
                equipment_type=EquipmentType.PICK_CART,
                capacity=1,
                hourly_cost=2.0,
                efficiency_factor=1.0
            ))
        
        # Conveyors
        for i in range(3):
            equipment.append(Equipment(
                id=i + 35,
                name=f"Conveyor {i + 1}",
                equipment_type=EquipmentType.CONVEYOR,
                capacity=5,  # Can handle multiple items
                hourly_cost=8.0,
                efficiency_factor=1.0
            ))
        
        # Label printers
        for i in range(4):
            equipment.append(Equipment(
                id=i + 38,
                name=f"Label Printer {i + 1}",
                equipment_type=EquipmentType.LABEL_PRINTER,
                capacity=1,
                hourly_cost=3.0,
                efficiency_factor=1.0
            ))
        
        return equipment
    
    def _generate_skus(self) -> List[SKU]:
        """Generate 250 SKUs with Pareto distribution (80/15/5 rule)."""
        skus = []
        sku_id = 1
        
        # Generate SKUs with Pareto distribution
        for category, items in self.sku_categories.items():
            for item in items:
                # Create multiple variants of each item
                for variant in range(10):  # 10 variants per item = 250 total SKUs
                    
                    # Zone assignment (1-5)
                    zone = random.randint(1, 5)
                    
                    # Pick time (varies by category and efficiency)
                    base_pick_time = {
                        "Electronics": 3.0,
                        "Clothing": 2.0,
                        "Home": 4.0,
                        "Sports": 2.5,
                        "Books": 1.5
                    }[category]
                    
                    pick_time = base_pick_time + random.uniform(-0.5, 0.5)
                    
                    # Pack time (varies by item size)
                    pack_time = pick_time * random.uniform(0.8, 1.5)
                    
                    # Volume and weight (correlated with pack time)
                    volume = pack_time * random.uniform(0.5, 2.0)
                    weight = volume * random.uniform(0.3, 0.8)
                    
                    sku = SKU(
                        id=sku_id,
                        name=f"{item} {variant + 1}",
                        zone=zone,
                        pick_time_minutes=pick_time,
                        pack_time_minutes=pack_time,
                        volume_cubic_feet=volume,
                        weight_lbs=weight
                    )
                    skus.append(sku)
                    sku_id += 1
        
        return skus
    
    def generate_orders(self, num_orders: int = 100, 
                       start_time: Optional[datetime] = None) -> List[Order]:
        """Generate synthetic orders with realistic patterns and embedded inefficiencies."""
        if start_time is None:
            start_time = datetime.now()
        
        orders = []
        
        # Create SKU dictionary for reference
        sku_dict = {sku.id: sku for sku in self._generate_skus()}
        sku_ids = list(sku_dict.keys())
        
        for order_id in range(1, num_orders + 1):
            # Order characteristics
            customer_id = random.randint(1, 50)
            priority = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.3, 0.3, 0.1])[0]
            
            # Order creation time (within last 4 hours)
            created_at = start_time - timedelta(hours=random.uniform(0, 4))
            
            # Shipping deadline (creates some deadline pressure)
            deadline_hours = random.choices([2, 4, 6, 8, 12], weights=[0.1, 0.2, 0.3, 0.3, 0.1])[0]
            shipping_deadline = start_time + timedelta(hours=deadline_hours)
            
            # Order items (1-5 items per order)
            num_items = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.3, 0.2, 0.15, 0.05])[0]
            
            items = []
            for _ in range(num_items):
                sku_id = random.choice(sku_ids)
                quantity = random.randint(1, 5)
                
                item = OrderItem(
                    sku_id=sku_id,
                    quantity=quantity,
                    sku=sku_dict[sku_id]
                )
                items.append(item)
            
            # Create order
            order = Order(
                id=order_id,
                customer_id=customer_id,
                priority=priority,
                created_at=created_at,
                shipping_deadline=shipping_deadline,
                items=items
            )
            
            # Calculate processing times
            order.calculate_times(sku_dict)
            
            orders.append(order)
        
        return orders
    
    def generate_demo_scenario(self, scenario_type: str = "bottleneck") -> Dict:
        """
        Generate specific demo scenarios with embedded inefficiencies.
        
        Args:
            scenario_type: Type of scenario ("bottleneck", "deadline", "inefficient")
            
        Returns:
            Dictionary with warehouse config and orders
        """
        warehouse_config = self.generate_warehouse_config()
        
        if scenario_type == "bottleneck":
            # Create bottleneck scenario with too many orders needing packing
            orders = self._generate_bottleneck_scenario(warehouse_config)
        elif scenario_type == "deadline":
            # Create deadline pressure scenario
            orders = self._generate_deadline_scenario(warehouse_config)
        elif scenario_type == "inefficient":
            # Create inefficient worker assignment scenario
            orders = self._generate_inefficient_scenario(warehouse_config)
        else:
            # Default scenario
            orders = self.generate_orders(100)
        
        return {
            "warehouse_config": warehouse_config,
            "orders": orders,
            "scenario_type": scenario_type
        }
    
    def _generate_bottleneck_scenario(self, warehouse_config: WarehouseConfig) -> List[Order]:
        """Generate scenario with packing station bottleneck."""
        # Create orders that all need packing at the same time
        orders = []
        start_time = datetime.now()
        
        # Create 50 orders that all arrive within 1 hour
        for i in range(50):
            order = self._create_single_order(
                order_id=i + 1,
                start_time=start_time,
                deadline_hours=4,  # All need to ship within 4 hours
                high_pack_time=True  # Orders with high packing requirements
            )
            orders.append(order)
        
        return orders
    
    def _generate_deadline_scenario(self, warehouse_config: WarehouseConfig) -> List[Order]:
        """Generate scenario with tight deadlines."""
        orders = []
        start_time = datetime.now()
        
        # Create mix of urgent and normal orders
        for i in range(80):
            if i < 30:  # 30 urgent orders
                deadline_hours = random.uniform(1, 3)
            else:  # 50 normal orders
                deadline_hours = random.uniform(4, 8)
            
            order = self._create_single_order(
                order_id=i + 1,
                start_time=start_time,
                deadline_hours=deadline_hours
            )
            orders.append(order)
        
        return orders
    
    def _generate_inefficient_scenario(self, warehouse_config: WarehouseConfig) -> List[Order]:
        """Generate scenario with inefficient worker assignments."""
        # Create orders that require specific skills but workers are poorly assigned
        orders = []
        start_time = datetime.now()
        
        # Create orders that all need packing (but few workers have packing skills)
        for i in range(60):
            order = self._create_single_order(
                order_id=i + 1,
                start_time=start_time,
                deadline_hours=6,
                high_pack_time=True
            )
            orders.append(order)
        
        return orders
    
    def _create_single_order(self, order_id: int, start_time: datetime, 
                           deadline_hours: float, high_pack_time: bool = False) -> Order:
        """Helper method to create a single order."""
        # Generate SKUs for this order
        sku_dict = {sku.id: sku for sku in self._generate_skus()}
        sku_ids = list(sku_dict.keys())
        
        customer_id = random.randint(1, 50)
        priority = random.randint(1, 5)
        created_at = start_time - timedelta(hours=random.uniform(0, 2))
        shipping_deadline = start_time + timedelta(hours=deadline_hours)
        
        # Create items
        num_items = random.randint(1, 4)
        items = []
        
        for _ in range(num_items):
            sku_id = random.choice(sku_ids)
            quantity = random.randint(1, 3)
            
            item = OrderItem(
                sku_id=sku_id,
                quantity=quantity,
                sku=sku_dict[sku_id]
            )
            items.append(item)
        
        order = Order(
            id=order_id,
            customer_id=customer_id,
            priority=priority,
            created_at=created_at,
            shipping_deadline=shipping_deadline,
            items=items
        )
        
        order.calculate_times(sku_dict)
        return order 