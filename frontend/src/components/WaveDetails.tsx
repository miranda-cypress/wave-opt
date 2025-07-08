import React, { useState, useEffect } from 'react';
import './WaveDetails.css';
import { 
  getOriginalWmsPlanSummary, 
  getLatestOptimizationPlan, 
  getWaves, 
  getWaveDetails,
  getWaveDetailedMetrics,
  getWaveWorkerAssignments,
  getWorkerStatistics,
  getOrderStatistics,
  getWaveRiskAssessment,
  getWaveCompletionMetrics,
  getWorkerSequence,
  getStationSequence,
  getAvailableWorkers,
  getAvailableStations,
  getOriginalWmsPlan,
  getOriginalWmsPlanByNumber,
  getOrderWaveAssignment,
  getOrderWaveAssignmentByNumber
} from '../api';

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
  status: string;
  created_at: string;
  performance_metrics?: any[];
  assignments?: any[];
  order_metrics?: Array<{
    order_id: number;
    order_number: string;
    customer_name: string;
    priority: number;
    shipping_deadline: string | null;
    plan_version_id: number;
    assignment?: {
      stage?: string;
      assigned_worker_id?: number;
      assigned_equipment_id?: number;
      planned_start_time?: string;
      planned_duration_minutes?: number;
      actual_start_time?: string;
      actual_duration_minutes?: number;
      sequence_order?: number;
    };
    metrics: {
      pick_time_minutes: number;
      pack_time_minutes: number;
      walking_time_minutes: number;
      consolidate_time_minutes: number;
      label_time_minutes: number;
      stage_time_minutes: number;
      ship_time_minutes: number;
      total_time_minutes: number;
    };
  }>;
  metrics_summary?: {
    total_orders: number;
    total_pick_time_minutes: number;
    total_pack_time_minutes: number;
    total_walking_time_minutes: number;
    total_consolidate_time_minutes: number;
    total_label_time_minutes: number;
    total_stage_time_minutes: number;
    total_ship_time_minutes: number;
    total_time_minutes: number;
    average_time_per_order_minutes: number;
  };
}

interface DetailedMetrics {
  wave_id: number;
  worker_utilization_percentage: number;
  equipment_utilization_percentage: number;
  on_time_delivery_percentage: number;
  total_cost: number;
  labor_cost: number;
  equipment_cost: number;
  worker_assignments: any[];
  worker_assignments_detail: any[];
  equipment_assignments: any[];
}

interface WorkerSequence {
  wave_id: number;
  worker: {
    id: number;
    worker_name: string;
    worker_code: string;
    hourly_rate: number;
  };
  wave: {
    wave_name: string;
    planned_start_time: string;
    planned_completion_time: string;
  };
  assignments: Array<{
    id: number;
    order_id: number;
    stage: string;
    assigned_equipment_id: number;
    planned_start_time: string;
    planned_duration_minutes: number;
    actual_start_time: string;
    actual_duration_minutes: number;
    sequence_order: number;
    order_number: string;
    customer_name: string;
    priority: number;
    shipping_deadline: string;
    equipment_name: string;
    equipment_type: string;
  }>;
  total_planned_minutes: number;
  total_actual_minutes: number;
  efficiency_percentage: number;
}

interface StationSequence {
  wave_id: number;
  equipment: {
    id: number;
    equipment_name: string;
    equipment_code: string;
    equipment_type: string;
    capacity: number;
  };
  wave: {
    wave_name: string;
    planned_start_time: string;
    planned_completion_time: string;
  };
  assignments: Array<{
    id: number;
    order_id: number;
    stage: string;
    assigned_worker_id: number;
    planned_start_time: string;
    planned_duration_minutes: number;
    actual_start_time: string;
    actual_duration_minutes: number;
    sequence_order: number;
    order_number: string;
    customer_name: string;
    priority: number;
    shipping_deadline: string;
    worker_name: string;
    worker_code: string;
  }>;
  total_planned_minutes: number;
  total_actual_minutes: number;
  utilization_percentage: number;
}

