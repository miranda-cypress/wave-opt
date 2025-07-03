#!/usr/bin/env python3
"""
Test script to check database connection and waves data.
This will help diagnose the transaction error in the waves endpoint.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def test_connection():
    """Test basic database connection."""
    print("🔌 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        print("✅ Database connection successful")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_waves_table(conn):
    """Test waves table access."""
    print("\n📊 Testing waves table...")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if waves table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'waves'
                );
            """)
            table_exists_result = cursor.fetchone()
            
            if table_exists_result:
                if isinstance(table_exists_result, dict):
                    table_exists = table_exists_result['exists']
                else:
                    table_exists = table_exists_result[0]
            else:
                table_exists = False
            
            print(f"Waves table exists: {table_exists}")
            
            if not table_exists:
                print("❌ Waves table does not exist!")
                return False
            
            # Count waves
            cursor.execute("SELECT COUNT(*) as total FROM waves")
            total_waves = cursor.fetchone()['total']
            print(f"Total waves in database: {total_waves}")
            
            # Get sample waves
            cursor.execute("""
                SELECT id, wave_name, wave_type, total_orders, status, warehouse_id
                FROM waves 
                ORDER BY id 
                LIMIT 5
            """)
            
            waves = cursor.fetchall()
            print(f"\nSample waves:")
            for wave in waves:
                print(f"  ID: {wave['id']}, Name: {wave['wave_name']}, Orders: {wave['total_orders']}, Status: {wave['status']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing waves table: {e}")
        return False

def test_performance_metrics_table(conn):
    """Test performance_metrics table access."""
    print("\n📈 Testing performance_metrics table...")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if performance_metrics table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'performance_metrics'
                );
            """)
            table_exists_result = cursor.fetchone()
            
            if table_exists_result:
                if isinstance(table_exists_result, dict):
                    table_exists = table_exists_result['exists']
                else:
                    table_exists = table_exists_result[0]
            else:
                table_exists = False
            
            print(f"Performance_metrics table exists: {table_exists}")
            
            if table_exists:
                # Count metrics
                cursor.execute("SELECT COUNT(*) as total FROM performance_metrics")
                total_metrics = cursor.fetchone()['total']
                print(f"Total performance metrics: {total_metrics}")
            else:
                print("⚠️  Performance_metrics table does not exist - this is expected for new data")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing performance_metrics table: {e}")
        return False

def test_wave_assignments_table(conn):
    """Test wave_assignments table access."""
    print("\n📋 Testing wave_assignments table...")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if wave_assignments table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'wave_assignments'
                );
            """)
            table_exists_result = cursor.fetchone()
            
            if table_exists_result:
                if isinstance(table_exists_result, dict):
                    table_exists = table_exists_result['exists']
                else:
                    table_exists = table_exists_result[0]
            else:
                table_exists = False
            
            print(f"Wave_assignments table exists: {table_exists}")
            
            if table_exists:
                # Count assignments
                cursor.execute("SELECT COUNT(*) as total FROM wave_assignments")
                total_assignments = cursor.fetchone()['total']
                print(f"Total wave assignments: {total_assignments}")
                
                # Get sample assignments
                cursor.execute("""
                    SELECT wave_id, COUNT(*) as assignment_count
                    FROM wave_assignments 
                    GROUP BY wave_id 
                    ORDER BY wave_id 
                    LIMIT 3
                """)
                
                assignments = cursor.fetchall()
                print(f"\nSample wave assignments:")
                for assignment in assignments:
                    print(f"  Wave {assignment['wave_id']}: {assignment['assignment_count']} assignments")
            else:
                print("⚠️  Wave_assignments table does not exist!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing wave_assignments table: {e}")
        return False

def main():
    """Main test function."""
    print("="*60)
    print("DATABASE CONNECTION AND WAVES TEST")
    print("="*60)
    
    # Test connection
    conn = test_connection()
    if not conn:
        sys.exit(1)
    
    try:
        # Test waves table
        waves_ok = test_waves_table(conn)
        
        # Test performance_metrics table
        metrics_ok = test_performance_metrics_table(conn)
        
        # Test wave_assignments table
        assignments_ok = test_wave_assignments_table(conn)
        
        print("\n" + "="*60)
        if waves_ok:
            print("✅ WAVES TABLE TEST PASSED")
        else:
            print("❌ WAVES TABLE TEST FAILED")
        
        if metrics_ok:
            print("✅ PERFORMANCE_METRICS TABLE TEST PASSED")
        else:
            print("❌ PERFORMANCE_METRICS TABLE TEST FAILED")
        
        if assignments_ok:
            print("✅ WAVE_ASSIGNMENTS TABLE TEST PASSED")
        else:
            print("❌ WAVE_ASSIGNMENTS TABLE TEST FAILED")
        
        print("="*60)
        
    finally:
        conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    main() 