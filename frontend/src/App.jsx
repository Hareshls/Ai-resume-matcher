import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertCircle, RefreshCcw, Sparkles
} from 'lucide-react';

// Components
import Header from './components/Header';
import ResumeInput from './components/ResumeInput';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumePreview from './components/ResumePreview';
import MatchScore from './components/MatchScore';
import ResumeOptimizer from './components/ResumeOptimizer';
import SkillGaps from './components/SkillGaps';
import RoleCompass from './components/RoleCompass';
import InterviewPrep from './components/InterviewPrep';

const App = () => {
  const [file, setFile] = useState(null);
  const [jobFile, setJobFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [textContent, setTextContent] = useState("");
  const [showLanding, setShowLanding] = useState(true);

  useEffect(() => {
    if (file) {
      if (file.type === "application/pdf") {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        setTextContent("");
        return () => URL.revokeObjectURL(url);
      } else {
        setPreviewUrl(null);
        const reader = new FileReader();
        reader.onload = (e) => setTextContent(e.target.result);
        reader.readAsText(file);
      }
    } else {
      setPreviewUrl(null);
      setTextContent("");
    }
  }, [file]);

  const handleMatch = async () => {
    if (!file && !result) {
      if (!file && !jobFile && !jobDescription) {
        setError('Please provide a resume and job description.');
        return;
      }
    }
    setLoading(true);
    const formData = new FormData();
    if (file) formData.append('resume_file', file);
    if (jobFile) formData.append('job_file', jobFile);
    if (jobDescription) formData.append('job_description', jobDescription);

    try {
      const response = await axios.post('http://localhost:8000/match', formData);
      setResult(response.data);
      setError('');
    } catch (err) {
      setError('Failed to analyze. The AI engine might be waking up (Render free tier) or check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {!showLanding && <Header />}

      <main>
        <AnimatePresence>
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="processing-overlay"
            >
              <div className="loader-circle"></div>
              <div className="processing-text">AI IS ANALYZING YOUR MATCH...</div>
              <motion.div 
                animate={{ y: [0, 10, 0] }} 
                transition={{ repeat: Infinity, duration: 2 }}
                style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}
              >
                Auditing skills, optimizing bullets, and predicting interview questions
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {showLanding ? (
            <motion.div
              key="landing-page"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              className="landing-container"
            >
              <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="landing-content"
              >
                <div className="landing-badge">
                  <Sparkles size={16} /> <span>AI-Powered Career Intelligence</span>
                </div>
                <h1 className="landing-title">
                  Bridge the gap between <br />
                  <span className="text-gradient-cyan">your resume and your dream job.</span>
                </h1>
                <p className="landing-subtitle">
                  Our smart AI analyzes your resume against any job description, 
                  refines your bullet points, and predicts interview questions—all in seconds.
                </p>
                <div className="landing-actions">
                  <button 
                    className="btn-primary landing-btn"
                    onClick={() => setShowLanding(false)}
                  >
                    GET STARTED <Sparkles size={20} />
                  </button>
                </div>
              </motion.div>

              <motion.div 
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 0.5, scale: 1 }}
                transition={{ delay: 0.4, duration: 1 }}
                className="landing-visual-glow"
              />
            </motion.div>
          ) : !result ? (
            <motion.div 
              key="input-view"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="main-grid"
            >
              {/* Left Side: Inputs */}
              <div style={{ display: 'grid', gap: '2rem' }}>
                <ResumeInput 
                  file={file} 
                  onFileChange={(f) => { setFile(f); setError(''); }} 
                  onRemoveFile={() => setFile(null)} 
                />

                <JobDescriptionInput 
                  jobFile={jobFile}
                  jobDescription={jobDescription}
                  onJobFileChange={setJobFile}
                  onRemoveJobFile={() => setJobFile(null)}
                  onDescriptionChange={setJobDescription}
                />

                {error && (
                  <div style={{ padding: '15px', background: 'rgba(248, 113, 113, 0.1)', border: '1px solid var(--error)', borderRadius: '14px', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
                    <AlertCircle size={18} /> {error}
                  </div>
                )}

                <button 
                  className="btn-primary" 
                  onClick={handleMatch}
                  disabled={loading}
                  style={loading ? { opacity: 0.7, cursor: 'not-allowed' } : {}}
                >
                  {loading ? <RefreshCcw className="animate-spin" /> : <Sparkles size={22} />}
                  {loading ? "PROCESSING..." : "ANALYZE MATCH"}
                </button>
              </div>

              {/* Right Side: Live Preview */}
              <div style={{ position: 'relative' }}>
                {loading && <div className="scanning-line"></div>}
                <ResumePreview 
                  file={file}
                  previewUrl={previewUrl}
                  textContent={textContent}
                />
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="result-view"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: 20 }}
              style={{ display: 'grid', gap: '2rem' }}
            >
              <MatchScore result={result} onReset={() => setResult(null)} />

              <div className="main-grid" style={{ marginBottom: '2rem' }}>
                <ResumeOptimizer optimizedBullets={result.optimized_bullets} />
                <SkillGaps missingSkills={result.missing_skills} suggestions={result.suggestions} />
                <RoleCompass recommendedRoles={result.recommended_roles} />
              </div>

              <InterviewPrep interviewPrep={result.interview_prep} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
