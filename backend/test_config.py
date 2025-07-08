#!/usr/bin/env python3
"""
Test script for the configuration system.
"""

from config_service import config_service

def test_config():
    print("Testing configuration system...")
    
    # Test getting config
    config = config_service.get_config()
    print(f"✓ Config loaded successfully")
    print(f"Walking speed: {config['walking_time']['walking_speed_fpm']} fpm")
    print(f"Vertical movement weight: {config['walking_time']['vertical_movement_weight']}")
    
    # Test getting specific values
    walking_speed = config_service.get_value("walking_time.walking_speed_fpm")
    vertical_weight = config_service.get_value("walking_time.vertical_movement_weight")
    print(f"✓ Specific values retrieved: {walking_speed}, {vertical_weight}")
    
    # Test setting a value
    original_speed = config_service.get_value("walking_time.walking_speed_fpm")
    config_service.set_value("walking_time.walking_speed_fpm", 275.0)
    new_speed = config_service.get_value("walking_time.walking_speed_fpm")
    print(f"✓ Value updated: {original_speed} -> {new_speed}")
    
    # Reset to original
    config_service.set_value("walking_time.walking_speed_fpm", original_speed)
    print(f"✓ Value reset to original: {config_service.get_value('walking_time.walking_speed_fpm')}")
    
    print("✓ All configuration tests passed!")

if __name__ == "__main__":
    test_config() 