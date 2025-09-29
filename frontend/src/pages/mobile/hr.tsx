import React, { useState } from 'react';
import { Box, Grid, Typography, Avatar, Chip } from '@mui/material';
import { Add, Work, Person, Schedule } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// TODO: CRITICAL - Replace hardcoded data with real HR API integration
// TODO: Integrate with HR services (employee management, payroll, attendance)
// TODO: Implement mobile employee directory with advanced search and filters
// TODO: Add mobile timesheet entry with clock in/out functionality and geolocation
// TODO: Create leave request forms optimized for mobile with approval workflow
// TODO: Implement performance review interface with mobile forms and rating systems
// TODO: Add HR dashboard with real employee metrics and KPIs
// TODO: Create employee self-service portal for mobile access
// TODO: Add mobile attendance tracking with GPS-based check-in/check-out
// TODO: Implement HR analytics dashboard with mobile-friendly charts
// TODO: Add employee document upload and viewing capabilities
// TODO: Create payroll management interface for mobile
// TODO: Implement recruitment workflow with candidate management
// TODO: Add employee onboarding process for mobile
// TODO: Create time and attendance reporting with mobile charts

// Sample HR data - REPLACE WITH REAL API INTEGRATION
const employeesData = [
  {
    id: 'EMP-001',
    name: 'Alice Johnson',
    department: 'Engineering',
    position: 'Senior Developer',
    status: 'Active',
    joinDate: '2023-03-15',
    phone: '+91 98765 43210',
  },
  {
    id: 'EMP-002',
    name: 'Bob Smith',
    department: 'Marketing',
    position: 'Marketing Manager',
    status: 'Active',
    joinDate: '2023-01-20',
    phone: '+91 87654 32109',
  },
  {
    id: 'EMP-003',
    name: 'Carol Williams',
    department: 'Finance',
    position: 'Accountant',
    status: 'On Leave',
    joinDate: '2022-11-10',
    phone: '+91 76543 21098',
  },
];

const hrColumns = [
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
            {row.id} • {row.position}
          </Typography>
        </Box>
      </Box>
    ),
  },
  {
    key: 'department',
    label: 'Department',
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => (
      <Chip
        label={value}
        size="small"
        color={
          value === 'Active' ? 'success' 
          : value === 'On Leave' ? 'warning' 
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
  {
    key: 'joinDate',
    label: 'Join Date',
    render: (value: string) => (
      <Typography variant="body2">
        {new Date(value).toLocaleDateString()}
      </Typography>
    ),
  },
];

const MobileHR: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = employeesData.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.position.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      Add Employee
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="HR Management"
      subtitle="Human Resources"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search employees..."
      />

      {/* HR Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                247
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Employees
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                238
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                6
              </Typography>
              <Typography variant="caption" color="text.secondary">
                On Leave
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'info.main' }}>
                12
              </Typography>
              <Typography variant="caption" color="text.secondary">
                New Hires
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Employee List */}
      <MobileCard title="Recent Employees">
        <MobileTable
          columns={hrColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Employee clicked:', row)}
          showChevron={true}
          emptyMessage="No employees found"
        />
      </MobileCard>

      {/* Today's Activities */}
      <MobileCard title="Today's Activities">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'success.light',
            color: 'success.contrastText',
          }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                John Doe - Check In
              </Typography>
              <Typography variant="caption">
                Engineering • 09:15 AM
              </Typography>
            </Box>
            <Chip label="On Time" size="small" color="success" />
          </Box>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'warning.light',
            color: 'warning.contrastText',
          }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Leave Request - Sarah Wilson
              </Typography>
              <Typography variant="caption">
                Marketing • Medical Leave
              </Typography>
            </Box>
            <Chip label="Pending" size="small" color="warning" />
          </Box>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'info.light',
            color: 'info.contrastText',
          }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Interview Scheduled
              </Typography>
              <Typography variant="caption">
                Frontend Developer • 2:00 PM
              </Typography>
            </Box>
            <Chip label="Today" size="small" color="info" />
          </Box>
        </Box>
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Person />}
            >
              Attendance
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
              Payroll
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              HR Reports
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileHR;