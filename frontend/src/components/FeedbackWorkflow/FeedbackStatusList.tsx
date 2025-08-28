'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Pagination,
  Rating,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  Star as StarIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';

interface FeedbackStatusListProps {
  organizationId: number;
  onFeedbackSelect?: (feedback: any) => void;
  onClosureSelect?: (closure: any) => void;
}

const FEEDBACK_STATUS_CONFIG = {
  submitted: { label: 'Submitted', color: 'info', icon: FeedbackIcon },
  reviewed: { label: 'Reviewed', color: 'warning', icon: EditIcon },
  responded: { label: 'Responded', color: 'success', icon: CheckCircleIcon },
  closed: { label: 'Closed', color: 'default', icon: CloseIcon }
};

const CLOSURE_STATUS_CONFIG = {
  pending: { label: 'Pending', color: 'warning', icon: ScheduleIcon },
  approved: { label: 'Approved', color: 'info', icon: CheckCircleIcon },
  closed: { label: 'Closed', color: 'success', icon: CheckCircleIcon },
  reopened: { label: 'Reopened', color: 'error', icon: WarningIcon }
};

const SATISFACTION_CONFIG = {
  very_satisfied: { label: 'Very Satisfied', color: '#4caf50' },
  satisfied: { label: 'Satisfied', color: '#8bc34a' },
  neutral: { label: 'Neutral', color: '#ff9800' },
  dissatisfied: { label: 'Dissatisfied', color: '#f44336' },
  very_dissatisfied: { label: 'Very Dissatisfied', color: '#d32f2f' }
};

