import React from 'react';
import { Upload, FileText } from 'lucide-react';

const ResumeInput = ({ file, onFileChange, onRemoveFile }) => {
  return (
    <div className="glass-card">
      <h3 className="section-title">
        <span style={{ color: 'var(--accent-blue)' }}>01.</span> Resume Input
      </h3>
      <div 
        className="upload-zone"
        onClick={() => !file && document.getElementById('file-upload').click()}
        style={file ? { borderColor: 'var(--primary)', background: 'rgba(14, 165, 233, 0.05)', padding: '1.5rem' } : { padding: '2rem' }}
      >
        <input 
          id="file-upload" 
          type="file" 
          onChange={(e) => onFileChange(e.target.files[0])} 
          style={{ display: 'none' }} 
          accept=".pdf,.txt" 
        />
        {!file ? (
          <>
            <div style={{ color: 'var(--text-muted)', marginBottom: '10px' }}><Upload size={32} /></div>
            <p style={{ fontWeight: '700', fontSize: '0.9rem', color: '#fff' }}>Upload Resume (PDF/TXT)</p>
          </>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
            <FileText size={24} style={{ color: 'var(--primary)' }} />
            <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>{file.name}</span>
            <button 
              onClick={(e) => { e.stopPropagation(); onRemoveFile(); }} 
              style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer', fontSize: '0.7rem' }}
            >
              ✕
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeInput;
