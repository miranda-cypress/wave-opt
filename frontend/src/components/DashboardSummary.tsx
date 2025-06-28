import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

const API_BASE = 'http://localhost:8000';

const COLORS = ['#174c3c', '#2e6e5c', '#4db6ac', '#b2dfdb', '#80cbc4'];

interface DashboardSummaryProps {
  onNavigate?: (page: string) => void;
}

const DashboardSummary: React.FC<DashboardSummaryProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    axios.get(`${API_BASE}/data/stats/1`).then(res => setStats(res.data.statistics));
  }, []);

  const handleNavigate = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  if (!stats) return <div>Loading dashboard summary...</div>;

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Warehouse Summary</h2>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', marginBottom: '2rem' }}>
        <div className="dashboard-card">
          <h4>Workers</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_workers || stats.workers?.total}</div>
        </div>
        <div className="dashboard-card">
          <h4>Equipment</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_equipment || stats.equipment?.total}</div>
        </div>
        <div className="dashboard-card">
          <h4>SKUs</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_skus || stats.equipment?.total}</div>
        </div>
        <div className="dashboard-card">
          <h4>Customers</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_customers || stats.customers?.total || 120}</div>
        </div>
        <div className="dashboard-card">
          <h4>Pending Orders</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.pending_orders || stats.orders?.total}</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3rem', marginTop: '2rem' }}>
        <div>
          <h4>Equipment Breakdown</h4>
          <PieChart width={300} height={220}>
            <Pie
              data={stats.equipment_breakdown}
              dataKey="count"
              nameKey="equipment_type"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {stats.equipment_breakdown.map((entry: any, idx: number) => (
                <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>
        <div>
          <h4>Order Priority Breakdown</h4>
          <BarChart width={350} height={220} data={stats.order_priority_breakdown}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="priority" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#174c3c" />
          </BarChart>
        </div>
      </div>
    </div>
  );
};

export default DashboardSummary;