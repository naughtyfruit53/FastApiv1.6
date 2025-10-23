import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogContent,
  Button,
  Typography,
  IconButton,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
} from '@mui/material';
import {
  Close as CloseIcon,
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  CheckCircle as CompleteIcon,
} from '@mui/icons-material';

interface TourStep {
  title: string;
  description: string;
  target?: string;
  image?: string;
  action?: () => void;
}

interface OnboardingTourProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
  steps: TourStep[];
}

const OnboardingTour: React.FC<OnboardingTourProps> = ({
  open,
  onClose,
  onComplete,
  steps,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightedElement, setHighlightedElement] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (open && steps[currentStep]?.target) {
      const element = document.querySelector(steps[currentStep].target!) as HTMLElement;
      setHighlightedElement(element);

      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else {
      setHighlightedElement(null);
    }
  }, [currentStep, open, steps]);

  const handleNext = () => {
    if (steps[currentStep].action) {
      steps[currentStep].action!();
    }

    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    setCurrentStep(0);
    onComplete();
    onClose();
  };

  const handleSkip = () => {
    setCurrentStep(0);
    onClose();
  };

  const progress = ((currentStep + 1) / steps.length) * 100;
  const isLastStep = currentStep === steps.length - 1;

  return (
    <>
      {/* Overlay for highlighting elements */}
      {open && highlightedElement && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1300,
            pointerEvents: 'none',
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: `${highlightedElement.getBoundingClientRect().top}px`,
              left: `${highlightedElement.getBoundingClientRect().left}px`,
              width: `${highlightedElement.getBoundingClientRect().width}px`,
              height: `${highlightedElement.getBoundingClientRect().height}px`,
              boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
              borderRadius: '8px',
              pointerEvents: 'auto',
            }}
          />
        </Box>
      )}

      {/* Tour Dialog */}
      <Dialog
        open={open}
        onClose={handleSkip}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            zIndex: 1400,
          },
        }}
      >
        <Box sx={{ position: 'relative' }}>
          <IconButton
            onClick={handleSkip}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              zIndex: 1,
            }}
          >
            <CloseIcon />
          </IconButton>

          <LinearProgress variant="determinate" value={progress} />

          <DialogContent sx={{ p: 4 }}>
            <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
              {steps.map((step, index) => (
                <Step key={index}>
                  <StepLabel>{step.title}</StepLabel>
                </Step>
              ))}
            </Stepper>

            <Box sx={{ textAlign: 'center', mb: 3 }}>
              {steps[currentStep].image && (
                <Box
                  component="img"
                  src={steps[currentStep].image}
                  alt={steps[currentStep].title}
                  sx={{
                    width: '100%',
                    maxHeight: 300,
                    objectFit: 'contain',
                    mb: 3,
                    borderRadius: 2,
                  }}
                />
              )}

              <Typography variant="h5" gutterBottom fontWeight="bold">
                {steps[currentStep].title}
              </Typography>

              <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                {steps[currentStep].description}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                onClick={handleBack}
                disabled={currentStep === 0}
                startIcon={<BackIcon />}
              >
                Back
              </Button>

              <Typography variant="body2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                Step {currentStep + 1} of {steps.length}
              </Typography>

              <Button
                variant="contained"
                onClick={handleNext}
                endIcon={isLastStep ? <CompleteIcon /> : <NextIcon />}
              >
                {isLastStep ? 'Complete' : 'Next'}
              </Button>
            </Box>
          </DialogContent>
        </Box>
      </Dialog>
    </>
  );
};

export default OnboardingTour;
