#!/usr/bin/env python3
"""
Refresh Materialized Views

This script refreshes the materialized views used by the frontend
after updating the baseline plan, so the changes are visible in the UI.
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def refresh_materialized_views():
    """Refresh all materialized views used by the frontend."""
    print("🔄 Refreshing Materialized Views...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='warehouse_opt',
            user='wave_user',
            password='wave_password'
        )
        
        with conn.cursor() as cursor:
            # Refresh the main materialized view used for baseline plans
            print("  📊 Refreshing original_wms_plans...")
            cursor.execute("REFRESH MATERIALIZED VIEW original_wms_plans;")
            
            # Check if there are any other materialized views that need refreshing
            cursor.execute("""
                SELECT matviewname 
                FROM pg_matviews 
                WHERE schemaname = 'public'
                ORDER BY matviewname;
            """)
            
            materialized_views = cursor.fetchall()
            print(f"  📋 Found {len(materialized_views)} materialized views:")
            
            for view in materialized_views:
                view_name = view[0]
                print(f"    - {view_name}")
                
                # Refresh each materialized view
                cursor.execute(f"REFRESH MATERIALIZED VIEW {view_name};")
                print(f"    ✅ Refreshed {view_name}")
            
            conn.commit()
            print("✅ All materialized views refreshed successfully!")
            
            # Verify the refresh worked by checking row counts
            cursor.execute("SELECT COUNT(*) FROM original_wms_plans;")
            result = cursor.fetchone()
            row_count = result[0] if result else 0
            print(f"📊 original_wms_plans now contains {row_count} rows")
            
    except Exception as e:
        print(f"❌ Error refreshing materialized views: {e}")
        logger.error(f"Error refreshing materialized views: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """Main function to refresh materialized views."""
    print("Materialized View Refresh Tool")
    print("=" * 40)
    print("This will refresh all materialized views to reflect")
    print("the latest baseline plan changes.")
    print()
    
    try:
        refresh_materialized_views()
        print("\n🎉 Materialized views refreshed successfully!")
        print("   Your frontend should now show the updated baseline plan.")
        
    except Exception as e:
        print(f"\n❌ Failed to refresh materialized views: {e}")
        print("   Please check the database connection and try again.")


if __name__ == "__main__":
    main() 