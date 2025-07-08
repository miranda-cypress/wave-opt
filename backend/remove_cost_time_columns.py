from database_service import DatabaseService

def remove_cost_time_columns():
    """Remove travel_time_minutes and labor_cost columns from the waves table."""
    try:
        db = DatabaseService()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("Removing travel_time_minutes and labor_cost columns from waves table...")
        
        # Check if columns exist before removing them
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'waves' 
            AND column_name IN ('travel_time_minutes', 'labor_cost')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Found existing columns: {existing_columns}")
        
        # Remove travel_time_minutes column if it exists
        if 'travel_time_minutes' in existing_columns:
            cursor.execute("ALTER TABLE waves DROP COLUMN travel_time_minutes")
            print("✓ Removed travel_time_minutes column")
        else:
            print("travel_time_minutes column does not exist")
        
        # Remove labor_cost column if it exists
        if 'labor_cost' in existing_columns:
            cursor.execute("ALTER TABLE waves DROP COLUMN labor_cost")
            print("✓ Removed labor_cost column")
        else:
            print("labor_cost column does not exist")
        
        conn.commit()
        print("Successfully removed columns from waves table")
        
        # Verify the table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'waves'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("\nUpdated waves table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error removing columns: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    remove_cost_time_columns() 