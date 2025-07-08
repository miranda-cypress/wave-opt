#!/usr/bin/env python3
"""
Update Demo Dates

This script moves all demo orders and wave plans forward to start tomorrow
based on the current date. This ensures the demo data is always current.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoDataUpdater:
    """Updates demo data dates to be current."""
    
    def __init__(self, host: str = "localhost", port: int = 5433, 
                 database: str = "warehouse_opt", user: str = "wave_user", 
                 password: str = "wave_password"):
        """Initialize database connection parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
    
    def get_connection(self):
        """Get a database connection."""
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def calculate_date_shift(self):
        """Calculate how many days to shift the data forward."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            # Get the earliest order date
            cursor.execute("""
                SELECT MIN(order_date) as earliest_date
                FROM orders 
                WHERE warehouse_id = 1
            """)
            result = cursor.fetchone()
            earliest_date = result[0] if result and result[0] else None
            
            if not earliest_date:
                logger.warning("No orders found in database")
                return 0
            
            # Calculate days to shift
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Make sure both dates are timezone-naive for comparison
            if earliest_date.tzinfo is not None:
                earliest_date = earliest_date.replace(tzinfo=None)
            if tomorrow.tzinfo is not None:
                tomorrow = tomorrow.replace(tzinfo=None)
            
            days_to_shift = (tomorrow - earliest_date).days
            
            logger.info(f"Earliest order date: {earliest_date}")
            logger.info(f"Target start date: {tomorrow}")
            logger.info(f"Days to shift: {days_to_shift}")
            
            return days_to_shift
    
    def update_order_dates(self, days_to_shift: int):
        """Update all order dates by the specified number of days."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info(f"Updating order dates by {days_to_shift} days...")
            
            # Update order_date and shipping_deadline
            cursor.execute("""
                UPDATE orders 
                SET order_date = order_date + INTERVAL '%s days',
                    shipping_deadline = shipping_deadline + INTERVAL '%s days'
                WHERE warehouse_id = 1
            """, (days_to_shift, days_to_shift))
            
            updated_orders = cursor.rowcount
            logger.info(f"Updated {updated_orders} orders")
            
            conn.commit()
    
    def update_wave_dates(self, days_to_shift: int):
        """Update all wave dates by the specified number of days."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info(f"Updating wave dates by {days_to_shift} days...")
            
            # Update wave start and completion times
            cursor.execute("""
                UPDATE waves 
                SET planned_start_time = planned_start_time + INTERVAL '%s days',
                    planned_completion_time = planned_completion_time + INTERVAL '%s days'
                WHERE warehouse_id = 1
            """, (days_to_shift, days_to_shift))
            
            updated_waves = cursor.rowcount
            logger.info(f"Updated {updated_waves} waves")
            
            conn.commit()
    
    def update_wave_names(self, days_to_shift: int):
        """Update wave names to reflect the new dates."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Updating wave names to reflect new dates...")
            
            # Get all waves with their new planned start times
            cursor.execute("""
                SELECT id, wave_name, planned_start_time 
                FROM waves 
                WHERE warehouse_id = 1
                ORDER BY planned_start_time
            """)
            waves = cursor.fetchall()
            
            updated_count = 0
            for wave in waves:
                wave_id = wave[0]
                current_name = wave[1]
                planned_start = wave[2]
                
                if planned_start is None:
                    logger.warning(f"Wave {wave_id} has no planned start time, skipping")
                    continue
                
                # Calculate wave number based on time of day
                hour = planned_start.hour
                if 8 <= hour < 10:
                    wave_num = 1
                elif 10 <= hour < 12:
                    wave_num = 2
                elif 13 <= hour < 15:
                    wave_num = 3
                elif 15 <= hour < 17:
                    wave_num = 4
                else:
                    # Fallback for other times
                    wave_num = ((hour - 8) // 2) + 1
                    if wave_num < 1:
                        wave_num = 1
                    elif wave_num > 4:
                        wave_num = 4
                
                # Generate new wave name
                date_str = planned_start.strftime("%B %-d")
                if wave_num == 1:
                    wave_type = "Morning Wave 1"
                elif wave_num == 2:
                    wave_type = "Morning Wave 2"
                elif wave_num == 3:
                    wave_type = "Afternoon Wave 1"
                elif wave_num == 4:
                    wave_type = "Afternoon Wave 2"
                else:
                    wave_type = f"Wave {wave_num}"
                
                new_name = f"{date_str} - {wave_type}"
                
                # Update the wave name
                cursor.execute("""
                    UPDATE waves 
                    SET wave_name = %s
                    WHERE id = %s
                """, (new_name, wave_id))
                
                logger.info(f"Updated wave {wave_id}: '{current_name}' -> '{new_name}'")
                updated_count += 1
            
            conn.commit()
            logger.info(f"Updated {updated_count} wave names")
            
            return updated_count
    
    def update_wave_assignment_dates(self, days_to_shift: int):
        """Update all wave assignment dates by the specified number of days."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info(f"Updating wave assignment dates by {days_to_shift} days...")
            
            # Update planned start times for wave assignments
            cursor.execute("""
                UPDATE wave_assignments 
                SET planned_start_time = planned_start_time + INTERVAL '%s days'
                WHERE planned_start_time IS NOT NULL
            """, (days_to_shift,))
            
            updated_assignments = cursor.rowcount
            logger.info(f"Updated {updated_assignments} wave assignments")
            
            conn.commit()
    
    def update_demo_data(self):
        """Main function to update all demo data dates."""
        try:
            logger.info("Starting demo data date update...")
            
            # Calculate how many days to shift
            days_to_shift = self.calculate_date_shift()
            
            if days_to_shift <= 0:
                logger.info("Demo data is already current or future-dated")
                return {
                    "success": True,
                    "message": "Demo data is already current",
                    "days_shifted": 0
                }
            
            # Update all date fields
            self.update_order_dates(days_to_shift)
            self.update_wave_dates(days_to_shift)
            self.update_wave_assignment_dates(days_to_shift)
            
            # Update wave names to reflect new dates
            self.update_wave_names(days_to_shift)
            
            logger.info("Demo data date update completed successfully!")
            
            return {
                "success": True,
                "message": f"Updated demo data by {days_to_shift} days",
                "days_shifted": days_to_shift
            }
            
        except Exception as e:
            logger.error(f"Error updating demo data: {e}")
            return {
                "success": False,
                "message": f"Error updating demo data: {str(e)}",
                "days_shifted": 0
            }


def main():
    """Main function to run the demo data updater."""
    updater = DemoDataUpdater()
    result = updater.update_demo_data()
    print(f"Result: {result}")


if __name__ == "__main__":
    main() 