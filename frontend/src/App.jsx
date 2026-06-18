import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertCircle, RefreshCcw, Sparkles, Zap, Play, CheckCircle, FileText, Code, BarChart2
} from 'lucide-react';

// Components
import Header from './components/Header';
import ResumeInput from './components/ResumeInput';
import JobDescriptionInput from './components/JobDescriptionInput';
import MatchScore from './components/MatchScore';
import ResumeOptimizer from './components/ResumeOptimizer';
import SkillGaps from './components/SkillGaps';
import RoleCompass from './components/RoleCompass';
import InterviewPrep from './components/InterviewPrep';
import LoadingScreen from './components/LoadingScreen';
import demoVideo from './assets/Recording 2026-06-18 162951 - Trim.mp4';

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : 'https://ai-resume-matcher-klto.onrender.com';

const App = () => {
  const [file, setFile] = useState(null);
  const [jobFile, setJobFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'inputs', 'results'
  const [isLandingMode, setIsLandingMode] = useState(true); // overflow lock (600ms)
  const [isLandingWide, setIsLandingWide] = useState(true);  // max-width:1600px (instant reset)
  const [showDemoModal, setShowDemoModal] = useState(false);
  const [pendingResult, setPendingResult] = useState(null); // result waiting for anim to finish

  const navigateToInputs = () => {
    setCurrentView('inputs');
    setTimeout(() => setIsLandingWide(false), 450);  // after exit anim (450ms) → inputs enters at 1280px
    setTimeout(() => setIsLandingMode(false), 650);  // after full transition → unlock overflow
  };

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
      const response = await axios.post(`${API_URL}/match`, formData);
      setPendingResult(response.data); // store result — navigation happens via onComplete
      setError('');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
        if (err.response.status === 429) {
          alert(err.response.data.detail);
        }
      } else {
        setError('Failed to analyze. The AI engine might be waking up (Render free tier) or check your connection.');
      }
      setLoading(false); // only hide loader on error
    }
  };

  const handleLoadingComplete = () => {
    setResult(pendingResult);
    setPendingResult(null);
    setLoading(false);
    setCurrentView('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoadSampleData = () => {
    setJobDescription("We are looking for a Senior Frontend Engineer with 5+ years of experience in React, TypeScript, and modern CSS frameworks. You should have a deep understanding of web performance, accessibility, and state management. Experience with Node.js and AWS is a strong plus.");
  };

  return (
    <div className={`app-container${isLandingMode ? ' landing-mode' : ''}${isLandingWide ? ' landing-wide' : ''}${currentView === 'results' ? ' results-mode' : ''}`}>
      <div className="grid-background"></div>
      
      <Header onStartClick={() => navigateToInputs()} currentView={currentView} />

      <main style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
        <AnimatePresence>
          {loading && (
            <LoadingScreen
              apiComplete={!!pendingResult}
              onComplete={handleLoadingComplete}
            />
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {currentView === 'landing' && (
            <motion.div
              key="landing-page"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } }}
              exit={{ opacity: 0, scale: 1.06, filter: 'blur(8px)', transition: { duration: 0.45, ease: [0.4, 0, 1, 1] } }}
              style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}
            >
              <div className="hero-section">
                <div className="hero-content">
                  <div className="hero-badge">
                    <span className="badge-dot"></span> Three-pass AI rubric · powered by LLaMA 3.3
                  </div>
                  
                  <h1 className="hero-title">
                    Know exactly where your resume stands <span className="text-gradient-cyan">before you apply.</span>
                  </h1>
                  
                  <p className="hero-subtitle">
                    Career Lens AI reads your resume and the job description, runs a strict inventory &rarr; gap analysis &rarr; scoring rubric, and hands back a match score, skill gaps, tailored bullets, alternative roles, and interview questions.
                  </p>

                  <div className="hero-actions">
                    <button className="btn-cyan btn-large" onClick={() => navigateToInputs()}>
                      Analyze my resume &rarr;
                    </button>
                    <button className="btn-dark btn-large" onClick={() => setShowDemoModal(true)}>
                      <Play size={16} fill="currentColor" /> Try a demo analysis
                    </button>
                  </div>

                  <div className="hero-features">
                    <span><CheckCircle size={16} className="text-success" /> No sign-up</span>
                    <span><Zap size={16} className="text-cyan" /> Sub-second results</span>
                  </div>
                </div>

                <div className="hero-visual">
                  <div className="orbit-container">
                    <div className="orbit-ring ring-1"></div>
                    <div className="orbit-ring ring-2"></div>
                    <div className="orbit-ring ring-3"></div>
                    
                    <div className="score-card-center">
                      <div className="score-label">MATCH SCORE</div>
                      <div className="score-value">87</div>
                      <div className="score-sub">out of 100</div>
                      <div className="score-progress">
                        <div className="score-progress-fill"></div>
                      </div>
                      <div className="score-badge-bottom">+12 skills</div>
                    </div>
                    
                    <div className="orbit-dot dot-react">React</div>
                    <div className="orbit-dot dot-python">Python</div>
                    <div className="orbit-dot dot-sql">SQL</div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {currentView === 'inputs' && (
            <motion.div
              key="inputs-page"
              initial={{ opacity: 0, y: 50, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] } }}
              exit={{ opacity: 0, y: -30, transition: { duration: 0.3, ease: [0.4, 0, 1, 1] } }}
              className="analyzer-view"
            >
              <div className="analyzer-header">
                <div className="analyzer-label">RESUME ANALYZER</div>
                <h2 className="analyzer-title">Drop your resume and target job</h2>
                <p className="analyzer-subtitle">Files are read locally in your browser. Nothing is sent until you run the analysis.</p>
              </div>

              <div className="inputs-grid">
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
              </div>

              {error && (
                <div className="error-banner">
                  <AlertCircle size={18} /> {error}
                </div>
              )}

              <div className="analyzer-actions">
                <button className="btn-dark" onClick={handleLoadSampleData}>
                  <Sparkles size={16} /> Load sample data
                </button>
                <button 
                  className="btn-cyan btn-large" 
                  onClick={handleMatch}
                  disabled={loading}
                >
                  {loading ? <RefreshCcw className="animate-spin" /> : <Sparkles size={18} />}
                  {loading ? "PROCESSING..." : "Run analysis"}
                </button>
              </div>
            </motion.div>
          )}

          {currentView === 'results' && result && (
            <motion.div 
              key="result-view" 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="results-view-container"
            >
              <div className="results-page-header">
                <div>
                  <div className="status-badge"><CheckCircle size={14} className="text-cyan" /> ANALYSIS COMPLETE</div>
                  <h2 className="results-title">Your match report</h2>
                </div>
                <div className="results-header-actions">
                  <button className="btn-dark" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                    &uarr; Top
                  </button>
                  <button className="btn-cyan" onClick={() => { setResult(null); setCurrentView('inputs'); window.scrollTo({ top: 0 }); }}>
                    <RefreshCcw size={16} /> New analysis
                  </button>
                </div>
              </div>

              <MatchScore result={result} />

              <div className="results-dashboard-grid">
                <div className="results-col-left">
                  <SkillGaps missingSkills={result.missing_skills || []} mainSkills={result.main_skills || []} />
                  {result.recommended_roles && result.recommended_roles.length > 0 && <RoleCompass recommendedRoles={result.recommended_roles} />}
                </div>
                <div className="results-col-right">
                  {result.optimized_bullets && result.optimized_bullets.length > 0 && <ResumeOptimizer optimizedBullets={result.optimized_bullets} />}
                  {result.interview_prep && result.interview_prep.length > 0 && <InterviewPrep interviewPrep={result.interview_prep} />}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Demo Video Modal */}
      <AnimatePresence>
        {showDemoModal && (
          <motion.div
            key="demo-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={() => setShowDemoModal(false)}
            style={{
              position: 'fixed', inset: 0, zIndex: 9999,
              background: 'rgba(0,0,0,0.85)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              backdropFilter: 'blur(6px)',
            }}
          >
            <motion.div
              initial={{ scale: 0.88, opacity: 0, y: 30 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.88, opacity: 0, y: 30 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              onClick={e => e.stopPropagation()}
              style={{
                position: 'relative', borderRadius: '16px', overflow: 'hidden',
                boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
                maxWidth: '90vw', maxHeight: '85vh',
                border: '1px solid rgba(255,255,255,0.08)',
              }}
            >
              <button
                onClick={() => setShowDemoModal(false)}
                style={{
                  position: 'absolute', top: '12px', right: '12px',
                  zIndex: 10, background: 'rgba(0,0,0,0.6)',
                  border: '1px solid rgba(255,255,255,0.15)', color: '#fff',
                  width: '32px', height: '32px', borderRadius: '50%',
                  cursor: 'pointer', fontSize: '1rem', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  backdropFilter: 'blur(4px)',
                }}
              >✕</button>
              <video
                src={demoVideo}
                autoPlay
                controls
                style={{ display: 'block', maxWidth: '90vw', maxHeight: '85vh' }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
