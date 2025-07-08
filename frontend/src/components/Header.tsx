import React from 'react';
import './Header.css';
import logo from '../assets/zoneflow-logo.png';

interface HeaderProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const Header: React.FC<HeaderProps> = ({ currentPage, onPageChange }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <img src={logo} alt="ZoneFlow Logo" />
        </div>
        
        <nav className="nav-menu">
          <ul className="nav-list">
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
                onClick={() => onPageChange('dashboard')}
              >
                Dashboard
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'optimize' ? 'active' : ''}`}
                onClick={() => onPageChange('optimize')}
              >
                Optimize
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'wave-details' ? 'active' : ''}`}
                onClick={() => onPageChange('wave-details')}
              >
                Wave Details
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'sku-details' ? 'active' : ''}`}
                onClick={() => onPageChange('sku-details')}
              >
                SKU Details
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'warehouse-layout' ? 'active' : ''}`}
                onClick={() => onPageChange('warehouse-layout')}
              >
                Warehouse Layout
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${currentPage === 'config' ? 'active' : ''}`}
                onClick={() => onPageChange('config')}
              >
                Config
              </button>
            </li>

          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header; 