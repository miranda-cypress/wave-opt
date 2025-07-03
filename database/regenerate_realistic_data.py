#!/usr/bin/env python3
"""
Regenerate database with realistic order volumes for warehouse optimization demo.
This script creates data that matches a real warehouse with ~2500 orders per day.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulated_wms_data_generator import SimulatedWMSDataGenerator
import psycopg2
from psycopg2.extras import RealDictCursor

def clean_database():
    """Clean existing data to start fresh."""
    print("🧹 Cleaning existing data...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor() as cursor:
            # Drop and recreate tables in correct order
            tables_to_drop = [
                'performance_metrics',
                'wave_assignments', 
                'waves',
                'order_items',
                'orders',
                'equipment',
                'worker_skills',
                'workers',
                'skus',
                'customers',
                'optimization_plans',
                'optimization_runs',
                'data_augmentations',
                'data_imports',
                'wave_plan_versions',
                'data_sources',
                'warehouses'
            ]
            
            for table in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"  Dropped {table}")
                except Exception as e:
                    print(f"  Warning: Could not drop {table}: {e}")
            
            conn.commit()
            print("✅ Database cleaned successfully")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def create_schema():
    """Create the database schema."""
    print("🏗️  Creating database schema...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        # Read and execute the schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'enhanced_wms_schema.sql')
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            conn.commit()
            
        print("✅ Database schema created successfully")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        raise
    finally:
        if conn:
            conn.close()

def regenerate_data():
    """Regenerate all data with realistic volumes."""
    print("\n🚀 Regenerating data with realistic warehouse volumes...")
    
    try:
        # Create generator with realistic order count
        generator = SimulatedWMSDataGenerator()
        
        # Generate 2500 orders to match realistic daily warehouse throughput
        # This gives us ~625 orders per wave (4 waves per day)
        generator.generate_all_data(num_orders=2500)
        
        print("✅ Data regeneration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error regenerating data: {e}")
        raise

def verify_data():
    """Verify the generated data has realistic volumes."""
    print("\n🔍 Verifying generated data...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check total orders
            cursor.execute("SELECT COUNT(*) as total FROM orders")
            total_orders = cursor.fetchone()['total']
            print(f"📦 Total orders: {total_orders:,}")
            
            # Check waves
            cursor.execute("SELECT COUNT(*) as total FROM waves")
            total_waves = cursor.fetchone()['total']
            print(f"🌊 Total waves: {total_waves}")
            
            # Check wave assignments
            cursor.execute("SELECT COUNT(*) as total FROM wave_assignments")
            total_assignments = cursor.fetchone()['total']
            print(f"📋 Total wave assignments: {total_assignments:,}")
            
            # Check orders per wave
            cursor.execute("""
                SELECT w.wave_name, w.total_orders, COUNT(wa.id) as actual_assignments
                FROM waves w
                LEFT JOIN wave_assignments wa ON w.id = wa.wave_id
                GROUP BY w.id, w.wave_name, w.total_orders
                ORDER BY w.id
            """)
            
            waves = cursor.fetchall()
            print(f"\n📊 Wave breakdown:")
            for wave in waves:
                print(f"  {wave['wave_name']}: {wave['total_orders']} planned, {wave['actual_assignments']} actual assignments")
            
            # Calculate average orders per wave
            if waves:
                avg_orders = sum(w['total_orders'] for w in waves) / len(waves)
                print(f"\n📈 Average orders per wave: {avg_orders:.0f}")
                
                # Check if this matches realistic warehouse throughput
                orders_per_day = total_orders
                print(f"📅 Daily order volume: {orders_per_day:,}")
                print(f"🎯 Target (2500/day): 2,500")
                
                if orders_per_day >= 2000:
                    print("✅ Realistic warehouse volume achieved!")
                else:
                    print("⚠️  Order volume is lower than expected for a real warehouse")
            
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        raise
    finally:
        if conn:
            conn.close()

def main():
    """Main function to regenerate realistic warehouse data."""
    print("="*60)
    print("WAREHOUSE DATA REGENERATION")
    print("="*60)
    print("This will create realistic data for a warehouse with ~2500 orders/day")
    print("="*60)
    
    try:
        # Step 1: Clean existing data
        clean_database()
        
        # Step 2: Create schema
        create_schema()
        
        # Step 3: Regenerate data
        regenerate_data()
        
        # Step 4: Verify results
        verify_data()
        
        print("\n" + "="*60)
        print("✅ REGENERATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("Your warehouse now has realistic data volumes:")
        print("- ~2500 orders per day")
        print("- ~625 orders per wave (4 waves per day)")
        print("- Proper wave assignments and scheduling")
        print("\nYou can now test the optimization with realistic workloads!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ REGENERATION FAILED: {e}")
        print("Please check your database connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 