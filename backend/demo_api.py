#!/usr/bin/env python3
"""
Demo script for testing the AI Wave Optimization Agent API.

This script tests the API endpoints by:
1. Checking API health and database connection
2. Getting warehouse data from database
3. Running optimization with database data
4. Viewing optimization history
"""

import requests
import json
import time
from datetime import datetime


class APIDemo:
    """Demo class for testing API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize with API base URL."""
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self):
        """Test the health endpoint."""
        print("🔍 Testing API health...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ API Status: {data['status']}")
            print(f"   Database: {'✅ Connected' if data.get('database_ready') else '❌ Disconnected'}")
            print(f"   Optimizer: {'✅ Ready' if data.get('optimizer_ready') else '❌ Not Ready'}")
            print(f"   Data Generator: {'✅ Ready' if data.get('data_generator_ready') else '❌ Not Ready'}")
            
            return data.get('database_ready', False)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def get_warehouse_data(self, warehouse_id: int = 1):
        """Get warehouse data from database."""
        print(f"\n📊 Getting warehouse {warehouse_id} data...")
        try:
            response = self.session.get(f"{self.base_url}/data/warehouse/{warehouse_id}")
            response.raise_for_status()
            data = response.json()
            
            summary = data['summary']
            print(f"✅ Warehouse {warehouse_id} Data Retrieved:")
            print(f"   Workers: {summary['total_workers']}")
            print(f"   Equipment: {summary['total_equipment']}")
            print(f"   SKUs: {summary['total_skus']}")
            print(f"   Pending Orders: {summary['total_orders']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get warehouse data: {e}")
            return None
    
    def get_warehouse_stats(self, warehouse_id: int = 1):
        """Get warehouse statistics."""
        print(f"\n📈 Getting warehouse {warehouse_id} statistics...")
        try:
            response = self.session.get(f"{self.base_url}/data/stats/{warehouse_id}")
            response.raise_for_status()
            data = response.json()
            
            stats = data['statistics']
            print(f"✅ Warehouse {warehouse_id} Statistics:")
            print(f"   Total Workers: {stats['total_workers']}")
            print(f"   Total Equipment: {stats['total_equipment']}")
            print(f"   Total SKUs: {stats['total_skus']}")
            print(f"   Pending Orders: {stats['pending_orders']}")
            
            if stats.get('equipment_breakdown'):
                print("   Equipment Breakdown:")
                for eq in stats['equipment_breakdown']:
                    print(f"     {eq['equipment_type']}: {eq['count']}")
            
            if stats.get('order_priority_breakdown'):
                print("   Order Priority Breakdown:")
                for priority in stats['order_priority_breakdown']:
                    print(f"     Priority {priority['priority']}: {priority['count']} orders")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get warehouse stats: {e}")
            return None
    
    def run_optimization(self, warehouse_id: int = 1, order_limit: int = 20):
        """Run optimization with database data."""
        print(f"\n🚀 Running optimization for warehouse {warehouse_id}...")
        print(f"   Order limit: {order_limit}")
        
        try:
            # Use POST with query parameters
            params = {
                'warehouse_id': warehouse_id,
                'order_limit': order_limit
            }
            response = self.session.post(f"{self.base_url}/optimize/database", params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Optimization completed!")
            print(f"   Run ID: {data['run_id']}")
            print(f"   Solver Status: {data['solver_status']}")
            print(f"   Optimization Time: {data['optimization_time']:.2f} seconds")
            
            result = data['result']
            print(f"   Total Cost: ${result['total_cost']:,.2f}")
            print(f"   Orders Scheduled: {result['orders_scheduled']}")
            print(f"   Workers Used: {result['workers_used']}")
            print(f"   Equipment Used: {result['equipment_used']}")
            
            if result.get('efficiency_improvement'):
                print(f"   Efficiency Improvement: {result['efficiency_improvement']:.1f}%")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Optimization failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"   Error details: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Response: {e.response.text}")
            return None
    
    def get_optimization_history(self, limit: int = 5):
        """Get optimization history."""
        print(f"\n📋 Getting optimization history (last {limit} runs)...")
        try:
            response = self.session.get(f"{self.base_url}/history", params={'limit': limit})
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Found {data['total_runs']} optimization runs:")
            
            for run in data['history']:
                start_time = run['start_time']
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                
                print(f"   Run {run['id']}: {run['scenario_type']} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     Orders: {run['total_orders']}, Workers: {run['total_workers']}, Equipment: {run['total_equipment']}")
                print(f"     Status: {run['status']}")
                
                if run.get('objective_value'):
                    print(f"     Cost: ${run['objective_value']:,.2f}")
                if run.get('solve_time_seconds'):
                    print(f"     Time: {run['solve_time_seconds']:.2f}s")
                print()
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get optimization history: {e}")
            return None
    
    def run_full_demo(self):
        """Run the complete demo sequence."""
        print("🎯 AI Wave Optimization Agent - API Demo")
        print("=" * 50)
        
        # Test health
        if not self.test_health():
            print("\n❌ API is not healthy. Please start the server first.")
            return False
        
        # Get warehouse data
        warehouse_data = self.get_warehouse_data()
        if not warehouse_data:
            print("\n❌ Failed to get warehouse data. Check database connection.")
            return False
        
        # Get warehouse stats
        self.get_warehouse_stats()
        
        # Run optimization
        optimization_result = self.run_optimization(order_limit=15)
        if not optimization_result:
            print("\n❌ Optimization failed. Check logs for details.")
            return False
        
        # Get history
        self.get_optimization_history()
        
        print("\n🎉 Demo completed successfully!")
        return True


def main():
    """Main demo function."""
    demo = APIDemo()
    
    try:
        success = demo.run_full_demo()
        if success:
            print("\n✅ All API endpoints working correctly!")
            print("   The backend is ready for frontend integration.")
        else:
            print("\n❌ Demo failed. Please check the server and database.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main() 