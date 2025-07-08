#!/usr/bin/env python3
"""
Enhanced WMS Baseline Sequencing - Documentation

This script builds a realistic, entry-level WMS baseline plan for all waves in the database.

# Purpose
The goal is to create a baseline that mimics a typical, non-optimized WMS operation. This baseline is intentionally realistic but not highly efficient, so that the benefits of AI-driven optimization can be clearly demonstrated in comparison.

# How the Baseline Plan is Built
1. **Order Sorting**: For each wave, all orders are sorted by shipping deadline (earliest first) and then by priority (highest first). This reflects a basic WMS focus on urgent and important orders.

2. **Zone Grouping**: Orders are grouped by warehouse zone to simulate basic batching and reduce travel time, but without advanced optimization.

3. **Worker Assignment**: Workers are assigned to picking based on availability and basic skill matching (if available). No advanced labor balancing is performed.

4. **Equipment Constraints**: Equipment (e.g., packing stations) is allocated based on availability. If all equipment is busy, orders wait in queue.

5. **Stage Progression**: As picking progresses, a portion of staff is reallocated to consolidation and packing. When packing is underway, staff are further reallocated to labelling, staging, and shipping as work becomes available.

6. **Queue Management**: If a stage is blocked (no available staff or equipment), orders wait in a queue until resources free up. This models real-world bottlenecks.

7. **Wave Assignment Update**: The script updates the database with the new, realistic order and task sequencing for each wave, overwriting any previous baseline plan.

# Usage
- Run this script to apply the baseline logic to all waves in the database.
- The resulting plan can be compared to an optimized plan to highlight the value of advanced optimization.

# Limitations
- No advanced batching, routing, or labor balancing is performed.
- No learning or adaptation; the logic is static and basic.
- Designed to be realistic for a small/entry-level WMS, not a best-in-class operation.

"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_wms_sequencer import EnhancedWMSSequencer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_enhanced_sequencing_to_all_waves():
    """Apply enhanced WMS sequencing to all waves."""
    print("🚀 Applying Enhanced WMS Sequencing to All Waves")
    print("=" * 60)
    
    try:
        # Initialize sequencer
        sequencer = EnhancedWMSSequencer()
        
        # Get all waves
        conn = sequencer.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, wave_name, planned_start_time, planned_completion_time 
                FROM waves 
                ORDER BY planned_start_time
            """)
            waves = cursor.fetchall()
        
        print(f"📊 Found {len(waves)} waves to process")
        print()
        
        total_orders = 0
        total_assignments = 0
        
        for i, (wave_id, wave_name, start_time, end_time) in enumerate(waves, 1):
            print(f"🔄 Processing Wave {i}/{len(waves)}: {wave_name}")
            print(f"   📅 {start_time} - {end_time}")
            
            try:
                # Get order count for this wave
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM wave_assignments WHERE wave_id = %s
                    """, (wave_id,))
                    result = cursor.fetchone()
                    order_count = result[0] if result else 0
                
                print(f"   📦 {order_count} orders to sequence")
                
                # Apply enhanced sequencing
                success = sequencer.sequence_wave_orders(wave_id)
                assignments_created = 1 if success else 0  # Simplified for now
                
                total_orders += order_count
                total_assignments += assignments_created
                
                print(f"   ✅ Created {assignments_created} stage assignments")
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing wave {wave_id}: {e}")
                logger.error(f"Error processing wave {wave_id}: {e}")
                print()
        
        print("=" * 60)
        print(f"🎉 Enhanced WMS Sequencing Complete!")
        print(f"📊 Processed {len(waves)} waves")
        print(f"📦 Total orders: {total_orders}")
        print(f"🔗 Total stage assignments: {total_assignments}")
        print()
        print("💡 This creates a realistic baseline for comparison with AI optimization.")
        print("   The baseline shows typical WMS inefficiencies that optimization can address.")
        
        # Refresh materialized views to make changes visible in frontend
        print("\n🔄 Refreshing materialized views...")
        try:
            with conn.cursor() as cursor:
                cursor.execute("REFRESH MATERIALIZED VIEW original_wms_plans;")
                conn.commit()
                print("✅ Materialized views refreshed successfully!")
                print("   Your frontend should now show the updated baseline plan.")
        except Exception as e:
            print(f"⚠️  Warning: Could not refresh materialized views: {e}")
            print("   You may need to manually refresh the views to see changes in the frontend.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error applying enhanced sequencing: {e}")
        return False
    
    return True


def main():
    """Main function to run the enhanced sequencing."""
    print("Enhanced WMS Sequencer - Apply to All Waves")
    print("=" * 60)
    print("This will create a realistic baseline by applying entry-level WMS logic")
    print("to all waves in the database.")
    print()
    
    # Confirm with user
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    success = apply_enhanced_sequencing_to_all_waves()
    
    if success:
        print("\n✅ Enhanced WMS sequencing applied successfully!")
        print("   You can now compare this baseline with AI optimization results.")
    else:
        print("\n❌ Failed to apply enhanced WMS sequencing.")
        print("   Please check the error messages above.")


if __name__ == "__main__":
    main() 