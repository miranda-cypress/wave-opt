import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const getWarehouseData = async (warehouseId = 1) => {
  const res = await axios.get(`${API_BASE}/data/warehouse/${warehouseId}`);
  return res.data;
};

export const runOptimization = async (warehouseId = 1, orderLimit = 50) => {
  const res = await axios.post(`${API_BASE}/optimize/database?warehouse_id=${warehouseId}&order_limit=${orderLimit}`);
  return res.data;
};

export const getOptimizationHistory = async (limit = 10) => {
  const res = await axios.get(`${API_BASE}/history?limit=${limit}`);
  return res.data;
};

export const getOptimizationPlan = async (runId: number) => {
  const res = await axios.get(`${API_BASE}/optimization/plans/${runId}`);
  return res.data;
};

export const getLatestOptimizationPlan = async () => {
  const res = await axios.get(`${API_BASE}/optimization/plans/latest`);
  return res.data;
};

export const getOptimizationPlansByScenario = async (scenarioType: string, limit = 5) => {
  const res = await axios.get(`${API_BASE}/optimization/plans/scenario/${scenarioType}?limit=${limit}`);
  return res.data;
};

export const getWarehouseStats = async (warehouseId = 1) => {
  const res = await axios.get(`${API_BASE}/data/stats/${warehouseId}`);
  return res.data;
};

export const getOptimizationConstraints = async () => {
  const res = await axios.get(`${API_BASE}/optimization/constraints`);
  return res.data;
};

export const getOriginalWmsPlan = async (orderId: number) => {
  const res = await axios.get(`${API_BASE}/optimization/original/order/${orderId}`);
  return res.data;
};

export const getOriginalWmsPlanByNumber = async (orderNumber: string) => {
  const res = await axios.get(`${API_BASE}/optimization/original/order-by-number/${orderNumber}`);
  return res.data;
};

export const getOriginalWmsPlanSummary = async () => {
  const res = await axios.get(`${API_BASE}/optimization/original/summary`);
  return res.data;
};

export const refreshOriginalPlans = async () => {
  const res = await axios.post(`${API_BASE}/optimization/original/refresh`);
  return res.data;
};

export const getWmsInefficiencies = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/optimization/original/inefficiencies`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching WMS inefficiencies:', error);
    throw error;
  }
};

// Wave-related API functions
export const getWaves = async (warehouseId: number = 1, limit: number = 10) => {
  console.log('getWaves API called', { warehouseId, limit });
  const url = `${API_BASE}/data/waves?warehouse_id=${warehouseId}&limit=${limit}`;
  console.log('getWaves API URL:', url);
  const res = await axios.get(url);
  console.log('getWaves API response:', res.data);
  return res.data;
};

export const getWaveDetails = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}`);
  return res.data;
};

export const getWaveAssignments = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/assignments`);
  return res.data;
};

export const getWavePerformance = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/performance`);
  return res.data;
};

// Wave optimization API functions
export const optimizeWave = async (waveId: number, optimizeType: 'within_wave' | 'cross_wave' = 'within_wave') => {
  console.log('optimizeWave API called', { waveId, optimizeType });
  const url = `${API_BASE}/optimization/wave/${waveId}?optimize_type=${optimizeType}`;
  console.log('API URL:', url);
  const res = await axios.post(url);
  console.log('optimizeWave API response:', res.data);
  return res.data;
};

export const optimizeCrossWave = async () => {
  const res = await axios.post(`${API_BASE}/optimization/cross-wave`);
  return res.data;
};

// New API functions for detailed wave metrics
export const getWaveUtilization = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/utilization`);
  return res.data;
};

export const getWaveOnTimeDelivery = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/on-time-delivery`);
  return res.data;
};

export const getWaveCosts = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/costs`);
  return res.data;
};

export const getWaveWorkerAssignments = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/worker-assignments`);
  return res.data;
};

export const getWaveDetailedMetrics = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/detailed-metrics`);
  return res.data;
};

export const getWaveCompletionMetrics = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/completion-metrics`);
  return res.data;
};

// Configuration API functions
export const getConfiguration = async () => {
  const res = await axios.get(`${API_BASE}/config`);
  return res.data;
};

export const updateConfiguration = async (config: any) => {
  const res = await axios.put(`${API_BASE}/config`, config);
  return res.data;
};

export const resetConfiguration = async () => {
  const res = await axios.post(`${API_BASE}/config/reset`);
  return res.data;
};

// Real calculation API functions
export const getWorkerStatistics = async (warehouseId: number = 1) => {
  const res = await axios.get(`${API_BASE}/data/calculations/worker-stats?warehouse_id=${warehouseId}`);
  return res.data;
};

export const getOrderStatistics = async (warehouseId: number = 1) => {
  const res = await axios.get(`${API_BASE}/data/calculations/order-stats?warehouse_id=${warehouseId}`);
  return res.data;
};

export const getWaveRiskAssessment = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/calculations/wave-risk-assessment/${waveId}`);
  return res.data;
};

// New API function for comprehensive wave comparison data
export const getWaveComparisonData = async (warehouseId: number = 1) => {
  const res = await axios.get(`${API_BASE}/data/waves/comparison/all?warehouse_id=${warehouseId}`);
  return res.data;
};

// Demo data management API function
export const updateDemoDates = async () => {
  const res = await axios.post(`${API_BASE}/demo/update-dates`);
  return res.data;
};

// Wave sequence exploration API functions
export const getWorkerSequence = async (waveId: number, workerId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/worker-sequence/${workerId}`);
  return res.data;
};

export const getStationSequence = async (waveId: number, equipmentId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/station-sequence/${equipmentId}`);
  return res.data;
};

export const getAvailableWorkers = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/available-workers`);
  return res.data;
};

export const getAvailableStations = async (waveId: number) => {
  const res = await axios.get(`${API_BASE}/data/waves/${waveId}/available-stations`);
  return res.data;
};

// Order wave assignment API functions
export const getOrderWaveAssignment = async (orderId: number) => {
  const res = await axios.get(`${API_BASE}/data/orders/${orderId}/wave-assignment`);
  return res.data;
};

export const getOrderWaveAssignmentByNumber = async (orderNumber: string) => {
  const res = await axios.get(`${API_BASE}/data/orders/number/${orderNumber}/wave-assignment`);
  return res.data;
}; 