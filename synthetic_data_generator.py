#!/usr/bin/env python3
"""
Synthetic Data Generator for AI Wave Optimization Agent

This module generates realistic warehouse data for demo scenarios including:
- Worker skills and efficiency patterns
- Equipment capacity and utilization
- Order patterns with embedded inefficiencies
- SKU distribution across zones
- Customer order behaviors

The generator creates data that showcases optimization opportunities:
1. Bottleneck scenarios (equipment/resource constraints)
2. Deadline pressure scenarios (tight shipping windows)
3. Inefficient assignment scenarios (skill mismatches)
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
import json
import csv
from pathlib import Path


@dataclass
class WorkerProfile:
    """Worker profile with skills and characteristics."""
    name: str
    skills: Set[str]
    hourly_rate: float
    efficiency_factor: float
    max_hours_per_day: float
    reliability_score: float  # 0.0-1.0, affects actual vs expected performance


@dataclass
class EquipmentProfile:
    """Equipment profile with capacity and characteristics."""
    name: str
    equipment_type: str
    capacity: int
    hourly_cost: float
    efficiency_factor: float
    maintenance_frequency: float  # Hours between maintenance
    current_utilization: float  # Current utilization rate


@dataclass
class SKUProfile:
    """SKU profile with processing characteristics."""
    name: str
    category: str
    zone: int
    pick_time_minutes: float
    pack_time_minutes: float
    volume_cubic_feet: float
    weight_lbs: float
    demand_pattern: str  # 'high', 'medium', 'low', 'seasonal'
    shelf_life_days: Optional[int] = None


@dataclass
class CustomerProfile:
    """Customer profile with ordering patterns."""
    name: str
    customer_type: str  # 'retail', 'wholesale', 'ecommerce', 'b2b'
    order_frequency: float  # Orders per week
    avg_order_value: float
    priority_tendency: str  # 'high', 'medium', 'low'
    deadline_preference: str  # 'tight', 'standard', 'flexible'


class SyntheticDataGenerator:
    """
    Generates synthetic warehouse data with embedded optimization opportunities.
    
    Creates realistic scenarios that demonstrate:
    - Equipment bottlenecks
    - Skill mismatches
    - Deadline pressures
    - Inefficient resource allocation
    """
    
    def __init__(self, seed: int = 42):
        """Initialize the generator with a random seed."""
        random.seed(seed)
        np.random.seed(seed)
        
        # Worker names for realistic data
        self.worker_names = [
            "Sarah Johnson", "Mike Chen", "Lisa Rodriguez", "David Kim", "Emma Wilson",
            "James Thompson", "Maria Garcia", "Robert Lee", "Jennifer Davis", "Christopher Brown",
            "Amanda Miller", "Daniel Martinez", "Jessica Taylor", "Kevin Anderson", "Nicole White",
            "Alex Turner", "Rachel Green", "Michael Scott", "Pam Beesly", "Dwight Schrute"
        ]
        
        # Equipment names by type
        self.equipment_names = {
            'packing_station': [f"Packing Station {i}" for i in range(1, 11)],
            'dock_door': [f"Dock Door {i}" for i in range(1, 9)],
            'pick_cart': [f"Pick Cart {i}" for i in range(1, 26)],
            'conveyor': [f"Conveyor {i}" for i in range(1, 6)],
            'label_printer': [f"Label Printer {i}" for i in range(1, 6)],
            'forklift': [f"Forklift {i}" for i in range(1, 4)],
            'pallet_jack': [f"Pallet Jack {i}" for i in range(1, 8)]
        }
        
        # SKU categories and items
        self.sku_categories = {
            "Electronics": [
                "Laptop Pro 15\"", "Laptop Pro 13\"", "Smartphone X", "Tablet Air", "Wireless Headphones",
                "USB-C Charger", "Bluetooth Speaker", "Gaming Mouse", "Mechanical Keyboard", "Monitor 27\"",
                "Webcam HD", "Microphone USB", "Headset Gaming", "Power Bank", "Cable Set"
            ],
            "Clothing": [
                "Cotton T-Shirt L", "Denim Jeans 32x32", "Wool Sweater M", "Leather Jacket L", "Running Shoes 10",
                "Hoodie XL", "Dress Shirt M", "Winter Coat L", "Athletic Shorts M", "Socks Pack 6",
                "Dress Pants 34x32", "Polo Shirt M", "Sneakers Casual", "Belt Leather", "Tie Silk"
            ],
            "Home": [
                "Table Lamp Modern", "Office Chair Ergonomic", "Coffee Table Wood", "Wall Mirror Round", "Area Rug 8x10",
                "Throw Pillow Decorative", "Desk Lamp LED", "Bookshelf 5-Shelf", "Bedside Table", "Floor Vase Ceramic",
                "Picture Frame 8x10", "Candle Set", "Plant Pot Ceramic", "Wall Clock", "Doormat Welcome"
            ],
            "Sports": [
                "Basketball Official", "Tennis Racket Pro", "Yoga Mat Premium", "Dumbbells 20lb Pair", "Mountain Bike 26\"",
                "Treadmill Electric", "Weight Bench Adjustable", "Golf Clubs Set", "Soccer Ball Size 5", "Swimming Goggles",
                "Baseball Glove", "Hockey Stick", "Volleyball", "Badminton Set", "Fishing Rod"
            ],
            "Books": [
                "Novel Bestseller", "Textbook Calculus", "Magazine Monthly", "Cookbook Recipes", "Journal Hardcover",
                "Children Book Illustrated", "Reference Dictionary", "Poetry Collection", "Biography Hardcover", "Self-Help Paperback",
                "Mystery Novel", "Science Fiction", "History Book", "Art Book", "Travel Guide"
            ]
        }
        
        # Customer names and types
        self.customer_profiles = [
            ("Acme Corporation", "b2b", 15.0, 2500.0, "high", "tight"),
            ("TechStart Inc", "b2b", 8.0, 1800.0, "high", "tight"),
            ("Global Retail Co", "retail", 25.0, 1200.0, "medium", "standard"),
            ("Local Store Chain", "retail", 12.0, 800.0, "medium", "standard"),
            ("Online Marketplace", "ecommerce", 50.0, 600.0, "low", "flexible"),
            ("University Bookstore", "b2b", 5.0, 3000.0, "high", "tight"),
            ("Sports Equipment Plus", "retail", 18.0, 1500.0, "medium", "standard"),
            ("Home Decor Outlet", "retail", 22.0, 900.0, "medium", "standard"),
            ("Fashion Forward", "ecommerce", 35.0, 700.0, "low", "flexible"),
            ("Electronics Hub", "b2b", 10.0, 2200.0, "high", "tight")
        ]
    
    def generate_worker_profiles(self, num_workers: int = 20) -> List[WorkerProfile]:
        """Generate worker profiles with realistic skill distributions."""
        workers = []
        
        # Define skill combinations with different efficiency levels
        skill_combinations = [
            # Multi-skilled workers (high efficiency)
            ({"picking", "packing", "shipping"}, 1.15, 0.95),
            ({"picking", "consolidation", "staging"}, 1.12, 0.93),
            ({"packing", "labeling", "shipping"}, 1.18, 0.97),
            ({"picking", "packing", "consolidation"}, 1.10, 0.94),
            ({"packing", "labeling", "shipping"}, 1.16, 0.96),
            
            # Specialized workers (lower efficiency)
            ({"picking"}, 0.95, 0.85),
            ({"packing"}, 0.98, 0.88),
            ({"shipping"}, 1.02, 0.90),
            ({"labeling"}, 0.92, 0.82),
            ({"consolidation"}, 1.00, 0.87),
            
            # Mixed skill workers (medium efficiency)
            ({"picking", "packing"}, 1.05, 0.91),
            ({"packing", "labeling"}, 1.07, 0.92),
            ({"shipping", "staging"}, 1.03, 0.89),
            ({"picking", "consolidation"}, 1.01, 0.88),
            ({"labeling", "shipping"}, 1.08, 0.93),
            
            # Additional workers for larger scenarios
            ({"picking", "packing", "labeling"}, 1.13, 0.94),
            ({"consolidation", "staging", "shipping"}, 1.09, 0.91),
            ({"picking", "staging"}, 1.04, 0.90),
            ({"packing", "shipping"}, 1.11, 0.95),
            ({"labeling", "consolidation"}, 1.06, 0.89)
        ]
        
        for i in range(min(num_workers, len(skill_combinations))):
            skills, efficiency, reliability = skill_combinations[i]
            
            # Vary hourly rates based on skills and efficiency
            base_rate = 20.0
            skill_bonus = len(skills) * 2.5  # More skills = higher pay
            efficiency_bonus = (efficiency - 1.0) * 10.0  # Efficiency bonus
            hourly_rate = base_rate + skill_bonus + efficiency_bonus + random.uniform(-3, 3)
            
            worker = WorkerProfile(
                name=self.worker_names[i],
                skills=skills,
                hourly_rate=max(15.0, hourly_rate),  # Minimum wage
                efficiency_factor=efficiency,
                max_hours_per_day=8.0,
                reliability_score=reliability
            )
            workers.append(worker)
        
        return workers
    
    def generate_equipment_profiles(self) -> List[EquipmentProfile]:
        """Generate equipment profiles with capacity constraints."""
        equipment = []
        
        # Packing stations (bottleneck equipment)
        for i, name in enumerate(self.equipment_names['packing_station'][:8]):
            equipment.append(EquipmentProfile(
                name=name,
                equipment_type='packing_station',
                capacity=1,
                hourly_cost=15.0,
                efficiency_factor=random.uniform(0.9, 1.1),
                maintenance_frequency=40.0,  # Every 40 hours
                current_utilization=random.uniform(0.7, 0.95)  # High utilization
            ))
        
        # Dock doors (shipping bottleneck)
        for i, name in enumerate(self.equipment_names['dock_door'][:6]):
            equipment.append(EquipmentProfile(
                name=name,
                equipment_type='dock_door',
                capacity=1,
                hourly_cost=5.0,
                efficiency_factor=1.0,
                maintenance_frequency=80.0,
                current_utilization=random.uniform(0.6, 0.9)
            ))
        
        # Pick carts
        for i, name in enumerate(self.equipment_names['pick_cart'][:20]):
            equipment.append(EquipmentProfile(
                name=name,
                equipment_type='pick_cart',
                capacity=1,
                hourly_cost=2.0,
                efficiency_factor=1.0,
                maintenance_frequency=60.0,
                current_utilization=random.uniform(0.5, 0.8)
            ))
        
        # Conveyors
        for i, name in enumerate(self.equipment_names['conveyor'][:3]):
            equipment.append(EquipmentProfile(
                name=name,
                equipment_type='conveyor',
                capacity=5,  # Can handle multiple items
                hourly_cost=8.0,
                efficiency_factor=1.0,
                maintenance_frequency=100.0,
                current_utilization=random.uniform(0.4, 0.7)
            ))
        
        # Label printers
        for i, name in enumerate(self.equipment_names['label_printer'][:4]):
            equipment.append(EquipmentProfile(
                name=name,
                equipment_type='label_printer',
                capacity=1,
                hourly_cost=3.0,
                efficiency_factor=1.0,
                maintenance_frequency=50.0,
                current_utilization=random.uniform(0.6, 0.9)
            ))
        
        return equipment
    
    def generate_sku_profiles(self) -> List[SKUProfile]:
        """Generate SKU profiles with realistic processing characteristics."""
        skus = []
        sku_id = 1
        
        # Base processing times by category
        category_times = {
            "Electronics": {"pick": 3.2, "pack": 3.8, "volume": 2.1, "weight": 3.5},
            "Clothing": {"pick": 2.1, "pack": 2.4, "volume": 0.9, "weight": 0.8},
            "Home": {"pick": 3.8, "pack": 4.2, "volume": 4.5, "weight": 6.2},
            "Sports": {"pick": 3.1, "pack": 3.5, "volume": 8.2, "weight": 12.8},
            "Books": {"pick": 1.8, "pack": 2.0, "volume": 0.7, "weight": 1.2}
        }
        
        # Demand patterns
        demand_patterns = ["high", "medium", "low", "seasonal"]
        demand_weights = [0.3, 0.4, 0.2, 0.1]  # 30% high, 40% medium, 20% low, 10% seasonal
        
        for category, items in self.sku_categories.items():
            base_times = category_times[category]
            
            for item in items:
                # Zone assignment (1-5)
                zone = random.randint(1, 5)
                
                # Vary processing times
                pick_time = base_times["pick"] + random.uniform(-0.5, 0.5)
                pack_time = base_times["pack"] + random.uniform(-0.3, 0.3)
                
                # Volume and weight (correlated with pack time)
                volume = base_times["volume"] + random.uniform(-0.5, 1.0)
                weight = base_times["weight"] + random.uniform(-1.0, 2.0)
                
                # Demand pattern
                demand_pattern = random.choices(demand_patterns, weights=demand_weights)[0]
                
                # Shelf life for perishable items (some clothing, books)
                shelf_life = None
                if category in ["Clothing", "Books"] and random.random() < 0.3:
                    shelf_life = random.randint(30, 365)  # 30 days to 1 year
                
                sku = SKUProfile(
                    name=item,
                    category=category,
                    zone=zone,
                    pick_time_minutes=max(0.5, pick_time),
                    pack_time_minutes=max(0.5, pack_time),
                    volume_cubic_feet=max(0.1, volume),
                    weight_lbs=max(0.1, weight),
                    demand_pattern=demand_pattern,
                    shelf_life_days=shelf_life
                )
                skus.append(sku)
                sku_id += 1
        
        return skus
    
    def generate_customer_profiles(self) -> List[CustomerProfile]:
        """Generate customer profiles with realistic ordering patterns."""
        customers = []
        
        for name, customer_type, order_freq, avg_value, priority, deadline in self.customer_profiles:
            customer = CustomerProfile(
                name=name,
                customer_type=customer_type,
                order_frequency=order_freq + random.uniform(-2, 2),
                avg_order_value=avg_value + random.uniform(-200, 200),
                priority_tendency=priority,
                deadline_preference=deadline
            )
            customers.append(customer)
        
        return customers
    
    def generate_orders(self, num_orders: int, customers: List[CustomerProfile], 
                       skus: List[SKUProfile], scenario_type: str = "mixed") -> List[Dict]:
        """Generate orders with embedded inefficiencies based on scenario type."""
        orders = []
        
        # Scenario-specific order generation
        if scenario_type == "bottleneck":
            orders = self._generate_bottleneck_orders(num_orders, customers, skus)
        elif scenario_type == "deadline":
            orders = self._generate_deadline_orders(num_orders, customers, skus)
        elif scenario_type == "inefficient":
            orders = self._generate_inefficient_orders(num_orders, customers, skus)
        else:
            orders = self._generate_mixed_orders(num_orders, customers, skus)
        
        return orders
    
    def _generate_bottleneck_orders(self, num_orders: int, customers: List[CustomerProfile], 
                                  skus: List[SKUProfile]) -> List[Dict]:
        """Generate orders that create equipment bottlenecks."""
        orders = []
        
        # Focus on orders that require packing stations
        packing_skus = [sku for sku in skus if sku.category in ["Electronics", "Home", "Sports"]]
        
        for i in range(num_orders):
            customer = random.choice(customers)
            
            # Create orders with high pack time requirements
            order_items = []
            total_pick_time = 0
            total_pack_time = 0
            total_volume = 0
            total_weight = 0
            
            # 3-6 items per order, mostly packing-intensive
            num_items = random.randint(3, 6)
            for _ in range(num_items):
                sku = random.choice(packing_skus)
                quantity = random.randint(1, 3)
                
                order_items.append({
                    "sku_id": sku.name,
                    "quantity": quantity,
                    "pick_time": sku.pick_time_minutes * quantity,
                    "pack_time": sku.pack_time_minutes * quantity,
                    "volume": sku.volume_cubic_feet * quantity,
                    "weight": sku.weight_lbs * quantity
                })
                
                total_pick_time += sku.pick_time_minutes * quantity
                total_pack_time += sku.pack_time_minutes * quantity
                total_volume += sku.volume_cubic_feet * quantity
                total_weight += sku.weight_lbs * quantity
            
            # Deadline: 4-8 hours (creates bottleneck pressure)
            deadline_hours = random.uniform(4, 8)
            deadline = datetime.now() + timedelta(hours=deadline_hours)
            
            order = {
                "id": i + 1,
                "customer": customer.name,
                "customer_type": customer.customer_type,
                "priority": random.choice(["1", "2", "3"]),  # Higher priority
                "created_at": datetime.now(),
                "shipping_deadline": deadline,
                "items": order_items,
                "total_pick_time": total_pick_time,
                "total_pack_time": total_pack_time,
                "total_volume": total_volume,
                "total_weight": total_weight,
                "status": "pending"
            }
            orders.append(order)
        
        return orders
    
    def _generate_deadline_orders(self, num_orders: int, customers: List[CustomerProfile], 
                                skus: List[SKUProfile]) -> List[Dict]:
        """Generate orders with tight deadlines."""
        orders = []
        
        for i in range(num_orders):
            customer = random.choice(customers)
            
            order_items = []
            total_pick_time = 0
            total_pack_time = 0
            total_volume = 0
            total_weight = 0
            
            # 2-4 items per order (smaller orders for tight deadlines)
            num_items = random.randint(2, 4)
            for _ in range(num_items):
                sku = random.choice(skus)
                quantity = random.randint(1, 2)
                
                order_items.append({
                    "sku_id": sku.name,
                    "quantity": quantity,
                    "pick_time": sku.pick_time_minutes * quantity,
                    "pack_time": sku.pack_time_minutes * quantity,
                    "volume": sku.volume_cubic_feet * quantity,
                    "weight": sku.weight_lbs * quantity
                })
                
                total_pick_time += sku.pick_time_minutes * quantity
                total_pack_time += sku.pack_time_minutes * quantity
                total_volume += sku.volume_cubic_feet * quantity
                total_weight += sku.weight_lbs * quantity
            
            # Very tight deadlines: 1-3 hours
            deadline_hours = random.uniform(1, 3)
            deadline = datetime.now() + timedelta(hours=deadline_hours)
            
            order = {
                "id": i + 1,
                "customer": customer.name,
                "customer_type": customer.customer_type,
                "priority": "1",  # Highest priority
                "created_at": datetime.now(),
                "shipping_deadline": deadline,
                "items": order_items,
                "total_pick_time": total_pick_time,
                "total_pack_time": total_pack_time,
                "total_volume": total_volume,
                "total_weight": total_weight,
                "status": "pending"
            }
            orders.append(order)
        
        return orders
    
    def _generate_inefficient_orders(self, num_orders: int, customers: List[CustomerProfile], 
                                   skus: List[SKUProfile]) -> List[Dict]:
        """Generate orders that highlight inefficient resource allocation."""
        orders = []
        
        for i in range(num_orders):
            customer = random.choice(customers)
            
            order_items = []
            total_pick_time = 0
            total_pack_time = 0
            total_volume = 0
            total_weight = 0
            
            # Larger orders with mixed requirements
            num_items = random.randint(4, 8)
            for _ in range(num_items):
                sku = random.choice(skus)
                quantity = random.randint(1, 4)
                
                order_items.append({
                    "sku_id": sku.name,
                    "quantity": quantity,
                    "pick_time": sku.pick_time_minutes * quantity,
                    "pack_time": sku.pack_time_minutes * quantity,
                    "volume": sku.volume_cubic_feet * quantity,
                    "weight": sku.weight_lbs * quantity
                })
                
                total_pick_time += sku.pick_time_minutes * quantity
                total_pack_time += sku.pack_time_minutes * quantity
                total_volume += sku.volume_cubic_feet * quantity
                total_weight += sku.weight_lbs * quantity
            
            # Longer deadlines (allows for inefficient processing)
            deadline_hours = random.uniform(8, 16)
            deadline = datetime.now() + timedelta(hours=deadline_hours)
            
            order = {
                "id": i + 1,
                "customer": customer.name,
                "customer_type": customer.customer_type,
                "priority": random.choice(["4", "5"]),  # Lower priority
                "created_at": datetime.now(),
                "shipping_deadline": deadline,
                "items": order_items,
                "total_pick_time": total_pick_time,
                "total_pack_time": total_pack_time,
                "total_volume": total_volume,
                "total_weight": total_weight,
                "status": "pending"
            }
            orders.append(order)
        
        return orders
    
    def _generate_mixed_orders(self, num_orders: int, customers: List[CustomerProfile], 
                             skus: List[SKUProfile]) -> List[Dict]:
        """Generate a mix of order types."""
        orders = []
        
        # Distribute orders across scenarios
        bottleneck_count = int(num_orders * 0.4)  # 40% bottleneck
        deadline_count = int(num_orders * 0.3)    # 30% deadline pressure
        inefficient_count = num_orders - bottleneck_count - deadline_count  # 30% inefficient
        
        # Generate orders for each scenario
        bottleneck_orders = self._generate_bottleneck_orders(bottleneck_count, customers, skus)
        deadline_orders = self._generate_deadline_orders(deadline_count, customers, skus)
        inefficient_orders = self._generate_inefficient_orders(inefficient_count, customers, skus)
        
        # Combine and renumber
        all_orders = bottleneck_orders + deadline_orders + inefficient_orders
        for i, order in enumerate(all_orders):
            order["id"] = i + 1
            orders.append(order)
        
        return orders
    
    def generate_complete_dataset(self, scenario_type: str = "mixed", num_orders: int = 50) -> Dict:
        """Generate a complete dataset for the specified scenario."""
        print(f"🎯 Generating {scenario_type} scenario with {num_orders} orders...")
        
        # Generate all profiles
        workers = self.generate_worker_profiles(20)
        equipment = self.generate_equipment_profiles()
        skus = self.generate_sku_profiles()
        customers = self.generate_customer_profiles()
        orders = self.generate_orders(num_orders, customers, skus, scenario_type)
        
        # Create warehouse configuration
        warehouse_config = {
            "name": "MidWest Distribution Co",
            "total_sqft": 85000,
            "zones": 5,
            "shift_start_hour": 6,
            "shift_end_hour": 22,
            "max_orders_per_day": 2500,
            "deadline_penalty_per_hour": 100.0,
            "overtime_multiplier": 1.5
        }
        
        # Calculate scenario statistics
        stats = self._calculate_scenario_statistics(workers, equipment, orders, scenario_type)
        
        dataset = {
            "scenario_type": scenario_type,
            "generated_at": datetime.now().isoformat(),
            "warehouse_config": warehouse_config,
            "workers": [self._worker_to_dict(w) for w in workers],
            "equipment": [self._equipment_to_dict(e) for e in equipment],
            "skus": [self._sku_to_dict(s) for s in skus],
            "customers": [self._customer_to_dict(c) for c in customers],
            "orders": orders,
            "statistics": stats
        }
        
        return dataset
    
    def _calculate_scenario_statistics(self, workers: List[WorkerProfile], 
                                     equipment: List[EquipmentProfile], 
                                     orders: List[Dict], 
                                     scenario_type: str) -> Dict:
        """Calculate statistics that highlight optimization opportunities."""
        
        # Worker statistics
        total_workers = len(workers)
        multi_skilled_workers = len([w for w in workers if len(w.skills) >= 3])
        specialized_workers = len([w for w in workers if len(w.skills) == 1])
        
        # Equipment statistics
        packing_stations = [e for e in equipment if e.equipment_type == 'packing_station']
        dock_doors = [e for e in equipment if e.equipment_type == 'dock_door']
        
        # Order statistics
        total_pack_time = sum(order['total_pack_time'] for order in orders)
        total_pick_time = sum(order['total_pick_time'] for order in orders)
        high_priority_orders = len([o for o in orders if o['priority'] in ['1', '2']])
        tight_deadline_orders = len([o for o in orders 
                                   if (o['shipping_deadline'] - datetime.now()).total_seconds() / 3600 < 4])
        
        # Calculate bottlenecks
        packing_capacity_hours = len(packing_stations) * 16  # 16-hour shift
        packing_demand_hours = total_pack_time / 60  # Convert minutes to hours
        packing_bottleneck = packing_demand_hours / packing_capacity_hours if packing_capacity_hours > 0 else 0
        
        shipping_capacity_hours = len(dock_doors) * 16
        shipping_demand_hours = len(orders) * 0.1  # Assume 6 minutes per order for shipping
        shipping_bottleneck = shipping_demand_hours / shipping_capacity_hours if shipping_capacity_hours > 0 else 0
        
        stats = {
            "workers": {
                "total": total_workers,
                "multi_skilled": multi_skilled_workers,
                "specialized": specialized_workers,
                "skill_distribution": {
                    "picking": len([w for w in workers if "picking" in w.skills]),
                    "packing": len([w for w in workers if "packing" in w.skills]),
                    "shipping": len([w for w in workers if "shipping" in w.skills]),
                    "labeling": len([w for w in workers if "labeling" in w.skills]),
                    "consolidation": len([w for w in workers if "consolidation" in w.skills]),
                    "staging": len([w for w in workers if "staging" in w.skills])
                }
            },
            "equipment": {
                "total": len(equipment),
                "packing_stations": len(packing_stations),
                "dock_doors": len(dock_doors),
                "pick_carts": len([e for e in equipment if e.equipment_type == 'pick_cart']),
                "conveyors": len([e for e in equipment if e.equipment_type == 'conveyor']),
                "label_printers": len([e for e in equipment if e.equipment_type == 'label_printer'])
            },
            "orders": {
                "total": len(orders),
                "high_priority": high_priority_orders,
                "tight_deadlines": tight_deadline_orders,
                "total_pick_time_hours": total_pick_time / 60,
                "total_pack_time_hours": total_pack_time / 60,
                "avg_order_value": sum(o['total_volume'] * 10 for o in orders) / len(orders)  # Rough estimate
            },
            "bottlenecks": {
                "packing_bottleneck_ratio": packing_bottleneck,
                "shipping_bottleneck_ratio": shipping_bottleneck,
                "packing_capacity_hours": packing_capacity_hours,
                "packing_demand_hours": packing_demand_hours,
                "shipping_capacity_hours": shipping_capacity_hours,
                "shipping_demand_hours": shipping_demand_hours
            },
            "optimization_opportunities": {
                "equipment_bottleneck": packing_bottleneck > 1.2,
                "deadline_pressure": tight_deadline_orders > len(orders) * 0.3,
                "skill_mismatch": specialized_workers > multi_skilled_workers,
                "resource_underutilization": any(e.current_utilization < 0.5 for e in equipment)
            }
        }
        
        return stats
    
    def _worker_to_dict(self, worker: WorkerProfile) -> Dict:
        """Convert worker profile to dictionary."""
        return {
            "name": worker.name,
            "skills": list(worker.skills),
            "hourly_rate": worker.hourly_rate,
            "efficiency_factor": worker.efficiency_factor,
            "max_hours_per_day": worker.max_hours_per_day,
            "reliability_score": worker.reliability_score
        }
    
    def _equipment_to_dict(self, equipment: EquipmentProfile) -> Dict:
        """Convert equipment profile to dictionary."""
        return {
            "name": equipment.name,
            "equipment_type": equipment.equipment_type,
            "capacity": equipment.capacity,
            "hourly_cost": equipment.hourly_cost,
            "efficiency_factor": equipment.efficiency_factor,
            "maintenance_frequency": equipment.maintenance_frequency,
            "current_utilization": equipment.current_utilization
        }
    
    def _sku_to_dict(self, sku: SKUProfile) -> Dict:
        """Convert SKU profile to dictionary."""
        return {
            "name": sku.name,
            "category": sku.category,
            "zone": sku.zone,
            "pick_time_minutes": sku.pick_time_minutes,
            "pack_time_minutes": sku.pack_time_minutes,
            "volume_cubic_feet": sku.volume_cubic_feet,
            "weight_lbs": sku.weight_lbs,
            "demand_pattern": sku.demand_pattern,
            "shelf_life_days": sku.shelf_life_days if sku.shelf_life_days is not None else None
        }
    
    def _customer_to_dict(self, customer: CustomerProfile) -> Dict:
        """Convert customer profile to dictionary."""
        return {
            "name": customer.name,
            "customer_type": customer.customer_type,
            "order_frequency": customer.order_frequency,
            "avg_order_value": customer.avg_order_value,
            "priority_tendency": customer.priority_tendency,
            "deadline_preference": customer.deadline_preference
        }
    
    def save_dataset(self, dataset: Dict, filename: str = None):
        """Save the generated dataset to JSON file."""
        if filename is None:
            scenario = dataset['scenario_type']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"synthetic_data_{scenario}_{timestamp}.json"
        
        output_dir = Path("generated_data")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        # Custom JSON encoder to handle datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, cls=DateTimeEncoder)
        
        print(f"💾 Dataset saved to: {filepath}")
        return filepath
    
    def generate_all_scenarios(self, orders_per_scenario: int = 50):
        """Generate datasets for all scenario types."""
        scenarios = ["bottleneck", "deadline", "inefficient", "mixed"]
        
        for scenario in scenarios:
            print(f"\n🎯 Generating {scenario} scenario...")
            dataset = self.generate_complete_dataset(scenario, orders_per_scenario)
            self.save_dataset(dataset, f"synthetic_data_{scenario}.json")
            
            # Print key statistics
            stats = dataset['statistics']
            print(f"   📊 Orders: {stats['orders']['total']}")
            print(f"   👥 Workers: {stats['workers']['total']} ({stats['workers']['multi_skilled']} multi-skilled)")
            print(f"   🏭 Equipment: {stats['equipment']['total']} ({stats['equipment']['packing_stations']} packing stations)")
            print(f"   ⚠️  Packing bottleneck: {stats['bottlenecks']['packing_bottleneck_ratio']:.2f}")
            print(f"   ⏰ Tight deadlines: {stats['orders']['tight_deadlines']}")


def main():
    """Main function to generate synthetic datasets."""
    print("🚀 AI Wave Optimization Agent - Synthetic Data Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate all scenarios
    generator.generate_all_scenarios(orders_per_scenario=50)
    
    print("\n🎉 All synthetic datasets generated successfully!")
    print("\n📁 Check the 'generated_data' directory for JSON files")
    print("📊 Each file contains complete warehouse data for optimization scenarios")


if __name__ == "__main__":
    main() 