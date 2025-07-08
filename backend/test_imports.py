#!/usr/bin/env python3
"""
Test script to check if all imports work correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all the imports needed for the API."""
    try:
        print("Testing imports...")
        
        # Test database service
        print("✓ Testing database_service import...")
        from database_service import DatabaseService
        print("✓ DatabaseService imported successfully")
        
        # Test walking time calculator
        print("✓ Testing walking_time_calculator import...")
        from walking_time_calculator import WalkingTimeCalculator
        print("✓ WalkingTimeCalculator imported successfully")
        
        # Test API main
        print("✓ Testing api.main import...")
        from api.main import app
        print("✓ FastAPI app imported successfully")
        
        print("✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 