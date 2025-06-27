import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OptimizationPanel.css';

const API_BASE = 'http://localhost:8000';

interface OptimizationResult {
  status: string;
  run_id: number;
  warehouse_id: number;
  result: {
    metrics: {
      total_cost: number;
      total_orders_processed: number;
      average_order_processing_time: number;
      worker_utilization: number;
      equipment_utilization: number;
      solver_status: string;
    };
    schedule_summary: {
      total_tasks: number;
      total_hours: number;
      zones_utilized: number;
    };
  };
  input_summary: {
    total_orders: number;
    total_workers: number;
    total_equipment: number;
  };
  optimization_time: number;
  solver_status: string;
}

const OptimizationPanel: React.FC = () => {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [orderLimit, setOrderLimit] = useState(100);
  const [optimizationProgress, setOptimizationProgress] = useState<string>('');
  const [constraints, setConstraints] = useState<any>(null);
  const [loadingConstraints, setLoadingConstraints] = useState(true);

  // Fetch optimization constraints on component mount
  useEffect(() => {
    const fetchConstraints = async () => {
      try {
        const response = await axios.get(`${API_BASE}/optimization/constraints`);
        setConstraints(response.data);
      } catch (err) {
        console.error('Failed to fetch constraints:', err);
        // Fallback to default constraints
        setConstraints({
          constraints: {
            stage_precedence: {
              name: "Stage Precedence",
              description: "Orders must complete stages in sequence: pick → consolidate → pack → label → stage → ship",
              priority: "Critical",
              enforcement: "Hard constraint"
            },
            worker_capacity: {
              name: "Worker Capacity", 
              description: "Workers cannot be assigned to multiple tasks simultaneously",
              priority: "Critical",
              enforcement: "Hard constraint"
            },
            equipment_limits: {
              name: "Equipment Capacity",
              description: "Equipment usage must not exceed available capacity", 
              priority: "Critical",
              enforcement: "Hard constraint"
            },
            skill_requirements: {
              name: "Skill Requirements",
              description: "Workers can only be assigned to tasks they are qualified for",
              priority: "Critical", 
              enforcement: "Hard constraint"
            },
            shipping_deadlines: {
              name: "Shipping Deadlines",
              description: "All orders must complete shipping before their deadline",
              priority: "High",
              enforcement: "Soft constraint (with penalties)"
            },
            overtime_limits: {
              name: "Overtime Limits",
              description: "Minimize worker overtime (max 4 hours per day)",
              priority: "Medium",
              enforcement: "Soft constraint (with costs)"
            }
          },
          objective_weights: {
            deadline_violation_penalty: 1000,
            labor_cost_multiplier: 1.0,
            overtime_cost_multiplier: 1.5,
            equipment_utilization_weight: 0.1
          }
        });
      } finally {
        setLoadingConstraints(false);
      }
    };

    fetchConstraints();
  }, []);

  const runOptimization = async () => {
    setIsOptimizing(true);
    setError(null);
    setResult(null);
    setOptimizationProgress('Starting optimization...');

    try {
      // Estimate optimization time based on order count
      const estimatedTime = orderLimit <= 100 ? '1-2 minutes' :
                           orderLimit <= 500 ? '3-5 minutes' :
                           orderLimit <= 1000 ? '5-10 minutes' :
                           orderLimit <= 2000 ? '10-20 minutes' : '20-30 minutes';
      
      setOptimizationProgress(`Optimizing ${orderLimit} orders (estimated time: ${estimatedTime})...`);

      const response = await axios.post(`${API_BASE}/optimize/database`, null, {
        params: {
          warehouse_id: 1,
          order_limit: Math.min(orderLimit, 3000) // Support up to 3000 orders for daily operations
        }
      });

      console.log('Optimization response:', response.data);
      setResult(response.data);
      setOptimizationProgress('Optimization completed successfully!');
    } catch (err: any) {
      console.error('Optimization error:', err);
      setError(err.response?.data?.detail || 'Optimization failed. Please try again.');
      setOptimizationProgress('');
    } finally {
      setIsOptimizing(false);
    }
  };

  const safeGet = (obj: any, path: string, defaultValue: any = 'N/A') => {
    try {
      return path.split('.').reduce((current, key) => current?.[key], obj) ?? defaultValue;
    } catch {
      return defaultValue;
    }
  };

  if (loadingConstraints) {
    return (
      <div className="optimization-panel">
        <h2>Warehouse Optimization</h2>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Loading optimization constraints...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="optimization-panel">
      <h2>Warehouse Optimization</h2>
      
      {/* Optimization Constraints Section */}
      <div className="optimization-constraints" style={{
        background: '#f8f9fa',
        padding: '1.5rem',
        borderRadius: '8px',
        marginBottom: '1.5rem',
        border: '1px solid #dee2e6'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>Optimization Engine Constraints</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {Object.values(constraints?.constraints || {}).map((constraint: any, index: number) => (
            <div key={index} style={{
              background: 'white',
              padding: '1rem',
              borderRadius: '6px',
              border: '1px solid #e9ecef',
              borderLeft: `4px solid ${
                constraint.priority === 'Critical' ? '#dc3545' :
                constraint.priority === 'High' ? '#fd7e14' : '#ffc107'
              }`
            }}>
              <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', color: '#495057' }}>
                {constraint.name}
              </h4>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#6c757d' }}>
                {constraint.description}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ 
                  color: constraint.priority === 'Critical' ? '#dc3545' : 
                         constraint.priority === 'High' ? '#fd7e14' : '#ffc107',
                  fontWeight: 'bold'
                }}>
                  {constraint.priority}
                </span>
                <span style={{ color: '#6c757d' }}>
                  {constraint.enforcement}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div style={{ background: 'white', padding: '1rem', borderRadius: '6px', border: '1px solid #e9ecef' }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Objective Function Weights</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.9rem' }}>
            <div><strong>Deadline Violations:</strong> {constraints?.objective_weights?.deadline_violation_penalty || 1000}x (highest priority)</div>
            <div><strong>Labor Costs:</strong> {constraints?.objective_weights?.labor_cost_multiplier || 1.0}x (regular)</div>
            <div><strong>Overtime Costs:</strong> {constraints?.objective_weights?.overtime_cost_multiplier || 1.5}x (1.5x premium)</div>
            <div><strong>Equipment Efficiency:</strong> {constraints?.objective_weights?.equipment_utilization_weight || 0.1}x (optimization)</div>
          </div>
        </div>
      </div>
      
      <div className="optimization-controls">
        <div className="control-group">
          <label htmlFor="orderLimit">Order Limit:</label>
          <input
            id="orderLimit"
            type="number"
            value={orderLimit}
            onChange={(e) => setOrderLimit(parseInt(e.target.value) || 100)}
            min="1"
            max="3000"
            disabled={isOptimizing}
          />
          <small style={{ color: '#666', fontSize: '0.8rem' }}>
            {orderLimit <= 100 && 'Quick test (5-15 min)'}
            {orderLimit > 100 && orderLimit <= 500 && 'Shift planning (15-30 min)'}
            {orderLimit > 500 && orderLimit <= 1000 && 'Daily planning (30-60 min)'}
            {orderLimit > 1000 && 'Full day optimization (1-2 hours)'}
          </small>
        </div>
        
        <button 
          onClick={runOptimization}
          disabled={isOptimizing}
          className="optimize-button"
        >
          {isOptimizing ? 'Optimizing...' : 'Run Optimization'}
        </button>
      </div>

      {isOptimizing && optimizationProgress && (
        <div className="optimization-progress" style={{
          background: '#e3f2fd',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          border: '1px solid #2196f3'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#1976d2' }}>Optimization Progress</h4>
          <p style={{ margin: 0, color: '#1976d2' }}>{optimizationProgress}</p>
        </div>
      )}

      <div className="optimization-tips" style={{ 
        background: '#e8f5e8', 
        padding: '1rem', 
        borderRadius: '8px', 
        marginBottom: '1rem',
        fontSize: '0.9rem'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#174c3c' }}>Optimization Guidelines:</h4>
        <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
          <li><strong>50-100 orders:</strong> Quick testing and validation</li>
          <li><strong>200-500 orders:</strong> Shift planning and resource allocation</li>
          <li><strong>1000-1500 orders:</strong> Daily operations optimization</li>
          <li><strong>2000-2500 orders:</strong> Full day warehouse optimization</li>
        </ul>
      </div>

      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="optimization-results">
          <h3>Optimization Results</h3>
          
          <div className="results-grid">
            <div className="result-card">
              <h4>Cost Analysis</h4>
              <p><strong>Total Cost:</strong> ${safeGet(result, 'result.metrics.total_cost', 0).toFixed(2)}</p>
              <p><strong>Optimization Time:</strong> {safeGet(result, 'optimization_time', 0).toFixed(2)}s</p>
              <p><strong>Solver Status:</strong> {safeGet(result, 'solver_status', 'Unknown')}</p>
            </div>

            <div className="result-card">
              <h4>Processing Metrics</h4>
              <p><strong>Orders Processed:</strong> {safeGet(result, 'result.metrics.total_orders_processed', 0)}</p>
              <p><strong>Avg Processing Time:</strong> {safeGet(result, 'result.metrics.average_order_processing_time', 0).toFixed(2)}h</p>
              <p><strong>Worker Utilization:</strong> {(safeGet(result, 'result.metrics.worker_utilization', 0) * 100).toFixed(1)}%</p>
            </div>

            <div className="result-card">
              <h4>Resource Utilization</h4>
              <p><strong>Equipment Utilization:</strong> {(safeGet(result, 'result.metrics.equipment_utilization', 0) * 100).toFixed(1)}%</p>
              <p><strong>Total Tasks:</strong> {safeGet(result, 'result.schedule_summary.total_tasks', 0)}</p>
              <p><strong>Total Hours:</strong> {safeGet(result, 'result.schedule_summary.total_hours', 0).toFixed(1)}h</p>
            </div>

            <div className="result-card">
              <h4>Input Summary</h4>
              <p><strong>Total Orders:</strong> {safeGet(result, 'input_summary.total_orders', 0)}</p>
              <p><strong>Total Workers:</strong> {safeGet(result, 'input_summary.total_workers', 0)}</p>
              <p><strong>Total Equipment:</strong> {safeGet(result, 'input_summary.total_equipment', 0)}</p>
            </div>
          </div>

          <div className="run-info">
            <p><strong>Run ID:</strong> {safeGet(result, 'run_id', 'N/A')}</p>
            <p><strong>Warehouse ID:</strong> {safeGet(result, 'warehouse_id', 'N/A')}</p>
          </div>

          <div className="raw-data" style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
            <h4>Raw Response Data</h4>
            <pre style={{ fontSize: '0.8rem', overflow: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizationPanel; 