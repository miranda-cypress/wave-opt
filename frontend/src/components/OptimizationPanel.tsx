import React, { useState } from 'react';
import './OptimizationPanel.css';
import { runOptimization } from '../api';

interface OptimizationPanelProps {
  onOptimizationComplete: (results: any) => void;
  onOptimizationError: (errorMessage: string) => void;
  onOptimizationStart: () => void;
  onOptimizationEnd: () => void;
  isLoading: boolean;
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({ 
  onOptimizationComplete, 
  onOptimizationError, 
  onOptimizationStart, 
  onOptimizationEnd,
  isLoading 
}) => {
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  const handleOptimize = async () => {
    onOptimizationStart();
    setError(null);
    
    try {
      const optimizationResults = await runOptimization();
      setResults(optimizationResults);
      onOptimizationComplete(optimizationResults);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during optimization';
      setError(errorMessage);
      onOptimizationError(errorMessage);
    } finally {
      onOptimizationEnd();
    }
  };

  return (
    <div className="optimization-panel">
      <h2>Warehouse Wave Optimization</h2>
      <p>
        Run our advanced constraint programming optimization engine to improve your warehouse workflow planning. 
        The system will process 100 orders and generate an optimized plan that reduces bottlenecks, 
        improves efficiency, and minimizes costs.
      </p>
      
      <div className="optimization-controls">
        <button
          className="optimize-button"
          onClick={handleOptimize}
          disabled={isLoading}
        >
          {isLoading ? 'Optimizing...' : 'Run Optimization'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results && (
        <div className="optimization-results">
          <h3>Optimization Complete!</h3>
          <div className="results-grid">
            <div className="result-item">
              <span className="label">Orders Processed</span>
              <span className="value">{results.total_orders}</span>
            </div>
            <div className="result-item">
              <span className="label">Total Hours</span>
              <span className="value">{results.total_hours?.toFixed(1)}</span>
            </div>
            <div className="result-item">
              <span className="label">Total Cost</span>
              <span className="value">${results.total_cost?.toFixed(2)}</span>
            </div>
            <div className="result-item">
              <span className="label">On-Time %</span>
              <span className="value success">{results.on_time_percentage?.toFixed(1)}%</span>
            </div>
          </div>
          <div className="message">
            Optimization completed successfully! View the comparison and timeline results below.
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizationPanel; 