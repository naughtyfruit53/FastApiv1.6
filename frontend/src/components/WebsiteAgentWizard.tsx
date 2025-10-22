// frontend/src/components/WebsiteAgentWizard.tsx

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Grid,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import websiteAgentService, {
  WebsiteProjectCreate,
} from '../services/websiteAgentService';

interface WebsiteAgentWizardProps {
  open: boolean;
  onClose: () => void;
}

const steps = ['Basic Info', 'Design', 'Content', 'Integration'];

const WebsiteAgentWizard: React.FC<WebsiteAgentWizardProps> = ({ open, onClose }) => {
  const queryClient = useQueryClient();
  const [activeStep, setActiveStep] = useState(0);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Step 1: Basic Information
  const [projectName, setProjectName] = useState('');
  const [projectType, setProjectType] = useState('landing_page');
  const [customerId, setCustomerId] = useState<number | undefined>(undefined);

  // Step 2: Design Configuration
  const [theme, setTheme] = useState('modern');
  const [primaryColor, setPrimaryColor] = useState('#3f51b5');
  const [secondaryColor, setSecondaryColor] = useState('#f50057');
  const [logoUrl, setLogoUrl] = useState('');
  const [faviconUrl, setFaviconUrl] = useState('');

  // Step 3: Content Configuration
  const [siteTitle, setSiteTitle] = useState('');
  const [siteDescription, setSiteDescription] = useState('');
  const [pages, setPages] = useState<any[]>([]);

  // Step 4: Integration & Features
  const [chatbotEnabled, setChatbotEnabled] = useState(false);
  const [analyticsEnabled, setAnalyticsEnabled] = useState(false);
  const [seoEnabled, setSeoEnabled] = useState(true);

  const createProjectMutation = useMutation({
    mutationFn: (data: WebsiteProjectCreate) => websiteAgentService.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['website-projects'] });
      toast.success('Website project created successfully!');
      handleClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    },
  });

  const validateStep = (step: number): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (step === 0) {
      if (!projectName.trim()) {
        newErrors.projectName = 'Project name is required';
      }
    } else if (step === 2) {
      if (!siteTitle.trim()) {
        newErrors.siteTitle = 'Site title is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleClose = () => {
    // Reset form
    setActiveStep(0);
    setProjectName('');
    setProjectType('landing_page');
    setCustomerId(undefined);
    setTheme('modern');
    setPrimaryColor('#3f51b5');
    setSecondaryColor('#f50057');
    setLogoUrl('');
    setFaviconUrl('');
    setSiteTitle('');
    setSiteDescription('');
    setPages([]);
    setChatbotEnabled(false);
    setAnalyticsEnabled(false);
    setSeoEnabled(true);
    setErrors({});
    onClose();
  };

  const handleSubmit = () => {
    if (!validateStep(activeStep)) {
      return;
    }

    const projectData: WebsiteProjectCreate = {
      project_name: projectName,
      project_type: projectType,
      customer_id: customerId,
      theme,
      primary_color: primaryColor,
      secondary_color: secondaryColor,
      site_title: siteTitle,
      site_description: siteDescription,
      logo_url: logoUrl,
      favicon_url: faviconUrl,
      pages_config: { pages },
      chatbot_enabled: chatbotEnabled,
      chatbot_config: chatbotEnabled ? { enabled: true } : undefined,
      analytics_config: analyticsEnabled ? { enabled: true } : undefined,
      seo_config: seoEnabled ? { enabled: true } : undefined,
      status: 'draft',
    };

    createProjectMutation.mutate(projectData);
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Project Name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                error={!!errors.projectName}
                helperText={errors.projectName}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Project Type</InputLabel>
                <Select
                  value={projectType}
                  onChange={(e) => setProjectType(e.target.value)}
                  label="Project Type"
                >
                  <MenuItem value="landing_page">Landing Page</MenuItem>
                  <MenuItem value="ecommerce">E-Commerce</MenuItem>
                  <MenuItem value="corporate">Corporate Website</MenuItem>
                  <MenuItem value="blog">Blog</MenuItem>
                  <MenuItem value="portfolio">Portfolio</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Customer ID (Optional)"
                value={customerId || ''}
                onChange={(e) =>
                  setCustomerId(e.target.value ? parseInt(e.target.value) : undefined)
                }
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Theme</InputLabel>
                <Select value={theme} onChange={(e) => setTheme(e.target.value)} label="Theme">
                  <MenuItem value="modern">Modern</MenuItem>
                  <MenuItem value="classic">Classic</MenuItem>
                  <MenuItem value="minimal">Minimal</MenuItem>
                  <MenuItem value="bold">Bold</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="color"
                label="Primary Color"
                value={primaryColor}
                onChange={(e) => setPrimaryColor(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="color"
                label="Secondary Color"
                value={secondaryColor}
                onChange={(e) => setSecondaryColor(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Logo URL (Optional)"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Favicon URL (Optional)"
                value={faviconUrl}
                onChange={(e) => setFaviconUrl(e.target.value)}
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Site Title"
                value={siteTitle}
                onChange={(e) => setSiteTitle(e.target.value)}
                error={!!errors.siteTitle}
                helperText={errors.siteTitle}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Site Description"
                value={siteDescription}
                onChange={(e) => setSiteDescription(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                Pages can be added after the project is created. Default pages (Home, About,
                Contact) will be automatically generated.
              </Alert>
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={chatbotEnabled}
                    onChange={(e) => setChatbotEnabled(e.target.checked)}
                  />
                }
                label="Enable AI Chatbot Integration"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 4 }}>
                Integrate your service chatbot with the website for customer support
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={analyticsEnabled}
                    onChange={(e) => setAnalyticsEnabled(e.target.checked)}
                  />
                }
                label="Enable Analytics"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 4 }}>
                Track visitor behavior and site performance
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox checked={seoEnabled} onChange={(e) => setSeoEnabled(e.target.checked)} />
                }
                label="Enable SEO Optimization"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 4 }}>
                Optimize your website for search engines
              </Typography>
            </Grid>
          </Grid>
        );

      default:
        return 'Unknown step';
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create Website Project</DialogTitle>
      <DialogContent>
        <Box sx={{ width: '100%', mt: 2 }}>
          <Stepper activeStep={activeStep}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          <Box sx={{ mt: 3 }}>{renderStepContent(activeStep)}</Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Box sx={{ flex: '1 1 auto' }} />
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        {activeStep === steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={createProjectMutation.isPending}
          >
            {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
          </Button>
        ) : (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WebsiteAgentWizard;
