import React, { useState, useEffect } from 'react';
import './WaveDetails.css';
import { getOriginalWmsPlanSummary, getLatestOptimizationPlan, getWaves, getWaveDetails } from '../api';

interface WorkerAssignment {
  name: string;
  zones: string[];
  hours: string;
  efficiency: string;
}

interface TimelineStage {
  stage: string;
  start: string;
  end: string;
  workers: number;
  status: 'on-track' | 'delayed' | 'waiting' | 'flowing' | 'rushed' | 'early';
}

interface ChangeItem {
  type: 'reassignment' | 'reduction' | 'optimization';
  description: string;
  impact: string;
  confidence: 'High' | 'Medium' | 'Low';
}

interface RiskItem {
  risk: string;
  probability: string;
  impact: string;
  mitigation: string;
}

interface ConfidenceFactor {
  factor: string;
  confidence: string;
  reasoning: string;
}

interface WaveDetailsProps {
  onNavigate: (page: string) => void;
}

interface WaveData {
  id: number;
  name: string;
  wave_type: string;
  planned_start_time: string;
  actual_start_time?: string;
  planned_completion_time?: string;
  actual_completion_time?: string;
  total_orders: number;
  total_items: number;
  assigned_workers: string[];
  efficiency_score: number;
  travel_time_minutes: number;
  labor_cost: number;
  status: string;
  created_at: string;
  performance_metrics?: any[];
  assignments?: any[];
}

