// frontend/src/components/CustomerAnalytics.tsx

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  FormControlLabel,
  Switch,
  TextField
} from '@mui/material';
import {
  TrendingUp,
  Person,
  DateRange,
  Category,
  Assessment,
  Timeline
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { analyticsService, CustomerAnalyticsData } from '../services/analyticsService';

interface CustomerAnalyticsProps {
  customerId: number;
  customerName?: string;
}

const CustomerAnalytics: React.FC<CustomerAnalyticsProps> = ({ 
  customerId, 
  customerName 
}) => {
  const [includeRecentInteractions, setIncludeRecentInteractions] = useState(true);
  const [recentInteractionsLimit, setRecentInteractionsLimit] = useState(5);

  const { 
    data: analytics, 
    isLoading, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['customerAnalytics', customerId, includeRecentInteractions, recentInteractionsLimit],
    queryFn: () => analyticsService.getCustomerAnalytics(
      customerId, 
      includeRecentInteractions, 
      recentInteractionsLimit
    ),
    enabled: !!customerId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading customer analytics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading customer analytics: {(error as Error).message}
      </Alert>
    );
  }

  if (!analytics) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        No analytics data available for this customer.
      </Alert>
    );
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getInteractionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      call: 'primary',
      email: 'secondary',
      meeting: 'success',
      support_ticket: 'warning',
      complaint: 'error',
      feedback: 'info'
    };
    return colors[type] || 'default';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'warning',
      in_progress: 'info',
      completed: 'success',
      cancelled: 'error'
    };
    return colors[status] || 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <Assessment sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" component="h1">
            Customer Analytics
          </Typography>
          <Typography variant="h6" color="textSecondary">
            {analytics.customer_name || customerName}
          </Typography>
        </Box>
      </Box>

      {/* Controls */}
      <Box mb={3}>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <FormControlLabel
              control={
                <Switch
                  checked={includeRecentInteractions}
                  onChange={(e) => setIncludeRecentInteractions(e.target.checked)}
                />
              }
              label="Show Recent Interactions"
            />
          </Grid>
          {includeRecentInteractions && (
            <Grid item>
              <TextField
                type="number"
                label="Recent Interactions Limit"
                value={recentInteractionsLimit}
                onChange={(e) => setRecentInteractionsLimit(Number(e.target.value))}
                InputProps={{ inputProps: { min: 1, max: 20 } }}
                size="small"
                sx={{ width: 200 }}
              />
            </Grid>
          )}
        </Grid>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Interactions
                  </Typography>
                  <Typography variant="h4">
                    {analytics.total_interactions}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <DateRange color="secondary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Last Interaction
                  </Typography>
                  <Typography variant="h6">
                    {formatDate(analytics.last_interaction_date)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Category color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Segments
                  </Typography>
                  <Typography variant="h4">
                    {analytics.segments.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Timeline color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Interaction Types
                  </Typography>
                  <Typography variant="h4">
                    {Object.keys(analytics.interaction_types).length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Interaction Types Breakdown */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Interaction Types
              </Typography>
              <Box>
                {Object.entries(analytics.interaction_types).map(([type, count]) => (
                  <Box key={type} display="flex" justifyContent="space-between" mb={1}>
                    <Chip 
                      label={type.replace('_', ' ').toUpperCase()} 
                      color={getInteractionTypeColor(type) as any}
                      size="small"
                    />
                    <Typography variant="body2">{count}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Interaction Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Interaction Status
              </Typography>
              <Box>
                {Object.entries(analytics.interaction_status).map(([status, count]) => (
                  <Box key={status} display="flex" justifyContent="space-between" mb={1}>
                    <Chip 
                      label={status.replace('_', ' ').toUpperCase()} 
                      color={getStatusColor(status) as any}
                      size="small"
                    />
                    <Typography variant="body2">{count}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Customer Segments */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Customer Segments
              </Typography>
              {analytics.segments.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Segment</TableCell>
                        <TableCell>Value</TableCell>
                        <TableCell>Assigned Date</TableCell>
                        <TableCell>Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analytics.segments.map((segment, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Chip 
                              label={segment.segment_name} 
                              color="primary" 
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>
                            {segment.segment_value ? segment.segment_value.toFixed(2) : '-'}
                          </TableCell>
                          <TableCell>{formatDate(segment.assigned_date)}</TableCell>
                          <TableCell>{segment.description || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="textSecondary">
                  No segments assigned to this customer.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Interactions */}
        {includeRecentInteractions && analytics.recent_interactions.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Interactions
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Subject</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analytics.recent_interactions.map((interaction, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Chip 
                              label={interaction.interaction_type} 
                              color={getInteractionTypeColor(interaction.interaction_type) as any}
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>{interaction.subject}</TableCell>
                          <TableCell>
                            <Chip 
                              label={interaction.status} 
                              color={getStatusColor(interaction.status) as any}
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>{formatDate(interaction.interaction_date)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Footer */}
      <Box mt={3}>
        <Typography variant="caption" color="textSecondary">
          Analytics calculated at: {formatDate(analytics.calculated_at)}
        </Typography>
      </Box>
    </Box>
  );
};

export default CustomerAnalytics;