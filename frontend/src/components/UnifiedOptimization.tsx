import React, { useState, useEffect } from 'react';
import './UnifiedOptimization.css';
import { runOptimization, getWaves, optimizeWave, optimizeCrossWave } from '../api';

interface WaveData {
  id: number;
  name: string;
  wave_type: string;
  total_orders: number;
  efficiency_score: number;
  labor_cost: number;
  status: string;
}

interface OptimizationResult {
  wave_id?: number;
  wave_name?: string;
  optimize_type?: string;
  original_metrics: {
    efficiency_score: number;
    total_orders: number;
    estimated_cost: number;
  };
  optimized_metrics: {
    efficiency_score: number;
    efficiency_gain: number;
    cost_savings: number;
    estimated_new_cost: number;
    worker_reassignments: number;
    order_movements: number;
  };
  order_changes?: Array<{
    order_id: string;
    customer_name: string;
    original_worker: string;
    optimized_worker: string;
    stage_optimization: string;
    time_savings_minutes: number;
  }>;
}

interface CrossWaveResult {
  optimization_type: string;
  total_waves: number;
  total_orders: number;
  overall_improvements: {
    avg_efficiency_gain: number;
    total_cost_savings: number;
    total_order_movements: number;
    total_worker_reassignments: number;
  };
  wave_optimizations: Array<{
    wave_id: number;
    wave_name: string;
    original_efficiency: number;
    improved_efficiency: number;
    efficiency_gain: number;
    orders_moved_in: number;
    orders_moved_out: number;
    worker_reassignments: number;
  }>;
  order_movements: Array<{
    order_id: string;
    customer_name: string;
    from_wave: number;
    to_wave: number;
    reason: string;
    estimated_savings_minutes: number;
  }>;
}

interface GeneralOptimizationResult {
  total_orders: number;
  total_hours: number;
  total_cost: number;
  on_time_percentage: number;
  walking_time_optimization?: {
    total_walking_time_minutes: number;
    average_walking_time_per_order: number;
    walking_time_optimization_enabled: boolean;
  };
}

interface UnifiedOptimizationProps {
  onOptimizationComplete?: (results: any) => void;
  onOptimizationError?: (errorMessage: string) => void;
  onOptimizationStart?: () => void;
  onOptimizationEnd?: () => void;
  isLoading?: boolean;
}

