import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit } from 'lucide-react';

const Header = () => {
  return (
    <header className="title-section">
      <motion.div 
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        style={{ 
          display: 'inline-flex', 
          padding: '8px 20px', 
          borderRadius: '50px', 
          background: 'rgba(14, 165, 233, 0.1)', 
          border: '1px solid rgba(14, 165, 233, 0.2)',
          color: 'var(--accent-blue)',
          fontWeight: 'bold',
          fontSize: '0.8rem',
          marginBottom: '20px',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        <BrainCircuit size={16} />
        AI RESUME MATCHER
      </motion.div>
      
      <h1 className="gradient-text">
        AI <span style={{ color: '#fff' }}>Matcher</span>
      </h1>
      <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '600px', margin: '20px auto' }}>
        AI-driven semantic analysis to align your professional profile with top job opportunities.
      </p>
    </header>
  );
};

export default Header;
