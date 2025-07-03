#!/usr/bin/env python3
"""
Simple script to regenerate realistic warehouse data.
This uses the existing setup infrastructure to ensure proper schema creation.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main function to regenerate data using existing setup scripts."""
    print("="*60)
    print("SIMPLE WAREHOUSE DATA REGENERATION")
    print("="*60)
    print("This will use existing setup scripts to ensure proper schema creation")
    print("="*60)
    
    # Change to database directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Step 1: Clean and setup database
    if not run_command("python clean_setup.py", "Cleaning and setting up database"):
        print("❌ Failed to clean and setup database")
        sys.exit(1)
    
    # Step 2: Run the enhanced data generator with realistic volumes
    if not run_command("python simulated_wms_data_generator.py", "Generating realistic warehouse data"):
        print("❌ Failed to generate data")
        sys.exit(1)
    
    # Step 3: Verify the data
    if not run_command("python check_waves.py", "Verifying generated data"):
        print("❌ Failed to verify data")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ REGENERATION COMPLETED SUCCESSFULLY")
    print("="*60)
    print("Your warehouse now has realistic data volumes!")
    print("Check the output above for verification details.")
    print("="*60)

if __name__ == "__main__":
    main() 