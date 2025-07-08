#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor

def update_order_times():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        # Update order items with pick and pack times from SKU data
        cursor.execute("""
            UPDATE order_items oi
            SET 
                pick_time = s.pick_time_minutes * oi.quantity,
                pack_time = s.pack_time_minutes * oi.quantity
            FROM skus s
            WHERE oi.sku_id = s.id
            AND (oi.pick_time = 0 OR oi.pick_time IS NULL OR oi.pack_time = 0 OR oi.pack_time IS NULL)
        """)
        
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} order items with pick and pack times")
        
        # Update order totals
        cursor.execute("""
            UPDATE orders 
            SET 
                total_pick_time = COALESCE(pick_totals.total_pick, 0),
                total_pack_time = COALESCE(pack_totals.total_pack, 0)
            FROM (
                SELECT 
                    order_id,
                    SUM(pick_time) as total_pick,
                    SUM(pack_time) as total_pack
                FROM order_items
                GROUP BY order_id
            ) pick_totals
            WHERE orders.id = pick_totals.order_id
        """)
        
        updated_orders = cursor.rowcount
        print(f"Updated {updated_orders} orders with total pick and pack times")
        
        # Check the specific order
        cursor.execute("""
            SELECT o.*, 
                   COUNT(oi.id) as item_count,
                   SUM(oi.pick_time) as total_pick,
                   SUM(oi.pack_time) as total_pack
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.order_number = %s
            GROUP BY o.id
        """, ('ORD00376899',))
        
        order_data = cursor.fetchone()
        if order_data:
            print(f"\nUpdated order data for ORD00376899:")
            print(f"  Item count: {order_data['item_count']}")
            print(f"  Total pick time: {order_data['total_pick']} min")
            print(f"  Total pack time: {order_data['total_pack']} min")
        
        conn.commit()
    
    conn.close()

if __name__ == "__main__":
    update_order_times() 