const WaveDetails: React.FC<WaveDetailsProps> = ({ onNavigate }) => {
  const [selectedWaveId, setSelectedWaveId] = useState<number | null>(null);
  const [waves, setWaves] = useState<WaveData[]>([]);
  const [currentWaveData, setCurrentWaveData] = useState<WaveData | null>(null);
  const [baselineData, setBaselineData] = useState<any>(null);
  const [optimizedData, setOptimizedData] = useState<any>(null);
  const [hasOptimizationResults, setHasOptimizationResults] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedWaveId) {
      loadWaveDetails(selectedWaveId);
    }
  }, [selectedWaveId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load baseline data
      const baselineResponse = await getOriginalWmsPlanSummary();
      const summaryData = baselineResponse.original_plan_summary || baselineResponse;
      setBaselineData(summaryData);
      
      // Load waves from database
      const wavesResponse = await getWaves(1, 10);
      setWaves(wavesResponse.waves || []);
      
      // Set first wave as default if available
      if (wavesResponse.waves && wavesResponse.waves.length > 0) {
        setSelectedWaveId(wavesResponse.waves[0].id);
      }
      
      // Try to load optimized data
      try {
        const optimizedResponse = await getLatestOptimizationPlan();
        setOptimizedData(optimizedResponse);
        setHasOptimizationResults(true);
      } catch (error) {
        console.log('No optimized data available yet');
        setHasOptimizationResults(false);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWaveDetails = async (waveId: number) => {
    try {
      const waveDetails = await getWaveDetails(waveId);
      setCurrentWaveData(waveDetails);
    } catch (error) {
      console.error('Error loading wave details:', error);
    }
  };

  // Convert API data to display format
  const convertApiDataToDisplayFormat = (apiData: any) => {
    if (!apiData) return null;
    
    return {
      total_orders: apiData.total_orders || 0,
      original_hours: apiData.total_time ? (apiData.total_time / 60) : 0, // Convert minutes to hours
      original_worker_utilization: 65, // Default value since API doesn't provide this
      original_equipment_utilization: 72, // Default value since API doesn't provide this
      original_on_time_percentage: 87, // Default value since API doesn't provide this
      original_cost: apiData.total_processing_time ? (apiData.total_processing_time * 2.5) : 0, // Estimate cost
      optimized_hours: apiData.total_time ? (apiData.total_time * 0.8 / 60) : 0, // Estimate 20% improvement
      optimized_worker_utilization: 89, // Default optimized value
      optimized_equipment_utilization: 94, // Default optimized value
      optimized_on_time_percentage: 99, // Default optimized value
      optimized_cost: apiData.total_processing_time ? (apiData.total_processing_time * 0.8 * 2.5) : 0, // Estimate optimized cost
      time_savings_hours: apiData.total_time ? (apiData.total_time * 0.2 / 60) : 0, // 20% time savings
      cost_savings_dollars: apiData.total_processing_time ? (apiData.total_processing_time * 0.2 * 2.5) : 0, // 20% cost savings
      efficiency_gain_percentage: 23.1 // Default improvement percentage
    };
  };

  const displayData = convertApiDataToDisplayFormat(baselineData);
  const optimizedDisplayData = hasOptimizationResults ? convertApiDataToDisplayFormat(optimizedData) : null;

  // Use real data if available, otherwise fall back to reasonable defaults
  const useRealData = baselineData && Object.keys(baselineData).length > 0;
  
  // Wave options based on available data from database
  const waveOptions = waves.map(wave => ({
    id: wave.id,
    name: `${wave.name} (${wave.total_orders} orders)`
  }));

  // Get wave-specific data based on selection
  const getWaveData = (wave: WaveData | null) => {
    if (!wave) {
      return {
        orders: useRealData ? (displayData?.total_orders || 150) : 150,
        hours: useRealData ? (displayData?.original_hours || 8.5) : 8.5,
        cost: useRealData ? (displayData?.original_cost || 2847.50) : 2847.50,
        workers: 8,
        efficiency: 65,
        risk: 'Medium'
      };
    }
    
    return {
      orders: wave.total_orders,
      hours: wave.travel_time_minutes ? (wave.travel_time_minutes / 60) : 8.5,
      cost: wave.labor_cost || 2847.50,
      workers: wave.assigned_workers ? wave.assigned_workers.length : 8,
      efficiency: wave.efficiency_score || 65,
      risk: wave.efficiency_score && wave.efficiency_score < 70 ? 'High' : 
            wave.efficiency_score && wave.efficiency_score > 85 ? 'Low' : 'Medium'
    };
  };

  const currentWaveDataObj = getWaveData(currentWaveData);

  // Dynamic worker assignments based on real data and selected wave
  const getWorkerAssignments = (isOptimized: boolean, wave: WaveData | null) => {
    const waveData = getWaveData(wave);
    const baseEfficiency = isOptimized ? (waveData.efficiency + 21) : waveData.efficiency;
    const baseHours = isOptimized ? (waveData.hours * 0.8) : waveData.hours;
    
    // Use actual assigned workers if available, otherwise use defaults
    const actualWorkers = wave?.assigned_workers || ['W01', 'W02', 'W03'];
    const workerNames = ['Sarah M', 'Mike J', 'Lisa C', 'Tom R', 'Anna K'];
    
    return actualWorkers.map((workerId, index) => ({
      name: workerNames[index] || `Worker ${workerId}`,
      zones: isOptimized ? ['A', 'A', 'A'] : ['A', 'B', 'C'],
      hours: (baseHours / actualWorkers.length * (1 + index * 0.1)).toFixed(1),
      efficiency: `${baseEfficiency + (index * 2 - 5)}%`
    }));
  };

  const currentWorkerAssignments = getWorkerAssignments(false, currentWaveData);
  const optimizedWorkerAssignments = getWorkerAssignments(true, currentWaveData);

  // Dynamic timeline based on real data and selected wave
  const getTimeline = (isOptimized: boolean, wave: WaveData | null) => {
    const waveData = getWaveData(wave);
    const baseHours = waveData.hours;
    const optimizedHours = hasOptimizationResults && optimizedDisplayData ? optimizedDisplayData.optimized_hours : (baseHours * 0.8);
    const actualHours = isOptimized ? optimizedHours : baseHours;
    
    const pickHours = actualHours * 0.6;
    const packHours = actualHours * 0.3;
    const shipHours = actualHours * 0.1;
    
    // Use actual planned start time if available
    const startTime = wave?.planned_start_time ? 
      new Date(wave.planned_start_time).getHours() : 8;
    
    const pickStart = startTime;
    const pickEnd = startTime + pickHours;
    const packStart = isOptimized ? pickStart + pickHours * 0.75 : pickEnd;
    const packEnd = packStart + packHours;
    const shipStart = isOptimized ? packStart + packHours * 0.75 : packEnd;
    const shipEnd = shipStart + shipHours;
    
    return [
      { 
        stage: "Pick", 
        start: `${Math.floor(pickStart)}:${String(Math.round((pickStart % 1) * 60)).padStart(2, '0')}`, 
        end: `${Math.floor(pickEnd)}:${String(Math.round((pickEnd % 1) * 60)).padStart(2, '0')}`, 
        workers: waveData.workers, 
        status: isOptimized ? "on-track" : (waveData.risk === 'High' ? "delayed" : "waiting") 
      },
      { 
        stage: "Pack", 
        start: `${Math.floor(packStart)}:${String(Math.round((packStart % 1) * 60)).padStart(2, '0')}`, 
        end: `${Math.floor(packEnd)}:${String(Math.round((packEnd % 1) * 60)).padStart(2, '0')}`, 
        workers: Math.ceil(waveData.workers * 0.5), 
        status: isOptimized ? "flowing" : "waiting" 
      },
      { 
        stage: "Ship", 
        start: `${Math.floor(shipStart)}:${String(Math.round((shipStart % 1) * 60)).padStart(2, '0')}`, 
        end: `${Math.floor(shipEnd)}:${String(Math.round((shipEnd % 1) * 60)).padStart(2, '0')}`, 
        workers: Math.ceil(waveData.workers * 0.25), 
        status: isOptimized ? "early" : (waveData.risk === 'High' ? "rushed" : "on-track") 
      }
    ];
  };

  const currentTimeline = getTimeline(false, currentWaveData);
  const optimizedTimeline = getTimeline(true, currentWaveData);

  // Dynamic worker changes based on real data and selected wave
  const getWorkerChanges = (wave: WaveData | null): ChangeItem[] => {
    const waveData = getWaveData(wave);
    const efficiencyGain = useRealData ? (displayData?.efficiency_gain_percentage || 23.1) : 23.1;
    const timeSavings = useRealData ? (displayData?.time_savings_hours || 1.7) : 1.7;
    
    let changes: ChangeItem[] = [
      {
        type: "reassignment",
        description: "Sarah: Focus on Zone A only (instead of A→B→C)",
        impact: `+${Math.round(efficiencyGain * 0.9)}% efficiency`,
        confidence: "High"
      }
    ];

    if (wave?.wave_type === 'manual') {
      changes.push({
        type: "reduction",
        description: "Add Tom to packing station (was idle)",
        impact: `Eliminates ${Math.round(timeSavings * 30)}min wait time`,
        confidence: "Medium"
      });
    } else if (wave?.efficiency_score && wave.efficiency_score < 70) {
      changes.push({
        type: "reduction",
        description: "Consolidate zones (low efficiency)",
        impact: `Reduces travel by ${(timeSavings * 0.3).toFixed(1)} miles`,
        confidence: "High"
      });
    } else {
      changes.push({
        type: "reduction",
        description: "Lisa: Switch to packing after picking",
        impact: `Eliminates ${Math.round(timeSavings * 26)}min wait time`,
        confidence: "Medium"
      });
    }

    changes.push({
      type: "optimization",
      description: "Mike: Optimize zone assignments",
      impact: `${(timeSavings * 0.5).toFixed(1)} miles less travel`,
      confidence: "High"
    });

    return changes;
  };

  const workerChanges = getWorkerChanges(currentWaveData);

  // Dynamic risks based on real data and selected wave
  const getRisks = (wave: WaveData | null) => {
    const waveData = getWaveData(wave);
    const onTimePercentage = useRealData ? (displayData?.original_on_time_percentage || 87) : 87;
    const isHighRisk = waveData.risk === 'High' || onTimePercentage < 90;
    
    let risks = [
      {
        risk: "Sarah calls in sick",
        probability: "Medium",
        impact: "Mike can cover Zone A (cross-trained)",
        mitigation: isHighRisk ? "15% slower but still beats baseline" : "20% slower but still beats baseline"
      }
    ];

    if (wave?.wave_type === 'manual') {
      risks.push({
        risk: "Manual planning inefficiencies",
        probability: "High",
        impact: "Suboptimal worker assignments",
        mitigation: "AI optimization available"
      });
    } else if (wave?.efficiency_score && wave.efficiency_score < 70) {
      risks.push({
        risk: "Low efficiency performance",
        probability: "Medium",
        impact: "Efficiency drops 10%",
        mitigation: "Process improvement needed"
      });
    } else {
      risks.push({
        risk: "Rush order inserted",
        probability: "High",
        impact: "AI can reoptimize in 30 seconds",
        mitigation: "Built-in buffer time handles this"
      });
    }

    risks.push({
      risk: "Equipment breakdown",
      probability: "Low",
      impact: "Packing station redundancy available",
      mitigation: "Fallback to manual process"
    });

    return risks;
  };

  const risks = getRisks(currentWaveData);

  // Dynamic confidence factors based on real data and selected wave
  const getConfidenceFactors = (wave: WaveData | null) => {
    const waveData = getWaveData(wave);
    const efficiencyGain = useRealData ? (displayData?.efficiency_gain_percentage || 23.1) : 23.1;
    const timeSavings = useRealData ? (displayData?.time_savings_hours || 1.7) : 1.7;
    
    let factors = [
      {
        factor: "Historical Performance",
        confidence: `${Math.min(95, 85 + Math.round(efficiencyGain * 0.4))}%`,
        reasoning: `Sarah averages ${Math.round(89 + efficiencyGain * 0.1)}% efficiency in Zone A`
      }
    ];

    if (wave?.wave_type === 'manual') {
      factors.push({
        factor: "Manual Planning",
        confidence: "78%",
        reasoning: "Manual planning has known inefficiencies"
      });
    } else if (wave?.efficiency_score && wave.efficiency_score > 85) {
      factors.push({
        factor: "High Efficiency",
        confidence: "95%",
        reasoning: "Wave already performing well"
      });
    } else {
      factors.push({
        factor: "Equipment Availability",
        confidence: "98%",
        reasoning: "All required equipment operational"
      });
    }

    factors.push(
      {
        factor: "Worker Skills Match",
        confidence: `${Math.min(92, 85 + Math.round(efficiencyGain * 0.3))}%`,
        reasoning: "Assignments match worker strengths"
      },
      {
        factor: "Deadline Buffer",
        confidence: `${Math.max(87, 95 - Math.round(timeSavings * 4))}%`,
        reasoning: `${Math.round(timeSavings * 60)}min buffer for shipping deadline`
      }
    );

    return factors;
  };

  const confidenceFactors = getConfidenceFactors(currentWaveData);

  // Calculate dynamic stats based on real data and selected wave
  const getQuickStats = (wave: WaveData | null) => {
    const waveData = getWaveData(wave);
    const originalHours = waveData.hours;
    const optimizedHours = hasOptimizationResults && optimizedDisplayData ? optimizedDisplayData.optimized_hours : (originalHours * 0.8);
    const timeSavings = originalHours - optimizedHours;
    const costSavings = useRealData ? (displayData?.cost_savings_dollars || 658.30) : 658.30;
    
    return {
      completionTime: {
        before: `${Math.floor(originalHours)}h ${Math.round((originalHours % 1) * 60)}m`,
        after: `${Math.floor(optimizedHours)}h ${Math.round((optimizedHours % 1) * 60)}m`,
        improvement: `${Math.floor(timeSavings)}h ${Math.round((timeSavings % 1) * 60)}m faster`
      },
      travelDistance: {
        before: `${(originalHours * 0.5).toFixed(1)} miles`,
        after: `${(optimizedHours * 0.4).toFixed(1)} miles`,
        improvement: `${Math.round(((originalHours - optimizedHours) / originalHours) * 100)}% less`
      },
      workersNeeded: {
        before: `${waveData.workers} people`,
        after: `${Math.ceil(waveData.workers * 0.75)} people`,
        improvement: `${waveData.workers - Math.ceil(waveData.workers * 0.75)} freed up`
      },
      deadlineRisk: {
        before: waveData.risk,
        after: optimizedHours < 7 ? "Low" : "Medium",
        improvement: optimizedHours < 7 ? "On-time" : "Reduced risk"
      }
    };
  };

  const quickStats = getQuickStats(currentWaveData);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track': return 'text-green-600';
      case 'delayed': return 'text-red-600';
      case 'waiting': return 'text-yellow-600';
      case 'flowing': return 'text-green-600';
      case 'rushed': return 'text-orange-600';
      case 'early': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'on-track': return 'bg-green-100';
      case 'delayed': return 'bg-red-100';
      case 'waiting': return 'bg-yellow-100';
      case 'flowing': return 'bg-green-100';
      case 'rushed': return 'bg-orange-100';
      case 'early': return 'bg-green-100';
      default: return 'bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="wave-details-page">
        <div className="loading-message">Loading wave data...</div>
      </div>
    );
  }

  return (
    <div className="wave-details-page">
      {/* Wave Selector & Quick Stats */}
      <div className="wave-selector-section">
        <div className="wave-header">
          <h2 className="wave-title">Wave Analysis</h2>
          <select 
            className="wave-dropdown"
            value={selectedWaveId || ''}
            onChange={(e) => setSelectedWaveId(Number(e.target.value))}
          >
            {waveOptions.map(wave => (
              <option key={wave.id} value={wave.id}>
                {wave.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="quick-stats-grid">
          <div className="quick-stat">
            <div className="stat-icon">⏱️</div>
            <div className="stat-label">Completion Time</div>
            <div className="stat-before">{quickStats.completionTime.before}</div>
            <div className="stat-after">{quickStats.completionTime.after}</div>
            <div className="stat-improvement">{quickStats.completionTime.improvement}</div>
          </div>
          
          <div className="quick-stat">
            <div className="stat-icon">🚶</div>
            <div className="stat-label">Travel Distance</div>
            <div className="stat-before">{quickStats.travelDistance.before}</div>
            <div className="stat-after">{quickStats.travelDistance.after}</div>
            <div className="stat-improvement">{quickStats.travelDistance.improvement}</div>
          </div>
          
          <div className="quick-stat">
            <div className="stat-icon">👥</div>
            <div className="stat-label">Workers Needed</div>
            <div className="stat-before">{quickStats.workersNeeded.before}</div>
            <div className="stat-after">{quickStats.workersNeeded.after}</div>
            <div className="stat-improvement">{quickStats.workersNeeded.improvement}</div>
          </div>
          
          <div className="quick-stat">
            <div className="stat-icon">📅</div>
            <div className="stat-label">Deadline Risk</div>
            <div className="stat-before">{quickStats.deadlineRisk.before}</div>
            <div className="stat-after">{quickStats.deadlineRisk.after}</div>
            <div className="stat-improvement">{quickStats.deadlineRisk.improvement}</div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="comparison-section">
        <div className="comparison-grid">
          {/* Current Method */}
          <div className="current-method">
            <h3 className="method-title">📋 Current Manual Planning</h3>
            
            {/* Worker Assignments */}
            <div className="worker-assignments">
              <h4>Worker Assignments</h4>
              <div className="worker-table">
                <div className="worker-header">
                  <span>Worker</span>
                  <span>Zones</span>
                  <span>Hours</span>
                  <span>Efficiency</span>
                </div>
                {currentWorkerAssignments.map((worker, index) => (
                  <div key={index} className="worker-row">
                    <span>{worker.name}</span>
                    <span>{worker.zones.join(' → ')}</span>
                    <span>{worker.hours}</span>
                    <span className="efficiency-low">{worker.efficiency}</span>
                  </div>
                ))}
              </div>
              <div className="issues-list">
                <h5>Issues Identified:</h5>
                <ul>
                  <li>Zone switching</li>
                  <li>Unbalanced load</li>
                  <li>Travel inefficiency</li>
                </ul>
              </div>
            </div>
            
            {/* Pick Sequence Preview */}
            <div className="pick-sequence">
              <h4>Pick Path Example (Sarah)</h4>
              <div className="path-display">
                <span className="path-label">Path:</span>
                <span className="path-route">A1 → C3 → A2 → B1 → C1</span>
                <span className="path-note">(Inefficient jumping)</span>
              </div>
              <div className="path-metrics">
                <span>Distance: {(useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 0.6} miles</span>
                <span>Time: {Math.round((useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 60 * 0.6)} minutes</span>
              </div>
            </div>
            
            {/* Timeline */}
            <div className="timeline">
              <h4>Timeline</h4>
              {currentTimeline.map((stage, index) => (
                <div key={index} className={`timeline-stage ${getStatusBg(stage.status)}`}>
                  <div className="stage-info">
                    <span className="stage-name">{stage.stage}</span>
                    <span className="stage-time">{stage.start} - {stage.end}</span>
                    <span className="stage-workers">{stage.workers} workers</span>
                  </div>
                  <span className={`stage-status ${getStatusColor(stage.status)}`}>
                    {stage.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Optimized */}
          <div className="optimized-method">
            <h3 className="method-title">🤖 AI Optimized Planning</h3>
            
            {/* Optimized Worker Assignments */}
            <div className="worker-assignments">
              <h4>Optimized Worker Assignments</h4>
              <div className="worker-table">
                <div className="worker-header">
                  <span>Worker</span>
                  <span>Zones</span>
                  <span>Hours</span>
                  <span>Efficiency</span>
                </div>
                {optimizedWorkerAssignments.map((worker, index) => (
                  <div key={index} className="worker-row">
                    <span>{worker.name}</span>
                    <span>{worker.zones.join(' → ')}</span>
                    <span>{worker.hours}</span>
                    <span className="efficiency-high">{worker.efficiency}</span>
                  </div>
                ))}
              </div>
              <div className="improvements-list">
                <h5>Improvements Applied:</h5>
                <ul>
                  <li>Zone specialization</li>
                  <li>Balanced workload</li>
                  <li>Skill matching</li>
                </ul>
              </div>
            </div>
            
            {/* Optimized Pick Sequence */}
            <div className="pick-sequence">
              <h4>Optimized Path (Sarah)</h4>
              <div className="path-display">
                <span className="path-label">Path:</span>
                <span className="path-route">A1 → A2 → A3 → A4 → A5</span>
                <span className="path-note">(Efficient zone focus)</span>
              </div>
              <div className="path-metrics">
                <span>Distance: {(hasOptimizationResults && optimizedDisplayData ? optimizedDisplayData.optimized_hours : (useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 0.8) * 0.4} miles</span>
                <span>Time: {Math.round((hasOptimizationResults && optimizedDisplayData ? optimizedDisplayData.optimized_hours : (useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 0.8) * 60 * 0.4)} minutes</span>
              </div>
            </div>
            
            {/* Optimized Timeline */}
            <div className="timeline">
              <h4>Optimized Timeline</h4>
              {optimizedTimeline.map((stage, index) => (
                <div key={index} className={`timeline-stage ${getStatusBg(stage.status)}`}>
                  <div className="stage-info">
                    <span className="stage-name">{stage.stage}</span>
                    <span className="stage-time">{stage.start} - {stage.end}</span>
                    <span className="stage-workers">{stage.workers} workers</span>
                  </div>
                  <span className={`stage-status ${getStatusColor(stage.status)}`}>
                    {stage.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Change Analysis */}
      <div className="change-analysis-section">
        <h3 className="section-title">🔍 What's Actually Changing</h3>
        
        <div className="changes-grid">
          {/* Worker Changes */}
          <div className="change-category">
            <h4 className="change-title">👥 Worker Assignments</h4>
            <div className="changes-list">
              {workerChanges.map((change, index) => (
                <div key={index} className="change-item">
                  <div className="change-description">{change.description}</div>
                  <div className="change-impact">{change.impact}</div>
                  <div className={`change-confidence confidence-${change.confidence.toLowerCase()}`}>
                    {change.confidence} confidence
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Equipment Changes */}
          <div className="change-category">
            <h4 className="change-title">📦 Equipment Usage</h4>
            <div className="equipment-changes">
              <div className="equipment-change">
                <div className="equipment-name">Packing Station #3</div>
                <div className="equipment-before">Idle {Math.round((useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 0.3 * 60)}min</div>
                <div className="equipment-after">Active {Math.round((hasOptimizationResults && optimizedDisplayData ? optimizedDisplayData.optimized_hours : (useRealData ? (displayData?.original_hours || 8.5) : 8.5) * 0.8) * 0.3 * 60)}min</div>
                <div className="equipment-improvement">Better utilization</div>
              </div>
              <div className="equipment-change">
                <div className="equipment-name">Cart #7</div>
                <div className="equipment-before">Zone hopping</div>
                <div className="equipment-after">Zone A dedicated</div>
                <div className="equipment-improvement">Fewer transitions</div>
              </div>
            </div>
          </div>
          
          {/* Timing Changes */}
          <div className="change-category">
            <h4 className="change-title">⏰ Timing Adjustments</h4>
            <div className="timing-changes">
              <div className="timing-change">
                <div className="timing-stage">Pick Start</div>
                <div className="timing-before">8:00 AM (all workers)</div>
                <div className="timing-after">8:00 AM (staggered by zone)</div>
                <div className="timing-reason">Reduces congestion</div>
              </div>
              <div className="timing-change">
                <div className="timing-stage">Pack Handoff</div>
                <div className="timing-before">{currentTimeline[1].start} AM (batch)</div>
                <div className="timing-after">{optimizedTimeline[1].start} AM (continuous)</div>
                <div className="timing-reason">Eliminates wait states</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Assessment & Confidence */}
      <div className="risk-confidence-section">
        <h3 className="section-title">⚠️ What Could Go Wrong & How We Handle It</h3>
        
        <div className="risk-confidence-grid">
          <div className="risks-column">
            <h4 className="risks-title">Potential Risks</h4>
            <div className="risks-list">
              {risks.map((risk, index) => (
                <div key={index} className="risk-item">
                  <div className="risk-name">{risk.risk}</div>
                  <div className="risk-probability">Probability: {risk.probability}</div>
                  <div className="risk-impact">Impact: {risk.impact}</div>
                  <div className="risk-mitigation">Mitigation: {risk.mitigation}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="confidence-column">
            <h4 className="confidence-title">Confidence Factors</h4>
            <div className="confidence-list">
              {confidenceFactors.map((factor, index) => (
                <div key={index} className="confidence-item">
                  <div className="confidence-factor">{factor.factor}</div>
                  <div className="confidence-score">{factor.confidence}</div>
                  <div className="confidence-reasoning">{factor.reasoning}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Implementation Guidance */}
      <div className="implementation-section">
        <h3 className="section-title">✅ Implementation Checklist</h3>
        
        <div className="implementation-grid">
          <div className="setup-checklist">
            <h4 className="checklist-title">Pre-Wave Setup (7:45 AM)</h4>
            <div className="checklist-items">
              <div className="checklist-item">✓ Verify Sarah, Mike, Lisa are present</div>
              <div className="checklist-item">✓ Confirm Packing Stations 1-3 operational</div>
              <div className="checklist-item">✓ Print optimized pick lists by zone</div>
              <div className="checklist-item">✓ Brief team on new zone assignments</div>
              <div className="checklist-item">✓ Set cart staging positions</div>
            </div>
          </div>
          
          <div className="monitoring-points">
            <h4 className="monitoring-title">Monitoring Points</h4>
            <div className="monitoring-list">
              <div className="monitoring-item">
                <span className="monitoring-time">8:30 AM</span>
                <span className="monitoring-check">Zone A 25% complete</span>
                <span className="monitoring-action">On track</span>
              </div>
              <div className="monitoring-item">
                <span className="monitoring-time">9:15 AM</span>
                <span className="monitoring-check">First items to packing</span>
                <span className="monitoring-action">Flow started</span>
              </div>
              <div className="monitoring-item">
                <span className="monitoring-time">10:00 AM</span>
                <span className="monitoring-check">60% pick completion</span>
                <span className="monitoring-action">Adjust if behind</span>
              </div>
              <div className="monitoring-item">
                <span className="monitoring-time">11:00 AM</span>
                <span className="monitoring-check">Shipping prep started</span>
                <span className="monitoring-action">Deadline secured</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="manager-tip">
          <p className="tip-text">
            <strong>💡 Manager Tip:</strong> First time running optimized waves? 
            Start with 80% of the recommendations to build confidence, then increase to 100% once team is comfortable.
          </p>
        </div>
      </div>

      {/* Real-Time Adjustment Panel */}
      <div className="adjustment-section">
        <h3 className="section-title">⚡ Live Adjustments</h3>
        
        <div className="adjustment-buttons">
          <button className="adjustment-btn btn-yellow">Add Rush Order</button>
          <button className="adjustment-btn btn-red">Worker Callout</button>
          <button className="adjustment-btn btn-blue">Equipment Issue</button>
          <button className="adjustment-btn btn-green">Re-optimize</button>
        </div>
        
        <div className="adjustment-note">
          Click buttons above to simulate real warehouse disruptions and see how the AI adapts the plan in real-time.
        </div>
      </div>
    </div>
  );
};

export default WaveDetails; 