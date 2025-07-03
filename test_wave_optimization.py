#!/usr/bin/env python3
import requests
import json

def test_wave_optimization():
    """Test wave optimization with real database data."""
    
    print("Testing wave optimization with real DB data...")
    
    try:
        # Test the wave optimization endpoint
        response = requests.post('http://localhost:8000/optimization/wave/1?optimize_type=within_wave')
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Wave optimization successful!")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Run ID: {result.get('run_id', 'N/A')}")
            
            # Print optimization metrics
            if 'optimization_result' in result:
                opt_result = result['optimization_result']
                print(f"Wave ID: {opt_result.get('wave_id', 'N/A')}")
                print(f"Wave Name: {opt_result.get('wave_name', 'N/A')}")
                print(f"Optimize Type: {opt_result.get('optimize_type', 'N/A')}")
                
                # Print original vs improved metrics
                if 'original_metrics' in opt_result and 'improved_metrics' in opt_result:
                    original = opt_result['original_metrics']
                    improved = opt_result['improved_metrics']
                    
                    print(f"Original Efficiency: {original.get('efficiency_score', 'N/A')}%")
                    print(f"Improved Efficiency: {improved.get('efficiency_score', 'N/A')}%")
                    print(f"Efficiency Gain: {improved.get('efficiency_score', 0) - original.get('efficiency_score', 0):.1f}%")
                    
                    print(f"Original Labor Cost: ${original.get('labor_cost', 'N/A')}")
                    print(f"Improved Labor Cost: ${improved.get('labor_cost', 'N/A')}")
                    print(f"Cost Savings: ${original.get('labor_cost', 0) - improved.get('labor_cost', 0):.2f}")
            
            # Print metrics
            if 'metrics' in result:
                metrics = result['metrics']
                print(f"Optimization Time: {metrics.get('optimization_time_seconds', 'N/A')}s")
                print(f"Worker Reassignments: {metrics.get('worker_reassignments', 'N/A')}")
                print(f"Order Movements: {metrics.get('order_movements', 'N/A')}")
                
        else:
            print(f"❌ Wave optimization failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing wave optimization: {e}")

def test_waves_endpoint():
    """Test the waves endpoint to see real wave data."""
    
    print("\nTesting waves endpoint...")
    
    try:
        response = requests.get('http://localhost:8000/data/waves?warehouse_id=1&limit=10')
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Waves endpoint successful!")
            print(f"Total waves: {result.get('total_count', 'N/A')}")
            
            waves = result.get('waves', [])
            for i, wave in enumerate(waves):
                print(f"Wave {i+1}:")
                print(f"  ID: {wave.get('id', 'N/A')}")
                print(f"  Name: {wave.get('name', 'N/A')}")
                print(f"  Type: {wave.get('wave_type', 'N/A')}")
                print(f"  Orders: {wave.get('total_orders', 'N/A')}")
                print(f"  Efficiency: {wave.get('efficiency_score', 'N/A')}%")
                print(f"  Status: {wave.get('status', 'N/A')}")
                print()
        else:
            print(f"❌ Waves endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing waves endpoint: {e}")

if __name__ == "__main__":
    test_waves_endpoint()
    test_wave_optimization() 