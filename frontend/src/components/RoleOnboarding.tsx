// frontend/src/components/RoleOnboarding.tsx
/**
 * Role-based Onboarding Component
 * Provides guided onboarding flow based on user role
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle,
  ArrowForward,
  ArrowBack,
  PlayArrow,
  School,
  AdminPanelSettings,
  Business,
  People,
  Assessment,
} from '@mui/icons-material';

export interface OnboardingStep {
  label: string;
  description: string;
  content: React.ReactNode;
  actions?: Array<{
    label: string;
    action: () => void;
    variant?: 'text' | 'outlined' | 'contained';
  }>;
}

interface RoleOnboardingProps {
  role: string;
  userName?: string;
  onComplete?: () => void;
  onSkip?: () => void;
}

const RoleOnboarding: React.FC<RoleOnboardingProps> = ({
  role,
  userName = 'User',
  onComplete,
  onSkip,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const getRoleIcon = (roleName: string) => {
    const roleIcons: Record<string, React.ReactNode> = {
      admin: <AdminPanelSettings />,
      super_admin: <AdminPanelSettings color="primary" />,
      manager: <People />,
      analyst: <Assessment />,
      user: <Business />,
    };
    return roleIcons[roleName.toLowerCase()] || <Business />;
  };

  const getRoleSteps = (roleName: string): OnboardingStep[] => {
    const baseSteps: OnboardingStep[] = [
      {
        label: 'Welcome',
        description: `Get started with your ${roleName} role`,
        content: (
          <Box>
            <Typography variant="body1" gutterBottom>
              Welcome, {userName}! Let's get you set up with your {roleName} account.
            </Typography>
            <Alert severity="info" sx={{ mt: 2 }}>
              This onboarding will take approximately 5-10 minutes to complete.
            </Alert>
          </Box>
        ),
      },
    ];

    const roleSpecificSteps: Record<string, OnboardingStep[]> = {
      super_admin: [
        {
          label: 'Platform Overview',
          description: 'Learn about system administration',
          content: (
            <List>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Manage Organizations"
                  secondary="Create and configure multiple organizations"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="User Management"
                  secondary="Control user access and permissions across the platform"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="System Configuration"
                  secondary="Configure global settings and integrations"
                />
              </ListItem>
            </List>
          ),
        },
        {
          label: 'Key Features',
          description: 'Explore administrative capabilities',
          content: (
            <Box>
              <Typography variant="body2" gutterBottom>
                As a Super Admin, you have access to:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
                <Chip label="Organization Management" color="primary" />
                <Chip label="License Administration" color="primary" />
                <Chip label="Audit Logs" color="primary" />
                <Chip label="System Analytics" color="primary" />
                <Chip label="Integration Management" color="primary" />
              </Box>
            </Box>
          ),
        },
      ],
      admin: [
        {
          label: 'Organization Setup',
          description: 'Configure your organization',
          content: (
            <List>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Manage Team Members"
                  secondary="Invite users and assign roles"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Configure Modules"
                  secondary="Enable features for your organization"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Set Preferences"
                  secondary="Customize dashboards and notifications"
                />
              </ListItem>
            </List>
          ),
        },
        {
          label: 'Quick Start',
          description: 'Begin using the platform',
          content: (
            <Box>
              <Typography variant="body2" gutterBottom>
                Recommended first steps:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon><PlayArrow /></ListItemIcon>
                  <ListItemText primary="Complete organization profile" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><PlayArrow /></ListItemIcon>
                  <ListItemText primary="Invite team members" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><PlayArrow /></ListItemIcon>
                  <ListItemText primary="Explore the dashboard" />
                </ListItem>
              </List>
            </Box>
          ),
        },
      ],
      manager: [
        {
          label: 'Dashboard Overview',
          description: 'Understand your management tools',
          content: (
            <List>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Team Analytics"
                  secondary="Monitor team performance and activities"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Task Management"
                  secondary="Assign and track team tasks"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                <ListItemText
                  primary="Reports & Insights"
                  secondary="Generate management reports"
                />
              </ListItem>
            </List>
          ),
        },
      ],
      user: [
        {
          label: 'Getting Started',
          description: 'Learn the basics',
          content: (
            <List>
              <ListItem>
                <ListItemIcon><School /></ListItemIcon>
                <ListItemText
                  primary="Navigation"
                  secondary="Learn to navigate the platform efficiently"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><School /></ListItemIcon>
                <ListItemText
                  primary="Basic Operations"
                  secondary="Understand common tasks and workflows"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon><School /></ListItemIcon>
                <ListItemText
                  primary="Help & Support"
                  secondary="Access documentation and support resources"
                />
              </ListItem>
            </List>
          ),
        },
      ],
    };

    const finalStep: OnboardingStep = {
      label: 'Complete',
      description: 'You\'re all set!',
      content: (
        <Box>
          <Typography variant="h6" gutterBottom>
            Onboarding Complete!
          </Typography>
          <Typography variant="body1" gutterBottom>
            You're ready to start using the platform. You can always access this guide from the help menu.
          </Typography>
          <Card sx={{ mt: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <CardContent>
              <Typography variant="body2">
                💡 <strong>Pro Tip:</strong> Customize your dashboard by adding widgets that matter most to you.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      ),
    };

    const steps = roleSpecificSteps[roleName.toLowerCase()] || roleSpecificSteps.user;
    return [...baseSteps, ...steps, finalStep];
  };

  const steps = getRoleSteps(role);

  const handleNext = () => {
    setCompletedSteps((prev) => new Set([...prev, activeStep]));
    if (activeStep === steps.length - 1) {
      if (onComplete) {
        onComplete();
      }
    } else {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        {getRoleIcon(role)}
        <Box sx={{ ml: 2 }}>
          <Typography variant="h5">
            {role.charAt(0).toUpperCase() + role.slice(1)} Onboarding
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Step {activeStep + 1} of {steps.length}
          </Typography>
        </Box>
      </Box>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label} completed={completedSteps.has(index)}>
            <StepLabel>{step.label}</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {step.description}
              </Typography>
              <Box sx={{ my: 2 }}>{step.content}</Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleNext}
                  endIcon={index === steps.length - 1 ? <CheckCircle /> : <ArrowForward />}
                >
                  {index === steps.length - 1 ? 'Finish' : 'Continue'}
                </Button>
                {index > 0 && (
                  <Button
                    onClick={handleBack}
                    startIcon={<ArrowBack />}
                  >
                    Back
                  </Button>
                )}
                {index === 0 && onSkip && (
                  <Button onClick={handleSkip} color="inherit">
                    Skip Onboarding
                  </Button>
                )}
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
};

export default RoleOnboarding;
