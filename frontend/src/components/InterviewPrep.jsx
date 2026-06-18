import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';

const InterviewPrep = ({ interviewPrep }) => {
  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <h3 className="section-title">
        <MessageSquare size={20} /> INTERVIEW PREP
      </h3>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Anticipate these questions based on your profile's gaps and strengths.
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {interviewPrep?.map((item, i) => {
          const questionText = typeof item === 'string' ? item : item.question || item.text || JSON.stringify(item);
          const topic = item.topic || 'General';
          const difficulty = item.difficulty || 'Medium';

          let difficultyColor = '#f59e0b';
          let difficultyBg = 'rgba(245, 158, 11, 0.1)';
          if (difficulty.toLowerCase() === 'hard') {
            difficultyColor = 'var(--error)';
            difficultyBg = 'rgba(239, 68, 68, 0.1)';
          } else if (difficulty.toLowerCase() === 'easy') {
            difficultyColor = 'var(--success)';
            difficultyBg = 'rgba(16, 185, 129, 0.1)';
          }

          return (
            <motion.div 
              key={i}
              whileHover={{ x: 5 }}
              style={{ 
                background: 'rgba(255, 255, 255, 0.02)', 
                borderRadius: '16px', 
                border: '1px solid rgba(255, 255, 255, 0.05)',
                padding: '1.25rem',
                display: 'flex',
                gap: '1rem'
              }}
            >
              <div style={{ fontSize: '1.5rem', fontWeight: '900', color: 'rgba(255,255,255,0.1)' }}>
                {String(i + 1).padStart(2, '0')}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
                <p style={{ fontSize: '0.9rem', color: '#fff', fontWeight: '500', lineHeight: '1.5' }}>
                  {questionText}
                </p>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.65rem', fontWeight: '700', padding: '0.2rem 0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    {topic}
                  </span>
                  <span style={{ fontSize: '0.65rem', fontWeight: '700', padding: '0.2rem 0.5rem', background: difficultyBg, borderRadius: '4px', color: difficultyColor, textTransform: 'uppercase' }}>
                    {difficulty}
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default InterviewPrep;
