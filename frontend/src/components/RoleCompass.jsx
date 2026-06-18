import React from 'react';
import { motion } from 'framer-motion';
import { Compass } from 'lucide-react';

const RoleCompass = ({ recommendedRoles }) => {
  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <h3 className="section-title">
        <Compass size={20} /> ROLE COMPASS
      </h3>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Alternative job titles that strongly align with your extracted skills.
      </p>
      
      <div style={{ display: 'grid', gap: '1rem' }}>
        {recommendedRoles?.map((r, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            key={i} 
            style={{ 
              background: 'rgba(255, 255, 255, 0.02)', 
              borderRadius: '12px', 
              border: '1px solid rgba(255, 255, 255, 0.05)',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '1rem', fontWeight: '700', color: '#fff' }}>{typeof r === 'string' ? r : r.role}</span>
              <span style={{ fontSize: '0.75rem', fontWeight: '800', color: 'var(--primary)', background: 'rgba(14, 165, 233, 0.1)', padding: '0.2rem 0.6rem', borderRadius: '100px' }}>
                {typeof r === 'object' && typeof r.match !== 'function' ? r.match : ''} Match
              </span>
            </div>
            
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', lineHeight: '1.4' }}>
              "{typeof r === 'object' ? r.reason : ''}"
            </p>
            
            <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden', marginTop: '0.25rem' }}>
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: typeof r === 'object' && typeof r.match !== 'function' ? r.match : 0 }}
                style={{ height: '100%', background: 'var(--primary)', borderRadius: '2px' }}
              />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RoleCompass;
