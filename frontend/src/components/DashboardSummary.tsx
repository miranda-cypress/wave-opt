import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  ResponsiveContainer, LineChart, Line, AreaChart, Area, ComposedChart
} from 'recharts';
import { getWorkerStatistics, getOrderStatistics } from '../api';

const API_BASE = 'http://localhost:8000';

const COLORS = {
  primary: '#0A4A2D',
  secondary: '#57a55a',
  accent: '#0082c8',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  neutral: '#6B7280',
  light: '#E5E7EB'
};

// Add CSS for data warning
const dataWarningStyle = {
  backgroundColor: '#FEF3C7',
  border: '1px solid #F59E0B',
  borderRadius: '0.5rem',
  padding: '1rem',
  marginBottom: '1rem',
  color: '#92400E'
};

interface DashboardSummaryProps {
  onNavigate?: (page: string) => void;
}

interface WaveData {
  id: number;
  name: string;
  efficiency_score: number;
  total_orders: number;
  status: string;
  created_at: string;
}

interface PerformanceMetrics {
  wave_id: number;
  worker_utilization_percentage: number;
  equipment_utilization_percentage: number;
  on_time_delivery_percentage: number;
  total_cost: number;
  labor_cost: number;
  equipment_cost: number;
}

const DashboardSummary: React.FC<DashboardSummaryProps> = ({ onNavigate }) => {
  const [waves, setWaves] = useState<WaveData[]>([]);
  const [performanceData, setPerformanceData] = useState<PerformanceMetrics[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [workerStats, setWorkerStats] = useState<any>(null);
  const [orderStats, setOrderStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Load waves data
        const wavesResponse = await axios.get(`${API_BASE}/data/waves?limit=10`);
        const wavesData = wavesResponse.data.waves || [];
        setWaves(wavesData);
        
        // Load warehouse stats
        const statsResponse = await axios.get(`${API_BASE}/data/stats/1`);
        setStats(statsResponse.data.statistics);
        
        // Load worker statistics for real cost calculations
        try {
          const workerResponse = await getWorkerStatistics(1);
          setWorkerStats(workerResponse);
        } catch (workerError) {
          console.warn('Could not load worker statistics:', workerError);
          setWorkerStats(null);
        }
        
        // Load order statistics for real time calculations
        try {
          const orderResponse = await getOrderStatistics(1);
          setOrderStats(orderResponse);
        } catch (orderError) {
          console.warn('Could not load order statistics:', orderError);
          setOrderStats(null);
        }
        
                 // Load performance metrics for each wave
         const performancePromises = wavesData.map((wave: WaveData) => 
           axios.get(`${API_BASE}/data/waves/${wave.id}/detailed-metrics`)
             .then(response => response.data)
             .catch(() => null)
         );
        
        const performanceResults = await Promise.all(performancePromises);
        const validPerformanceData = performanceResults.filter(data => data !== null);
        setPerformanceData(validPerformanceData);
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
        setError(errorMessage);
        console.error('Dashboard data loading error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const handleNavigate = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  // Chart 1: Efficiency Trend Over Time
  const getEfficiencyTrendData = () => {
    return waves.map(wave => ({
      name: wave.name,
      efficiency: wave.efficiency_score || 0,
      date: new Date(wave.created_at).toLocaleDateString()
    }));
  };

  // Chart 2: Cost vs Orders Correlation
  const getCostOrdersData = () => {
    if (!workerStats || !orderStats) {
      return waves.map(wave => ({
        name: wave.name,
        orders: wave.total_orders,
        cost: 0,
        efficiency: wave.efficiency_score || 0,
        error: 'No worker or order statistics available'
      }));
    }
    
    return waves.map(wave => {
      // Use real data from database
      const avgTimePerOrder = orderStats.avg_total_time || 2.5; // minutes
      const efficiencyFactor = (wave.efficiency_score || 75) / 100;
      const estimatedMinutes = wave.total_orders * avgTimePerOrder / efficiencyFactor;
      const estimatedHours = estimatedMinutes / 60;
      const hourlyRate = workerStats.avg_hourly_rate || 25;
      const estimatedCost = estimatedHours * hourlyRate;
      
      return {
        name: wave.name,
        orders: wave.total_orders,
        cost: estimatedCost,
        efficiency: wave.efficiency_score || 0
      };
    });
  };

  // Chart 3: Worker Utilization by Wave
  const getUtilizationData = () => {
    return performanceData.map(data => ({
      name: `Wave ${data.wave_id}`,
      worker: data.worker_utilization_percentage || 0,
      equipment: data.equipment_utilization_percentage || 0
    }));
  };

  // Chart 4: On-Time Delivery Performance
  const getOnTimeDeliveryData = () => {
    return performanceData.map(data => ({
      name: `Wave ${data.wave_id}`,
      onTime: data.on_time_delivery_percentage || 0,
      delayed: 100 - (data.on_time_delivery_percentage || 0)
    }));
  };

  // Chart 5: Cost Breakdown
  const getCostBreakdownData = () => {
    const totalLabor = performanceData.reduce((sum, data) => sum + (data.labor_cost || 0), 0);
    const totalEquipment = performanceData.reduce((sum, data) => sum + (data.equipment_cost || 0), 0);
    
    return [
      { name: 'Labor Cost', value: totalLabor, color: COLORS.primary },
      { name: 'Equipment Cost', value: totalEquipment, color: COLORS.accent }
    ];
  };

  // Chart 6: Wave Status Distribution
  const getWaveStatusData = () => {
    const statusCounts = waves.reduce((acc, wave) => {
      const status = wave.status || 'unknown';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(statusCounts).map(([status, count]) => ({
      name: status.charAt(0).toUpperCase() + status.slice(1),
      value: count,
      color: status === 'completed' ? COLORS.success : 
             status === 'in_progress' ? COLORS.warning : 
             status === 'planned' ? COLORS.accent : COLORS.neutral
    }));
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading warehouse performance data...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Error Loading Dashboard Data</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  // Show warning if real calculation data is not available
  const showDataWarning = !workerStats || !orderStats;

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Warehouse Performance Dashboard</h1>
          <p>Real-time insights for optimization and efficiency improvement</p>
        </div>
        <div className="dashboard-actions">
          <button 
            onClick={() => handleNavigate('optimize')} 
            className="btn btn-primary"
          >
            🚀 Run Optimization
          </button>
          <button 
            onClick={() => handleNavigate('wave-details')} 
            className="btn btn-outline"
          >
            📊 Wave Details
          </button>
        </div>
      </div>

      {/* Data Warning */}
      {showDataWarning && (
        <div style={dataWarningStyle}>
          <h3>⚠️ Limited Data Available</h3>
          <p>Some calculations are using default values because real worker and order statistics are not available in the database.</p>
          <p>To see accurate cost and time calculations, ensure you have:</p>
          <ul>
            <li>Active workers with hourly rates in the database</li>
            <li>Completed orders with pick/pack times in the database</li>
          </ul>
        </div>
      )}

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <h3>Average Efficiency</h3>
            <div className="metric-value">
              {waves.length > 0 
                ? `${(waves.reduce((sum, wave) => sum + (wave.efficiency_score || 0), 0) / waves.length).toFixed(1)}%`
                : 'N/A'
              }
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">📦</div>
          <div className="metric-content">
            <h3>Total Orders</h3>
            <div className="metric-value">
              {waves.reduce((sum, wave) => sum + wave.total_orders, 0)}
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <h3>Total Cost</h3>
            <div className="metric-value">
              ${performanceData.reduce((sum, data) => sum + (data.total_cost || 0), 0).toFixed(2)}
            </div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <h3>Avg On-Time Delivery</h3>
            <div className="metric-value">
              {performanceData.length > 0 
                ? `${(performanceData.reduce((sum, data) => sum + (data.on_time_delivery_percentage || 0), 0) / performanceData.length).toFixed(1)}%`
                : 'N/A'
              }
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Chart 1: Efficiency Trend */}
        <div className="chart-card">
          <h3>📈 Efficiency Trend</h3>
          <p>Wave efficiency scores over time</p>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={getEfficiencyTrendData()}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.light} />
              <XAxis dataKey="date" stroke={COLORS.neutral} />
              <YAxis stroke={COLORS.neutral} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="efficiency" 
                stroke={COLORS.primary} 
                strokeWidth={3}
                dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 2: Cost vs Orders */}
        <div className="chart-card">
          <h3>💰 Cost vs Orders Correlation</h3>
          <p>Relationship between order volume and labor costs</p>
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={getCostOrdersData()}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.light} />
              <XAxis dataKey="orders" stroke={COLORS.neutral} />
              <YAxis yAxisId="left" stroke={COLORS.primary} />
              <YAxis yAxisId="right" orientation="right" stroke={COLORS.accent} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
              <Bar yAxisId="left" dataKey="cost" fill={COLORS.primary} opacity={0.7} />
              <Line yAxisId="right" type="monotone" dataKey="efficiency" stroke={COLORS.accent} strokeWidth={2} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 3: Utilization Comparison */}
        <div className="chart-card">
          <h3>👥 Resource Utilization</h3>
          <p>Worker vs Equipment utilization by wave</p>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={getUtilizationData()}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.light} />
              <XAxis dataKey="name" stroke={COLORS.neutral} />
              <YAxis stroke={COLORS.neutral} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="worker" fill={COLORS.primary} name="Worker Utilization" />
              <Bar dataKey="equipment" fill={COLORS.accent} name="Equipment Utilization" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 4: On-Time Delivery */}
        <div className="chart-card">
          <h3>✅ On-Time Delivery Performance</h3>
          <p>Delivery success rate by wave</p>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={getOnTimeDeliveryData()}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.light} />
              <XAxis dataKey="name" stroke={COLORS.neutral} />
              <YAxis stroke={COLORS.neutral} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="onTime" 
                stackId="1"
                stroke={COLORS.success} 
                fill={COLORS.success} 
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="delayed" 
                stackId="1"
                stroke={COLORS.danger} 
                fill={COLORS.danger} 
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 5: Cost Breakdown */}
        <div className="chart-card">
          <h3>💸 Cost Breakdown</h3>
          <p>Labor vs Equipment cost distribution</p>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={getCostBreakdownData()}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                                 label={({ name, value }) => `${name}: $${(value || 0).toFixed(2)}`}
              >
                {getCostBreakdownData().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Chart 6: Wave Status */}
        <div className="chart-card">
          <h3>📊 Wave Status Distribution</h3>
          <p>Current status of all waves</p>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={getWaveStatusData()}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {getWaveStatusData().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: `1px solid ${COLORS.light}`,
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Insights Section */}
      <div className="insights-section">
        <h2>🔍 Key Insights</h2>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>Efficiency Opportunities</h4>
            <p>
              {waves.length > 0 && waves.some(w => w.efficiency_score < 75) 
                ? `${waves.filter(w => w.efficiency_score < 75).length} waves have efficiency below 75%. Consider optimization.`
                : 'All waves are performing well above efficiency targets.'
              }
            </p>
          </div>
          
          <div className="insight-card">
            <h4>Cost Optimization</h4>
            <p>
              {performanceData.length > 0 
                ? `Average cost per order: $${(performanceData.reduce((sum, data) => sum + (data.total_cost || 0), 0) / waves.reduce((sum, wave) => sum + wave.total_orders, 0)).toFixed(2)}`
                : 'Cost data not available.'
              }
            </p>
          </div>
          
          <div className="insight-card">
            <h4>Delivery Performance</h4>
            <p>
              {performanceData.length > 0 
                ? `Overall on-time delivery rate: ${(performanceData.reduce((sum, data) => sum + (data.on_time_delivery_percentage || 0), 0) / performanceData.length).toFixed(1)}%`
                : 'Delivery performance data not available.'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardSummary;