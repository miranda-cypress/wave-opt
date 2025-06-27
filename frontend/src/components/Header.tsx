import React from 'react';
import './Header.css';
import logo from '../assets/zoneflow-logo.png';

const Header: React.FC = () => (
  <header className="zf-header">
    <div className="zf-header-content">
      <img src={logo} alt="ZoneFlow AI Logo" className="zf-logo" />
      <div className="zf-title-group">
        <h1 className="zf-title">ZoneFlow AI</h1>
        <span className="zf-tagline">From tasks to teamwork — with insight</span>
      </div>
    </div>
  </header>
);

export default Header; 