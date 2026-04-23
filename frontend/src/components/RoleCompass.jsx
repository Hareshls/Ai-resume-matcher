import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const RoleCompass = ({ recommendedRoles }) => {
  return (
    <div className="glass-card">
      <h3 className="section-title">
        <Sparkles size={20} style={{ color: 'var(--accent-blue)' }} /> Role Compass
      </h3>
      <div className="role-grid">
        {recommendedRoles?.map((r, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            key={i} 
            className="role-card"
          >
            <div className="role-header">
              <span className="role-title">{r.role}</span>
              <span className="match-badge">{r.match}</span>
            </div>
            <p className="role-reason">"{r.reason}"</p>
            <div className="match-progress-container">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: r.match }}
                className="match-progress-bar"
              />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RoleCompass;
