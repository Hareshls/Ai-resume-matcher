import React from 'react';
import { RefreshCcw } from 'lucide-react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer 
} from 'recharts';

const MatchScore = ({ result, onReset }) => {
  return (
    <div className="glass-card" style={{ position: 'relative', overflow: 'hidden', padding: '3rem 2rem' }}>
      <div style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', zIndex: 10 }}>
        <button 
          onClick={onReset} 
          style={{ padding: '10px', background: 'rgba(255,255,255,0.05)', border: 'none', color: 'var(--text-muted)', borderRadius: '50%', cursor: 'pointer' }}
        >
          <RefreshCcw size={20} />
        </button>
      </div>
      
      <div className="main-grid" style={{ alignItems: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: '900', color: 'var(--accent-blue)', letterSpacing: '0.2em', textTransform: 'uppercase' }}>Current Match Grade</div>
          <div className="score-badge gradient-text">{result.match_score}%</div>
          
          <p style={{ color: 'var(--text-muted)', maxWidth: '400px', margin: '0 auto', fontStyle: 'italic', fontSize: '1rem' }}>
            "{result.summary}"
          </p>
        </div>

        {/* Radar Chart */}
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={result.radar_data}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
              <Radar
                name="Resume"
                dataKey="A"
                stroke="var(--primary)"
                fill="var(--primary)"
                fillOpacity={0.5}
              />
              <Radar
                name="Job"
                dataKey="B"
                stroke="var(--accent-purple)"
                fill="var(--accent-purple)"
                fillOpacity={0.3}
              />
            </RadarChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', fontSize: '0.7rem', fontWeight: 'bold' }}>
            <span style={{ color: 'var(--primary)' }}>● YOUR RESUME</span>
            <span style={{ color: 'var(--accent-purple)' }}>● JOB REQUIREMENTS</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MatchScore;
