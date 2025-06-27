import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';
import { useNavigate } from 'react-router-dom';

const API_BASE = 'http://localhost:8000';

const COLORS = ['#174c3c', '#2e6e5c', '#4db6ac', '#b2dfdb', '#80cbc4'];

const DashboardSummary: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API_BASE}/data/stats/1`).then(res => setStats(res.data.statistics));
  }, []);

  if (!stats) return <div>Loading dashboard summary...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h2>Warehouse Summary</h2>
        <button 
          onClick={() => navigate('/optimize')}
          style={{
            background: 'linear-gradient(135deg, #174c3c 0%, #2e6e5c 100%)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 2rem',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 6px 12px rgba(23, 76, 60, 0.3)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          🚀 Run Optimization
        </button>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', marginBottom: '2rem' }}>
        <div className="dashboard-card" onClick={() => navigate('/workers')} style={{ cursor: 'pointer' }}>
          <h4>Workers</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_workers || stats.workers?.total}</div>
        </div>
        <div className="dashboard-card" onClick={() => navigate('/equipment')} style={{ cursor: 'pointer' }}>
          <h4>Equipment</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_equipment || stats.equipment?.total}</div>
        </div>
        <div className="dashboard-card" onClick={() => navigate('/skus')} style={{ cursor: 'pointer' }}>
          <h4>SKUs</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_skus || stats.equipment?.total}</div>
        </div>
        <div className="dashboard-card" onClick={() => navigate('/customers')} style={{ cursor: 'pointer' }}>
          <h4>Customers</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.total_customers || stats.customers?.total || 120}</div>
        </div>
        <div className="dashboard-card" onClick={() => navigate('/orders')} style={{ cursor: 'pointer' }}>
          <h4>Pending Orders</h4>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.pending_orders || stats.orders?.total}</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3rem', marginTop: '2rem' }}>
        <div style={{ cursor: 'pointer' }} onClick={() => navigate('/equipment')}>
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
        <div style={{ cursor: 'pointer' }} onClick={() => navigate('/orders')}>
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