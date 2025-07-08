#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_sku_times():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT sku_code, name, pick_time_minutes, pack_time_minutes 
            FROM skus 
            ORDER BY sku_code
        """)
        
        skus = cursor.fetchall()
        print("Current SKU Pick and Pack Times:")
        print("=" * 60)
        
        for sku in skus:
            print(f"{sku['sku_code']}: Pick={sku['pick_time_minutes']} min, Pack={sku['pack_time_minutes']} min")
        
        # Check for zero values
        zero_pick = [s for s in skus if s['pick_time_minutes'] == 0]
        zero_pack = [s for s in skus if s['pack_time_minutes'] == 0]
        
        print(f"\nSKUs with zero pick time: {len(zero_pick)}")
        print(f"SKUs with zero pack time: {len(zero_pack)}")
        
        if zero_pick:
            print("SKUs with zero pick time:")
            for sku in zero_pick:
                print(f"  {sku['sku_code']}: {sku['name']}")
        
        if zero_pack:
            print("SKUs with zero pack time:")
            for sku in zero_pack:
                print(f"  {sku['sku_code']}: {sku['name']}")
    
    conn.close()

if __name__ == "__main__":
    check_sku_times() 