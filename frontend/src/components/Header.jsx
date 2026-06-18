import React from 'react';
import { motion } from 'framer-motion';
import { ScanLine, ShieldCheck, Sparkles } from 'lucide-react';

const Header = ({ onStartClick, currentView }) => {
  const isLanding = currentView === 'landing';

  return (
    <nav className="top-nav">
      <div
        className="nav-logo"
        onClick={isLanding ? onStartClick : undefined}
        style={{ cursor: isLanding ? 'pointer' : 'default', visibility: isLanding ? 'visible' : 'hidden' }}
      >
        <div className="logo-icon-container">
          <ScanLine size={22} className="logo-icon" />
        </div>
        <div className="logo-text">
          <span className="logo-title">Career Lens AI</span>
          <span className="logo-subtitle">AI Resume Matcher</span>
        </div>
      </div>
    </nav>
  );
};

export default Header;

