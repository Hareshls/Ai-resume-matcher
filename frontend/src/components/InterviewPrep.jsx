import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCcw } from 'lucide-react';

const InterviewPrep = ({ interviewPrep }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card" 
      style={{ 
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(14, 165, 233, 0.1))',
        borderTop: '4px solid var(--accent-purple)',
        marginTop: '1rem'
      }}
    >
      <h3 className="section-title">
        <RefreshCcw size={20} style={{ color: 'var(--accent-purple)' }} /> Recruiters Likely Questions
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem', fontStyle: 'italic' }}>
        Based on your profile, be prepared for these "Pressure Test" questions:
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {interviewPrep?.map((q, i) => (
          <div key={i} style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '20px', border: '1px solid var(--glass-border)', display: 'flex', gap: '1rem' }}>
            <div style={{ fontWeight: '900', color: 'var(--accent-purple)', fontSize: '1.2rem' }}>0{i+1}</div>
            <p style={{ fontSize: '0.9rem', color: '#fff', fontWeight: '500', lineHeight: '1.4' }}>{q}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default InterviewPrep;
