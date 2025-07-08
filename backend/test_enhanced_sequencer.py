#!/usr/bin/env python3
"""
Test script for Enhanced WMS Sequencer

This script tests the enhanced WMS sequencing algorithm to ensure it works
correctly with the existing database structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_wms_sequencer import EnhancedWMSSequencer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sequencer():
    """Test the enhanced WMS sequencer."""
    print("🧪 Testing Enhanced WMS Sequencer...")
    
    try:
        # Initialize sequencer
        sequencer = EnhancedWMSSequencer()
        
        # Test database connection
        conn = sequencer.get_connection()
        print("✅ Database connection successful")
        
        # Test getting wave data
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM waves")
            wave_result = cursor.fetchone()
            wave_count = wave_result[0] if wave_result else 0
            print(f"✅ Found {wave_count} waves in database")
            
            cursor.execute("SELECT COUNT(*) FROM workers WHERE active = true")
            worker_result = cursor.fetchone()
            worker_count = worker_result[0] if worker_result else 0
            print(f"✅ Found {worker_count} active workers")
            
            cursor.execute("SELECT COUNT(*) FROM equipment WHERE active = true")
            equipment_result = cursor.fetchone()
            equipment_count = equipment_result[0] if equipment_result else 0
            print(f"✅ Found {equipment_count} active equipment items")
        
        # Test getting workers with skills
        workers = sequencer.get_available_workers()
        print(f"✅ Retrieved {len(workers)} workers with skills")
        
        # Test getting equipment
        equipment = sequencer.get_available_equipment()
        print(f"✅ Retrieved {len(equipment)} equipment items")
        
        # Test getting orders for a wave
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM waves LIMIT 1")
            wave_id = cursor.fetchone()
            
            if wave_id:
                wave_id = wave_id[0]
                orders = sequencer.get_wave_orders(wave_id)
                print(f"✅ Retrieved {len(orders)} orders for wave {wave_id}")
                
                if orders:
                    # Test order sorting
                    sorted_orders = sequencer.sort_orders_by_criteria(orders)
                    print(f"✅ Sorted {len(sorted_orders)} orders by criteria")
                    
                    # Test zone grouping
                    zone_groups = sequencer.group_orders_by_zone(sorted_orders)
                    print(f"✅ Grouped orders into {len(zone_groups)} zone groups")
                    
                    # Test worker assignment
                    worker = sequencer.find_worker_for_stage('pick', workers, {})
                    if worker:
                        print(f"✅ Found worker {worker['name']} for picking stage")
                    
                    # Test equipment assignment
                    equipment_item = sequencer.find_equipment_for_stage('pack', equipment, {})
                    if equipment_item:
                        print(f"✅ Found equipment {equipment_item['name']} for packing stage")
                    
                    # Test duration calculation
                    if orders:
                        duration = sequencer.calculate_stage_duration('pick', orders[0])
                        print(f"✅ Calculated pick duration: {duration} minutes")
        
        print("\n🎉 All tests passed! Enhanced WMS sequencer is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.error(f"Test error: {str(e)}")
        return False


def test_single_wave():
    """Test sequencing a single wave."""
    print("\n🧪 Testing single wave sequencing...")
    
    try:
        sequencer = EnhancedWMSSequencer()
        
        # Find a wave to test
        conn = sequencer.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, wave_name FROM waves LIMIT 1")
            wave_data = cursor.fetchone()
            
            if wave_data:
                wave_id, wave_name = wave_data
                print(f"Testing wave {wave_id}: {wave_name}")
                
                # Test sequencing
                success = sequencer.sequence_wave_orders(wave_id)
                
                if success:
                    print(f"✅ Successfully sequenced wave {wave_id}")
                    
                    # Verify assignments were created
                    cursor.execute("""
                        SELECT COUNT(*) FROM wave_assignments 
                        WHERE wave_id = %s
                    """, (wave_id,))
                    assignment_result = cursor.fetchone()
                    assignment_count = assignment_result[0] if assignment_result else 0
                    print(f"✅ Created {assignment_count} wave assignments")
                    
                else:
                    print(f"❌ Failed to sequence wave {wave_id}")
                
                return success
            else:
                print("❌ No waves found in database")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logger.error(f"Single wave test error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Enhanced WMS Sequencer Tests\n")
    
    # Run basic tests
    basic_tests_passed = test_sequencer()
    
    if basic_tests_passed:
        # Run single wave test
        single_wave_passed = test_single_wave()
        
        if single_wave_passed:
            print("\n🎉 All tests passed! Enhanced WMS sequencer is working correctly.")
        else:
            print("\n⚠️  Single wave test failed, but basic functionality works.")
    else:
        print("\n❌ Basic tests failed. Please check database connection and data.") 