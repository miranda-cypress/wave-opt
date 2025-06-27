#!/usr/bin/env python3
"""
Database setup script for AI Wave Optimization Agent.

This script helps set up the PostgreSQL database with:
1. Schema creation
2. Demo data population
3. Connection testing
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from pathlib import Path


def read_sql_file(file_path: str) -> str | None:
    """Read SQL file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ SQL file not found: {file_path}")
        return None


def create_database(host: str, port: int, user: str, password: str, database: str):
    """Create database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📦 Creating database: {database}")
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"✅ Database '{database}' created successfully")
        else:
            print(f"✅ Database '{database}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False
    
    return True


def execute_sql_file(host: str, port: int, user: str, password: str, database: str, file_path: str, description: str):
    """Execute SQL file against the database."""
    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Read and execute SQL file
        sql_content = read_sql_file(file_path)
        if sql_content is None:
            return False
        
        print(f"📝 Executing {description}...")
        cursor.execute(sql_content)
        conn.commit()
        
        print(f"✅ {description} executed successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to execute {description}: {e}")
        return False


def test_connection(host: str, port: int, user: str, password: str, database: str):
    """Test database connection and basic queries."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Test basic queries
        print("🔍 Testing database connection and data...")
        
        # Check warehouse
        cursor.execute("SELECT COUNT(*) FROM warehouses")
        result = cursor.fetchone()
        warehouse_count = result[0] if result else 0
        print(f"   - Warehouses: {warehouse_count}")
        
        # Check workers
        cursor.execute("SELECT COUNT(*) FROM workers")
        result = cursor.fetchone()
        worker_count = result[0] if result else 0
        print(f"   - Workers: {worker_count}")
        
        # Check equipment
        cursor.execute("SELECT COUNT(*) FROM equipment")
        result = cursor.fetchone()
        equipment_count = result[0] if result else 0
        print(f"   - Equipment: {equipment_count}")
        
        # Check SKUs
        cursor.execute("SELECT COUNT(*) FROM skus")
        result = cursor.fetchone()
        sku_count = result[0] if result else 0
        print(f"   - SKUs: {sku_count}")
        
        # Check orders
        cursor.execute("SELECT COUNT(*) FROM orders")
        result = cursor.fetchone()
        order_count = result[0] if result else 0
        print(f"   - Orders: {order_count}")
        
        # Check customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        result = cursor.fetchone()
        customer_count = result[0] if result else 0
        print(f"   - Customers: {customer_count}")
        
        cursor.close()
        conn.close()
        
        print("✅ Database connection and queries successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup PostgreSQL database for AI Wave Optimization Agent')
    parser.add_argument('--host', default='localhost', help='PostgreSQL host (default: localhost)')
    parser.add_argument('--port', type=int, default=5432, help='PostgreSQL port (default: 5432)')
    parser.add_argument('--user', default='postgres', help='PostgreSQL user (default: postgres)')
    parser.add_argument('--password', required=True, help='PostgreSQL password')
    parser.add_argument('--database', default='wave_opt', help='Database name (default: wave_opt)')
    parser.add_argument('--skip-schema', action='store_true', help='Skip schema creation')
    parser.add_argument('--skip-data', action='store_true', help='Skip demo data insertion')
    
    args = parser.parse_args()
    
    print("🚀 AI Wave Optimization Agent - Database Setup")
    print("=" * 50)
    print(f"Host: {args.host}:{args.port}")
    print(f"User: {args.user}")
    print(f"Database: {args.database}")
    print("-" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    schema_file = current_dir / "schema.sql"
    demo_data_file = current_dir / "demo_data.sql"
    
    # Create database
    if not create_database(args.host, args.port, args.user, args.password, args.database):
        sys.exit(1)
    
    # Execute schema
    if not args.skip_schema:
        if not execute_sql_file(args.host, args.port, args.user, args.password, args.database, 
                              str(schema_file), "database schema"):
            sys.exit(1)
    
    # Execute demo data
    if not args.skip_data:
        if not execute_sql_file(args.host, args.port, args.user, args.password, args.database, 
                              str(demo_data_file), "demo data"):
            sys.exit(1)
    
    # Test connection
    if not test_connection(args.host, args.port, args.user, args.password, args.database):
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your application's database connection settings")
    print("2. Run the backend API: cd backend && uvicorn api.main:app --reload")
    print("3. Access the API at: http://localhost:8000")
    print("4. View API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    main() 