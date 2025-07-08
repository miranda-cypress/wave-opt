#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def check_order_items():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Check if the order has any items
        cursor.execute("""
            SELECT oi.*, s.sku_code, s.name as sku_name, s.pick_time_minutes, s.pack_time_minutes
            FROM order_items oi
            JOIN skus s ON oi.sku_id = s.id
            WHERE oi.order_id = (SELECT id FROM orders WHERE order_number = %s)
        """, ('ORD00376899',))
        
        items = cursor.fetchall()
        
        if not items:
            print("Order ORD00376899 has no items!")
            
            # Check if the order exists
            cursor.execute("""
                SELECT * FROM orders WHERE order_number = %s
            """, ('ORD00376899',))
            
            order = cursor.fetchone()
            if order:
                print(f"Order exists but has no items. Order details: {order}")
            else:
                print("Order ORD00376899 not found!")
        else:
            print(f"Order ORD00376899 has {len(items)} items:")
            print("=" * 80)
            
            total_pick = 0
            total_pack = 0
            
            for item in items:
                pick_time = item['pick_time'] or 0
                pack_time = item['pack_time'] or 0
                total_pick += pick_time
                total_pack += pack_time
                
                print(f"SKU: {item['sku_code']} | Name: {item['sku_name']} | Qty: {item['quantity']}")
                print(f"  Pick time: {pick_time} min | Pack time: {pack_time} min")
                print()
            
            print(f"Total pick time: {total_pick} min")
            print(f"Total pack time: {total_pack} min")
        
        # Check walking time calculation
        cursor.execute("""
            SELECT calculate_order_walking_time((SELECT id FROM orders WHERE order_number = %s)) as walking_time
        """, ('ORD00376899',))
        
        walking_result = cursor.fetchone()
        if walking_result:
            print(f"Walking time for order: {walking_result['walking_time']} minutes")
        
        # Check item count
        cursor.execute("""
            SELECT get_order_item_count((SELECT id FROM orders WHERE order_number = %s)) as item_count
        """, ('ORD00376899',))
        
        count_result = cursor.fetchone()
        if count_result:
            print(f"Item count for order: {count_result['item_count']}")
    
    conn.close()

if __name__ == "__main__":
    check_order_items() 