const UnifiedOptimization: React.FC<UnifiedOptimizationProps> = ({
  onOptimizationComplete,
  onOptimizationError,
  onOptimizationStart,
  onOptimizationEnd,
  isLoading: externalLoading
}) => {
  const [optimizationMode, setOptimizationMode] = useState<'general' | 'wave'>('wave');
  const [waves, setWaves] = useState<WaveData[]>([]);
  const [selectedWaveId, setSelectedWaveId] = useState<number | null>(null);
  const [optimizeType, setOptimizeType] = useState<'within_wave' | 'cross_wave'>('within_wave');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | CrossWaveResult | GeneralOptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isLoading = externalLoading || isOptimizing;

  useEffect(() => {
    if (optimizationMode === 'wave') {
      loadWaves();
    }
  }, [optimizationMode]);

  const loadWaves = async () => {
    console.log('loadWaves called');
    try {
      const response = await getWaves(1, 1000);
      console.log('getWaves response:', response);
      setWaves(response.waves || []);
      if (response.waves && response.waves.length > 0) {
        setSelectedWaveId(response.waves[0].id);
        console.log('Set selectedWaveId to:', response.waves[0].id);
      }
    } catch (error) {
      console.error('Error loading waves:', error);
      setError('Failed to load waves');
    }
  };

  const handleOptimize = async () => {
    if (optimizationMode === 'general') {
      await runGeneralOptimization();
    } else {
      if (optimizeType === 'cross_wave') {
        await runCrossWaveOptimization();
      } else {
        await runWaveOptimization();
      }
    }
  };

  const runGeneralOptimization = async () => {
    if (onOptimizationStart) onOptimizationStart();
    setIsOptimizing(true);
    setError(null);
    setOptimizationResult(null);
    
    try {
      const optimizationResults = await runOptimization();
      setOptimizationResult(optimizationResults);
      if (onOptimizationComplete) onOptimizationComplete(optimizationResults);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during optimization';
      setError(errorMessage);
      if (onOptimizationError) onOptimizationError(errorMessage);
    } finally {
      setIsOptimizing(false);
      if (onOptimizationEnd) onOptimizationEnd();
    }
  };

  const runWaveOptimization = async () => {
    console.log('runWaveOptimization called', { selectedWaveId, optimizeType });
    if (!selectedWaveId) {
      setError('Please select a wave to optimize');
      return;
    }

    setIsOptimizing(true);
    setError(null);
    setOptimizationResult(null);

    try {
      console.log('Making API call to optimizeWave', { selectedWaveId, optimizeType });
      const result = await optimizeWave(selectedWaveId, optimizeType);
      console.log('API call successful', result);
      setOptimizationResult(result.optimization_result);
      if (onOptimizationComplete) onOptimizationComplete(result.optimization_result);
    } catch (error: any) {
      console.error('Optimization error:', error);
      const errorMessage = error.response?.data?.detail || 'Optimization failed';
      setError(errorMessage);
      if (onOptimizationError) onOptimizationError(errorMessage);
    } finally {
      setIsOptimizing(false);
    }
  };

  const runCrossWaveOptimization = async () => {
    setIsOptimizing(true);
    setError(null);
    setOptimizationResult(null);

    try {
      const result = await optimizeCrossWave();
      setOptimizationResult(result.optimization_result);
      if (onOptimizationComplete) onOptimizationComplete(result.optimization_result);
    } catch (error: any) {
      console.error('Cross-wave optimization error:', error);
      const errorMessage = error.response?.data?.detail || 'Cross-wave optimization failed';
      setError(errorMessage);
      if (onOptimizationError) onOptimizationError(errorMessage);
    } finally {
      setIsOptimizing(false);
    }
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 85) return 'text-green-600';
    if (efficiency >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="unified-optimization-page">
      <div className="optimization-header">
        <h2 className="page-title">🚀 Warehouse Optimization Engine</h2>
        <p className="page-description">
          Choose your optimization strategy: run general warehouse optimization or focus on specific wave optimization.
        </p>
      </div>

      {/* Optimization Mode Selection */}
      <div className="optimization-mode-selector">
        <h3 className="section-title">Optimization Mode</h3>
        <div className="mode-options">
          <label className="mode-option">
            <input
              type="radio"
              name="optimizationMode"
              value="general"
              checked={optimizationMode === 'general'}
              onChange={(e) => setOptimizationMode(e.target.value as 'general' | 'wave')}
            />
            <span className="mode-label">
              <strong>General Warehouse Optimization</strong>
              <span className="mode-description">Optimize the entire warehouse workflow with constraint programming</span>
            </span>
          </label>
          
          <label className="mode-option">
            <input
              type="radio"
              name="optimizationMode"
              value="wave"
              checked={optimizationMode === 'wave'}
              onChange={(e) => setOptimizationMode(e.target.value as 'general' | 'wave')}
            />
            <span className="mode-label">
              <strong>Wave-Specific Optimization</strong>
              <span className="mode-description">Optimize individual waves or across all waves</span>
            </span>
          </label>
        </div>
      </div>

      {/* General Optimization Controls */}
      {optimizationMode === 'general' && (
        <div className="optimization-controls general">
          <div className="control-section">
            <h3 className="section-title">General Warehouse Optimization</h3>
            <p className="control-description">
              Run our advanced constraint programming optimization engine to improve your warehouse workflow planning. 
              The system will process orders and generate an optimized plan that reduces bottlenecks, 
              improves efficiency, and minimizes costs.
            </p>
          </div>
        </div>
      )}

      {/* Wave Optimization Controls */}
      {optimizationMode === 'wave' && (
        <div className="optimization-controls wave">
          <div className="control-section">
            <h3 className="section-title">Wave Optimization Type</h3>
            <div className="optimization-type-selector">
              <label className="radio-option">
                <input
                  type="radio"
                  name="optimizeType"
                  value="within_wave"
                  checked={optimizeType === 'within_wave'}
                  onChange={(e) => setOptimizeType(e.target.value as 'within_wave' | 'cross_wave')}
                />
                <span className="radio-label">
                  <strong>Within Wave</strong>
                  <span className="radio-description">Optimize worker assignments and timing within the selected wave</span>
                </span>
              </label>
              
              <label className="radio-option">
                <input
                  type="radio"
                  name="optimizeType"
                  value="cross_wave"
                  checked={optimizeType === 'cross_wave'}
                  onChange={(e) => setOptimizeType(e.target.value as 'within_wave' | 'cross_wave')}
                />
                <span className="radio-label">
                  <strong>Cross-Wave</strong>
                  <span className="radio-description">Optimize across all waves, potentially moving orders between waves</span>
                </span>
              </label>
            </div>
          </div>

          {optimizeType === 'within_wave' && (
            <div className="control-section">
              <h3 className="section-title">Select Wave</h3>
              <select
                className="wave-selector"
                value={selectedWaveId || ''}
                onChange={(e) => setSelectedWaveId(Number(e.target.value))}
              >
                {waves.map(wave => (
                  <option key={wave.id} value={wave.id}>
                    {wave.name} ({wave.total_orders} orders, {wave.efficiency_score}% efficiency)
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* Optimize Button */}
      <div className="control-section">
        <button
          className={`optimize-button ${isLoading ? 'optimizing' : ''}`}
          onClick={handleOptimize}
          disabled={isLoading || (optimizationMode === 'wave' && optimizeType === 'within_wave' && !selectedWaveId)}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Optimizing...
            </>
          ) : (
            <>
              🚀 {optimizationMode === 'general' 
                ? 'Run General Optimization' 
                : optimizeType === 'cross_wave' 
                  ? 'Optimize All Waves' 
                  : 'Optimize Wave'
              }
            </>
          )}
        </button>
      </div>

      {/* Optimization Methodology */}
      <div className="optimization-methodology">
        <h3 className="section-title">Optimization Methodology</h3>
        <div className="methodology-grid">
          <div className="methodology-section">
            <h4>🎯 Objective Function</h4>
            <p>Minimize total operational cost while maximizing efficiency:</p>
            <div className="objective-formula">
              <strong>Minimize:</strong> Total Cost = Labor Cost + Equipment Cost + Deadline Penalties + Overtime Cost
            </div>
            <ul className="objective-details">
              <li><strong>Labor Cost:</strong> Worker hourly rates × hours worked</li>
              <li><strong>Equipment Cost:</strong> Equipment hourly rates × utilization time</li>
              <li><strong>Deadline Penalties:</strong> $100/hour for missed shipping deadlines</li>
              <li><strong>Overtime Cost:</strong> 1.5× regular rate for hours beyond 8-hour shifts</li>
            </ul>
          </div>

          <div className="methodology-section">
            <h4>🔒 Key Constraints</h4>
            <div className="constraints-list">
              <div className="constraint-group">
                <h5>Worker Constraints</h5>
                <ul>
                  <li>Maximum 8 hours per worker per shift</li>
                  <li>Workers can only perform tasks they're skilled for</li>
                  <li>One worker per task at any given time</li>
                  <li>Worker efficiency factors affect task duration</li>
                </ul>
              </div>
              
              <div className="constraint-group">
                <h5>Equipment Constraints</h5>
                <ul>
                  <li>Equipment capacity limits (e.g., packing stations, dock doors)</li>
                  <li>One order per equipment unit at any given time</li>
                  <li>Equipment efficiency factors affect processing time</li>
                  <li>Equipment availability during shift hours (6 AM - 10 PM)</li>
                </ul>
              </div>
              
              <div className="constraint-group">
                <h5>Order Constraints</h5>
                <ul>
                  <li>All order stages must be completed (picking → packing → shipping)</li>
                  <li>Stage precedence: picking must complete before packing</li>
                  <li>Shipping deadline compliance</li>
                  <li>Order priority levels (1-5, where 1 is highest priority)</li>
                </ul>
              </div>
              
              <div className="constraint-group">
                <h5>Warehouse Constraints</h5>
                <ul>
                  <li>Zone-based picking (workers assigned to specific zones)</li>
                  <li>Maximum 2,500 orders per day capacity</li>
                  <li>Shift hours: 6 AM to 10 PM (16 hours total)</li>
                  <li>SKU-specific pick and pack times</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="methodology-section">
            <h4>⚙️ Optimization Algorithm</h4>
            <p>Our constraint programming solver uses advanced techniques:</p>
            <ul className="algorithm-details">
              <li><strong>Multi-Stage Optimization:</strong> Simultaneously optimizes picking, packing, and shipping stages</li>
              <li><strong>Resource Allocation:</strong> Optimizes worker and equipment assignments across all orders</li>
              <li><strong>Time Window Management:</strong> Schedules tasks within available time windows</li>
              <li><strong>Conflict Resolution:</strong> Automatically resolves resource conflicts and bottlenecks</li>
              <li><strong>Deadline Optimization:</strong> Prioritizes orders based on shipping deadlines and priority levels</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* General Optimization Results */}
      {optimizationResult && optimizationMode === 'general' && 'total_orders' in optimizationResult && (
        <div className="optimization-results general">
          <h3 className="results-title">General Optimization Complete!</h3>
          <div className="results-grid">
            <div className="result-item">
              <span className="label">Orders Processed</span>
              <span className="value">{optimizationResult.total_orders}</span>
            </div>
            <div className="result-item">
              <span className="label">Total Hours</span>
              <span className="value">{(optimizationResult as GeneralOptimizationResult).total_hours?.toFixed(1)}</span>
            </div>
            <div className="result-item">
              <span className="label">Total Cost</span>
              <span className="value">${(optimizationResult as GeneralOptimizationResult).total_cost?.toFixed(2)}</span>
            </div>
            <div className="result-item">
              <span className="label">On-Time %</span>
              <span className="value success">{(optimizationResult as GeneralOptimizationResult).on_time_percentage?.toFixed(1)}%</span>
            </div>
          </div>
          
          {/* Walking Time Optimization Results */}
          {(optimizationResult as GeneralOptimizationResult).walking_time_optimization && (
            <div className="walking-time-results">
              <h4>🚶 Walking Time Optimization</h4>
              <div className="walking-time-grid">
                <div className="walking-time-item">
                  <span className="label">Total Walking Time:</span>
                  <span className="value">{(optimizationResult as GeneralOptimizationResult).walking_time_optimization?.total_walking_time_minutes?.toFixed(1) || '0.0'} minutes</span>
                </div>
                <div className="walking-time-item">
                  <span className="label">Avg Walking Time per Order:</span>
                  <span className="value">{(optimizationResult as GeneralOptimizationResult).walking_time_optimization?.average_walking_time_per_order?.toFixed(1) || '0.0'} minutes</span>
                </div>
                <div className="walking-time-item">
                  <span className="label">Walking Optimization:</span>
                  <span className={`value ${(optimizationResult as GeneralOptimizationResult).walking_time_optimization?.walking_time_optimization_enabled ? 'success' : 'warning'}`}>
                    {(optimizationResult as GeneralOptimizationResult).walking_time_optimization?.walking_time_optimization_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <div className="message">
            Optimization completed successfully! View the comparison and timeline results below.
          </div>
        </div>
      )}

      {/* Wave Optimization Results */}
      {optimizationResult && optimizationMode === 'wave' && (
        <div className="optimization-results wave">
          <h3 className="results-title">Wave Optimization Results</h3>
          
          {/* Single Wave Results */}
          {'wave_id' in optimizationResult && (
            <div className="wave-results">
              <div className="result-header">
                <h4>Wave: {optimizationResult.wave_name}</h4>
                <span className="optimization-type-badge">
                  {optimizationResult.optimize_type === 'within_wave' ? 'Within Wave' : 'Cross Wave'}
                </span>
              </div>

              <div className="metrics-comparison">
                <div className="metric-card original">
                  <h5>Before Optimization</h5>
                  <div className="metric-value">
                    <span className="metric-label">Efficiency:</span>
                    <span className={`metric-number ${getEfficiencyColor(optimizationResult.original_metrics.efficiency_score)}`}>
                      {optimizationResult.original_metrics.efficiency_score}%
                    </span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Orders:</span>
                    <span className="metric-number">{optimizationResult.original_metrics.total_orders}</span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Estimated Cost:</span>
                    <span className="metric-number">${optimizationResult.original_metrics.estimated_cost.toFixed(2)}</span>
                  </div>
                </div>

                <div className="metric-card optimized">
                  <h5>After Optimization</h5>
                  <div className="metric-value">
                    <span className="metric-label">Efficiency:</span>
                    <span className={`metric-number ${getEfficiencyColor(optimizationResult.optimized_metrics.efficiency_score)}`}>
                      {optimizationResult.optimized_metrics.efficiency_score}%
                    </span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Efficiency Gain:</span>
                    <span className="metric-number positive">+{optimizationResult.optimized_metrics.efficiency_gain.toFixed(1)}%</span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Cost Savings:</span>
                    <span className="metric-number positive">${optimizationResult.optimized_metrics.cost_savings.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="optimization-details">
                <div className="detail-item">
                  <span className="detail-label">Worker Reassignments:</span>
                  <span className="detail-value">{optimizationResult.optimized_metrics.worker_reassignments}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Order Movements:</span>
                  <span className="detail-value">{optimizationResult.optimized_metrics.order_movements}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">New Estimated Cost:</span>
                  <span className="detail-value">${optimizationResult.optimized_metrics.estimated_new_cost.toFixed(2)}</span>
                </div>
              </div>

              {/* Order Changes */}
              {optimizationResult.order_changes && optimizationResult.order_changes.length > 0 && (
                <div className="order-changes">
                  <h5>Key Order Changes</h5>
                  <div className="changes-table">
                    <div className="table-header">
                      <span>Order</span>
                      <span>Customer</span>
                      <span>Original Worker</span>
                      <span>Optimized Worker</span>
                      <span>Time Savings</span>
                    </div>
                    {optimizationResult.order_changes.map((change, index) => (
                      <div key={index} className="table-row">
                        <span>{change.order_id}</span>
                        <span>{change.customer_name}</span>
                        <span>{change.original_worker}</span>
                        <span>{change.optimized_worker}</span>
                        <span className="time-savings">{change.time_savings_minutes} min</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Cross-Wave Results */}
          {'optimization_type' in optimizationResult && optimizationResult.optimization_type === 'cross_wave' && (
            <div className="cross-wave-results">
              <div className="overall-improvements">
                <h4>Overall Improvements</h4>
                <div className="improvements-grid">
                  <div className="improvement-card">
                    <span className="improvement-label">Average Efficiency Gain</span>
                    <span className="improvement-value positive">
                      +{optimizationResult.overall_improvements.avg_efficiency_gain.toFixed(1)}%
                    </span>
                  </div>
                  <div className="improvement-card">
                    <span className="improvement-label">Total Cost Savings</span>
                    <span className="improvement-value positive">
                      ${optimizationResult.overall_improvements.total_cost_savings.toFixed(2)}
                    </span>
                  </div>
                  <div className="improvement-card">
                    <span className="improvement-label">Order Movements</span>
                    <span className="improvement-value">
                      {optimizationResult.overall_improvements.total_order_movements}
                    </span>
                  </div>
                  <div className="improvement-card">
                    <span className="improvement-label">Worker Reassignments</span>
                    <span className="improvement-value">
                      {optimizationResult.overall_improvements.total_worker_reassignments}
                    </span>
                  </div>
                </div>
              </div>

              {/* Wave-by-Wave Results */}
              <div className="wave-breakdown">
                <h4>Wave-by-Wave Breakdown</h4>
                <div className="waves-grid">
                  {optimizationResult.wave_optimizations.map((wave, index) => (
                    <div key={index} className="wave-card">
                      <h5>{wave.wave_name}</h5>
                      <div className="wave-metrics">
                        <div className="wave-metric">
                          <span className="metric-label">Efficiency:</span>
                          <span className={`metric-value ${getEfficiencyColor(wave.original_efficiency)}`}>
                            {wave.original_efficiency}% → {wave.improved_efficiency}%
                          </span>
                        </div>
                        <div className="wave-metric">
                          <span className="metric-label">Gain:</span>
                          <span className="metric-value positive">+{wave.efficiency_gain.toFixed(1)}%</span>
                        </div>
                        <div className="wave-metric">
                          <span className="metric-label">Orders In:</span>
                          <span className="metric-value">{wave.orders_moved_in}</span>
                        </div>
                        <div className="wave-metric">
                          <span className="metric-label">Orders Out:</span>
                          <span className="metric-value">{wave.orders_moved_out}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Order Movements */}
              {optimizationResult.order_movements && optimizationResult.order_movements.length > 0 && (
                <div className="order-movements">
                  <h4>Order Movements</h4>
                  <div className="movements-table">
                    <div className="table-header">
                      <span>Order</span>
                      <span>Customer</span>
                      <span>From Wave</span>
                      <span>To Wave</span>
                      <span>Reason</span>
                      <span>Time Savings</span>
                    </div>
                    {optimizationResult.order_movements.map((movement, index) => (
                      <div key={index} className="table-row">
                        <span>{movement.order_id}</span>
                        <span>{movement.customer_name}</span>
                        <span>Wave {movement.from_wave}</span>
                        <span>Wave {movement.to_wave}</span>
                        <span>{movement.reason}</span>
                        <span className="time-savings">{movement.estimated_savings_minutes} min</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UnifiedOptimization; 