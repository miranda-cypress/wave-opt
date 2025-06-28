import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import DashboardSummary from './components/DashboardSummary';
import OptimizationPanel from './components/OptimizationPanel';
import ComparisonPage from './components/ComparisonPage';
import StageTimeline from './components/StageTimeline';
import Footer from './components/Footer';
import { getOriginalWmsPlanSummary } from './api';

interface OptimizationResults {
  original_plan: any;
  optimized_plan: any;
  summary: any;
}

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResults | null>(null);
  const [baselineData, setBaselineData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get current page from URL path
  const getCurrentPage = () => {
    const path = location.pathname;
    if (path === '/optimize') return 'optimize';
    return 'dashboard';
  };

  const currentPage = getCurrentPage();

  // Load baseline data when optimize page is first opened
  useEffect(() => {
    if (currentPage === 'optimize' && !baselineData) {
      loadBaselineData();
    }
  }, [currentPage]);

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
    setError(null);
  };

  const handleOptimizationError = (errorMessage: string) => {
    setError(errorMessage);
    setOptimizationResults(null);
  };

  const handleOptimizationStart = () => {
    setIsLoading(true);
    setError(null);
  };

  const handleOptimizationEnd = () => {
    setIsLoading(false);
  };

  const handlePageChange = (page: string) => {
    if (page === 'dashboard') {
      navigate('/');
    } else {
      navigate(`/${page}`);
    }
  };

  const DashboardPage = () => (
    <DashboardSummary onNavigate={handlePageChange} />
  );

  const OptimizePage = () => (
    <div className="container">
      <h1 className="page-title">Warehouse Workflow Optimization</h1>
      <p className="page-subtitle">
        Optimize your warehouse operations with constraint programming to improve efficiency, reduce costs, and meet deadlines.
      </p>
      
      <OptimizationPanel 
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
          hasOptimizationResults={!!optimizationResults}
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
      <Header 
        currentPage={currentPage}
        onPageChange={handlePageChange}
      />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/optimize" element={<OptimizePage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App; 