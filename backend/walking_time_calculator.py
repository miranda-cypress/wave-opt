"""
Walking Time Calculator for Warehouse Optimization

This module provides functions to calculate walking times between bins
using various algorithms, starting with weighted Manhattan distance.
"""

import math
from typing import List, Dict, Tuple
from decimal import Decimal
from database_service import DatabaseService
from config_service import config_service


class WalkingTimeCalculator:
    """Calculate walking times between warehouse bins."""
    
    def __init__(self, warehouse_id: int = 1):
        self.warehouse_id = warehouse_id
        self.db = DatabaseService()
        
        # Load configuration values
        self.walking_speed_fpm = config_service.get_value("walking_time.walking_speed_fpm", 250.0)
        self.x_weight = config_service.get_value("walking_time.x_weight", 1.0)
        self.y_weight = config_service.get_value("walking_time.y_weight", 1.0)
        self.z_weight = config_service.get_value("walking_time.vertical_movement_weight", 2.0)
        self.zone_change_penalty_minutes = config_service.get_value("walking_time.zone_change_penalty_minutes", 0.5)
        self.level_change_penalty_minutes = config_service.get_value("walking_time.level_change_penalty_minutes", 1.0)
        
    def calculate_weighted_manhattan_distance(
        self, 
        from_coords: Tuple[float, float, float], 
        to_coords: Tuple[float, float, float]
    ) -> float:
        """
        Calculate weighted Manhattan distance between two points.
        
        Args:
            from_coords: (x, y, z) coordinates of starting point
            to_coords: (x, y, z) coordinates of ending point
            
        Returns:
            Weighted Manhattan distance in feet
        """
        x1, y1, z1 = from_coords
        x2, y2, z2 = to_coords
        
        # Calculate weighted Manhattan distance
        x_distance = abs(x2 - x1) * self.x_weight
        y_distance = abs(y2 - y1) * self.y_weight
        z_distance = abs(z2 - z1) * self.z_weight
        
        return x_distance + y_distance + z_distance
    
    def calculate_walking_time_minutes(
        self, 
        from_coords: Tuple[float, float, float], 
        to_coords: Tuple[float, float, float],
        from_zone: str | None = None,
        to_zone: str | None = None,
        from_level: int | None = None,
        to_level: int | None = None
    ) -> float:
        """
        Calculate walking time between two points including penalties.
        
        Args:
            from_coords: Starting coordinates (x, y, z)
            to_coords: Ending coordinates (x, y, z)
            from_zone: Starting zone (optional, for zone change penalty)
            to_zone: Ending zone (optional, for zone change penalty)
            from_level: Starting level (optional, for level change penalty)
            to_level: Ending level (optional, for level change penalty)
            
        Returns:
            Walking time in minutes
        """
        # Calculate base distance
        distance_feet = self.calculate_weighted_manhattan_distance(from_coords, to_coords)
        
        # Calculate base walking time
        base_time_minutes = distance_feet / self.walking_speed_fpm
        
        # Add zone change penalty if applicable
        if from_zone and to_zone and from_zone != to_zone:
            base_time_minutes += self.zone_change_penalty_minutes
        
        # Add level change penalty if applicable
        if from_level and to_level and from_level != to_level:
            base_time_minutes += self.level_change_penalty_minutes
        
        return round(base_time_minutes, 2)
    
    def get_all_bins(self) -> List[Dict]:
        """Get all bins for the warehouse."""
        return self.db.get_bins(self.warehouse_id)
    
    def calculate_walking_times_matrix(self) -> List[Dict]:
        """
        Calculate walking times between all bins and return as a list of records.
        
        Returns:
            List of dictionaries with walking time data
        """
        bins = self.get_all_bins()
        walking_times = []
        
        print(f"Calculating walking times for {len(bins)} bins...")
        
        for i, from_bin in enumerate(bins):
            for j, to_bin in enumerate(bins):
                # Skip same bin
                if from_bin['id'] == to_bin['id']:
                    continue
                
                # Get coordinates
                from_coords = (
                    float(from_bin['x_coordinate']),
                    float(from_bin['y_coordinate']),
                    float(from_bin['z_coordinate'])
                )
                to_coords = (
                    float(to_bin['x_coordinate']),
                    float(to_bin['y_coordinate']),
                    float(to_bin['z_coordinate'])
                )
                
                # Calculate distance and walking time
                distance_feet = self.calculate_weighted_manhattan_distance(from_coords, to_coords)
                walking_time_minutes = self.calculate_walking_time_minutes(
                    from_coords, to_coords,
                    from_bin.get('zone'), to_bin.get('zone'),
                    from_bin.get('level'), to_bin.get('level')
                )
                
                walking_times.append({
                    'from_bin_id': from_bin['id'],
                    'to_bin_id': to_bin['id'],
                    'from_bin_code': from_bin['bin_id'],
                    'to_bin_code': to_bin['bin_id'],
                    'distance_feet': round(distance_feet, 2),
                    'walking_time_minutes': walking_time_minutes,
                    'path_type': 'weighted_manhattan'
                })
        
        print(f"✓ Calculated {len(walking_times)} walking time records")
        return walking_times
    
    def save_walking_times_matrix(self, walking_times: List[Dict]) -> bool:
        """
        Save the walking times matrix to the database.
        
        Args:
            walking_times: List of walking time records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Clear existing walking times
            cursor.execute("DELETE FROM walking_times")
            
            # Insert new walking times
            for record in walking_times:
                cursor.execute("""
                    INSERT INTO walking_times 
                    (from_bin_id, to_bin_id, distance_feet, walking_time_minutes, path_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    record['from_bin_id'],
                    record['to_bin_id'],
                    record['distance_feet'],
                    record['walking_time_minutes'],
                    record['path_type']
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✓ Saved {len(walking_times)} walking time records to database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving walking times: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def recompute_walking_times(self) -> bool:
        """
        Recompute and save the walking times matrix.
        
        Returns:
            True if successful, False otherwise
        """
        print("Starting walking times recomputation...")
        
        # Calculate walking times matrix
        walking_times = self.calculate_walking_times_matrix()
        
        # Save to database
        success = self.save_walking_times_matrix(walking_times)
        
        if success:
            print("✓ Walking times recomputation completed successfully!")
        else:
            print("❌ Walking times recomputation failed!")
        
        return success


def calculate_walking_time_between_bins(
    from_bin_id: int, 
    to_bin_id: int, 
    warehouse_id: int = 1
) -> Dict:
    """
    Calculate walking time between two specific bins.
    
    Args:
        from_bin_id: ID of starting bin
        to_bin_id: ID of ending bin
        warehouse_id: Warehouse ID
        
    Returns:
        Dictionary with walking time information
    """
    calculator = WalkingTimeCalculator(warehouse_id)
    bins = calculator.get_all_bins()
    
    # Find the specific bins
    from_bin = next((b for b in bins if b['id'] == from_bin_id), None)
    to_bin = next((b for b in bins if b['id'] == to_bin_id), None)
    
    if not from_bin or not to_bin:
        raise ValueError(f"Bin not found: from_bin_id={from_bin_id}, to_bin_id={to_bin_id}")
    
    # Calculate walking time
    from_coords = (
        float(from_bin['x_coordinate']),
        float(from_bin['y_coordinate']),
        float(from_bin['z_coordinate'])
    )
    to_coords = (
        float(to_bin['x_coordinate']),
        float(to_bin['y_coordinate']),
        float(to_bin['z_coordinate'])
    )
    
    distance_feet = calculator.calculate_weighted_manhattan_distance(from_coords, to_coords)
    walking_time_minutes = calculator.calculate_walking_time_minutes(
        from_coords, to_coords,
        from_bin.get('zone'), to_bin.get('zone'),
        from_bin.get('level'), to_bin.get('level')
    )
    
    return {
        'from_bin_id': from_bin_id,
        'to_bin_id': to_bin_id,
        'from_bin_code': from_bin['bin_id'],
        'to_bin_code': to_bin['bin_id'],
        'distance_feet': round(distance_feet, 2),
        'walking_time_minutes': walking_time_minutes,
        'path_type': 'weighted_manhattan'
    } 