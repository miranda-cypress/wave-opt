"""
Configuration Service for Wave Optimization Application

Manages application configuration values including walking time parameters,
optimization settings, and UI preferences.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_path = Path(__file__).parent / config_file
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            else:
                # Create default config if file doesn't exist
                self._config = self._get_default_config()
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "walking_time": {
                "walking_speed_fpm": 250.0,
                "vertical_movement_weight": 2.0,
                "zone_change_penalty_minutes": 0.5,
                "level_change_penalty_minutes": 1.0,
                "x_weight": 1.0,
                "y_weight": 1.0
            },
            "optimization": {
                "default_hourly_rate": 25.0,
                "estimated_minutes_per_order": 2.5,
                "efficiency_threshold_low": 70,
                "efficiency_threshold_high": 85
            },
            "standard_times": {
                "label_minutes_per_order": 5.0,
                "stage_minutes_per_order": 10.0,
                "ship_minutes_per_order": 8.0,
                "consolidate_minutes_per_item": 0.5,
                "pack_minutes_per_item": 1.5,
                "pick_minutes_per_item": 2.0
            },
            "ui": {
                "company_name": "Cypress Falls Consulting",
                "app_name": "ZoneFlow",
                "version": "1.0.0"
            }
        }
    
    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        if self._config is None:
            self._load_config()
        return self._config.copy() if self._config else {}
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Path to the value (e.g., "walking_time.walking_speed_fpm")
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        if self._config is None:
            self._load_config()
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                if value is None or not isinstance(value, dict):
                    return default
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Path to the value (e.g., "walking_time.walking_speed_fpm")
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        if self._config is None:
            self._load_config()
        
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config or not isinstance(config, dict):
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        return self._save_config()
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update the entire configuration.
        
        Args:
            new_config: New configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        self._config = new_config
        return self._save_config()
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        self._config = self._get_default_config()
        return self._save_config()


# Global instance
config_service = ConfigService() 