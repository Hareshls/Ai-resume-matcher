import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, ChevronRight } from 'lucide-react';

const SkillGaps = ({ missingSkills, suggestions }) => {
  return (
    <div className="glass-card">
      <h3 className="section-title" style={{ color: 'var(--error)' }}>
        <AlertCircle size={20} /> Skill Gaps
      </h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '2rem' }}>
        {missingSkills?.map((s, i) => (
          <motion.span 
            key={i} 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            style={{ 
              padding: '5px 12px', 
              background: 'rgba(248, 113, 113, 0.08)', 
              border: '1px solid rgba(248, 113, 113, 0.2)', 
              color: 'var(--error)', 
              borderRadius: '100px', 
              fontSize: '0.7rem', 
              fontWeight: '600'
            }}
          >
            {s}
          </motion.span>
        ))}
      </div>
      <div style={{ paddingTop: '20px', borderTop: '1px solid var(--glass-border)' }}>
        <h4 style={{ fontSize: '0.8rem', fontWeight: '900', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '15px' }}>How to bridge</h4>
        <ul style={{ listStyle: 'none', display: 'grid', gap: '12px' }}>
          {suggestions?.map((s, i) => (
            <li key={i} style={{ display: 'flex', gap: '10px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <ChevronRight size={16} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '4px' }} /> {s}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SkillGaps;
