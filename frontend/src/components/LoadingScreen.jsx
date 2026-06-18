import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, FileSearch, Scale, Calculator } from 'lucide-react';

const steps = [
  {
    id: 1,
    title: "Inventory",
    subtitle: "Extracting skills from your resume",
    icon: FileSearch
  },
  {
    id: 2,
    title: "Gap Analysis",
    subtitle: "Classifying missing requirements",
    icon: Brain
  },
  {
    id: 3,
    title: "Scoring Rubric",
    subtitle: "Calculating final match score",
    icon: Calculator
  }
];

const LoadingScreen = ({ apiComplete, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const firedRef = useRef(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 700);

  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth <= 700);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  // Advance steps every 2.5s, stop at last step
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  // Fire onComplete when animation is at last step AND api is done
  useEffect(() => {
    if (firedRef.current) return;
    const isLastStep = activeStep === steps.length - 1;
    if (isLastStep && apiComplete) {
      firedRef.current = true;
      const timer = setTimeout(() => {
        onComplete && onComplete();
      }, 800); // hold last step for 800ms so user can see it
      return () => clearTimeout(timer);
    }
  }, [activeStep, apiComplete, onComplete]);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="processing-overlay"
      style={{
        position: 'fixed',
        top: 0, left: 0, width: '100%', height: '100%',
        background: 'rgba(11, 17, 32, 0.95)',
        backdropFilter: 'blur(20px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '2rem'
      }}
    >
      {/* Top Spinner & Brain */}
      <div style={{ position: 'relative', width: '100px', height: '100px', marginBottom: '2rem' }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
          style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            borderRadius: '50%',
            border: '3px solid rgba(14, 165, 233, 0.1)',
            borderTopColor: 'var(--primary)',
            borderRightColor: 'var(--primary)'
          }}
        />
        <div style={{ 
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, 
          display: 'flex', alignItems: 'center', justifyContent: 'center' 
        }}>
          <Brain size={32} className="text-cyan" />
        </div>
      </div>

      {/* Headings */}
      <h2 style={{ fontSize: isMobile ? '1.4rem' : '2rem', fontWeight: '700', color: '#fff', marginBottom: '0.5rem', textAlign: 'center' }}>
        Running the three-pass rubric...
      </h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: isMobile ? '2rem' : '4rem', textAlign: 'center' }}>
        This usually takes a few seconds.
      </p>

      {/* Step Cards */}
      <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: '1.5rem', flexWrap: 'wrap', justifyContent: 'center', maxWidth: '1000px', width: isMobile ? '100%' : undefined, padding: isMobile ? '0 1rem' : 0 }}>
        {steps.map((step, index) => {
          const isActive = index === activeStep;
          const isPast = index < activeStep;
          const StepIcon = step.icon;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              style={{
                width: isMobile ? '100%' : '300px',
                padding: '1.5rem',
                borderRadius: '16px',
                background: isActive ? 'rgba(15, 23, 42, 0.8)' : 'rgba(15, 23, 42, 0.3)',
                border: `1px solid ${isActive ? 'rgba(14, 165, 233, 0.3)' : 'rgba(255, 255, 255, 0.03)'}`,
                boxShadow: isActive ? '0 0 20px rgba(14, 165, 233, 0.1)' : 'none',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: isMobile ? 'flex-start' : 'center',
                textAlign: isMobile ? 'left' : 'center',
                transition: 'all 0.5s ease'
              }}
            >
              <div style={{ alignSelf: 'flex-start', marginBottom: '1rem' }}>
                <StepIcon 
                  size={24} 
                  style={{ color: isActive ? 'var(--primary)' : 'rgba(255, 255, 255, 0.1)' }} 
                />
              </div>
              
              <h3 style={{ 
                fontSize: '1.1rem', 
                fontWeight: '700', 
                color: isActive ? '#fff' : 'rgba(255, 255, 255, 0.3)',
                marginBottom: '0.5rem'
              }}>
                {step.title}
              </h3>
              
              <p style={{ 
                fontSize: '0.85rem', 
                color: isActive ? 'var(--text-muted)' : 'rgba(255, 255, 255, 0.2)' 
              }}>
                {step.subtitle}
              </p>

              {/* Progress Dot */}
              <div style={{ position: 'absolute', bottom: '1.25rem', left: '1.25rem' }}>
                <motion.div 
                  animate={{ 
                    scale: isActive ? [1, 1.5, 1] : 1,
                    opacity: isActive ? 1 : (isPast ? 0.5 : 0.1)
                  }}
                  transition={{ repeat: isActive ? Infinity : 0, duration: 1.5 }}
                  style={{ 
                    width: '6px', height: '6px', 
                    borderRadius: '50%', 
                    background: isActive ? 'var(--primary)' : (isPast ? 'var(--primary)' : '#fff')
                  }} 
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default LoadingScreen;
