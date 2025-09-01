// frontend/src/pages/calendar/dashboard.tsx
'use client';
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import {
  CalendarToday,
  Dashboard,
  Event,
  Today,
  DateRange,
  Schedule,
  Notifications,
  Add,
  Person,
  VideoCall,
  LocationOn
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
interface CalendarStats {
  total_events: number;
  today_events: number;
  this_week_events: number;
  this_month_events: number;
  upcoming_events: number;
  overdue_events: number;
  my_events: number;
  shared_events: number;
}
interface UpcomingEvent {
  id: number;
  title: string;
  start_datetime: string;
  end_datetime: string;
  event_type: string;
  location?: string;
  meeting_url?: string;
  attendees_count: number;
}
const CalendarDashboard: React.FC = () => {
  const router = useRouter();
  const [stats, setStats] = useState<CalendarStats | null>(null);
  const [upcomingEvents, setUpcomingEvents] = useState<UpcomingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    // Simulate API call - replace with actual API integration
    const fetchData = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API calls
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        // Mock data for demonstration
        const mockStats: CalendarStats = {
          total_events: 34,
          today_events: 4,
          this_week_events: 12,
          this_month_events: 25,
          upcoming_events: 18,
          overdue_events: 2,
          my_events: 28,
          shared_events: 6
        };
        const mockEvents: UpcomingEvent[] = [
          {
            id: 1,
            title: 'Team Standup Meeting',
            start_datetime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
            end_datetime: new Date(Date.now() + 2.5 * 60 * 60 * 1000).toISOString(),
            event_type: 'meeting',
            meeting_url: 'https://meet.google.com/abc-def-ghi',
            attendees_count: 5
          },
          {
            id: 2,
            title: 'Client Presentation',
            start_datetime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
            end_datetime: new Date(Date.now() + 25 * 60 * 60 * 1000).toISOString(),
            event_type: 'appointment',
            location: 'Conference Room A',
            attendees_count: 3
          },
          {
            id: 3,
            title: 'Project Review',
            start_datetime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days
            end_datetime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(),
            event_type: 'meeting',
            attendees_count: 8
          }
        ];
        setStats(mockStats);
        setUpcomingEvents(mockEvents);
      } catch {
        setError('Failed to load calendar dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
  const handleNavigate = (path: string) => {
    router.push(path);
  };
  const formatDateTime = (dateTime: string) => {
    const date = new Date(dateTime);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
    const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    let dateStr = '';
    if (eventDate.getTime() === today.getTime()) {
      dateStr = 'Today';
    } else if (eventDate.getTime() === tomorrow.getTime()) {
      dateStr = 'Tomorrow';
    } else {
      dateStr = date.toLocaleDateString();
    }
    const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return `${dateStr} ${timeStr}`;
  };
  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'meeting': return 'primary';
      case 'appointment': return 'secondary';
      case 'task': return 'warning';
      case 'reminder': return 'info';
      default: return 'default';
    }
  };
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  if (!stats) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No calendar data available</Alert>
      </Box>
    );
  }
  return (
    <Box 
      sx={{ 
        p: 3,
        opacity: 0,
        animation: 'fadeInUp 0.6s ease-out forwards',
        '@keyframes fadeInUp': {
          from: { opacity: 0, transform: 'translateY(30px)' },
          to: { opacity: 1, transform: 'translateY(0)' }
        }
      }}
    >
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 4,
        pb: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        position: 'relative',
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: '-1px',
          left: 0,
          width: '60px',
          height: '3px',
          background: 'linear-gradient(90deg, primary.main, primary.light)',
          borderRadius: '2px',
        }
      }}>
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1,
            fontWeight: 'bold',
            color: 'text.primary'
          }}
        >
          <Dashboard color="primary" />
          Calendar Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleNavigate('/calendar/create')}
          sx={{
            borderRadius: 2,
            px: 3,
            py: 1.5,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
            }
          }}
        >
          Create Event
        </Button>
      </Box>
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                '& .card-icon': {
                  transform: 'scale(1.1) rotate(5deg)',
                }
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Total Events
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {stats.total_events}
                  </Typography>
                </Box>
                <Box
                  className="card-icon"
                  sx={{
                    backgroundColor: 'primary.50',
                    borderRadius: 2,
                    p: 1.5,
                    transition: 'all 0.3s ease',
                  }}
                >
                  <Event color="primary" sx={{ fontSize: 32 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                '& .card-icon': {
                  transform: 'scale(1.1) rotate(5deg)',
                }
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    Today's Events
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                    {stats.today_events}
                  </Typography>
                </Box>
                <Box
                  className="card-icon"
                  sx={{
                    backgroundColor: 'info.50',
                    borderRadius: 2,
                    p: 1.5,
                    transition: 'all 0.3s ease',
                  }}
                >
                  <Today color="info" sx={{ fontSize: 32 }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                '& .card-icon': {
                  transform: 'scale(1.1) rotate(5deg)',
                }
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2" sx={{ fontWeight: 500 }}>
                    This Week
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                    {stats.this_week_events}
                  </Typography>
                </Box>
                <DateRange color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Upcoming
                  </Typography>
                  <Typography variant="h5">
                    {stats.upcoming_events}
                  </Typography>
                </Box>
                <Schedule color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Schedule color="primary" />
                Upcoming Events
              </Typography>
              <List>
                {upcomingEvents.map((event, index) => (
                  <React.Fragment key={event.id}>
                    <ListItem
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 1,
                        '&:hover': {
                          backgroundColor: 'action.hover'
                        }
                      }}
                      onClick={() => handleNavigate(`/calendar/events/${event.id}`)}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: `${getEventTypeColor(event.event_type)}.main` }}>
                          {event.event_type === 'meeting' ? <VideoCall /> : <Event />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="subtitle1">{event.title}</Typography>
                            <Chip
                              label={event.event_type}
                              size="small"
                              color={getEventTypeColor(event.event_type) as any}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {formatDateTime(event.start_datetime)}
                            </Typography>
                            {event.location && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                <LocationOn sx={{ fontSize: 16 }} />
                                <Typography variant="caption">{event.location}</Typography>
                              </Box>
                            )}
                            {event.meeting_url && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                <VideoCall sx={{ fontSize: 16 }} />
                                <Typography variant="caption">Video Meeting</Typography>
                              </Box>
                            )}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                              <Person sx={{ fontSize: 16 }} />
                              <Typography variant="caption">{event.attendees_count} attendees</Typography>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < upcomingEvents.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              {upcomingEvents.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="textSecondary">No upcoming events</Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => handleNavigate('/calendar/create')}
                    sx={{ mt: 2 }}
                  >
                    Create Your First Event
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <Button
                      variant="outlined"
                      startIcon={<CalendarToday />}
                      onClick={() => handleNavigate('/calendar')}
                      fullWidth
                    >
                      View Calendar
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Event />}
                      onClick={() => handleNavigate('/calendar/events')}
                      fullWidth
                    >
                      All Events
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Schedule />}
                      onClick={() => handleNavigate('/calendar/appointments')}
                      fullWidth
                    >
                      Appointments
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Notifications />}
                      onClick={() => handleNavigate('/calendar/reminders')}
                      fullWidth
                    >
                      Reminders
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Calendar Stats
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">My Events</Typography>
                      <Typography variant="body2">{stats.my_events}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Shared Events</Typography>
                      <Typography variant="body2">{stats.shared_events}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">This Month</Typography>
                      <Typography variant="body2">{stats.this_month_events}</Typography>
                    </Box>
                    {stats.overdue_events > 0 && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="error">Overdue</Typography>
                        <Typography variant="body2" color="error">{stats.overdue_events}</Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};
export default CalendarDashboard;