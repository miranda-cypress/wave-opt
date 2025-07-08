import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Dashboard from './components/DashboardSummary';
import UnifiedOptimization from './components/UnifiedOptimization';
import ComparisonPage from './components/ComparisonPage';
import StageTimeline from './components/StageTimeline';
import WaveDetails from './components/WaveDetails';
import SKUDetails from './components/SKUDetails';
import WarehouseLayout from './components/WarehouseLayout';
import ConfigurationPage from './components/ConfigurationPage';
import Footer from './components/Footer';
import { getOriginalWmsPlanSummary } from './api';

interface OptimizationResults {
  original_plan: any;
  optimized_plan: any;
  summary: any;
}

function AppContent() {
  const location = useLocation();
  const navigate = useNavigate();
  const [baselineData, setBaselineData] = useState<any>(null);
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResults | null>(null);
  const [hasOptimizationResults, setHasOptimizationResults] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState('dashboard');

  // Sync navigation state with URL
  useEffect(() => {
    const path = location.pathname;
    if (path === '/') setCurrentPage('dashboard');
    else if (path === '/optimize') setCurrentPage('optimize');
    else if (path === '/wave-details') setCurrentPage('wave-details');
    else if (path === '/sku-details') setCurrentPage('sku-details');
    else if (path === '/warehouse-layout') setCurrentPage('warehouse-layout');
    else if (path === '/config') setCurrentPage('config');
  }, [location]);

  useEffect(() => {
    // Load baseline data on app start
    loadBaselineData();
  }, []);

  const loadBaselineData = async () => {
    try {
      const response = await getOriginalWmsPlanSummary();
      console.log('Baseline API response:', response);
      
      // Extract the actual summary data from the API response
      const summaryData = response.original_plan_summary || response;
      console.log('Extracted summary data:', summaryData);
      
      setBaselineData(summaryData);
    } catch (error) {
      console.error('Error loading baseline data:', error);
      // Don't set error state here as it's not critical for page functionality
    }
  };

  const handleOptimizationComplete = (results: OptimizationResults) => {
    setOptimizationResults(results);
    setHasOptimizationResults(true);
    setError(null);
  };

  const handleOptimizationError = (errorMessage: string) => {
    setError(errorMessage);
    setOptimizationResults(null);
    setHasOptimizationResults(false);
  };

  const handleOptimizationStart = () => {
    setIsLoading(true);
    setError(null);
  };

  const handleOptimizationEnd = () => {
    setIsLoading(false);
  };

  const handlePageChange = (page: string) => {
    setCurrentPage(page);
    switch (page) {
      case 'dashboard':
        navigate('/');
        break;
      case 'optimize':
        navigate('/optimize');
        break;
      case 'wave-details':
        navigate('/wave-details');
        break;
      case 'sku-details':
        navigate('/sku-details');
        break;
      case 'warehouse-layout':
        navigate('/warehouse-layout');
        break;
      case 'config':
        navigate('/config');
        break;
      default:
        navigate('/');
    }
  };

  const DashboardPage = () => (
    <Dashboard onNavigate={handlePageChange} />
  );

  const OptimizePage = () => (
    <div className="container">
      <UnifiedOptimization 
        onOptimizationComplete={handleOptimizationComplete}
        onOptimizationError={handleOptimizationError}
        onOptimizationStart={handleOptimizationStart}
        onOptimizationEnd={handleOptimizationEnd}
        isLoading={isLoading}
      />

      {error && (
        <div className="error-message">
          <h3>Optimization Error</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Show comparison page with baseline data initially, then with optimization results */}
      <div className="results-section">
        <ComparisonPage 
          originalPlan={optimizationResults?.original_plan || baselineData}
          optimizedPlan={optimizationResults?.optimized_plan}
          summary={optimizationResults?.summary || baselineData}
          showHeader={false}
          hasOptimizationResults={hasOptimizationResults}
        />
        
        {optimizationResults && (
          <div className="timeline-section">
            <h2 className="section-title">Workflow Timeline Analysis</h2>
            <StageTimeline 
              originalPlan={optimizationResults.original_plan}
              optimizedPlan={optimizationResults.optimized_plan}
            />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="App">
      <Header currentPage={currentPage} onPageChange={handlePageChange} />
      
      <main className="main-content">
        <Routes>
          <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />} 
          />
          <Route 
            path="/dashboard" 
            element={<DashboardPage />} 
          />
          <Route 
            path="/optimize" 
            element={<OptimizePage />} 
          />
          <Route 
            path="/wave-details" 
            element={<WaveDetails onNavigate={handlePageChange} />} 
          />
          <Route 
            path="/sku-details" 
            element={<SKUDetails onNavigate={handlePageChange} />} 
          />
          <Route 
            path="/warehouse-layout" 
            element={<WarehouseLayout onNavigate={handlePageChange} />} 
          />
          <Route 
            path="/config" 
            element={<ConfigurationPage onNavigate={handlePageChange} />} 
          />

        </Routes>
      </main>
      
      <Footer />
    </div>
  );
}

function App() {
  return <AppContent />;
}

export default App; 