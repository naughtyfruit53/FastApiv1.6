'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Rating,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  Star as StarIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon
} from '@mui/icons-material';

interface CustomerFeedbackModalProps {
  open: boolean;
  onClose: () => void;
  installationJobId: number;
  customerId: number;
  completionRecordId?: number;
  onSubmit: (feedbackData: any) => Promise<void>;
}

const SATISFACTION_LEVELS = [
  { value: 'very_satisfied', label: 'Very Satisfied', color: '#4caf50' },
  { value: 'satisfied', label: 'Satisfied', color: '#8bc34a' },
  { value: 'neutral', label: 'Neutral', color: '#ff9800' },
  { value: 'dissatisfied', label: 'Dissatisfied', color: '#f44336' },
  { value: 'very_dissatisfied', label: 'Very Dissatisfied', color: '#d32f2f' }
];

const CONTACT_METHODS = [
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'sms', label: 'SMS' }
];

export const CustomerFeedbackModal: React.FC<CustomerFeedbackModalProps> = ({
  open,
  onClose,
  installationJobId,
  customerId,
  completionRecordId,
  onSubmit
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    overall_rating: 0,
    service_quality_rating: 0,
    technician_rating: 0,
    timeliness_rating: 0,
    communication_rating: 0,
    feedback_comments: '',
    improvement_suggestions: '',
    would_recommend: true,
    satisfaction_level: 'satisfied',
    follow_up_preferred: false,
    preferred_contact_method: 'email',
    survey_responses: {}
  });
  const [error, setError] = useState<string | null>(null);

  const handleRatingChange = (field: string) => (event: any, value: number | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: value || 0
    }));
  };

  const handleTextChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSelectChange = (field: string) => (event: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSwitchChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.checked
    }));
  };

  const handleSubmit = async () => {
    setError(null);
    
    if (formData.overall_rating === 0) {
      setError('Please provide an overall rating');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const feedbackData = {
        installation_job_id: installationJobId,
        customer_id: customerId,
        completion_record_id: completionRecordId,
        ...formData
      };
      
      await onSubmit(feedbackData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      overall_rating: 0,
      service_quality_rating: 0,
      technician_rating: 0,
      timeliness_rating: 0,
      communication_rating: 0,
      feedback_comments: '',
      improvement_suggestions: '',
      would_recommend: true,
      satisfaction_level: 'satisfied',
      follow_up_preferred: false,
      preferred_contact_method: 'email',
      survey_responses: {}
    });
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const getSatisfactionColor = (level: string) => {
    const satisfaction = SATISFACTION_LEVELS.find(s => s.value === level);
    return satisfaction?.color || '#757575';
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      scroll="paper"
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <FeedbackIcon color="primary" />
          <Typography variant="h6">Service Feedback</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Please share your experience with our service to help us improve
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Overall Rating */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Overall Service Rating *
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <Rating
                    value={formData.overall_rating}
                    onChange={handleRatingChange('overall_rating')}
                    size="large"
                    icon={<StarIcon fontSize="inherit" />}
                    emptyIcon={<StarIcon fontSize="inherit" />}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {formData.overall_rating > 0 ? `${formData.overall_rating}/5` : 'Please rate'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Detailed Ratings */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Detailed Ratings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Service Quality
                  </Typography>
                  <Rating
                    value={formData.service_quality_rating}
                    onChange={handleRatingChange('service_quality_rating')}
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Technician Performance
                  </Typography>
                  <Rating
                    value={formData.technician_rating}
                    onChange={handleRatingChange('technician_rating')}
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Timeliness
                  </Typography>
                  <Rating
                    value={formData.timeliness_rating}
                    onChange={handleRatingChange('timeliness_rating')}
                    size="small"
                  />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Communication
                  </Typography>
                  <Rating
                    value={formData.communication_rating}
                    onChange={handleRatingChange('communication_rating')}
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>
          </Grid>

          {/* Satisfaction Level */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Satisfaction Level</InputLabel>
              <Select
                value={formData.satisfaction_level}
                onChange={handleSelectChange('satisfaction_level')}
                label="Satisfaction Level"
              >
                {SATISFACTION_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={level.color}
                      />
                      {level.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Would Recommend */}
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.would_recommend}
                  onChange={handleSwitchChange('would_recommend')}
                  color="primary"
                />
              }
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  {formData.would_recommend ? (
                    <ThumbUpIcon color="success" fontSize="small" />
                  ) : (
                    <ThumbDownIcon color="error" fontSize="small" />
                  )}
                  Would recommend our service
                </Box>
              }
            />
          </Grid>

          {/* Feedback Comments */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Feedback Comments"
              placeholder="Please share your thoughts about the service..."
              value={formData.feedback_comments}
              onChange={handleTextChange('feedback_comments')}
            />
          </Grid>

          {/* Improvement Suggestions */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Suggestions for Improvement"
              placeholder="How can we improve our service?"
              value={formData.improvement_suggestions}
              onChange={handleTextChange('improvement_suggestions')}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider />
          </Grid>

          {/* Follow-up Preferences */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Follow-up Preferences
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.follow_up_preferred}
                  onChange={handleSwitchChange('follow_up_preferred')}
                  color="primary"
                />
              }
              label="I would like follow-up contact"
            />
          </Grid>

          {formData.follow_up_preferred && (
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Preferred Contact Method</InputLabel>
                <Select
                  value={formData.preferred_contact_method}
                  onChange={handleSelectChange('preferred_contact_method')}
                  label="Preferred Contact Method"
                >
                  {CONTACT_METHODS.map((method) => (
                    <MenuItem key={method.value} value={method.value}>
                      {method.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting || formData.overall_rating === 0}
          startIcon={isSubmitting ? <CircularProgress size={20} /> : <FeedbackIcon />}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CustomerFeedbackModal;