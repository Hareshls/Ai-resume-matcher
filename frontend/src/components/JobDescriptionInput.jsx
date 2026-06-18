import React, { useState } from 'react';
import { Upload, Briefcase } from 'lucide-react';

const JobDescriptionInput = ({ jobFile, jobDescription, onJobFileChange, onRemoveJobFile, onDescriptionChange }) => {
  const [mode, setMode] = useState('text'); // 'file' or 'text'

  return (
    <div className="input-card">
      <div className="input-header">
        <div className="input-title">
          <div className="logo-icon-container" style={{ padding: '6px' }}>
            <Briefcase size={18} className="input-icon" />
          </div>
          <div>
            <div style={{ fontSize: '1rem', fontWeight: '700' }}>Job Description</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF or TXT</div>
          </div>
        </div>
        
        <div className="input-toggle">
          <button 
            className={`toggle-btn ${mode === 'file' ? 'active' : ''}`}
            onClick={() => setMode('file')}
          >
            File
          </button>
          <button 
            className={`toggle-btn ${mode === 'text' ? 'active' : ''}`}
            onClick={() => setMode('text')}
          >
            Text
          </button>
        </div>
      </div>
      
      {mode === 'file' ? (
        <div 
          className="upload-zone"
          onClick={() => !jobFile && document.getElementById('job-upload').click()}
          style={{ borderColor: jobFile ? 'var(--primary)' : 'rgba(255, 255, 255, 0.2)' }}
        >
          <input 
            id="job-upload" 
            type="file" 
            onChange={(e) => onJobFileChange(e.target.files[0])} 
            style={{ display: 'none' }} 
            accept=".pdf,.txt" 
          />
          {jobFile ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <div className="logo-icon-container"><Briefcase size={24} className="input-icon" /></div>
              <span style={{ fontSize: '0.9rem', fontWeight: '700' }}>{jobFile.name}</span>
              <button 
                onClick={(e) => { e.stopPropagation(); onRemoveJobFile(); }} 
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
                <span style={{ fontWeight: '600' }}>Drop your JD</span> <span style={{ color: 'var(--text-muted)' }}>or click to browse</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF or TXT · up to ~10MB</div>
            </>
          )}
        </div>
      ) : (
        <textarea 
          className="job-textarea"
          value={jobDescription}
          onChange={(e) => onDescriptionChange(e.target.value)}
          placeholder="Paste the job description here..."
        />
      )}
    </div>
  );
};

export default JobDescriptionInput;

