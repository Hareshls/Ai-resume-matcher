import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileEdit } from 'lucide-react';

const ResumeOptimizer = ({ optimizedBullets }) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 600);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth <= 600);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  return (
    <div className="glass-card" style={{ 
      padding: isMobile ? '1.25rem' : '2rem', 
      height: isMobile ? 'auto' : '550px', 
      display: 'flex', 
      flexDirection: 'column' 
    }}>
      <div style={{ flexShrink: 0 }}>
        <h3 className="section-title">
          <FileEdit size={20} /> Resume Optimizer
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          Add these tailored bullets to your resume to instantly boost your match score.
        </p>
      </div>
      
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '1rem', 
        overflowY: isMobile ? 'visible' : 'auto', 
        paddingRight: isMobile ? 0 : '0.5rem', 
        flex: isMobile ? 'none' : 1, 
        minHeight: 0 
      }}>
        {optimizedBullets?.map((item, i) => {
          const topic = typeof item === 'object' && item.topic ? item.topic : `SUGGESTION ${i + 1}`;
          const bulletText = typeof item === 'string' ? item : item.bullet || item.text || JSON.stringify(item);
          
          return (
            <motion.div 
              key={i}
              whileHover={{ x: 5 }}
              style={{ 
                background: 'rgba(255, 255, 255, 0.02)', 
                borderRadius: '12px', 
                border: '1px solid rgba(255, 255, 255, 0.05)',
                overflow: 'hidden'
              }}
            >
              <div style={{ padding: '0.5rem 1rem', background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', fontSize: '0.7rem', fontWeight: '800', color: 'var(--primary)', letterSpacing: '1px' }}>
                {topic}
              </div>
              <div style={{ padding: '1rem', fontSize: '0.9rem', color: '#fff', lineHeight: '1.6' }}>
                <span style={{ color: 'var(--primary)', marginRight: '0.5rem' }}>•</span>
                {bulletText}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default ResumeOptimizer;
