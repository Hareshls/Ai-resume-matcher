import React from 'react';
import { Upload, FileText } from 'lucide-react';

const ResumeInput = ({ file, textContent, onFileChange, onRemoveFile }) => {
  return (
    <div className="input-card">
      <div className="input-header">
        <div className="input-title">
          <div className="logo-icon-container" style={{ padding: '6px' }}>
            <FileText size={18} className="input-icon" />
          </div>
          <div>
            <div style={{ fontSize: '1rem', fontWeight: '700' }}>Your Resume</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF or TXT</div>
          </div>
        </div>
      </div>
      
      <div 
        className="upload-zone"
        onClick={() => !file && document.getElementById('resume-upload').click()}
        style={{ borderColor: file ? 'var(--primary)' : 'rgba(255, 255, 255, 0.2)' }}
      >
        <input 
          id="resume-upload" 
          type="file" 
          onChange={(e) => onFileChange(e.target.files[0])} 
          style={{ display: 'none' }} 
          accept=".pdf,.txt" 
        />
        {file ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <div className="logo-icon-container"><FileText size={24} className="input-icon" /></div>
            <span style={{ fontSize: '0.9rem', fontWeight: '700' }}>{file.name}</span>
            <button 
              onClick={(e) => { e.stopPropagation(); onRemoveFile(); }} 
              style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer' }}
            >
              Remove File
            </button>
          </div>
        ) : (
          <>
            <div className="logo-icon-container" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}>
              <Upload size={24} />
            </div>
            <div>
              <span style={{ fontWeight: '600' }}>Drop your resume</span> <span style={{ color: 'var(--text-muted)' }}>or click to browse</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF or TXT · up to ~10MB</div>
          </>
        )}
      </div>
    </div>
  );
};

export default ResumeInput;
