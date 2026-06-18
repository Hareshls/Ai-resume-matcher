import React, { useState, useEffect } from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

const MatchScore = ({ result }) => {
  const matchScore = result.match_score || 0;

  const [isMobile, setIsMobile] = useState(window.innerWidth <= 700);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth <= 700);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  // Prepare data for the donut chart
  const donutData = [
    { name: 'Score', value: matchScore },
    { name: 'Remaining', value: 100 - matchScore }
  ];
  const COLORS = ['#0ea5e9', 'rgba(255, 255, 255, 0.05)'];

  // Prepare data for the category breakdown (Progress bars)
  const subScores = result.sub_scores || {};
  const maxScores = {
    "Technical": 50,
    "Experience": 30,
    "Education": 10,
    "Keywords": 10
  };

  const categories = Object.keys(subScores).map(key => ({
    name: key,
    score: subScores[key],
    max: maxScores[key] || 10,
    percentage: Math.min(100, Math.round((subScores[key] / (maxScores[key] || 10)) * 100))
  }));

  return (
    <div className="glass-card" style={{ padding: isMobile ? '1.25rem' : '2rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr 1fr',
        gap: isMobile ? '1.5rem' : '2rem',
        alignItems: 'center',
      }}>

        {/* Left: Overall Score Donut */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ position: 'relative', width: isMobile ? '160px' : '200px', height: isMobile ? '160px' : '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={isMobile ? 55 : 70}
                  outerRadius={isMobile ? 72 : 90}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
            }}>
              <span style={{ fontSize: isMobile ? '2.2rem' : '3rem', fontWeight: '800', lineHeight: 1, color: '#fff' }}>
                {matchScore}%
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginTop: '0.25rem' }}>
                Overall Match
              </span>
            </div>
          </div>
        </div>

        {/* Middle: Radar Chart */}
        {result.radar_data && result.radar_data.length > 0 && (
          <div style={{
            height: '220px',
            width: '100%',
            borderLeft: isMobile ? 'none' : '1px solid rgba(255,255,255,0.05)',
            borderRight: isMobile ? 'none' : '1px solid rgba(255,255,255,0.05)',
            borderTop: isMobile ? '1px solid rgba(255,255,255,0.05)' : 'none',
            borderBottom: isMobile ? '1px solid rgba(255,255,255,0.05)' : 'none',
            padding: isMobile ? '1rem 0' : '0 1rem',
          }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={result.radar_data}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <Radar
                  name="Resume"
                  dataKey="A"
                  stroke="var(--primary)"
                  fill="var(--primary)"
                  fillOpacity={0.5}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Right: Category Breakdown */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', paddingLeft: isMobile ? 0 : '1rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.5rem' }}>
            Category Breakdown
          </div>

          {categories.map((cat, idx) => (
            <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: '600' }}>
                <span style={{ color: '#fff' }}>{cat.name}</span>
                <span style={{ color: 'var(--text-muted)' }}>{cat.score} / {cat.max}</span>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{
                  width: `${cat.percentage}%`,
                  height: '100%',
                  background: 'var(--primary)',
                  borderRadius: '3px',
                  boxShadow: '0 0 10px rgba(14, 165, 233, 0.5)'
                }}></div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default MatchScore;
