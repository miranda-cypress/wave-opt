#!/usr/bin/env python3
"""
Test script to verify the wave optimizer fixes work correctly.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_wave_optimizer():
    """Test the wave optimizer with improved error handling."""
    try:
        from optimizer.wave_constraint_optimizer import WaveConstraintOptimizer
        
        print("Testing Wave Constraint Optimizer...")
        
        # Initialize optimizer
        optimizer = WaveConstraintOptimizer()
        print("✓ Optimizer initialized successfully")
        
        # Test with a known wave ID (wave 9 from the logs)
        wave_id = 9
        print(f"Testing optimization for wave {wave_id}...")
        
        # Run optimization
        result = optimizer.optimize_wave(wave_id, time_limit=60)  # 1 minute time limit for testing
        
        print(f"Optimization result: {result}")
        
        if result.get("error"):
            print(f"❌ Optimization failed: {result['error']}")
            return False
        else:
            print("✓ Optimization completed successfully")
            print(f"  - Status: {result.get('status', 'unknown')}")
            print(f"  - Solve time: {result.get('solve_time', 0):.2f}s")
            print(f"  - Objective value: {result.get('objective_value', 0)}")
            print(f"  - Number of orders: {result.get('num_orders', 0)}")
            print(f"  - Number of workers: {result.get('num_workers', 0)}")
            print(f"  - Number of equipment: {result.get('num_equipment', 0)}")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection with multiple configurations."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("\nTesting database connections...")
        
        connection_configs = [
            {
                "host": "localhost",
                "port": 5432,
                "database": "warehouse_opt",
                "user": "wave_user",
                "password": "wave_password"
            },
            {
                "host": "localhost", 
                "port": 5433,
                "database": "warehouse_opt",
                "user": "wave_user",
                "password": "wave_password"
            }
        ]
        
        for i, config in enumerate(connection_configs):
            try:
                print(f"  Testing connection {i+1}: {config['host']}:{config['port']}")
                conn = psycopg2.connect(**config)
                
                # Test a simple query
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT COUNT(*) as count FROM waves")
                    result = cursor.fetchone()
                    print(f"    ✓ Connected successfully. Found {result['count']} waves")
                
                conn.close()
                return True
                
            except Exception as e:
                print(f"    ❌ Connection failed: {e}")
                continue
        
        print("❌ All database connections failed")
        return False
        
    except ImportError as e:
        print(f"❌ psycopg2 not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("WAVE OPTIMIZER FIX TEST")
    print("=" * 60)
    
    # Test database connection first
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n⚠️  Database connection failed. Some tests may not work.")
        print("   Make sure PostgreSQL is running and accessible.")
    
    # Test wave optimizer
    optimizer_ok = test_wave_optimizer()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✓ PASS' if db_ok else '❌ FAIL'}")
    print(f"Wave Optimizer: {'✓ PASS' if optimizer_ok else '❌ FAIL'}")
    
    if optimizer_ok:
        print("\n🎉 All tests passed! The wave optimizer fixes are working.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return optimizer_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 