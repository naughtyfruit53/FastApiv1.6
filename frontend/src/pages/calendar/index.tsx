// pages/calendar/index.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
  Fab
} from '@mui/material';
import { 
  CalendarToday, 
  Add,
  Today,
  ViewWeek,
  ViewModule,
  Schedule
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const CalendarPage: React.FC = () => {
  const [view, setView] = React.useState('month');

  const upcomingEvents = [
    { id: 1, title: 'Team Meeting', time: '10:00 AM', date: 'Today' },
    { id: 2, title: 'Project Review', time: '2:00 PM', date: 'Tomorrow' },
    { id: 3, title: 'Client Presentation', time: '9:00 AM', date: 'Friday' },
  ];

  return (
    <DashboardLayout
      title="Calendar"
      subtitle="Manage your schedule and events"
      actions={
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant={view === 'day' ? 'contained' : 'outlined'}
            onClick={() => setView('day')}
            startIcon={<Today />}
          >
            Day
          </Button>
          <Button 
            variant={view === 'week' ? 'contained' : 'outlined'}
            onClick={() => setView('week')}
            startIcon={<ViewWeek />}
          >
            Week
          </Button>
          <Button 
            variant={view === 'month' ? 'contained' : 'outlined'}
            onClick={() => setView('month')}
            startIcon={<ViewModule />}
          >
            Month
          </Button>
        </Box>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Calendar integration with Google, Outlook, and other services available in settings.
          </Alert>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card sx={{ minHeight: 600 }}>
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                minHeight: 500,
                flexDirection: 'column'
              }}>
                <CalendarToday sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" color="textSecondary" gutterBottom>
                  Calendar View ({view})
                </Typography>
                <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                  Interactive calendar component will be integrated here
                </Typography>
                <Button variant="contained" startIcon={<Add />}>
                  Create Event
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Schedule sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Upcoming Events</Typography>
              </Box>
              
              {upcomingEvents.map((event) => (
                <Box 
                  key={event.id}
                  sx={{ 
                    p: 2, 
                    border: 1, 
                    borderColor: 'grey.200',
                    borderRadius: 1,
                    mb: 1
                  }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    {event.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {event.date} at {event.time}
                  </Typography>
                </Box>
              ))}
              
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                href="/calendar/events"
              >
                View All Events
              </Button>
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mb: 1 }}
                href="/calendar/create"
              >
                Schedule Meeting
              </Button>
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mb: 1 }}
                href="/calendar/appointments"
              >
                Book Appointment
              </Button>
              <Button 
                fullWidth 
                variant="outlined"
                href="/calendar/meeting-rooms"
              >
                Reserve Room
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Fab 
        color="primary" 
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        href="/calendar/create"
      >
        <Add />
      </Fab>
    </DashboardLayout>
  );
};

export default CalendarPage;