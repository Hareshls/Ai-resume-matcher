import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const ResumeOptimizer = ({ optimizedBullets }) => {
  return (
    <div className="glass-card" style={{ gridColumn: '1 / -1', borderLeft: '4px solid var(--primary)' }}>
      <h3 className="section-title">
        <Sparkles size={20} style={{ color: 'var(--primary)' }} /> AI Resume Optimizer
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem', fontStyle: 'italic' }}>
        Copy and adapt these bullet points to your resume to increase your match density:
      </p>
      <div style={{ display: 'grid', gap: '1rem' }}>
        {optimizedBullets?.map((bullet, i) => (
          <motion.div 
            key={i}
            whileHover={{ x: 5 }}
            style={{ 
              padding: '1rem', 
              background: 'rgba(14, 165, 233, 0.05)', 
              borderRadius: '12px', 
              border: '1px solid rgba(14, 165, 233, 0.1)',
              fontSize: '0.85rem',
              color: '#fff',
              lineHeight: '1.5',
              position: 'relative'
            }}
          >
            <div style={{ position: 'absolute', left: '-5px', top: '50%', transform: 'translateY(-50%)', width: '3px', height: '60%', background: 'var(--primary)', borderRadius: '10px' }}></div>
            "{bullet}"
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ResumeOptimizer;
