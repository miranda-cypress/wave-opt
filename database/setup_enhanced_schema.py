#!/usr/bin/env python3
"""
Setup script for enhanced WMS schema with simulated data.

This script:
1. Applies the enhanced WMS schema
2. Generates realistic simulated data
3. Sets up data import tracking
4. Creates wave plan versions

The generated data is structured to easily accept real WMS data later.
"""

import psycopg2
import os
import sys
import logging
from pathlib import Path

# Add the database directory to the path
sys.path.append(str(Path(__file__).parent))

from simulated_wms_data_generator import SimulatedWMSDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_schema():
    """Apply the enhanced WMS schema."""
    try:
        # Read the schema file
        schema_file = Path(__file__).parent / "enhanced_wms_schema.sql"
        
        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor() as cursor:
            # Execute the schema
            cursor.execute(schema_sql)
            conn.commit()
        
        conn.close()
        logger.info("Enhanced WMS schema applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error applying schema: {e}")
        return False


def generate_simulated_data():
    """Generate simulated WMS data."""
    try:
        generator = SimulatedWMSDataGenerator()
        generator.generate_all_data(num_orders=100)
        logger.info("Simulated data generated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error generating simulated data: {e}")
        return False


def verify_setup():
    """Verify that the setup was successful."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse_opt",
            user="wave_user",
            password="wave_password"
        )
        
        with conn.cursor() as cursor:
            # Check key tables
            tables_to_check = [
                'warehouses', 'customers', 'skus', 'workers', 'equipment',
                'orders', 'waves', 'data_sources', 'wave_plan_versions'
            ]
            
            for table in tables_to_check:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                result = cursor.fetchone()
                count = result[0] if result else 0
                logger.info(f"Table {table}: {count} records")
        
        conn.close()
        logger.info("Setup verification completed")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying setup: {e}")
        return False


def main():
    """Main setup function."""
    print("="*60)
    print("ENHANCED WMS SCHEMA SETUP")
    print("="*60)
    
    # Step 1: Apply schema
    print("\nStep 1: Applying enhanced WMS schema...")
    if not apply_schema():
        print("❌ Schema application failed")
        return False
    print("✅ Schema applied successfully")
    
    # Step 2: Generate simulated data
    print("\nStep 2: Generating simulated WMS data...")
    if not generate_simulated_data():
        print("❌ Data generation failed")
        return False
    print("✅ Simulated data generated successfully")
    
    # Step 3: Verify setup
    print("\nStep 3: Verifying setup...")
    if not verify_setup():
        print("❌ Setup verification failed")
        return False
    print("✅ Setup verification completed")
    
    print("\n" + "="*60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nThe enhanced WMS schema is now ready with:")
    print("✅ Realistic simulated data")
    print("✅ Data import tracking")
    print("✅ Wave plan versioning")
    print("✅ External system integration fields")
    print("✅ Audit trails")
    print("\nThis structure supports:")
    print("- Real WMS/OMS data import")
    print("- Data augmentation tracking")
    print("- Wave plan optimization and versioning")
    print("- Complete audit trails")
    print("\nNext steps:")
    print("1. Test the backend API endpoints")
    print("2. Run wave optimization")
    print("3. Replace simulated data with real WMS data when ready")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 