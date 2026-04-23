import React from 'react';
import { Upload, FileText } from 'lucide-react';

const JobDescriptionInput = ({ jobFile, jobDescription, onJobFileChange, onRemoveJobFile, onDescriptionChange }) => {
  return (
    <div className="glass-card">
      <h3 className="section-title">
        <span style={{ color: 'var(--accent-blue)' }}>02.</span> Job Description
      </h3>
      
      {/* JD File Option */}
      <div 
        className="upload-zone"
        onClick={() => !jobFile && document.getElementById('job-upload').click()}
        style={{ 
          borderColor: jobFile ? 'var(--primary)' : 'var(--glass-border)',
          background: jobFile ? 'rgba(14, 165, 233, 0.05)' : 'rgba(0,0,0,0.1)',
          padding: '1rem',
          marginBottom: '1rem'
        }}
      >
        <input 
          id="job-upload" 
          type="file" 
          onChange={(e) => onJobFileChange(e.target.files[0])} 
          style={{ display: 'none' }} 
          accept=".pdf,.txt" 
        />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
          {jobFile ? <FileText size={18} style={{ color: 'var(--primary)' }} /> : <Upload size={18} style={{ color: 'var(--text-muted)' }} />}
          <span style={{ fontSize: '0.8rem', fontWeight: '700' }}>{jobFile ? jobFile.name : "Upload JD Document (Optional)"}</span>
          {jobFile && (
            <button 
              onClick={(e) => { e.stopPropagation(); onRemoveJobFile(); }} 
              style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer' }}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {!jobFile && (
        <textarea 
          className="job-textarea"
          style={{ height: '140px' }}
          value={jobDescription}
          onChange={(e) => onDescriptionChange(e.target.value)}
          placeholder="Or paste the job description text here..."
        />
      )}
    </div>
  );
};

export default JobDescriptionInput;
