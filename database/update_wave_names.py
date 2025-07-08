#!/usr/bin/env python3
"""
Update Wave Names

This script updates wave names to follow the format:
"July 8 - Morning Wave 1", "July 8 - Morning Wave 2", etc.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, timedelta
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WaveNameUpdater:
    """Updates wave names to the new format with dates and wave types."""
    
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
    
    def format_date(self, dt):
        # Cross-platform day without leading zero
        if sys.platform == "win32":
            return dt.strftime("%B %#d")
        else:
            return dt.strftime("%B %-d")
    
    def generate_wave_name(self, wave_date: datetime, wave_num: int) -> str:
        """Generate a wave name in the new format."""
        date_str = self.format_date(wave_date)
        
        # Determine wave type based on wave number (1-4 per day)
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
        
        return f"{date_str} - {wave_type}"
    
    def update_wave_names(self):
        """Update all wave names to the new format."""
        conn = self.get_connection()
        with conn.cursor() as cursor:
            logger.info("Updating wave names to new format...")
            
            # Get all waves ordered by planned start time
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
                new_name = self.generate_wave_name(planned_start, wave_num)
                
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


def main():
    """Main function to run the wave name updater."""
    updater = WaveNameUpdater()
    try:
        updated_count = updater.update_wave_names()
        print(f"Successfully updated {updated_count} wave names")
    except Exception as e:
        print(f"Error updating wave names: {e}")


if __name__ == "__main__":
    main() 