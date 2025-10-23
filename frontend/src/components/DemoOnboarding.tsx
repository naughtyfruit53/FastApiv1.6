import React, { useState, useEffect } from 'react';
import OnboardingTour from './OnboardingTour';

interface DemoOnboardingProps {
  onComplete: () => void;
}

const DemoOnboarding: React.FC<DemoOnboardingProps> = ({ onComplete }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding
    const hasCompletedOnboarding = localStorage.getItem('demo-onboarding-completed');
    
    if (!hasCompletedOnboarding) {
      // Show onboarding after a brief delay
      const timer = setTimeout(() => {
        setOpen(true);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, []);

  const handleComplete = () => {
    localStorage.setItem('demo-onboarding-completed', 'true');
    setOpen(false);
    onComplete();
  };

  const handleClose = () => {
    setOpen(false);
  };

  const demoSteps = [
    {
      title: 'Welcome to TritIQ Demo',
      description: 'Explore all features of TritIQ Business Suite with realistic demo data. This guided tour will help you get started.',
      image: '/icons/icon-512x512.png',
    },
    {
      title: 'Navigate the Dashboard',
      description: 'Your dashboard provides an overview of key metrics, recent activities, and quick actions. All data shown is mock data for demonstration purposes.',
      target: '[data-tour="dashboard"]',
    },
    {
      title: 'Explore Modules',
      description: 'Access different modules like Sales, CRM, Inventory, and more from the navigation menu. Each module is fully functional with demo data.',
      target: '[data-tour="navigation"]',
    },
    {
      title: 'Try Mobile Features',
      description: 'Switch to mobile view to experience our responsive design. All features are optimized for mobile devices.',
      target: '[data-tour="mobile-toggle"]',
    },
    {
      title: 'Safe to Experiment',
      description: 'Feel free to create, edit, and delete data. All changes are temporary and won\'t affect any real data. Your demo session will reset automatically.',
    },
    {
      title: 'Demo Mode Indicator',
      description: 'The demo mode badge reminds you that you\'re in a safe demo environment. You can exit demo mode anytime from the menu.',
      target: '[data-tour="demo-badge"]',
    },
    {
      title: 'Get Started!',
      description: 'You\'re all set! Start exploring the features. If you need help, look for the help icon (?) throughout the app.',
    },
  ];

  return (
    <OnboardingTour
      open={open}
      onClose={handleClose}
      onComplete={handleComplete}
      steps={demoSteps}
    />
  );
};

export default DemoOnboarding;
