import React from 'react';
import { FileText } from 'lucide-react';

const ResumePreview = ({ file, previewUrl, textContent }) => {
  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', padding: '1.5rem' }}>
      <h3 className="section-title" style={{ marginBottom: '1rem' }}>
        <FileText size={20} style={{ color: 'var(--accent-blue)' }} /> Resume Preview
      </h3>
      
      <div className="preview-container">
        {file ? (
          previewUrl ? (
            <iframe 
              src={`${previewUrl}#toolbar=0&navpanes=0&scrollbar=0`} 
              className="preview-frame" 
              title="Resume Preview"
            />
          ) : (
            <div className="preview-text">
              {textContent}
            </div>
          )
        ) : (
          <div className="preview-placeholder">
            <div style={{ opacity: 0.1 }}>
              <FileText size={80} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p style={{ fontWeight: '700', fontSize: '1rem' }}>No File Selected</p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Upload your resume to see a live preview in this section.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumePreview;
