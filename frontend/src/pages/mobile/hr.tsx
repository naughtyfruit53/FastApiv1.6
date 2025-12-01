import React, { useState } from 'react';
import { Box, Grid, Typography, Avatar, Chip } from '@mui/material';
import { Add, Work, Person, Schedule, Group } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';
import useSharedHR from '../../hooks/useSharedHR';
import ModernLoading from "../../components/ModernLoading";
import { MobileNavProvider } from '../../context/MobileNavContext';

// Define mobile-optimized table columns for employees
const employeeColumns = [
  {
    key: 'name',
    label: 'Employee',
    render: (value: string, row: any) => (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
          {value.charAt(0)}
        </Avatar>
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.employee_id} • {row.department}
          </Typography>
        </Box>
      </Box>
    ),
  },
  {
    key: 'position',
    label: 'Position',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>{value}</Typography>
        <Typography variant="caption" color="text.secondary">
          {row.employment_type.replace('_', ' ')}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => (
      <Chip
        label={value.charAt(0).toUpperCase() + value.slice(1).replace('_', ' ')}
        size="small"
        color={
          value === 'active' ? 'success' 
          : value === 'on_leave' ? 'warning' 
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
];

const MobileHR: React.FC = () => {
  // Use shared HR business logic
  const {
    metrics,
    filteredEmployees,
    leaveRequests,
    payrollSummary,
    loading,
    error,
    refreshing,
    searchEmployees,
    refresh,
    getEmployeeStatuses,
  } = useSharedHR();

  const [localSearchQuery, setLocalSearchQuery] = useState('');

  // Handle search with local state and shared logic
  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    searchEmployees(query);
  };

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      Add Employee
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="HR Management"
          subtitle="Human Resources"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <ModernLoading
            type="skeleton"
            skeletonType="dashboard"
            count={6}
            message="Loading HR data..."
          />
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  if (error) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="HR Management"
          subtitle="Human Resources"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <Box sx={{ p: 2 }}>
            <Typography color="error" variant="body1">
              Error: {error}
            </Typography>
            <MobileButton 
              variant="outlined" 
              onClick={refresh}
              disabled={refreshing}
              sx={{ mt: 2 }}
            >
              {refreshing ? 'Retrying...' : 'Retry'}
            </MobileButton>
          </Box>
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  return (
    <MobileNavProvider>
      <MobileDashboardLayout
        title="HR Management"
        subtitle="Human Resources"
        rightActions={rightActions}
        showBottomNav={true}
      >
      {/* Search */}
      <MobileSearchBar
        value={localSearchQuery}
        onChange={handleSearch}
        placeholder="Search employees, departments..."
      />

      {/* HR Metrics - Using shared business logic */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <Group sx={{ fontSize: '1.8rem', color: 'primary.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {metrics?.active_employees || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active Employees
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'primary.main' }}>
                of {metrics?.total_employees || 0} total
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <Person sx={{ fontSize: '1.8rem', color: 'success.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                {metrics?.new_hires_this_month || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                New Hires
              </Typography>
              <Typography variant="caption" sx={{ display: 'block' }}>
                this month
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <Schedule sx={{ fontSize: '1.8rem', color: 'warning.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>
                {metrics?.pending_leave_requests || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Pending Leaves
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Payroll Summary */}
      {payrollSummary && (
        <MobileCard title={`Payroll - ${payrollSummary.period}`}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {payrollSummary.formatted_total_gross_pay}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Gross Pay
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {payrollSummary.formatted_total_net_pay}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Net Pay
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">
                  {payrollSummary.total_employees} employees
                </Typography>
                <Chip 
                  label={payrollSummary.status.charAt(0).toUpperCase() + payrollSummary.status.slice(1)} 
                  size="small" 
                  color={payrollSummary.status === 'completed' ? 'success' : 'warning'}
                />
              </Box>
            </Grid>
          </Grid>
        </MobileCard>
      )}

      {/* Department Breakdown */}
      {metrics && metrics.departments && (
        <MobileCard title="Department Overview">
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {metrics.departments.slice(0, 4).map((dept, index) => (
              <Box key={dept.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">
                  {dept.name}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {dept.employee_count}
                  </Typography>
                  <Chip 
                    label={`${dept.percentage.toFixed(1)}%`} 
                    size="small" 
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: 20 }}
                  />
                </Box>
              </Box>
            ))}
          </Box>
        </MobileCard>
      )}

      {/* Employee List - Using shared data */}
      <MobileCard title="Employees">
        <MobileTable
          columns={employeeColumns}
          data={filteredEmployees}
          onRowClick={(row) => console.log('Employee clicked:', row)}
          showChevron={true}
          emptyMessage="No employees found"
        />
      </MobileCard>

      {/* Recent Leave Requests */}
      {leaveRequests.length > 0 && (
        <MobileCard title="Recent Leave Requests">
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {leaveRequests.slice(0, 3).map((request) => (
              <Box key={request.id} sx={{ p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {request.employee_name}
                  </Typography>
                  <Chip 
                    label={request.status.charAt(0).toUpperCase() + request.status.slice(1)} 
                    size="small" 
                    color={
                      request.status === 'approved' ? 'success' 
                      : request.status === 'pending' ? 'warning' 
                      : 'error'
                    }
                    sx={{ fontSize: '0.7rem' }}
                  />
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {request.leave_type.replace('_', ' ')} • {request.days_requested} days
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary">
                  {request.start_date} to {request.end_date}
                </Typography>
              </Box>
            ))}
          </Box>
        </MobileCard>
      )}

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Person />}
            >
              Employee Directory
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Schedule />}
            >
              Leave Requests
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Work />}
            >
              Attendance
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              HR Reports
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>

      {/* TODO: Future implementations using shared business logic */}
      {/* TODO: Integrate with HR services - now implemented via useSharedHR */}
      {/* TODO: Implement mobile employee directory with advanced search and filters - partially implemented */}
      {/* TODO: Add mobile timesheet entry with clock in/out functionality and geolocation */}
      {/* TODO: Create leave request forms optimized for mobile with approval workflow - data available */}
      {/* TODO: Implement performance review interface with mobile forms and rating systems */}
      {/* TODO: Add HR dashboard with real employee metrics and KPIs - implemented */}
      {/* TODO: Create employee self-service portal for mobile access */}
      {/* TODO: Add mobile attendance tracking with GPS-based check-in/check-out */}
      {/* TODO: Implement HR analytics dashboard with mobile-friendly charts - data available */}
      {/* TODO: Add employee document upload and viewing capabilities */}
      {/* TODO: Create payroll management interface for mobile - summary implemented */}
      {/* TODO: Implement recruitment workflow with candidate management */}
      {/* TODO: Add employee onboarding process for mobile */}
      {/* TODO: Create time and attendance reporting with mobile charts */}
    </MobileDashboardLayout>
    </MobileNavProvider>
  );
};

export default MobileHR;
