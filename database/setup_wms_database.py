#!/usr/bin/env python3
"""
Setup WMS Database Script

This script sets up the PostgreSQL database with the WMS wave optimization schema
that matches what the backend API expects.
"""

import psycopg2
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WMSDatabaseSetup:
    """Handles setup of the WMS database with proper schema."""
    
    def __init__(self, host: str = "localhost", port: int = 5433, 
                 database: str = "warehouse_opt", user: str = "wave_user", 
                 password: str = "wave_password"):
        """Initialize database connection parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"✅ Connected to PostgreSQL database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Database connection closed")
    
    def setup_database(self):
        """Set up the complete database schema and sample data."""
        if not self.connect():
            return False
        
        try:
            # Read and execute the schema file
            schema_file = Path("wms_wave_schema.sql")
            if not schema_file.exists():
                logger.error(f"❌ Schema file not found: {schema_file}")
                return False
            
            logger.info("📂 Reading schema file...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute the schema
            if self.conn:
                with self.conn.cursor() as cursor:
                    logger.info("🔨 Creating database schema...")
                    cursor.execute(schema_sql)
                    self.conn.commit()
                    logger.info("✅ Database schema created successfully")
                
                # Verify the setup
                self.verify_setup()
            
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"❌ Error setting up database: {e}")
            return False
        finally:
            self.disconnect()
    
    def verify_setup(self):
        """Verify that the database was set up correctly."""
        logger.info("🔍 Verifying database setup...")
        
        if not self.conn:
            logger.error("❌ No database connection available")
            return
        
        with self.conn.cursor() as cursor:
            # Check tables
            tables_to_check = [
                'warehouses', 'customers', 'skus', 'workers', 'worker_skills',
                'equipment', 'orders', 'order_items', 'waves', 'wave_assignments',
                'performance_metrics', 'optimization_runs', 'optimization_plans'
            ]
            
            for table in tables_to_check:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                result = cursor.fetchone()
                count = result[0] if result else 0
                logger.info(f"   {table}: {count} records")
            
            # Check specific data
            cursor.execute("SELECT COUNT(*) FROM workers WHERE warehouse_id = 1")
            result = cursor.fetchone()
            worker_count = result[0] if result else 0
            logger.info(f"   Workers in warehouse 1: {worker_count}")
            
            cursor.execute("SELECT COUNT(*) FROM orders WHERE warehouse_id = 1 AND status = 'pending'")
            result = cursor.fetchone()
            order_count = result[0] if result else 0
            logger.info(f"   Pending orders in warehouse 1: {order_count}")
            
            cursor.execute("SELECT COUNT(*) FROM waves WHERE warehouse_id = 1")
            result = cursor.fetchone()
            wave_count = result[0] if result else 0
            logger.info(f"   Waves in warehouse 1: {wave_count}")
        
        logger.info("✅ Database verification completed")
    
    def reset_database(self):
        """Reset the database by dropping and recreating all tables."""
        if not self.connect():
            return False
        
        try:
            logger.info("🔄 Resetting database...")
            
            # Read the schema file to get the DROP statements
            schema_file = Path("wms_wave_schema.sql")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Extract and execute only the DROP statements
            drop_statements = []
            for line in schema_sql.split('\n'):
                if line.strip().startswith('DROP TABLE IF EXISTS'):
                    drop_statements.append(line.strip())
            
            if self.conn:
                with self.conn.cursor() as cursor:
                    for drop_stmt in drop_statements:
                        cursor.execute(drop_stmt)
                        logger.info(f"   {drop_stmt}")
                    
                    self.conn.commit()
                    logger.info("✅ Database reset completed")
            
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"❌ Error resetting database: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main function to run the database setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup WMS Database')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5433, help='Database port')
    parser.add_argument('--database', default='warehouse_opt', help='Database name')
    parser.add_argument('--user', default='wave_user', help='Database user')
    parser.add_argument('--password', default='wave_password', help='Database password')
    parser.add_argument('--reset', action='store_true', help='Reset database before setup')
    
    args = parser.parse_args()
    
    setup = WMSDatabaseSetup(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    
    if args.reset:
        logger.info("🔄 Resetting database...")
        if not setup.reset_database():
            sys.exit(1)
    
    logger.info("🚀 Setting up WMS database...")
    if setup.setup_database():
        logger.info("✅ Database setup completed successfully!")
        logger.info("🎉 You can now run the backend server and test wave optimization!")
    else:
        logger.error("❌ Database setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 