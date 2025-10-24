import React, { useState } from 'react';
import {
  Box,
  Popover,
  Paper,
  Typography,
  Button,
  IconButton,
  Fade,
} from '@mui/material';
import {
  Close as CloseIcon,
  NavigateNext as NextIcon,
  CheckCircle as CompleteIcon,
  Help as HelpIcon,
} from '@mui/icons-material';

interface TutorialStep {
  id: string;
  target: string;
  title: string;
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  action?: string;
}

interface InteractiveTutorialProps {
  steps: TutorialStep[];
  featureId: string;
  onComplete?: () => void;
}

const InteractiveTutorial: React.FC<InteractiveTutorialProps> = ({
  steps,
  featureId,
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [active, setActive] = useState(false);

  React.useEffect(() => {
    // Check if user has completed this tutorial
    const completed = localStorage.getItem(`tutorial-completed-${featureId}`);
    if (!completed && steps.length > 0) {
      // Auto-start tutorial
      const timer = setTimeout(() => {
        startTutorial();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [featureId, steps.length]);

  const startTutorial = () => {
    if (steps.length === 0) return;

    const target = document.querySelector(steps[0].target) as HTMLElement;
    if (target) {
      setAnchorEl(target);
      setActive(true);
      setCurrentStep(0);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      const nextStep = currentStep + 1;
      const target = document.querySelector(steps[nextStep].target) as HTMLElement;
      
      if (target) {
        setAnchorEl(target);
        setCurrentStep(nextStep);
        
        // Scroll to target
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else {
      handleComplete();
    }
  };

  const handleComplete = () => {
    localStorage.setItem(`tutorial-completed-${featureId}`, 'true');
    setActive(false);
    setAnchorEl(null);
    setCurrentStep(0);
    
    if (onComplete) {
      onComplete();
    }
  };

  const handleClose = () => {
    setActive(false);
    setAnchorEl(null);
  };

  const isLastStep = currentStep === steps.length - 1;
  const open = Boolean(anchorEl) && active;

  return (
    <>
      {/* Help button to restart tutorial */}
      <IconButton
        onClick={startTutorial}
        size="small"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          bgcolor: 'primary.main',
          color: 'white',
          zIndex: 1200,
          '&:hover': {
            bgcolor: 'primary.dark',
          },
        }}
      >
        <HelpIcon />
      </IconButton>

      {/* Tutorial popover */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
        TransitionComponent={Fade}
        PaperProps={{
          elevation: 8,
          sx: {
            maxWidth: 400,
            borderRadius: 2,
            overflow: 'visible',
          },
        }}
      >
        <Paper sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle2" color="primary">
              Step {currentStep + 1} of {steps.length}
            </Typography>
            <IconButton size="small" onClick={handleClose}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>

          <Typography variant="h6" gutterBottom>
            {steps[currentStep]?.title}
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {steps[currentStep]?.content}
          </Typography>

          {steps[currentStep]?.action && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                p: 1,
                bgcolor: 'primary.50',
                borderRadius: 1,
                mb: 2,
                color: 'primary.main',
              }}
            >
              💡 {steps[currentStep].action}
            </Typography>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button size="small" onClick={handleClose}>
              Skip
            </Button>
            <Button
              variant="contained"
              size="small"
              onClick={handleNext}
              endIcon={isLastStep ? <CompleteIcon /> : <NextIcon />}
            >
              {isLastStep ? 'Got it' : 'Next'}
            </Button>
          </Box>
        </Paper>

        {/* Arrow indicator */}
        <Box
          sx={{
            position: 'absolute',
            top: -8,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '8px solid transparent',
            borderRight: '8px solid transparent',
            borderBottom: '8px solid white',
          }}
        />
      </Popover>

      {/* Spotlight overlay */}
      {open && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0, 0, 0, 0.3)',
            zIndex: 1199,
            pointerEvents: 'none',
          }}
        />
      )}
    </>
  );
};

export default InteractiveTutorial;
