// pages/tasks/assignments.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert
} from '@mui/material';
import { 
  AssignmentTurnedIn
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const TasksAssignmentsPage: React.FC = () => {
  return (
    <DashboardLayout
      title="Assignments"
      subtitle="Manage task assignments"
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            This assignments module is under development. Core functionality will be available soon.
          </Alert>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center', 
                minHeight: 400,
                textAlign: 'center'
              }}>
                <AssignmentTurnedIn sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" gutterBottom>
                  Assignments
                </Typography>
                <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                  Manage task assignments
                </Typography>
                <Button variant="contained" disabled>
                  Feature Coming Soon
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default TasksAssignmentsPage;