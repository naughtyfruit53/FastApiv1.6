// frontend/src/components/SLAStatus.tsx

import React from 'react';
import {
  Box,
  Chip,
  Typography,
  LinearProgress,
  Tooltip,
  Card,
  CardContent,
  Grid,
  Stack,
} from '@mui/material';
import {
  Schedule,
  CheckCircle,
  Warning,
  Error,
  TrendingUp,
} from '@mui/icons-material';
import { SLATrackingWithPolicy } from '../services/slaService';

interface SLAStatusProps {
  slaTracking: SLATrackingWithPolicy;
  variant?: 'compact' | 'detailed';
}

const SLAStatus: React.FC<SLAStatusProps> = ({ slaTracking, variant = 'compact' }) => {
  const calculateTimeRemaining = (deadline: string, completedAt?: string) => {
    const deadlineDate = new Date(deadline);
    const now = completedAt ? new Date(completedAt) : new Date();
    const diffMs = deadlineDate.getTime() - now.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);
    
    return {
      hours: Math.abs(diffHours),
      isOverdue: diffHours < 0,
      isCompleted: !!completedAt,
    };
  };

  const getStatusIcon = (status: string, isOverdue: boolean) => {
    switch (status) {
      case 'met':
        return <CheckCircle color="success" />;
      case 'breached':
        return <Error color="error" />;
      case 'pending':
        return isOverdue ? <Warning color="error" /> : <Schedule color="warning" />;
      default:
        return <Schedule />;
    }
  };

  const getStatusColor = (status: string, isOverdue: boolean) => {
    switch (status) {
      case 'met':
        return 'success';
      case 'breached':
        return 'error';
      case 'pending':
        return isOverdue ? 'error' : 'warning';
      default:
        return 'default';
    }
  };

  const calculateProgress = (startTime: string, deadline: string, currentTime?: string) => {
    const start = new Date(startTime).getTime();
    const end = new Date(deadline).getTime();
    const current = currentTime ? new Date(currentTime).getTime() : new Date().getTime();
    
    const totalDuration = end - start;
    const elapsed = current - start;
    
    return Math.min(Math.max((elapsed / totalDuration) * 100, 0), 100);
  };

  const responseTimeInfo = calculateTimeRemaining(
    slaTracking.response_deadline,
    slaTracking.first_response_at
  );

  const resolutionTimeInfo = calculateTimeRemaining(
    slaTracking.resolution_deadline,
    slaTracking.resolved_at
  );

  const responseProgress = calculateProgress(
    slaTracking.created_at,
    slaTracking.response_deadline,
    slaTracking.first_response_at
  );

  const resolutionProgress = calculateProgress(
    slaTracking.created_at,
    slaTracking.resolution_deadline,
    slaTracking.resolved_at
  );

  if (variant === 'compact') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        <Tooltip title={`Response SLA: ${slaTracking.response_status}`}>
          <Chip
            icon={getStatusIcon(slaTracking.response_status, responseTimeInfo.isOverdue)}
            label={`Response: ${responseTimeInfo.hours.toFixed(1)}h`}
            size="small"
            color={getStatusColor(slaTracking.response_status, responseTimeInfo.isOverdue) as any}
            variant={responseTimeInfo.isCompleted ? 'filled' : 'outlined'}
          />
        </Tooltip>
        
        <Tooltip title={`Resolution SLA: ${slaTracking.resolution_status}`}>
          <Chip
            icon={getStatusIcon(slaTracking.resolution_status, resolutionTimeInfo.isOverdue)}
            label={`Resolution: ${resolutionTimeInfo.hours.toFixed(1)}h`}
            size="small"
            color={getStatusColor(slaTracking.resolution_status, resolutionTimeInfo.isOverdue) as any}
            variant={resolutionTimeInfo.isCompleted ? 'filled' : 'outlined'}
          />
        </Tooltip>

        {slaTracking.escalation_triggered && (
          <Chip
            icon={<TrendingUp />}
            label={`Escalated (L${slaTracking.escalation_level})`}
            size="small"
            color="error"
          />
        )}
      </Box>
    );
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          SLA Status - {slaTracking.policy.name}
        </Typography>
        
        <Grid container spacing={3}>
          {/* Response SLA */}
          <Grid item xs={12} md={6}>
            <Stack spacing={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Response Time</Typography>
                <Chip
                  icon={getStatusIcon(slaTracking.response_status, responseTimeInfo.isOverdue)}
                  label={slaTracking.response_status.toUpperCase()}
                  size="small"
                  color={getStatusColor(slaTracking.response_status, responseTimeInfo.isOverdue) as any}
                />
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={responseProgress}
                color={getStatusColor(slaTracking.response_status, responseTimeInfo.isOverdue) as any}
                sx={{ height: 8, borderRadius: 4 }}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption">
                  Target: {slaTracking.policy.response_time_hours}h
                </Typography>
                <Typography variant="caption">
                  {responseTimeInfo.isCompleted ? 'Completed' : 
                   responseTimeInfo.isOverdue ? `Overdue by ${responseTimeInfo.hours.toFixed(1)}h` : 
                   `${responseTimeInfo.hours.toFixed(1)}h remaining`}
                </Typography>
              </Box>
              
              {slaTracking.response_breach_hours !== null && slaTracking.response_breach_hours !== undefined && (
                <Typography variant="caption" color={slaTracking.response_breach_hours > 0 ? 'error' : 'success'}>
                  {slaTracking.response_breach_hours > 0 ? 
                    `Breached by ${slaTracking.response_breach_hours.toFixed(1)}h` :
                    `Met by ${Math.abs(slaTracking.response_breach_hours).toFixed(1)}h`}
                </Typography>
              )}
            </Stack>
          </Grid>

          {/* Resolution SLA */}
          <Grid item xs={12} md={6}>
            <Stack spacing={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Resolution Time</Typography>
                <Chip
                  icon={getStatusIcon(slaTracking.resolution_status, resolutionTimeInfo.isOverdue)}
                  label={slaTracking.resolution_status.toUpperCase()}
                  size="small"
                  color={getStatusColor(slaTracking.resolution_status, resolutionTimeInfo.isOverdue) as any}
                />
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={resolutionProgress}
                color={getStatusColor(slaTracking.resolution_status, resolutionTimeInfo.isOverdue) as any}
                sx={{ height: 8, borderRadius: 4 }}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption">
                  Target: {slaTracking.policy.resolution_time_hours}h
                </Typography>
                <Typography variant="caption">
                  {resolutionTimeInfo.isCompleted ? 'Completed' : 
                   resolutionTimeInfo.isOverdue ? `Overdue by ${resolutionTimeInfo.hours.toFixed(1)}h` : 
                   `${resolutionTimeInfo.hours.toFixed(1)}h remaining`}
                </Typography>
              </Box>
              
              {slaTracking.resolution_breach_hours !== null && slaTracking.resolution_breach_hours !== undefined && (
                <Typography variant="caption" color={slaTracking.resolution_breach_hours > 0 ? 'error' : 'success'}>
                  {slaTracking.resolution_breach_hours > 0 ? 
                    `Breached by ${slaTracking.resolution_breach_hours.toFixed(1)}h` :
                    `Met by ${Math.abs(slaTracking.resolution_breach_hours).toFixed(1)}h`}
                </Typography>
              )}
            </Stack>
          </Grid>

          {/* Escalation Status */}
          {slaTracking.escalation_triggered && (
            <Grid item xs={12}>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'error.light', 
                borderRadius: 1, 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1 
              }}>
                <TrendingUp color="error" />
                <Typography variant="body2" color="error.dark">
                  Escalated to Level {slaTracking.escalation_level} on{' '}
                  {slaTracking.escalation_triggered_at && 
                    new Date(slaTracking.escalation_triggered_at).toLocaleString()}
                </Typography>
              </Box>
            </Grid>
          )}

          {/* Policy Info */}
          <Grid item xs={12}>
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" color="textSecondary">
                Policy: {slaTracking.policy.name} | 
                Escalation: {slaTracking.policy.escalation_enabled ? 'Enabled' : 'Disabled'} |
                Threshold: {slaTracking.policy.escalation_threshold_percent}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SLAStatus;