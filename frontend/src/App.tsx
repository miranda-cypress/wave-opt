import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import DashboardSummary from './components/DashboardSummary';
import WorkersTable from './components/WorkersTable';
import EquipmentTable from './components/EquipmentTable';
import SKUsTable from './components/SKUsTable';
import CustomersTable from './components/CustomersTable';
import OrdersTable from './components/OrdersTable';
import OptimizationPanel from './components/OptimizationPanel';
import './App.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-root">
        <Header />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<DashboardSummary />} />
            <Route path="/workers" element={<WorkersTable />} />
            <Route path="/equipment" element={<EquipmentTable />} />
            <Route path="/skus" element={<SKUsTable />} />
            <Route path="/customers" element={<CustomersTable />} />
            <Route path="/orders" element={<OrdersTable />} />
            <Route path="/optimize" element={<OptimizationPanel />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App; 