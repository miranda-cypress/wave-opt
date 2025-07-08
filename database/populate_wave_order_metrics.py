import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from config_service import config_service

SQL_INSERT = '''
INSERT INTO wave_order_metrics (
    wave_id, order_id, plan_version_id,
    pick_time_minutes, pack_time_minutes, walking_time_minutes,
    consolidate_time_minutes, label_time_minutes, stage_time_minutes, ship_time_minutes
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (wave_id, order_id, plan_version_id) DO UPDATE
SET pick_time_minutes = EXCLUDED.pick_time_minutes,
    pack_time_minutes = EXCLUDED.pack_time_minutes,
    walking_time_minutes = EXCLUDED.walking_time_minutes,
    consolidate_time_minutes = EXCLUDED.consolidate_time_minutes,
    label_time_minutes = EXCLUDED.label_time_minutes,
    stage_time_minutes = EXCLUDED.stage_time_minutes,
    ship_time_minutes = EXCLUDED.ship_time_minutes,
    updated_at = NOW();
'''

def main():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="warehouse_opt",
        user="wave_user",
        password="wave_password"
    )
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get the original plan version id
        cur.execute("SELECT id FROM wave_plan_versions WHERE version_type = 'original' ORDER BY id LIMIT 1;")
        plan_version = cur.fetchone()
        if not plan_version:
            print("No original plan version found!")
            return
        plan_version_id = plan_version['id']

        # Get config values
        std = config_service.get_value('standard_times', {})
        label_minutes_per_order = std.get('label_minutes_per_order', 5)
        stage_minutes_per_order = std.get('stage_minutes_per_order', 10)
        ship_minutes_per_order = std.get('ship_minutes_per_order', 8)
        consolidate_minutes_per_item = std.get('consolidate_minutes_per_item', 0.5)
        pack_minutes_per_item = std.get('pack_minutes_per_item', 1.5)
        pick_minutes_per_item = std.get('pick_minutes_per_item', 2.0)

        # Get all wave assignments with their wave and order info
        cur.execute('''
            SELECT wa.wave_id, wa.order_id, w.version_id,
                   o.total_pick_time, o.total_pack_time
            FROM wave_assignments wa
            JOIN waves w ON wa.wave_id = w.id
            JOIN orders o ON wa.order_id = o.id
        ''')
        assignments = cur.fetchall()
        print(f"Found {len(assignments)} wave assignments.")

        for a in assignments:
            order_id = a['order_id']
            # Get order items and their SKU times
            cur.execute('''
                SELECT oi.quantity, s.pick_time_minutes, s.pack_time_minutes
                FROM order_items oi
                JOIN skus s ON oi.sku_id = s.id
                WHERE oi.order_id = %s
            ''', (order_id,))
            items = cur.fetchall()
            # Per-SKU pick/pack times if available, else config
            pick_time = sum((item['pick_time_minutes'] or pick_minutes_per_item) * item['quantity'] for item in items)
            pack_time = sum((item['pack_time_minutes'] or pack_minutes_per_item) * item['quantity'] for item in items)
            consolidate_time = sum(consolidate_minutes_per_item * item['quantity'] for item in items)
            # Per-order times from config
            label_time = label_minutes_per_order
            stage_time = stage_minutes_per_order
            ship_time = ship_minutes_per_order
            # Walking time and other times can be set to NULL or 0 for now
            walking_time = None
            cur.execute(SQL_INSERT, (
                a['wave_id'], a['order_id'], plan_version_id,
                pick_time, pack_time, walking_time,
                consolidate_time, label_time, stage_time, ship_time
            ))
        conn.commit()
        print("wave_order_metrics table populated for original plan version (with config standard times).")
    conn.close()

if __name__ == "__main__":
    main() 