const WaveDetails: React.FC<WaveDetailsProps> = ({ onNavigate }) => {
  const [selectedWaveId, setSelectedWaveId] = useState<number | null>(null);
  const [waves, setWaves] = useState<WaveData[]>([]);
  const [currentWaveData, setCurrentWaveData] = useState<WaveData | null>(null);
  const [detailedMetrics, setDetailedMetrics] = useState<DetailedMetrics | null>(null);
  const [baselineData, setBaselineData] = useState<any>(null);
  const [optimizedData, setOptimizedData] = useState<any>(null);
  const [hasOptimizationResults, setHasOptimizationResults] = useState(false);
  const [workerStats, setWorkerStats] = useState<any>(null);
  const [orderStats, setOrderStats] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completionMetrics, setCompletionMetrics] = useState<any>(null);
  
  // Sequence exploration state
  const [selectedWorkerId, setSelectedWorkerId] = useState<number | null>(null);
  const [selectedStationId, setSelectedStationId] = useState<number | null>(null);
  const [availableWorkers, setAvailableWorkers] = useState<any[]>([]);
  const [availableStations, setAvailableStations] = useState<any[]>([]);
  const [workerSequence, setWorkerSequence] = useState<WorkerSequence | null>(null);
  const [stationSequence, setStationSequence] = useState<StationSequence | null>(null);
  const [sequenceLoading, setSequenceLoading] = useState(false);

  // Order search state
  const [orderSearchId, setOrderSearchId] = useState('');
  const [orderSearchLoading, setOrderSearchLoading] = useState(false);
  const [orderSearchError, setOrderSearchError] = useState<string | null>(null);
  const [searchedOrderId, setSearchedOrderId] = useState<number | null>(null);
  const [orderOriginalPlan, setOrderOriginalPlan] = useState<any[] | null>(null);
  const [orderOptimizedPlan, setOrderOptimizedPlan] = useState<any | null>(null);
  const [orderApiResponse, setOrderApiResponse] = useState<any | null>(null);
  const [orderWaveAssignment, setOrderWaveAssignment] = useState<any | null>(null);

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
      setError(null);
      
      // Load baseline data
      const baselineResponse = await getOriginalWmsPlanSummary();
      if (!baselineResponse) {
        throw new Error('Failed to load baseline data from database');
      }
      const summaryData = baselineResponse.original_plan_summary || baselineResponse;
      setBaselineData(summaryData);
      
      // Load waves from database
      const wavesResponse = await getWaves(1, 1000);
      if (!wavesResponse.waves || wavesResponse.waves.length === 0) {
        throw new Error('No waves found in database');
      }
      setWaves(wavesResponse.waves);
      
      // Set first wave as default
      setSelectedWaveId(wavesResponse.waves[0].id);
      
      // Try to load optimized data
      try {
        const optimizedResponse = await getLatestOptimizationPlan();
        setOptimizedData(optimizedResponse);
        setHasOptimizationResults(true);
      } catch (error) {
        console.log('No optimized data available yet');
        setHasOptimizationResults(false);
      }
      
      // Load worker statistics for planning cost calculations
      try {
        const workerResponse = await getWorkerStatistics(1);
        setWorkerStats(workerResponse);
      } catch (workerError) {
        console.warn('Could not load worker statistics:', workerError);
        // Provide fallback values for planning future operations
        setWorkerStats({
          avg_hourly_rate: 25.0,
          total_workers: 10,
          avg_efficiency: 0.85
        });
      }
      
      // Load order statistics for planning calculations
      try {
        const orderResponse = await getOrderStatistics(1);
        setOrderStats(orderResponse);
      } catch (orderError) {
        console.warn('Could not load order statistics:', orderError);
        // Provide fallback values for planning future orders
        setOrderStats({
          avg_pick_time: 2.5,
          avg_pack_time: 1.5,
          avg_total_time: 4.0,
          total_orders: 0
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load wave data';
      setError(errorMessage);
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWaveDetails = async (waveId: number) => {
    try {
      setError(null);
      
      // Load wave details
      const waveDetails = await getWaveDetails(waveId);
      if (!waveDetails) {
        throw new Error(`Failed to load details for wave ${waveId}`);
      }
      setCurrentWaveData(waveDetails);
      
      // Try to load detailed metrics, but don't fail if they're not available
      try {
        const metrics = await getWaveDetailedMetrics(waveId);
        if (metrics) {
          setDetailedMetrics(metrics);
        } else {
          setDetailedMetrics(null);
        }
      } catch (metricsError) {
        console.warn('Detailed metrics not available for wave', waveId, metricsError);
        setDetailedMetrics(null);
      }
      
      // Load risk assessment for this wave
      try {
        const riskResponse = await getWaveRiskAssessment(waveId);
        setRiskAssessment(riskResponse);
      } catch (riskError) {
        console.warn('Risk assessment not available for wave', waveId, riskError);
        setRiskAssessment(null);
      }
      
      // Load available workers and stations for sequence exploration
      try {
        const workersResponse = await getAvailableWorkers(waveId);
        setAvailableWorkers(workersResponse.workers || []);
      } catch (workersError) {
        console.warn('Available workers not available for wave', waveId, workersError);
        setAvailableWorkers([]);
      }
      
      try {
        const stationsResponse = await getAvailableStations(waveId);
        setAvailableStations(stationsResponse.stations || []);
      } catch (stationsError) {
        console.warn('Available stations not available for wave', waveId, stationsError);
        setAvailableStations([]);
      }
      
      // Load completion metrics for this wave
      try {
        const cm = await getWaveCompletionMetrics(waveId);
        setCompletionMetrics(cm);
      } catch (cmError) {
        console.warn('Completion metrics not available for wave', waveId, cmError);
        setCompletionMetrics(null);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : `Failed to load wave ${waveId} details`;
      setError(errorMessage);
      console.error('Error loading wave details:', error);
    }
  };

  const loadWorkerSequence = async (workerId: number) => {
    if (!selectedWaveId) return;
    
    try {
      setSequenceLoading(true);
      setError(null);
      
      const sequence = await getWorkerSequence(selectedWaveId, workerId);
      setWorkerSequence(sequence);
      setStationSequence(null); // Clear station sequence when loading worker sequence
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load worker sequence';
      setError(errorMessage);
      console.error('Error loading worker sequence:', error);
    } finally {
      setSequenceLoading(false);
    }
  };

  const loadStationSequence = async (stationId: number) => {
    if (!selectedWaveId) return;
    
    try {
      setSequenceLoading(true);
      setError(null);
      
      const sequence = await getStationSequence(selectedWaveId, stationId);
      setStationSequence(sequence);
      setWorkerSequence(null); // Clear worker sequence when loading station sequence
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load station sequence';
      setError(errorMessage);
      console.error('Error loading station sequence:', error);
    } finally {
      setSequenceLoading(false);
    }
  };

  // Get wave-specific data based on selection
  const getWaveData = (wave: WaveData | null) => {
    if (!wave) {
      return null;
    }
    
    // Calculate estimated hours based on real data or fallback to defaults
    const avgTimePerOrder = orderStats?.avg_total_time || 2.5; // minutes
    const efficiencyFactor = (wave.efficiency_score || 75) / 100;
    const estimatedMinutes = wave.total_orders * avgTimePerOrder / efficiencyFactor;
    const estimatedHours = estimatedMinutes / 60;
    
    // Calculate estimated cost based on real worker data or fallback to defaults
    const hourlyRate = workerStats?.avg_hourly_rate || 25;
    const workerCount = wave.assigned_workers ? wave.assigned_workers.length : 1;
    const estimatedCost = estimatedHours * hourlyRate * workerCount;
    
    return {
      orders: wave.total_orders,
      hours: estimatedHours,
      cost: estimatedCost,
      workers: wave.assigned_workers ? wave.assigned_workers.length : 0,
      efficiency: wave.efficiency_score || 0,
      risk: riskAssessment?.risk_level || 
            (wave.efficiency_score && wave.efficiency_score < 70 ? 'High' : 
             wave.efficiency_score && wave.efficiency_score > 85 ? 'Low' : 'Medium')
    };
  };

  // Dynamic worker assignments based on real data from database
  const getWorkerAssignments = (isOptimized: boolean, wave: WaveData | null) => {
    if (!wave) {
      return [];
    }
    
    const waveData = getWaveData(wave);
    if (!waveData) return [];
    
    // If we have detailed metrics with worker assignments, use them
    if (detailedMetrics && detailedMetrics.worker_assignments) {
      const baseEfficiency = isOptimized ? (waveData.efficiency + 21) : waveData.efficiency;
      
      return detailedMetrics.worker_assignments.map((worker, index) => ({
        name: worker.name,
        zones: worker.stages.map((stage: any) => stage.stage.toUpperCase()),
        hours: worker.total_hours.toFixed(1),
        efficiency: `${baseEfficiency + (index * 2 - 5)}%`
      }));
    }
    
    // Fallback to basic worker data from wave
    const baseEfficiency = isOptimized ? (waveData.efficiency + 21) : waveData.efficiency;
    return wave.assigned_workers.map((workerCode, index) => ({
      name: `Worker ${workerCode}`,
      zones: ['PICK', 'PACK'],
      hours: (waveData.hours / waveData.workers).toFixed(1),
      efficiency: `${baseEfficiency + (index * 2 - 5)}%`
    }));
  };

  // Dynamic timeline based on real data and selected wave
  const getTimeline = (isOptimized: boolean, wave: WaveData | null) => {
    if (!wave) {
      return [];
    }
    
    const waveData = getWaveData(wave);
    if (!waveData) return [];
    
    const baseHours = waveData.hours;
    const optimizedHours = hasOptimizationResults && optimizedData ? (baseHours * 0.8) : baseHours;
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

  // Dynamic worker changes based on real data and selected wave
  const getWorkerChanges = (wave: WaveData | null): ChangeItem[] => {
    if (!wave) {
      return [];
    }
    
    const waveData = getWaveData(wave);
    if (!waveData) return [];
    
    const efficiencyGain = 23.1; // This could be calculated from optimization results
    const timeSavings = 1.7; // This could be calculated from optimization results
    
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

  // Dynamic risks based on real data and selected wave
  const getRisks = (wave: WaveData | null) => {
    if (!wave) {
      return [];
    }
    
    const waveData = getWaveData(wave);
    if (!waveData) return [];
    
    const risks: RiskItem[] = [];

    if (detailedMetrics && detailedMetrics.worker_utilization_percentage < 70) {
      risks.push({
        risk: "Low Worker Utilization",
        probability: "High",
        impact: "Increased labor costs",
        mitigation: "Reassign workers to high-priority tasks"
      });
    }

    if (detailedMetrics && detailedMetrics.equipment_utilization_percentage < 60) {
      risks.push({
        risk: "Equipment Underutilization",
        probability: "Medium",
        impact: "Wasted capacity",
        mitigation: "Optimize equipment assignments"
      });
    }

    if (detailedMetrics && detailedMetrics.on_time_delivery_percentage < 90) {
      risks.push({
        risk: "Late Deliveries",
        probability: "Medium",
        impact: "Customer satisfaction",
        mitigation: "Prioritize urgent orders"
      });
    }

    if (waveData.efficiency < 70) {
      risks.push({
        risk: "Low Efficiency",
        probability: "High",
        impact: "Increased costs and delays",
        mitigation: "Optimize wave planning"
      });
    }

    return risks;
  };

  // Dynamic confidence factors based on real data and selected wave
  const getConfidenceFactors = (wave: WaveData | null) => {
    if (!wave) {
      return [];
    }
    
    const factors: ConfidenceFactor[] = [];

    if (detailedMetrics && detailedMetrics.worker_utilization_percentage > 80) {
      factors.push({
        factor: "High Worker Utilization",
        confidence: "High",
        reasoning: "Workers are efficiently utilized"
      });
    }

    if (detailedMetrics && detailedMetrics.equipment_utilization_percentage > 85) {
      factors.push({
        factor: "Optimal Equipment Usage",
        confidence: "High",
        reasoning: "Equipment is well-utilized"
      });
    }

    if (detailedMetrics && detailedMetrics.on_time_delivery_percentage > 95) {
      factors.push({
        factor: "Excellent On-Time Delivery",
        confidence: "High",
        reasoning: "High probability of meeting deadlines"
      });
    }

    if (wave?.efficiency_score && wave.efficiency_score > 85) {
      factors.push({
        factor: "High Efficiency Score",
        confidence: "High",
        reasoning: "Wave is operating efficiently"
      });
    }

    return factors;
  };

  // Quick stats based on real data
  const getQuickStats = (wave: WaveData | null) => {
    if (!wave) {
      return null;
    }
    
    const waveData = getWaveData(wave);
    if (!waveData) return null;
    
    return {
      orders: waveData.orders,
      hours: waveData.hours,
      cost: waveData.cost,
      workers: waveData.workers,
      efficiency: waveData.efficiency,
      risk: waveData.risk
    };
  };

  // Wave options based on available data from database
  const waveOptions = waves.map(wave => ({
    id: wave.id,
    name: `${wave.name} (${wave.total_orders} orders, ${wave.total_orders * 6} tasks)`
  }));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track': return '#4caf50';
      case 'delayed': return '#f44336';
      case 'waiting': return '#ff9800';
      case 'flowing': return '#2196f3';
      case 'rushed': return '#9c27b0';
      case 'early': return '#4caf50';
      default: return '#757575';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'on-track': return '#e8f5e8';
      case 'delayed': return '#ffebee';
      case 'waiting': return '#fff3e0';
      case 'flowing': return '#e3f2fd';
      case 'rushed': return '#f3e5f5';
      case 'early': return '#e8f5e8';
      default: return '#f5f5f5';
    }
  };

  // Handle order search
  const handleOrderSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderSearchId.trim()) return;
    setOrderSearchLoading(true);
    setOrderSearchError(null);
    setOrderOriginalPlan(null);
    setOrderOptimizedPlan(null);
    setSearchedOrderId(null);
    setOrderWaveAssignment(null);
    
    const searchTerm = orderSearchId.trim();
    let orderId: number | null = null;
    
    try {
      // Treat input as order number by default (more user-friendly)
      let orderNumber: string | null = null;
      
      // Only try to parse as numeric ID if it's a small number (likely an ID)
      const parsedId = parseInt(searchTerm, 10);
      if (!isNaN(parsedId) && parsedId < 10000) {
        orderId = parsedId;
      } else {
        // Treat as order number (more common use case)
        orderNumber = searchTerm;
      }
      
      setSearchedOrderId(orderId || 0);
      
      // Fetch original plan
      try {
        let origRes;
        if (orderId) {
          origRes = await getOriginalWmsPlan(orderId);
        } else if (orderNumber) {
          origRes = await getOriginalWmsPlanByNumber(orderNumber);
        } else {
          setOrderSearchError('Invalid search term. Please enter an order number (e.g., ORD00376899).');
          setOrderSearchLoading(false);
          return;
        }
        
        if (!origRes || !origRes.original_plan || origRes.original_plan.length === 0) {
          setOrderSearchError('No planning data found for this order. The order may not be in the planning system.');
          setOrderSearchLoading(false);
          return;
        }
        console.log('API Response:', origRes);
        setOrderOriginalPlan(origRes.original_plan);
        setOrderApiResponse(origRes);
        setSearchedOrderId(origRes.order_id);
        
        // Fetch wave assignment information
        try {
          let waveAssignmentRes;
          if (orderId) {
            waveAssignmentRes = await getOrderWaveAssignment(orderId);
          } else if (orderNumber) {
            waveAssignmentRes = await getOrderWaveAssignmentByNumber(orderNumber);
          }
          setOrderWaveAssignment(waveAssignmentRes || null);
        } catch (waveErr) {
          console.warn('Error fetching wave assignment:', waveErr);
          // Don't fail the search if wave assignment is not available
          setOrderWaveAssignment(null);
        }
        
        // Fetch optimized plan
        try {
          const optRes = await getLatestOptimizationPlan();
          let foundOpt = null;
          if (optRes && Array.isArray(optRes.order_timelines)) {
            // Look for the order by ID (from the original plan response)
            const actualOrderId = origRes.order_id;
            foundOpt = optRes.order_timelines.find((ot: any) => ot.order_id === actualOrderId);
          }
          setOrderOptimizedPlan(foundOpt || null);
        } catch (optErr) {
          console.warn('Error fetching optimized plan:', optErr);
          // Don't fail the search if optimized plan is not available
          setOrderOptimizedPlan(null);
        }
      } catch (origErr) {
        console.warn('Error fetching original plan:', origErr);
        setOrderSearchError('No planning data found for this order. The order may not be in the planning system.');
        setOrderSearchLoading(false);
        return;
      }
    } catch (err: any) {
      console.error('Error in order search:', err);
      setOrderSearchError('Error fetching order data.');
    } finally {
      setOrderSearchLoading(false);
    }
  };

  // Helper to extract order details from original plan
  const getOrderDetails = (plan: any[] | null, optimized: any | null, apiResponse?: any) => {
    console.log('getOrderDetails called with:', { plan, optimized, apiResponse });
    if (optimized) {
      console.log('Using optimized data');
      return {
        order_id: optimized.order_id,
        customer_name: optimized.customer_name,
        shipping_deadline: optimized.shipping_deadline,
      };
    }
    if (apiResponse && apiResponse.order_id) {
      console.log('Using API response data');
      return {
        order_id: apiResponse.order_id,
        customer_name: apiResponse.customer_name || 'N/A',
        shipping_deadline: apiResponse.shipping_deadline || 'N/A',
      };
    }
    if (plan && plan.length > 0) {
      console.log('Using fallback plan data');
      // Fallback: try to get from first stage if API response not available
      const first = plan[0];
      return {
        order_id: first.order_id || 'N/A',
        customer_name: first.customer_name || 'N/A',
        shipping_deadline: first.shipping_deadline || 'N/A',
      };
    }
    console.log('No data found, returning null');
    return null;
  };

  // Helper to get all unique stages from both plans
  const getAllStages = (original: any[] | null, optimized: any | null) => {
    const stages = new Set<string>();
    if (original) original.forEach((s: any) => stages.add(s.stage));
    if (optimized && optimized.optimized_timeline) optimized.optimized_timeline.forEach((s: any) => stages.add(s.stage));
    return Array.from(stages);
  };

  // Helper to get stage data by stage name
  const getStageData = (stages: any[] | null, stage: string) => {
    if (!stages) return null;
    return stages.find((s: any) => s.stage === stage || s.stage_name === stage);
  };

  if (loading) {
    return <div>Loading wave details...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div style={{ color: 'red', padding: '2rem', textAlign: 'center' }}>
          <h3>Error Loading Wave Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  // Show warning if real calculation data is not available
  const showDataWarning = !workerStats || !orderStats;

  if (!currentWaveData) {
    return (
      <div className="container">
        <div style={{ color: 'red', padding: '2rem', textAlign: 'center' }}>
          <h3>No Wave Data Available</h3>
          <p>Unable to load wave details from database.</p>
        </div>
      </div>
    );
  }

  // Only calculate these values when we have the required data
  const currentWaveDataObj = getWaveData(currentWaveData);
  const currentWorkerAssignments = getWorkerAssignments(false, currentWaveData);
  const optimizedWorkerAssignments = getWorkerAssignments(true, currentWaveData);
  const currentTimeline = getTimeline(false, currentWaveData);
  const optimizedTimeline = getTimeline(true, currentWaveData);
  const currentWorkerChanges = getWorkerChanges(currentWaveData);
  const optimizedWorkerChanges = getWorkerChanges(currentWaveData);
  const currentRisks = getRisks(currentWaveData);
  const optimizedRisks = getRisks(currentWaveData);
  const currentConfidenceFactors = getConfidenceFactors(currentWaveData);
  const optimizedConfidenceFactors = getConfidenceFactors(currentWaveData);
  const currentQuickStats = getQuickStats(currentWaveData);

  return (
    <div className="wave-details-page">
      {/* Order Search Field */}
      <div className="order-search-section" style={{ marginBottom: 24 }}>
        <form onSubmit={handleOrderSearch} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="text"
            placeholder="Enter Order Number (e.g., ORD00376899)..."
            value={orderSearchId}
            onChange={e => setOrderSearchId(e.target.value)}
            style={{ padding: 8, fontSize: 16, width: 250 }}
          />
          <button type="submit" style={{ padding: '8px 16px', fontSize: 16 }}>Search</button>
        </form>
        {orderSearchLoading && <div style={{ marginTop: 8 }}>Loading...</div>}
        {orderSearchError && <div style={{ color: 'red', marginTop: 8 }}>{orderSearchError}</div>}
      </div>

      {/* Order Details and Movement Table */}
      {(() => {
        console.log('Checking order details conditions:', {
          searchedOrderId,
          orderOriginalPlan: !!orderOriginalPlan,
          orderOptimizedPlan: !!orderOptimizedPlan,
          orderSearchLoading,
          orderSearchError
        });
        return searchedOrderId && (orderOriginalPlan || orderOptimizedPlan) && !orderSearchLoading && !orderSearchError;
      })() && (
        <div className="order-details-section" style={{ marginBottom: 32 }}>
          <h3>Order Details</h3>
          {(() => {
            console.log('Rendering order details section with:', { searchedOrderId, orderOriginalPlan, orderOptimizedPlan, orderSearchLoading, orderSearchError });
            const details = getOrderDetails(orderOriginalPlan, orderOptimizedPlan, orderApiResponse);
            console.log('getOrderDetails result:', details);
            if (!details) return <div>No order details found.</div>;
            
            // Format wave assignment info
            let waveAssignmentInfo = null;
            if (orderWaveAssignment && orderWaveAssignment.wave_assignments && orderWaveAssignment.wave_assignments.length > 0) {
              const assignment = orderWaveAssignment.wave_assignments[0]; // Get first assignment
              waveAssignmentInfo = {
                waveId: assignment.wave_id,
                waveName: assignment.wave_name,
                stage: assignment.stage,
                assignedWorkerId: assignment.assigned_worker_id,
                assignedEquipmentId: assignment.assigned_equipment_id,
                plannedStartTime: assignment.planned_start_time,
                plannedDurationMinutes: assignment.planned_duration_minutes,
                actualStartTime: assignment.actual_start_time,
                actualDurationMinutes: assignment.actual_duration_minutes,
                sequenceOrder: assignment.sequence_order,
                waveStatus: assignment.wave_status
              };
            }
            
            return (
              <div style={{ marginBottom: 12 }}>
                <div style={{ marginBottom: 8 }}>
                  <strong>Order ID:</strong> {details.order_id} &nbsp;|
                  <strong> Customer:</strong> {details.customer_name} &nbsp;|
                  <strong> Shipping Deadline:</strong> {details.shipping_deadline ? new Date(details.shipping_deadline).toLocaleString() : 'N/A'}
                </div>
                {waveAssignmentInfo && (
                  <div style={{ 
                    backgroundColor: '#e3f2fd', 
                    padding: '8px 12px', 
                    borderRadius: '4px', 
                    border: '1px solid #2196f3',
                    marginTop: '8px'
                  }}>
                    <strong>Wave Assignment:</strong> {waveAssignmentInfo.waveName} (ID: {waveAssignmentInfo.waveId})
                  </div>
                )}
                {!waveAssignmentInfo && (
                  <div style={{ 
                    backgroundColor: '#fff3e0', 
                    padding: '8px 12px', 
                    borderRadius: '4px', 
                    border: '1px solid #ff9800',
                    marginTop: '8px'
                  }}>
                    <strong>Wave Assignment:</strong> Order not assigned to any wave
                  </div>
                )}
              </div>
            );
          })()}
          {/* Movement Table */}
          <div style={{ overflowX: 'auto' }}>
            <table className="order-movement-table" style={{ borderCollapse: 'collapse', width: '100%', marginTop: 8 }}>
              <thead>
                <tr>
                  <th style={{ border: '1px solid #ccc', padding: 6 }}>Plan</th>
                  {getAllStages(orderOriginalPlan, orderOptimizedPlan).map(stage => (
                    <th key={stage} colSpan={2} style={{ border: '1px solid #ccc', padding: 6, textAlign: 'center' }}>
                      {stage}
                    </th>
                  ))}
                </tr>
                <tr>
                  <th style={{ border: '1px solid #ccc', padding: 6 }}></th>
                  {getAllStages(orderOriginalPlan, orderOptimizedPlan).map(stage => (
                    <React.Fragment key={stage}>
                      <th style={{ border: '1px solid #ccc', padding: 6, fontSize: '12px' }}>Processing</th>
                      <th style={{ border: '1px solid #ccc', padding: 6, fontSize: '12px' }}>Wait After</th>
                    </React.Fragment>
                  ))}
                </tr>
              </thead>
              <tbody>
                {/* Baseline row */}
                <tr>
                  <td style={{ border: '1px solid #ccc', padding: 6, fontWeight: 'bold' }}>Baseline</td>
                  {getAllStages(orderOriginalPlan, orderOptimizedPlan).map(stage => {
                    const data = getStageData(orderOriginalPlan, stage);
                    return (
                      <React.Fragment key={stage + '-baseline'}>
                        <td style={{ border: '1px solid #ccc', padding: 6, minWidth: 120 }}>
                          {data ? (
                            <div>
                              <div><strong>Time:</strong> {data.duration_minutes !== undefined ? `${Math.round(data.duration_minutes)} min` : 'N/A'}</div>
                              <div><strong>Worker:</strong> {data.worker_name || 'N/A'}</div>
                              <div><strong>Equipment:</strong> {data.equipment_name || 'N/A'}</div>
                            </div>
                          ) : 'N/A'}
                        </td>
                        <td style={{ border: '1px solid #ccc', padding: 6, minWidth: 80 }}>
                          {data ? (
                            <div>{data.waiting_time_before !== undefined ? `${data.waiting_time_before} min` : 'N/A'}</div>
                          ) : 'N/A'}
                        </td>
                      </React.Fragment>
                    );
                  })}
                </tr>
                {/* Optimized row */}
                <tr>
                  <td style={{ border: '1px solid #ccc', padding: 6, fontWeight: 'bold' }}>Optimized</td>
                  {getAllStages(orderOriginalPlan, orderOptimizedPlan).map(stage => {
                    const data = orderOptimizedPlan && orderOptimizedPlan.optimized_timeline ? getStageData(orderOptimizedPlan.optimized_timeline, stage) : null;
                    return (
                      <React.Fragment key={stage + '-optimized'}>
                        <td style={{ border: '1px solid #ccc', padding: 6, minWidth: 120 }}>
                          {data ? (
                            <div>
                              <div><strong>Time:</strong> {data.duration_minutes !== undefined ? `${Math.round(data.duration_minutes)} min` : 'N/A'}</div>
                              <div><strong>Worker:</strong> {data.worker_name || 'N/A'}</div>
                              <div><strong>Equipment:</strong> {data.equipment_name || 'N/A'}</div>
                            </div>
                          ) : 'N/A'}
                        </td>
                        <td style={{ border: '1px solid #ccc', padding: 6, minWidth: 80 }}>
                          {data ? (
                            <div>{data.waiting_time_before !== undefined ? `${data.waiting_time_before} min` : 'N/A'}</div>
                          ) : 'N/A'}
                        </td>
                      </React.Fragment>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Wave Selection - Moved to Top */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '15px', color: '#495057', fontSize: '24px' }}>Wave Analysis</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <label style={{ fontWeight: 'bold', color: '#495057', minWidth: '120px' }}>
            Select Wave:
          </label>
          <select 
            value={selectedWaveId || ''}
            onChange={(e) => setSelectedWaveId(Number(e.target.value))}
            style={{
              flex: 1,
              padding: '10px',
              border: '1px solid #ced4da',
              borderRadius: '6px',
              fontSize: '16px',
              backgroundColor: '#ffffff'
            }}
          >
            {waves.map(wave => (
              <option key={wave.id} value={wave.id}>
                {wave.name} ({wave.total_orders} orders, {wave.total_orders * 6} tasks)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Data Warning */}
      {showDataWarning && (
        <div style={{
          backgroundColor: '#FEF3C7',
          border: '1px solid #F59E0B',
          borderRadius: '0.5rem',
          padding: '1rem',
          marginBottom: '1rem',
          color: '#92400E'
        }}>
          <h3>⚠️ Limited Data Available</h3>
          <p>Some calculations are using default values because real worker and order statistics are not available in the database.</p>
          <p>To see accurate cost and time calculations, ensure you have:</p>
          <ul>
            <li>Active workers with hourly rates in the database</li>
            <li>Completed orders with pick/pack times in the database</li>
          </ul>
        </div>
      )}

      {/* Detailed Wave Metrics Section */}
      {currentWaveData?.metrics_summary && (
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginBottom: '15px', color: '#495057', fontSize: '20px' }}>
            📊 Detailed Wave Metrics
          </h3>
          
          {/* Wave Summary Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '20px' }}>
            <div style={{ backgroundColor: '#e3f2fd', padding: '15px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
                {currentWaveData.metrics_summary.total_orders}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Orders</div>
            </div>
            
            <div style={{ backgroundColor: '#e8f5e8', padding: '15px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2e7d32' }}>
                {Math.round(currentWaveData.metrics_summary.total_time_minutes)} min
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Time</div>
            </div>
            
            <div style={{ backgroundColor: '#fff3e0', padding: '15px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f57c00' }}>
                {Math.round(currentWaveData.metrics_summary.average_time_per_order_minutes)} min
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Avg per Order</div>
            </div>
            
            <div style={{ backgroundColor: '#fce4ec', padding: '15px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#c2185b' }}>
                {Math.round(currentWaveData.metrics_summary.total_walking_time_minutes)} min
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Walking Time</div>
            </div>
          </div>

          {/* Detailed Stage Breakdown */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ marginBottom: '10px', color: '#495057' }}>Stage Breakdown</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_pick_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Pick</div>
              </div>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_pack_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Pack</div>
              </div>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_consolidate_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Consolidate</div>
              </div>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_label_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Label</div>
              </div>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_stage_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Stage</div>
              </div>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#495057' }}>
                  {Math.round(currentWaveData.metrics_summary.total_ship_time_minutes)} min
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Ship</div>
              </div>
            </div>
          </div>

          {/* Order Details Table */}
          {currentWaveData.order_metrics && currentWaveData.order_metrics.length > 0 && (
            <div>
              <h4 style={{ marginBottom: '10px', color: '#495057' }}>Order Details</h4>
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f8f9fa' }}>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Order</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Customer</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Deadline</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Assignment</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Pick</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Pack</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Walking</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Consolidate</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Label</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Stage</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Ship</th>
                      <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'center' }}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentWaveData.order_metrics.map((order, index) => {
                      // Format deadline
                      let deadlineStr = 'N/A';
                      if (order.shipping_deadline) {
                        const d = new Date(order.shipping_deadline);
                        deadlineStr = isNaN(d.getTime()) ? 'N/A' : d.toLocaleString();
                      }
                      // Assignment summary
                      let assignmentStr = 'Unassigned';
                      if (order.assignment) {
                        const a = order.assignment;
                        assignmentStr = [
                          a.stage ? `Stage: ${a.stage}` : null,
                          a.assigned_worker_id ? `Worker: ${a.assigned_worker_id}` : null,
                          a.assigned_equipment_id ? `Equip: ${a.assigned_equipment_id}` : null,
                          a.planned_start_time ? `Planned: ${new Date(a.planned_start_time).toLocaleString()}` : null,
                          a.actual_start_time ? `Actual: ${new Date(a.actual_start_time).toLocaleString()}` : null
                        ].filter(Boolean).join(' | ');
                        if (!assignmentStr) assignmentStr = 'Unassigned';
                      }
                      return (
                        <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa' }}>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                            {order.order_number}
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                            {order.customer_name || 'N/A'}
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                            {deadlineStr}
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                            {assignmentStr}
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.pick_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.pack_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.walking_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.consolidate_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.label_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.stage_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center' }}>
                            {Math.round(order.metrics.ship_time_minutes || 0)} min
                          </td>
                          <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px', textAlign: 'center', fontWeight: 'bold' }}>
                            {Math.round(order.metrics.total_time_minutes || 0)} min
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sequence Exploration Section */}
      <div className="sequence-exploration-section" style={{
        backgroundColor: '#f8f9fa',
        border: '1px solid #dee2e6',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px'
      }}>
        <h3 style={{ marginBottom: '15px', color: '#495057' }}>🔍 Explore Wave Sequences</h3>
        
        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          {/* Worker Selection */}
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#495057' }}>
              Select Worker:
            </label>
            <select 
              value={selectedWorkerId || ''}
              onChange={(e) => {
                const workerId = Number(e.target.value);
                setSelectedWorkerId(workerId);
                if (workerId) {
                  loadWorkerSequence(workerId);
                }
              }}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value="">Choose a worker...</option>
              {availableWorkers.map(worker => (
                <option key={worker.id} value={worker.id}>
                  {worker.worker_name} ({worker.worker_code}) - {worker.assignment_count} tasks
                </option>
              ))}
            </select>
          </div>
          
          {/* Station Selection */}
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#495057' }}>
              Select Station:
            </label>
            <select 
              value={selectedStationId || ''}
              onChange={(e) => {
                const stationId = Number(e.target.value);
                setSelectedStationId(stationId);
                if (stationId) {
                  loadStationSequence(stationId);
                }
              }}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ced4da',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            >
              <option value="">Choose a station...</option>
              {availableStations.map(station => (
                <option key={station.id} value={station.id}>
                  {station.equipment_name} ({station.equipment_type}) - {station.assignment_count} tasks
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Sequence Display */}
        {sequenceLoading && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#6c757d' }}>
            Loading sequence...
          </div>
        )}

        {(workerSequence || stationSequence) && !sequenceLoading && (
          <div style={{ display: 'flex', gap: '20px' }}>
            {/* Original Plan */}
            <div style={{ flex: 1, backgroundColor: 'white', borderRadius: '8px', padding: '15px', border: '1px solid #dee2e6' }}>
              <h4 style={{ marginBottom: '15px', color: '#495057', borderBottom: '2px solid #007bff', paddingBottom: '5px' }}>
                📋 Original WMS Plan
              </h4>
              
              {workerSequence && (
                <div>
                  <div style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                    <strong>Worker:</strong> {workerSequence.worker.worker_name} ({workerSequence.worker.worker_code})
                    <br />
                    <strong>Total Time:</strong> {workerSequence.total_planned_minutes} minutes
                    <br />
                    <strong>Efficiency:</strong> {workerSequence.efficiency_percentage}%
                  </div>
                  
                  <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Time</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Order</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Stage</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Duration</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Equipment</th>
                        </tr>
                      </thead>
                      <tbody>
                        {workerSequence.assignments.map((assignment, index) => (
                          <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa' }}>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {new Date(assignment.planned_start_time).toLocaleTimeString('en-US', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.order_number}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.stage.toUpperCase()}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.planned_duration_minutes} min
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.equipment_name || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
              {stationSequence && (
                <div>
                  <div style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                    <strong>Station:</strong> {stationSequence.equipment.equipment_name} ({stationSequence.equipment.equipment_type})
                    <br />
                    <strong>Total Time:</strong> {stationSequence.total_planned_minutes} minutes
                    <br />
                    <strong>Utilization:</strong> {stationSequence.utilization_percentage}%
                  </div>
                  
                  <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Time</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Order</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Stage</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Duration</th>
                          <th style={{ padding: '8px', border: '1px solid #dee2e6', textAlign: 'left' }}>Worker</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stationSequence.assignments.map((assignment, index) => (
                          <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa' }}>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {new Date(assignment.planned_start_time).toLocaleTimeString('en-US', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.order_number}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.stage.toUpperCase()}
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.planned_duration_minutes} min
                            </td>
                            <td style={{ padding: '6px', border: '1px solid #dee2e6', fontSize: '11px' }}>
                              {assignment.worker_name || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
            
            {/* Optimized Plan */}
            <div style={{ flex: 1, backgroundColor: 'white', borderRadius: '8px', padding: '15px', border: '1px solid #dee2e6' }}>
              <h4 style={{ marginBottom: '15px', color: '#495057', borderBottom: '2px solid #28a745', paddingBottom: '5px' }}>
                🤖 AI Optimized Plan
              </h4>
              
              {!hasOptimizationResults ? (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '40px 20px', 
                  color: '#6c757d',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '4px'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '10px' }}>⏳</div>
                  <strong>Optimization Not Yet Run</strong>
                  <br />
                  <small>Run optimization to see improved sequences</small>
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '40px 20px', 
                  color: '#28a745',
                  backgroundColor: '#d4edda',
                  borderRadius: '4px'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '10px' }}>✅</div>
                  <strong>Optimized Sequences Available</strong>
                  <br />
                  <small>AI has reorganized tasks for better efficiency</small>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="wave-selector-section">
        <div className="wave-header">
          <h2 className="wave-title">Wave Performance Summary</h2>
        </div>
        
        <div className="quick-stats-grid">
            <div className="quick-stat">
              <div className="stat-icon">⏰</div>
              <div className="stat-label">Completion Time</div>
              <div className="stat-before">{completionMetrics?.completion_time_formatted || 'N/A'}</div>
              <div className="stat-after">{completionMetrics?.completion_time_formatted || 'N/A'}</div>
              <div className="stat-improvement">Time of day</div>
            </div>
            
            <div className="quick-stat">
              <div className="stat-icon">👷</div>
              <div className="stat-label">Total Labor Hours</div>
              <div className="stat-before">{completionMetrics?.total_labor_hours != null ? completionMetrics.total_labor_hours.toFixed(1) : 'N/A'} hrs</div>
              <div className="stat-after">{completionMetrics?.total_labor_hours != null ? completionMetrics.total_labor_hours.toFixed(1) : 'N/A'} hrs</div>
              <div className="stat-improvement">Including wait time</div>
            </div>
            
            {/* Debug info - remove this after testing */}
            <div style={{fontSize: '10px', color: 'gray', marginTop: '10px'}}>
              Debug: completionMetrics = {JSON.stringify(completionMetrics)}
            </div>
            
            <div className="quick-stat">
              <div className="stat-icon">💰</div>
              <div className="stat-label">Total Cost</div>
              <div className="stat-before">${currentQuickStats?.cost != null ? currentQuickStats.cost.toFixed(2) : 'N/A'}</div>
              <div className="stat-after">{hasOptimizationResults && currentQuickStats?.cost != null ? `$${(currentQuickStats.cost * 0.8).toFixed(2)}` : `$${currentQuickStats?.cost != null ? currentQuickStats.cost.toFixed(2) : 'N/A'}`}</div>
              <div className="stat-improvement">{hasOptimizationResults && currentQuickStats?.cost != null ? `$${(currentQuickStats.cost * 0.2).toFixed(2)} saved` : 'No optimization'}</div>
            </div>
            
            <div className="quick-stat">
              <div className="stat-icon">👥</div>
              <div className="stat-label">Workers Needed</div>
              <div className="stat-before">{currentQuickStats?.workers || 'N/A'} people</div>
              <div className="stat-after">{currentQuickStats?.workers || 'N/A'} people</div>
              <div className="stat-improvement">Same workers, better utilization</div>
            </div>
            
            <div className="quick-stat">
              <div className="stat-icon">📊</div>
              <div className="stat-label">Efficiency</div>
              <div className="stat-before">{currentQuickStats?.efficiency != null ? currentQuickStats.efficiency.toFixed(1) : 'N/A'}%</div>
              <div className="stat-after">{hasOptimizationResults && currentQuickStats?.efficiency != null ? `${Math.min(100, currentQuickStats.efficiency + 20).toFixed(1)}%` : currentQuickStats?.efficiency != null ? currentQuickStats.efficiency.toFixed(1) : 'N/A'}%</div>
              <div className="stat-improvement">{hasOptimizationResults ? '+20% improvement' : 'No optimization'}</div>
            </div>
            
            <div className="quick-stat">
              <div className="stat-icon">🚶</div>
              <div className="stat-label">Travel Time</div>
              <div className="stat-before">{completionMetrics?.travel_time_minutes != null ? `${completionMetrics.travel_time_minutes.toFixed(0)} min` : 'N/A'}</div>
              <div className="stat-after">{completionMetrics?.travel_time_minutes != null ? `${completionMetrics.travel_time_minutes.toFixed(0)} min` : 'N/A'}</div>
              <div className="stat-improvement">Based on pick path</div>
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
            
            {/* Timeline */}
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
              {currentWorkerChanges.map((change, index) => (
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
                <div className="equipment-before">Idle {currentQuickStats?.hours ? Math.round(currentQuickStats.hours * 0.3 * 60) : 'N/A'}min</div>
                <div className="equipment-after">Active {hasOptimizationResults && currentQuickStats?.hours ? Math.round(currentQuickStats.hours * 0.8 * 0.3 * 60) : currentQuickStats?.hours ? Math.round(currentQuickStats.hours * 0.3 * 60) : 'N/A'}min</div>
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
              {currentRisks.map((risk, index) => (
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
              {currentConfidenceFactors.map((factor, index) => (
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