export const FeedbackStatusList: React.FC<FeedbackStatusListProps> = ({
  organizationId,
  onFeedbackSelect,
  onClosureSelect
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [feedbackList, setFeedbackList] = useState<any[]>([]);
  const [closureList, setClosureList] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackFilters, setFeedbackFilters] = useState({
    feedback_status: '',
    overall_rating: '',
    satisfaction_level: ''
  });
  const [closureFilters, setClosureFilters] = useState({
    closure_status: '',
    requires_manager_approval: '',
    escalation_required: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0
  });
  const [selectedFeedback, setSelectedFeedback] = useState<any>(null);
  const [selectedClosure, setSelectedClosure] = useState<any>(null);

  // Mock data - replace with actual API calls
  const loadFeedback = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await feedbackService.getFeedbackList(organizationId, feedbackFilters);
      const mockFeedback = [
        {
          id: 1,
          installation_job_id: 1,
          customer_name: 'John Doe',
          overall_rating: 5,
          service_quality_rating: 4,
          feedback_status: 'submitted',
          satisfaction_level: 'very_satisfied',
          feedback_comments: 'Excellent service!',
          submitted_at: new Date().toISOString(),
          would_recommend: true
        },
        {
          id: 2,
          installation_job_id: 2,
          customer_name: 'Jane Smith',
          overall_rating: 3,
          service_quality_rating: 3,
          feedback_status: 'reviewed',
          satisfaction_level: 'neutral',
          feedback_comments: 'Service was okay, could be improved.',
          submitted_at: new Date(Date.now() - 86400000).toISOString(),
          would_recommend: false
        }
      ];
      setFeedbackList(mockFeedback);
    } catch (err: any) {
      setError(err.message || 'Failed to load feedback');
    } finally {
      setLoading(false);
    }
  };

  const loadClosures = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await feedbackService.getClosureList(organizationId, closureFilters);
      const mockClosures = [
        {
          id: 1,
          installation_job_id: 1,
          closure_status: 'pending',
          closure_reason: 'completed',
          requires_manager_approval: true,
          feedback_received: true,
          minimum_rating_met: true,
          escalation_required: false,
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          installation_job_id: 2,
          closure_status: 'closed',
          closure_reason: 'completed',
          requires_manager_approval: true,
          feedback_received: true,
          minimum_rating_met: false,
          escalation_required: true,
          created_at: new Date(Date.now() - 172800000).toISOString(),
          closed_at: new Date(Date.now() - 86400000).toISOString()
        }
      ];
      setClosureList(mockClosures);
    } catch (err: any) {
      setError(err.message || 'Failed to load closures');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 0) {
      loadFeedback();
    } else {
      loadClosures();
    }
  }, [activeTab, feedbackFilters, closureFilters, organizationId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setError(null);
  };

  const handleFeedbackFilterChange = (field: string) => (event: any) => {
    setFeedbackFilters(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleClosureFilterChange = (field: string) => (event: any) => {
    setClosureFilters(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleViewFeedback = (feedback: any) => {
    setSelectedFeedback(feedback);
    onFeedbackSelect?.(feedback);
  };

  const handleViewClosure = (closure: any) => {
    setSelectedClosure(closure);
    onClosureSelect?.(closure);
  };

  const renderFeedbackTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Customer</TableCell>
            <TableCell>Rating</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Satisfaction</TableCell>
            <TableCell>Submitted</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {feedbackList.map((feedback) => (
            <TableRow key={feedback.id} hover>
              <TableCell>
                <Typography variant="body2">{feedback.customer_name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Job #{feedback.installation_job_id}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  <Rating value={feedback.overall_rating} readOnly size="small" />
                  <Typography variant="caption">
                    {feedback.overall_rating}/5
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Chip
                  size="small"
                  label={FEEDBACK_STATUS_CONFIG[feedback.feedback_status as keyof typeof FEEDBACK_STATUS_CONFIG]?.label}
                  color={FEEDBACK_STATUS_CONFIG[feedback.feedback_status as keyof typeof FEEDBACK_STATUS_CONFIG]?.color as any}
                  icon={React.createElement(FEEDBACK_STATUS_CONFIG[feedback.feedback_status as keyof typeof FEEDBACK_STATUS_CONFIG]?.icon, { fontSize: 'small' })}
                />
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  <Box
                    width={12}
                    height={12}
                    borderRadius="50%"
                    bgcolor={SATISFACTION_CONFIG[feedback.satisfaction_level as keyof typeof SATISFACTION_CONFIG]?.color}
                  />
                  <Typography variant="caption">
                    {SATISFACTION_CONFIG[feedback.satisfaction_level as keyof typeof SATISFACTION_CONFIG]?.label}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="caption">
                  {new Date(feedback.submitted_at).toLocaleDateString()}
                </Typography>
              </TableCell>
              <TableCell>
                <Tooltip title="View Feedback">
                  <IconButton
                    size="small"
                    onClick={() => handleViewFeedback(feedback)}
                  >
                    <ViewIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderClosureTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Job ID</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Reason</TableCell>
            <TableCell>Feedback</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {closureList.map((closure) => (
            <TableRow key={closure.id} hover>
              <TableCell>
                <Typography variant="body2">#{closure.installation_job_id}</Typography>
              </TableCell>
              <TableCell>
                <Chip
                  size="small"
                  label={CLOSURE_STATUS_CONFIG[closure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.label}
                  color={CLOSURE_STATUS_CONFIG[closure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.color as any}
                  icon={React.createElement(CLOSURE_STATUS_CONFIG[closure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.icon, { fontSize: 'small' })}
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                  {closure.closure_reason.replace('_', ' ')}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  {closure.feedback_received ? (
                    <CheckCircleIcon color="success" fontSize="small" />
                  ) : (
                    <ScheduleIcon color="warning" fontSize="small" />
                  )}
                  <Typography variant="caption">
                    {closure.feedback_received ? 'Received' : 'Pending'}
                  </Typography>
                  {closure.escalation_required && (
                    <WarningIcon color="error" fontSize="small" />
                  )}
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="caption">
                  {new Date(closure.created_at).toLocaleDateString()}
                </Typography>
              </TableCell>
              <TableCell>
                <Tooltip title="View Closure">
                  <IconButton
                    size="small"
                    onClick={() => handleViewClosure(closure)}
                  >
                    <AssignmentIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab 
            label="Customer Feedback" 
            icon={<FeedbackIcon />}
            iconPosition="start"
          />
          <Tab 
            label="Service Closures" 
            icon={<AssignmentIcon />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2}>
            {activeTab === 0 ? (
              <>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={feedbackFilters.feedback_status}
                      onChange={handleFeedbackFilterChange('feedback_status')}
                      label="Status"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="submitted">Submitted</MenuItem>
                      <MenuItem value="reviewed">Reviewed</MenuItem>
                      <MenuItem value="responded">Responded</MenuItem>
                      <MenuItem value="closed">Closed</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Rating</InputLabel>
                    <Select
                      value={feedbackFilters.overall_rating}
                      onChange={handleFeedbackFilterChange('overall_rating')}
                      label="Rating"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="5">5 Stars</MenuItem>
                      <MenuItem value="4">4 Stars</MenuItem>
                      <MenuItem value="3">3 Stars</MenuItem>
                      <MenuItem value="2">2 Stars</MenuItem>
                      <MenuItem value="1">1 Star</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Satisfaction</InputLabel>
                    <Select
                      value={feedbackFilters.satisfaction_level}
                      onChange={handleFeedbackFilterChange('satisfaction_level')}
                      label="Satisfaction"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="very_satisfied">Very Satisfied</MenuItem>
                      <MenuItem value="satisfied">Satisfied</MenuItem>
                      <MenuItem value="neutral">Neutral</MenuItem>
                      <MenuItem value="dissatisfied">Dissatisfied</MenuItem>
                      <MenuItem value="very_dissatisfied">Very Dissatisfied</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={closureFilters.closure_status}
                      onChange={handleClosureFilterChange('closure_status')}
                      label="Status"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="approved">Approved</MenuItem>
                      <MenuItem value="closed">Closed</MenuItem>
                      <MenuItem value="reopened">Reopened</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Manager Approval</InputLabel>
                    <Select
                      value={closureFilters.requires_manager_approval}
                      onChange={handleClosureFilterChange('requires_manager_approval')}
                      label="Manager Approval"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="true">Required</MenuItem>
                      <MenuItem value="false">Not Required</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Escalation</InputLabel>
                    <Select
                      value={closureFilters.escalation_required}
                      onChange={handleClosureFilterChange('escalation_required')}
                      label="Escalation"
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="true">Required</MenuItem>
                      <MenuItem value="false">Not Required</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Loading */}
      {loading && (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Tables */}
      {!loading && (
        <>
          {activeTab === 0 ? renderFeedbackTable() : renderClosureTable()}
          
          {/* Pagination */}
          <Box display="flex" justifyContent="center" mt={2}>
            <Pagination
              count={Math.ceil(pagination.total / pagination.limit)}
              page={pagination.page}
              onChange={(event, value) => setPagination(prev => ({ ...prev, page: value }))}
              color="primary"
            />
          </Box>
        </>
      )}

      {/* Feedback Detail Dialog */}
      <Dialog
        open={!!selectedFeedback}
        onClose={() => setSelectedFeedback(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Feedback Details</DialogTitle>
        <DialogContent>
          {selectedFeedback && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Customer</Typography>
                <Typography variant="body1">{selectedFeedback.customer_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Overall Rating</Typography>
                <Rating value={selectedFeedback.overall_rating} readOnly />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Comments</Typography>
                <Typography variant="body1">{selectedFeedback.feedback_comments}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedFeedback(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FeedbackStatusList;