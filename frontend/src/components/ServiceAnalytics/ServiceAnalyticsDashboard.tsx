// frontend/src/components/ServiceAnalytics/ServiceAnalyticsDashboard.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  TextField,
  IconButton,
  Tooltip,
  Chip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  DateRange as DateRangeIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  serviceAnalyticsService, 
  ReportPeriod, 
  AnalyticsDashboard,
  AnalyticsRequest,
  TechnicianOption,
  CustomerOption
} from '../../services/serviceAnalyticsService';
import { useAuth } from '../../hooks/useAuth';
import JobCompletionChart from './JobCompletionChart';
import TechnicianPerformanceChart from './TechnicianPerformanceChart';
import CustomerSatisfactionChart from './CustomerSatisfactionChart';
import JobVolumeChart from './JobVolumeChart';
import SLAComplianceChart from './SLAComplianceChart';
import AnalyticsFilters from './AnalyticsFilters';

interface ServiceAnalyticsDashboardProps {
  organizationId?: number;
}

const ServiceAnalyticsDashboard: React.FC<ServiceAnalyticsDashboardProps> = ({
  organizationId: propOrganizationId
}) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // Use the organization ID from props or fall back to the user's organization
  const organizationId = propOrganizationId || user?.organization_id;
  
  // State for filters
  const [filters, setFilters] = useState<AnalyticsRequest>({
    period: ReportPeriod.MONTH
  });
  
  const [showFilters, setShowFilters] = useState(false);

  // Query for dashboard data
  const {
    data: dashboardData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['service-analytics-dashboard', organizationId, filters],
    queryFn: () => serviceAnalyticsService.getAnalyticsDashboard(organizationId!, filters),
    enabled: !!organizationId,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    staleTime: 2 * 60 * 1000 // Consider data stale after 2 minutes
  });

  // Query for filter options
  const { data: technicians } = useQuery({
    queryKey: ['analytics-technicians', organizationId],
    queryFn: () => serviceAnalyticsService.getAvailableTechnicians(organizationId!),
    enabled: !!organizationId
  });

  const { data: customers } = useQuery({
    queryKey: ['analytics-customers', organizationId],
    queryFn: () => serviceAnalyticsService.getAvailableCustomers(organizationId!),
    enabled: !!organizationId
  });

  const handleFilterChange = (newFilters: AnalyticsRequest) => {
    setFilters(newFilters);
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['service-analytics-dashboard'] });
    refetch();
  };

  const handleExport = async () => {
    if (!organizationId) return;
    
    try {
      const blob = await serviceAnalyticsService.exportAnalyticsData(organizationId, {
        format: 'csv',
        metric_types: ['job_completion', 'technician_performance', 'customer_satisfaction', 'job_volume'],
        filters: filters,
        include_raw_data: false
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `service-analytics-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export analytics data:', error);
    }
  };

  if (!organizationId) {
    return (
      <Alert severity="error">
        No organization ID available. Please ensure you are logged in.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading analytics dashboard...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={handleRefresh}>
          Retry
        </Button>
      }>
        Failed to load analytics dashboard: {(error as Error).message}
      </Alert>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="info">
        No analytics data available for the selected period.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Service Analytics Dashboard
        </Typography>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Toggle Filters">
            <IconButton 
              onClick={() => setShowFilters(!showFilters)}
              color={showFilters ? 'primary' : 'default'}
            >
              <FilterIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Export Data">
            <IconButton onClick={handleExport}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filters */}
      {showFilters && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <AnalyticsFilters
              filters={filters}
              onFiltersChange={handleFilterChange}
              technicians={technicians || []}
              customers={customers || []}
            />
          </CardContent>
        </Card>
      )}

      {/* Dashboard Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" flexWrap="wrap" gap={2} alignItems="center">
            <Chip 
              icon={<DateRangeIcon />}
              label={`Period: ${dashboardData.report_period.toUpperCase()}`}
              color="primary"
            />
            <Chip 
              label={`${dashboardData.start_date} to ${dashboardData.end_date}`}
              variant="outlined"
            />
            <Chip 
              label={`Generated: ${new Date(dashboardData.generated_at).toLocaleString()}`}
              variant="outlined"
              size="small"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Analytics Charts Grid */}
      <Grid container spacing={3}>
        {/* Job Completion Metrics */}
        <Grid item xs={12} md={6}>
          <JobCompletionChart data={dashboardData.job_completion} />
        </Grid>

        {/* Customer Satisfaction Metrics */}
        <Grid item xs={12} md={6}>
          <CustomerSatisfactionChart data={dashboardData.customer_satisfaction} />
        </Grid>

        {/* Job Volume Chart */}
        <Grid item xs={12} md={6}>
          <JobVolumeChart data={dashboardData.job_volume} />
        </Grid>

        {/* SLA Compliance Chart */}
        <Grid item xs={12} md={6}>
          <SLAComplianceChart data={dashboardData.sla_compliance} />
        </Grid>

        {/* Technician Performance - Full width if data available */}
        {dashboardData.technician_performance.length > 0 && (
          <Grid item xs={12}>
            <TechnicianPerformanceChart data={dashboardData.technician_performance} />
          </Grid>
        )}
      </Grid>

      {/* Summary Statistics */}
      <Card sx={{ mt: 3 }}>
        <CardHeader title="Summary Statistics" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {dashboardData.job_completion.total_jobs}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Jobs
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {dashboardData.job_completion.completion_rate.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completion Rate
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="info.main">
                  {dashboardData.customer_satisfaction.average_overall_rating.toFixed(1)}/5
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Customer Rating
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {dashboardData.technician_performance.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Technicians
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ServiceAnalyticsDashboard;