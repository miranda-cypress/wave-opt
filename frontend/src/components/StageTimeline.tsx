import React, { useState, useEffect } from 'react';
import './StageTimeline.css';
import { getOriginalWmsPlanSummary, getOptimizationPlan } from '../api';

interface StageTiming {
  stage: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  waiting_time_before: number;
  worker_name: string;
  equipment_name?: string;
}

interface OrderTimeline {
  order_id: number;
  customer_name: string;
  priority: number;
  original_timeline: StageTiming[];
  optimized_timeline: StageTiming[];
  total_processing_time_original: number;
  total_processing_time_optimized: number;
  total_waiting_time_original: number;
  total_waiting_time_optimized: number;
  time_savings: number;
  waiting_time_reduction: number;
}

interface StageTimelineProps {
  originalPlan?: any;
  optimizedPlan?: any;
}

const StageTimeline: React.FC<StageTimelineProps> = ({ originalPlan, optimizedPlan }) => {
  const [selectedOrder, setSelectedOrder] = useState<string>('1');
  const [showDetails, setShowDetails] = useState<boolean>(false);

  // Use real data if available, otherwise fall back to fake data
  const useRealData = originalPlan && optimizedPlan;

  // Fake data for demonstration
  const orderTimelines: Record<string, OrderTimeline> = {
    'aggregate': {
      order_id: 0,
      customer_name: "All Orders in Wave",
      priority: 0,
      original_timeline: [
        {
          stage: "PICK",
          start_time: "08:00",
          end_time: "10:30",
          duration_minutes: 150,
          waiting_time_before: 0,
          worker_name: "All Pick Workers",
          equipment_name: "All Pick Carts"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "10:45",
          end_time: "11:15",
          duration_minutes: 30,
          waiting_time_before: 15,
          worker_name: "All Consolidation Workers",
          equipment_name: "All Conveyors"
        },
        {
          stage: "PACK",
          start_time: "11:30",
          end_time: "12:45",
          duration_minutes: 75,
          waiting_time_before: 15,
          worker_name: "All Packing Workers",
          equipment_name: "All Packing Stations"
        },
        {
          stage: "LABEL",
          start_time: "13:00",
          end_time: "13:20",
          duration_minutes: 20,
          waiting_time_before: 15,
          worker_name: "All Labeling Workers",
          equipment_name: "All Label Printers"
        },
        {
          stage: "STAGE",
          start_time: "13:35",
          end_time: "13:50",
          duration_minutes: 15,
          waiting_time_before: 15,
          worker_name: "All Staging Workers",
          equipment_name: "All Staging Areas"
        },
        {
          stage: "SHIP",
          start_time: "14:05",
          end_time: "14:30",
          duration_minutes: 25,
          waiting_time_before: 15,
          worker_name: "All Shipping Workers",
          equipment_name: "All Dock Doors"
        }
      ],
      optimized_timeline: [
        {
          stage: "PICK",
          start_time: "08:00",
          end_time: "09:45",
          duration_minutes: 105,
          waiting_time_before: 0,
          worker_name: "All Pick Workers",
          equipment_name: "All Pick Carts"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "09:45",
          end_time: "10:05",
          duration_minutes: 20,
          waiting_time_before: 0,
          worker_name: "All Consolidation Workers",
          equipment_name: "All Conveyors"
        },
        {
          stage: "PACK",
          start_time: "10:05",
          end_time: "11:05",
          duration_minutes: 60,
          waiting_time_before: 0,
          worker_name: "All Packing Workers",
          equipment_name: "All Packing Stations"
        },
        {
          stage: "LABEL",
          start_time: "11:05",
          end_time: "11:15",
          duration_minutes: 10,
          waiting_time_before: 0,
          worker_name: "All Labeling Workers",
          equipment_name: "All Label Printers"
        },
        {
          stage: "STAGE",
          start_time: "11:15",
          end_time: "11:22",
          duration_minutes: 7,
          waiting_time_before: 0,
          worker_name: "All Staging Workers",
          equipment_name: "All Staging Areas"
        },
        {
          stage: "SHIP",
          start_time: "11:22",
          end_time: "11:35",
          duration_minutes: 13,
          waiting_time_before: 0,
          worker_name: "All Shipping Workers",
          equipment_name: "All Dock Doors"
        }
      ],
      total_processing_time_original: 315,
      total_processing_time_optimized: 215,
      total_waiting_time_original: 75,
      total_waiting_time_optimized: 0,
      time_savings: 100,
      waiting_time_reduction: 75
    },
    '1': {
      order_id: 1,
      customer_name: "Acme Corp",
      priority: 1,
      original_timeline: [
        {
          stage: "PICK",
          start_time: "08:00",
          end_time: "08:15",
          duration_minutes: 15,
          waiting_time_before: 0,
          worker_name: "Sarah",
          equipment_name: "Pick Cart A"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "08:25",
          end_time: "08:30",
          duration_minutes: 5,
          waiting_time_before: 10,
          worker_name: "Mike",
          equipment_name: "Conveyor 1"
        },
        {
          stage: "PACK",
          start_time: "08:45",
          end_time: "08:55",
          duration_minutes: 10,
          waiting_time_before: 15,
          worker_name: "Lisa",
          equipment_name: "Packing Station 2"
        },
        {
          stage: "LABEL",
          start_time: "09:05",
          end_time: "09:08",
          duration_minutes: 3,
          waiting_time_before: 10,
          worker_name: "Tom",
          equipment_name: "Label Printer 1"
        },
        {
          stage: "STAGE",
          start_time: "09:15",
          end_time: "09:18",
          duration_minutes: 3,
          waiting_time_before: 7,
          worker_name: "Alex",
          equipment_name: "Staging Area 3"
        },
        {
          stage: "SHIP",
          start_time: "09:25",
          end_time: "09:30",
          duration_minutes: 5,
          waiting_time_before: 7,
          worker_name: "Jenny",
          equipment_name: "Dock Door 2"
        }
      ],
      optimized_timeline: [
        {
          stage: "PICK",
          start_time: "08:00",
          end_time: "08:12",
          duration_minutes: 12,
          waiting_time_before: 0,
          worker_name: "Sarah",
          equipment_name: "Pick Cart A"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "08:12",
          end_time: "08:16",
          duration_minutes: 4,
          waiting_time_before: 0,
          worker_name: "Mike",
          equipment_name: "Conveyor 1"
        },
        {
          stage: "PACK",
          start_time: "08:16",
          end_time: "08:24",
          duration_minutes: 8,
          waiting_time_before: 0,
          worker_name: "Lisa",
          equipment_name: "Packing Station 2"
        },
        {
          stage: "LABEL",
          start_time: "08:24",
          end_time: "08:26",
          duration_minutes: 2,
          waiting_time_before: 0,
          worker_name: "Tom",
          equipment_name: "Label Printer 1"
        },
        {
          stage: "STAGE",
          start_time: "08:26",
          end_time: "08:28",
          duration_minutes: 2,
          waiting_time_before: 0,
          worker_name: "Alex",
          equipment_name: "Staging Area 3"
        },
        {
          stage: "SHIP",
          start_time: "08:28",
          end_time: "08:32",
          duration_minutes: 4,
          waiting_time_before: 0,
          worker_name: "Jenny",
          equipment_name: "Dock Door 2"
        }
      ],
      total_processing_time_original: 41,
      total_processing_time_optimized: 32,
      total_waiting_time_original: 49,
      total_waiting_time_optimized: 0,
      time_savings: 9,
      waiting_time_reduction: 49
    },
    '2': {
      order_id: 2,
      customer_name: "TechStart Inc",
      priority: 2,
      original_timeline: [
        {
          stage: "PICK",
          start_time: "08:30",
          end_time: "08:50",
          duration_minutes: 20,
          waiting_time_before: 0,
          worker_name: "David",
          equipment_name: "Pick Cart B"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "09:10",
          end_time: "09:18",
          duration_minutes: 8,
          waiting_time_before: 20,
          worker_name: "Rachel",
          equipment_name: "Conveyor 2"
        },
        {
          stage: "PACK",
          start_time: "09:35",
          end_time: "09:50",
          duration_minutes: 15,
          waiting_time_before: 17,
          worker_name: "Chris",
          equipment_name: "Packing Station 1"
        },
        {
          stage: "LABEL",
          start_time: "10:00",
          end_time: "10:05",
          duration_minutes: 5,
          waiting_time_before: 10,
          worker_name: "Emma",
          equipment_name: "Label Printer 2"
        },
        {
          stage: "STAGE",
          start_time: "10:15",
          end_time: "10:20",
          duration_minutes: 5,
          waiting_time_before: 10,
          worker_name: "Sam",
          equipment_name: "Staging Area 1"
        },
        {
          stage: "SHIP",
          start_time: "10:30",
          end_time: "10:38",
          duration_minutes: 8,
          waiting_time_before: 10,
          worker_name: "Jordan",
          equipment_name: "Dock Door 1"
        }
      ],
      optimized_timeline: [
        {
          stage: "PICK",
          start_time: "08:30",
          end_time: "08:45",
          duration_minutes: 15,
          waiting_time_before: 0,
          worker_name: "David",
          equipment_name: "Pick Cart B"
        },
        {
          stage: "CONSOLIDATE",
          start_time: "08:45",
          end_time: "08:51",
          duration_minutes: 6,
          waiting_time_before: 0,
          worker_name: "Rachel",
          equipment_name: "Conveyor 2"
        },
        {
          stage: "PACK",
          start_time: "08:51",
          end_time: "09:01",
          duration_minutes: 10,
          waiting_time_before: 0,
          worker_name: "Chris",
          equipment_name: "Packing Station 1"
        },
        {
          stage: "LABEL",
          start_time: "09:01",
          end_time: "09:03",
          duration_minutes: 2,
          waiting_time_before: 0,
          worker_name: "Emma",
          equipment_name: "Label Printer 2"
        },
        {
          stage: "STAGE",
          start_time: "09:03",
          end_time: "09:05",
          duration_minutes: 2,
          waiting_time_before: 0,
          worker_name: "Sam",
          equipment_name: "Staging Area 1"
        },
        {
          stage: "SHIP",
          start_time: "09:05",
          end_time: "09:10",
          duration_minutes: 5,
          waiting_time_before: 0,
          worker_name: "Jordan",
          equipment_name: "Dock Door 1"
        }
      ],
      total_processing_time_original: 61,
      total_processing_time_optimized: 40,
      total_waiting_time_original: 67,
      total_waiting_time_optimized: 0,
      time_savings: 21,
      waiting_time_reduction: 67
    }
  };

  const currentOrder = orderTimelines[selectedOrder];
  const isAggregateView = selectedOrder === 'aggregate';
  const stages = ["PICK", "CONSOLIDATE", "PACK", "LABEL", "STAGE", "SHIP"];
  const stageColors = {
    PICK: "#3498db",
    CONSOLIDATE: "#e74c3c", 
    PACK: "#f39c12",
    LABEL: "#9b59b6",
    STAGE: "#1abc9c",
    SHIP: "#34495e"
  };

  const formatTime = (timeStr: string) => {
    return timeStr;
  };

  const calculateTimePosition = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes;
    const startMinutes = 8 * 60; // 8:00 AM
    return ((totalMinutes - startMinutes) / (4 * 60)) * 100; // 4 hour window
  };

  return (
    <div className="stage-timeline">
      <div className="timeline-header">
        <h2>Multi-Stage Workflow Timeline</h2>
        <p>Compare original vs optimized stage timing and waiting periods</p>
      </div>

      {/* Order Selection */}
      <div className="order-selector">
        <label htmlFor="orderSelect">Select Order:</label>
        <select 
          id="orderSelect" 
          value={selectedOrder} 
          onChange={(e) => setSelectedOrder(e.target.value)}
        >
          {Object.keys(orderTimelines).map(orderId => (
            <option key={orderId} value={orderId}>
              {orderId === 'aggregate' ? 'Aggregate View' : orderId === '1' ? 'Order 1 - Acme Corp' : 'Order 2 - TechStart Inc'}
            </option>
          ))}
        </select>
      </div>

      {/* Order Info */}
      <div className="order-info">
        <h3>
          {isAggregateView ? (
            <>Wave Overview - All Orders</>
          ) : (
            <>Order {currentOrder.order_id} - {currentOrder.customer_name}</>
          )}
        </h3>
        <div className="order-metrics">
          {!isAggregateView && (
            <div className="metric">
              <span className="label">Priority:</span>
              <span className="value">{currentOrder.priority}</span>
            </div>
          )}
          <div className="metric">
            <span className="label">Processing Time Saved:</span>
            <span className="value positive">{currentOrder.time_savings} min</span>
          </div>
          <div className="metric">
            <span className="label">Waiting Time Eliminated:</span>
            <span className="value positive">{currentOrder.waiting_time_reduction} min</span>
          </div>
          {isAggregateView && (
            <div className="metric">
              <span className="label">Total Time Saved:</span>
              <span className="value positive">{currentOrder.time_savings + currentOrder.waiting_time_reduction} min</span>
            </div>
          )}
        </div>
        {isAggregateView && (
          <div className="aggregate-description">
            <p>
              This view shows the total time spent in each stage across all orders in the wave, 
              demonstrating how optimization eliminates bottlenecks and creates a smooth workflow.
            </p>
          </div>
        )}
      </div>

      {/* Stage Legend */}
      <div className="stage-legend">
        <h4>Stage Types:</h4>
        <div className="legend-items">
          {stages.map(stage => (
            <div key={stage} className="legend-item">
              <div 
                className="legend-color" 
                style={{ backgroundColor: stageColors[stage as keyof typeof stageColors] }}
              ></div>
              <span>{stage}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline Visualization */}
      <div className="timeline-container">
        {/* Comprehensive Flow Table with Icons */}
        <div className="flow-table-container">
          <h4>Workflow Timing Analysis</h4>
          <div className="flow-table">
            <table>
              {/* Stage Icons Header Row */}
              <thead>
                <tr className="stage-icons-row">
                  <th className="plan-header"></th>
                  {stages.map((stage, index) => (
                    <React.Fragment key={stage}>
                      <th className="stage-header">
                        <div className="stage-icon-container">
                          <div 
                            className="stage-icon"
                            style={{ backgroundColor: stageColors[stage as keyof typeof stageColors] }}
                          >
                            {stage === 'PICK' && '📦'}
                            {stage === 'CONSOLIDATE' && '🔄'}
                            {stage === 'PACK' && '📋'}
                            {stage === 'LABEL' && '🏷️'}
                            {stage === 'STAGE' && '📍'}
                            {stage === 'SHIP' && '🚚'}
                          </div>
                          <div className="stage-name">{stage}</div>
                        </div>
                      </th>
                      {index < stages.length - 1 && (
                        <th className="wait-header">
                          <div className="wait-label">Wait {index + 1}</div>
                        </th>
                      )}
                    </React.Fragment>
                  ))}
                  <th className="total-header">Total Time</th>
                </tr>
              </thead>
              
              {/* Data Rows */}
              <tbody>
                {/* Original WMS Plan Row */}
                <tr className="original-row">
                  <td className="plan-name">Original WMS Plan</td>
                  {stages.map((stage, index) => {
                    const originalStage = currentOrder.original_timeline.find(s => s.stage === stage);
                    const nextStage = stages[index + 1];
                    const nextOriginalStage = nextStage ? currentOrder.original_timeline.find(s => s.stage === nextStage) : null;
                    
                    return (
                      <React.Fragment key={stage}>
                        <td className="stage-time">
                          <div className="time-value">{originalStage?.duration_minutes || 0} min</div>
                          <div className="time-detail">{originalStage?.worker_name || ''}</div>
                        </td>
                        {index < stages.length - 1 && (
                          <td className="wait-time">
                            <div className="time-value">{nextOriginalStage?.waiting_time_before || 0} min</div>
                            <div className="time-detail">wait</div>
                          </td>
                        )}
                      </React.Fragment>
                    );
                  })}
                  <td className="total-time">
                    <strong>{currentOrder.total_processing_time_original + currentOrder.total_waiting_time_original} min</strong>
                  </td>
                </tr>

                {/* Optimized Plan Row */}
                <tr className="optimized-row">
                  <td className="plan-name">Optimized Plan</td>
                  {stages.map((stage, index) => {
                    const optimizedStage = currentOrder.optimized_timeline.find(s => s.stage === stage);
                    const nextStage = stages[index + 1];
                    const nextOptimizedStage = nextStage ? currentOrder.optimized_timeline.find(s => s.stage === nextStage) : null;
                    
                    return (
                      <React.Fragment key={stage}>
                        <td className="stage-time optimized">
                          <div className="time-value">{optimizedStage?.duration_minutes || 0} min</div>
                          <div className="time-detail">{optimizedStage?.worker_name || ''}</div>
                        </td>
                        {index < stages.length - 1 && (
                          <td className="wait-time optimized">
                            <div className="time-value">{nextOptimizedStage?.waiting_time_before || 0} min</div>
                            <div className="time-detail">wait</div>
                          </td>
                        )}
                      </React.Fragment>
                    );
                  })}
                  <td className="total-time optimized">
                    <strong>{currentOrder.total_processing_time_optimized + currentOrder.total_waiting_time_optimized} min</strong>
                  </td>
                </tr>

                {/* Change Row */}
                <tr className="change-row">
                  <td className="plan-name">Change</td>
                  {stages.map((stage, index) => {
                    const originalStage = currentOrder.original_timeline.find(s => s.stage === stage);
                    const optimizedStage = currentOrder.optimized_timeline.find(s => s.stage === stage);
                    const processingChange = (optimizedStage?.duration_minutes || 0) - (originalStage?.duration_minutes || 0);
                    
                    const nextStage = stages[index + 1];
                    const nextOriginalStage = nextStage ? currentOrder.original_timeline.find(s => s.stage === nextStage) : null;
                    const nextOptimizedStage = nextStage ? currentOrder.optimized_timeline.find(s => s.stage === nextStage) : null;
                    const waitingChange = (nextOptimizedStage?.waiting_time_before || 0) - (nextOriginalStage?.waiting_time_before || 0);
                    
                    return (
                      <React.Fragment key={stage}>
                        <td className={`stage-time change ${processingChange < 0 ? 'positive' : processingChange > 0 ? 'negative' : ''}`}>
                          <div className="time-value">
                            {processingChange > 0 ? '+' : ''}{processingChange} min
                          </div>
                          <div className="time-detail">change</div>
                        </td>
                        {index < stages.length - 1 && (
                          <td className={`wait-time change ${waitingChange < 0 ? 'positive' : waitingChange > 0 ? 'negative' : ''}`}>
                            <div className="time-value">
                              {waitingChange > 0 ? '+' : ''}{waitingChange} min
                            </div>
                            <div className="time-detail">change</div>
                          </td>
                        )}
                      </React.Fragment>
                    );
                  })}
                  <td className="total-time change positive">
                    <strong>-{currentOrder.time_savings + currentOrder.waiting_time_reduction} min</strong>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StageTimeline; 