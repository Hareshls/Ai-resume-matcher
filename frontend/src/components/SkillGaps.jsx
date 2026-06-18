import React, { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const SkillGaps = ({ missingSkills = [], mainSkills = [] }) => {
  const critical = missingSkills.filter(s => s.severity === 'critical');
  const moderate = missingSkills.filter(s => s.severity === 'moderate');
  const minor = missingSkills.filter(s => s.severity === 'minor');

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
      flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', flexShrink: 0 }}>
        <div style={{ background: 'rgba(14, 165, 233, 0.1)', padding: '10px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <CheckCircle2 size={24} className="text-cyan" />
        </div>
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#fff', margin: 0 }}>Skill Gaps</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>What's missing, by severity</p>
        </div>
      </div>

      {/* Two Columns */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
        gap: isMobile ? '1.5rem' : '2rem',
        flex: isMobile ? 'none' : 1,
        minHeight: 0,
      }}>
        {/* Left Column - Breakdown */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflowY: isMobile ? 'visible' : 'auto', paddingRight: isMobile ? 0 : '0.5rem' }}>

          {/* Critical */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <XCircle size={16} color="#ef4444" />
              <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.75rem', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', color: '#ef4444', borderRadius: '100px', fontWeight: '600' }}>
                Critical gaps · {critical.length}
              </span>
            </div>
            {critical.length > 0 ? critical.map((skill, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '1.25rem', borderRadius: '12px' }}>
                <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem', marginTop: 0 }}>{skill.skill || skill}</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5', margin: 0 }}>{skill.reason || "Missing requirement detected."}</p>
              </div>
            )) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '1.5rem' }}>None detected. Strong fit here.</p>
            )}
          </div>

          {/* Moderate */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={16} color="#eab308" />
              <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.75rem', background: 'rgba(234,179,8,0.1)', border: '1px solid rgba(234,179,8,0.2)', color: '#eab308', borderRadius: '100px', fontWeight: '600' }}>
                Moderate gaps · {moderate.length}
              </span>
            </div>
            {moderate.length > 0 ? moderate.map((skill, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '1.25rem', borderRadius: '12px' }}>
                <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem', marginTop: 0 }}>{skill.skill || skill}</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5', margin: 0 }}>{skill.reason || "Preferred qualification missing."}</p>
              </div>
            )) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '1.5rem' }}>None detected. Strong fit here.</p>
            )}
          </div>

          {/* Minor */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <XCircle size={16} color="var(--text-muted)" />
              <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)', borderRadius: '100px', fontWeight: '600' }}>
                Minor gaps · {minor.length}
              </span>
            </div>
            {minor.length > 0 ? minor.map((skill, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '1.25rem', borderRadius: '12px' }}>
                <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem', marginTop: 0 }}>{skill.skill || skill}</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5', margin: 0 }}>{skill.reason || "Nice-to-have skill missing."}</p>
              </div>
            )) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0 0 0 1.5rem' }}>None detected. Strong fit here.</p>
            )}
          </div>

        </div>

        {/* Right Column - Skill Tags */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', overflowY: isMobile ? 'visible' : 'auto', paddingRight: isMobile ? 0 : '0.5rem' }}>

          {/* Present Skills */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <CheckCircle2 size={16} color="#10b981" />
              <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.75rem', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', color: '#10b981', borderRadius: '100px', fontWeight: '600' }}>
                Present · {mainSkills.length}
              </span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {mainSkills.map((skill, i) => (
                <span key={i} style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', color: '#10b981', borderRadius: '8px', fontWeight: '500' }}>
                  {skill.skill || skill}
                </span>
              ))}
              {mainSkills.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No required skills found.</span>}
            </div>
          </div>

          {/* All Missing */}
          <div>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '500', marginBottom: '1rem', marginTop: 0 }}>
              All missing ({missingSkills.length}):
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {missingSkills.map((skill, i) => (
                <span key={i} style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem', background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', borderRadius: '8px', fontWeight: '500' }}>
                  {skill.skill || skill}
                </span>
              ))}
              {missingSkills.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No missing skills!</span>}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default SkillGaps;
