#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_wave_assignments():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check wave_assignments for order 8
        cursor.execute("""
            SELECT order_id, stage, planned_start_time, planned_duration_minutes
            FROM wave_assignments 
            WHERE order_id = 8 
            ORDER BY stage
        """)
        
        results = cursor.fetchall()
        print("Wave Assignments for Order 8:")
        print("=" * 50)
        for row in results:
            print(f"  {row['stage']}: {row['planned_start_time']} ({row['planned_duration_minutes']} min)")
        
        # Check if we have all stages
        cursor.execute("""
            SELECT DISTINCT stage FROM wave_assignments WHERE order_id = 8
        """)
        stages = [r['stage'] for r in cursor.fetchall()]
        print(f"\nStages found: {stages}")
        
    conn.close()

if __name__ == "__main__":
    check_wave_assignments() 