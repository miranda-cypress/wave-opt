import React, { useState } from 'react';
import './WarehouseLayout.css';

interface WarehouseLayoutProps {
  onNavigate: (page: string) => void;
}

const WarehouseLayout: React.FC<WarehouseLayoutProps> = ({ onNavigate }) => {
  const [isComputing, setIsComputing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<'success' | 'error' | null>(null);

  const handleRecomputeWalkingTimes = async () => {
    setIsComputing(true);
    setMessage(null);
    setMessageType(null);

    try {
      const response = await fetch('/api/recompute-walking-times', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setMessage(`Successfully recomputed walking times for ${result.total_records} bin pairs.`);
        setMessageType('success');
      } else {
        const errorData = await response.json();
        setMessage(`Error: ${errorData.detail || 'Failed to recompute walking times'}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error: Failed to connect to server');
      setMessageType('error');
    } finally {
      setIsComputing(false);
    }
  };

  return (
    <div className="warehouse-layout">
      <div className="container">
        <div className="page-header">
          <h1>Warehouse Layout</h1>
          <p>Manage warehouse layout and walking time calculations</p>
        </div>

        <div className="layout-content">
          <div className="section">
            <h2>Walking Time Matrix</h2>
            <p>
              Calculate and store walking times between all bins in the warehouse using 
              weighted Manhattan distance algorithm. This data is used for optimization 
              calculations.
            </p>
            
            <div className="action-section">
              <button 
                className={`recompute-button ${isComputing ? 'computing' : ''}`}
                onClick={handleRecomputeWalkingTimes}
                disabled={isComputing}
              >
                {isComputing ? 'Computing...' : 'Recompute Walking Times'}
              </button>
              
              {message && (
                <div className={`message ${messageType}`}>
                  {message}
                </div>
              )}
            </div>

                          <div className="info-section">
                <h3>Algorithm Details</h3>
                <ul>
                  <li><strong>Distance Method:</strong> Weighted Manhattan Distance</li>
                  <li><strong>Walking Speed:</strong> 250 feet per minute (~4.2 ft/sec)</li>
                  <li><strong>Zone Change Penalty:</strong> 0.5 minutes</li>
                  <li><strong>Level Change Penalty:</strong> 1.0 minutes</li>
                  <li><strong>Vertical Movement Weight:</strong> 2x slower than horizontal</li>
                </ul>
                <p className="config-note">
                  <em>Note: These values can be configured in the Config page.</em>
                </p>
              </div>
          </div>

          <div className="section">
            <h2>Future Enhancements</h2>
            <p>Planned improvements for walking time calculations:</p>
            <ul>
              <li>Graph-based pathfinding with obstacle avoidance</li>
              <li>Real-time traffic and congestion modeling</li>
              <li>Equipment-specific routing (forklifts, carts, etc.)</li>
              <li>Time-of-day and shift-based speed adjustments</li>
              <li>Integration with warehouse management system data</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseLayout; 