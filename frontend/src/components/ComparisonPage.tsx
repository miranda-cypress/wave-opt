import React, { useState, useEffect } from 'react';
import './ComparisonPage.css';
import { getWaveComparisonData } from '../api';

interface WaveComparison {
  wave_id: string;
  default_plan: {
    total_orders: number;
    estimated_hours: number;
    worker_utilization: number;
    equipment_utilization: number;
    on_time_percentage: number;
    total_cost: number;
    bottlenecks: string[];
    issues: string[];
  };
  optimized_plan: {
    total_orders: number;
    estimated_hours: number;
    worker_utilization: number;
    equipment_utilization: number;
    on_time_percentage: number;
    total_cost: number;
    improvements: string[];
    savings: {
      time_savings_hours: number;
      cost_savings_dollars: number;
      efficiency_gain_percentage: number;
    };
  };
}

interface ComparisonPageProps {
  originalPlan?: any;
  optimizedPlan?: any;
  summary?: any;
  showHeader?: boolean;
  hasOptimizationResults?: boolean;
}

const ComparisonPage: React.FC<ComparisonPageProps> = ({ 
  originalPlan, 
  optimizedPlan, 
  summary, 
  showHeader = true,
  hasOptimizationResults = false
}) => {
  const [selectedWave, setSelectedWave] = useState<string>('');
  const [showDetails, setShowDetails] = useState<boolean>(false);
  const [waveComparisons, setWaveComparisons] = useState<Record<string, WaveComparison>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWaveComparisonData();
  }, []);

  const loadWaveComparisonData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getWaveComparisonData(1); // warehouse_id = 1
      const data = response.wave_comparisons || {};
      
      setWaveComparisons(data);
      
      // Set the first wave as default selection
      const waveKeys = Object.keys(data);
      if (waveKeys.length > 0) {
        setSelectedWave(waveKeys[0]);
      }
      
    } catch (err) {
      console.error('Error loading wave comparison data:', err);
      setError('Failed to load wave comparison data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="comparison-page">
        <div className="loading-message">Loading wave comparison data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="comparison-page">
        <div className="error-message">
          <h2>Error Loading Data</h2>
          <p>{error}</p>
          <button onClick={loadWaveComparisonData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (Object.keys(waveComparisons).length === 0) {
    return (
      <div className="comparison-page">
        <div className="no-data-message">
          <h2>No Wave Data Available</h2>
          <p>No waves found in the database. Please create some waves first.</p>
        </div>
      </div>
    );
  }

  const currentWave = waveComparisons[selectedWave];

  return (
    <div className="comparison-page">
      {showHeader && (
        <div className="comparison-header">
          <h1>WMS vs Optimized Planning Comparison</h1>
          <p className="subtitle">
            See how our constraint programming optimization engine transforms warehouse operations
          </p>
        </div>
      )}

      {/* Wave Selection */}
      <div className="wave-selector">
        <label htmlFor="waveSelect">Select Wave:</label>
        <select 
          id="waveSelect" 
          value={selectedWave} 
          onChange={(e) => setSelectedWave(e.target.value)}
        >
          {Object.keys(waveComparisons).map(waveId => (
            <option key={waveId} value={waveId}>
              {waveComparisons[waveId].wave_id}
            </option>
          ))}
        </select>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card default">
          <h3>Default WMS Plan</h3>
          <div className="metrics">
            <div className="metric">
              <span className="label">Orders: </span>
              <span className="value">{currentWave.default_plan.total_orders}</span>
            </div>
            <div className="metric">
              <span className="label">Hours: </span>
              <span className="value">{currentWave.default_plan.estimated_hours.toFixed(1)}h</span>
            </div>
            <div className="metric">
              <span className="label">Cost: </span>
              <span className="value">${currentWave.default_plan.total_cost.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="label">On-Time: </span>
              <span className="value">{currentWave.default_plan.on_time_percentage.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="label">Worker Utilization: </span>
              <span className="value">{currentWave.default_plan.worker_utilization.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="label">Equipment Utilization: </span>
              <span className="value">{currentWave.default_plan.equipment_utilization.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="summary-card optimized">
          <h3>{hasOptimizationResults ? 'Optimized Plan' : 'Expected Optimized Plan'}</h3>
          <div className="metrics">
            <div className="metric">
              <span className="label">Orders: </span>
              <span className="value">{currentWave.optimized_plan.total_orders}</span>
            </div>
            <div className="metric">
              <span className="label">Hours: </span>
              <span className="value">{currentWave.optimized_plan.estimated_hours.toFixed(1)}h</span>
            </div>
            <div className="metric">
              <span className="label">Cost: </span>
              <span className="value">${currentWave.optimized_plan.total_cost.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="label">On-Time: </span>
              <span className="value">{currentWave.optimized_plan.on_time_percentage.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="label">Worker Utilization: </span>
              <span className="value">{currentWave.optimized_plan.worker_utilization.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="label">Equipment Utilization: </span>
              <span className="value">{currentWave.optimized_plan.equipment_utilization.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="summary-card savings">
          <h3>Optimization Impact</h3>
          <div className="metrics">
            <div className="metric positive">
              <span className="label">Time Saved: </span>
              <span className="value">{currentWave.optimized_plan.savings.time_savings_hours.toFixed(1)}h</span>
            </div>
            <div className="metric positive">
              <span className="label">Cost Saved: </span>
              <span className="value">${currentWave.optimized_plan.savings.cost_savings_dollars.toFixed(2)}</span>
            </div>
            <div className="metric positive">
              <span className="label">Efficiency Gain: </span>
              <span className="value">+{currentWave.optimized_plan.savings.efficiency_gain_percentage.toFixed(1)}%</span>
            </div>
            <div className="metric positive">
              <span className="label">On-Time Improvement: </span>
              <span className="value">+{((currentWave.optimized_plan.on_time_percentage) - (currentWave.default_plan.on_time_percentage)).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Comparison */}
      <div className="detailed-comparison">
        <button 
          className="toggle-details"
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'Hide Details' : 'Show Detailed Analysis'}
        </button>

        {showDetails && (
          <div className="details-content">
            <div className="comparison-columns">
              <div className="column default-column">
                <h3>Default WMS Issues</h3>
                <div className="issues-section">
                  <h4>Bottlenecks Identified:</h4>
                  <ul>
                    {currentWave.default_plan.bottlenecks.length > 0 ? (
                      currentWave.default_plan.bottlenecks.map((bottleneck, index) => (
                        <li key={index}>{bottleneck}</li>
                      ))
                    ) : (
                      <li>No significant bottlenecks identified</li>
                    )}
                  </ul>
                  
                  <h4>Risk Factors:</h4>
                  <ul>
                    {currentWave.default_plan.issues.length > 0 ? (
                      currentWave.default_plan.issues.map((issue, index) => (
                        <li key={index}>{issue}</li>
                      ))
                    ) : (
                      <li>No significant risk factors identified</li>
                    )}
                  </ul>
                </div>
              </div>

              <div className="column optimized-column">
                <h3>Optimization Solutions</h3>
                <div className="improvements-section">
                  <h4>Improvements Applied:</h4>
                  <ul>
                    {currentWave.optimized_plan.improvements.length > 0 ? (
                      currentWave.optimized_plan.improvements.map((improvement, index) => (
                        <li key={index}>{improvement}</li>
                      ))
                    ) : (
                      <li>No specific improvements needed</li>
                    )}
                  </ul>
                  
                  <h4>Constraint Programming Benefits:</h4>
                  <ul>
                    <li>Stage precedence enforced</li>
                    <li>Worker capacity optimized</li>
                    <li>Equipment conflicts eliminated</li>
                    <li>Deadline compliance maximized</li>
                    <li>Overtime minimized</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparisonPage; 