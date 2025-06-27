import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const getWarehouseData = async (warehouseId = 1) => {
  const res = await axios.get(`${API_BASE}/data/warehouse/${warehouseId}`);
  return res.data;
}; 