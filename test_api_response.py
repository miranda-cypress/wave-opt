#!/usr/bin/env python3
import requests
import json

def test_api_response():
    try:
        response = requests.get('http://localhost:8000/data/waves?warehouse_id=1&limit=10')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total waves returned: {data.get('total_count', 'N/A')}")
            print(f"Warehouse ID: {data.get('warehouse_id', 'N/A')}")
            
            waves = data.get('waves', [])
            print(f"\nWaves returned:")
            for i, wave in enumerate(waves):
                print(f"  Wave {i+1}:")
                print(f"    ID: {wave.get('id', 'N/A')}")
                print(f"    Name: {wave.get('name', 'N/A')}")
                print(f"    Orders: {wave.get('total_orders', 'N/A')}")
                print(f"    Type: {wave.get('wave_type', 'N/A')}")
                print(f"    Status: {wave.get('status', 'N/A')}")
                print()
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_response() 