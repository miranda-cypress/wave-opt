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