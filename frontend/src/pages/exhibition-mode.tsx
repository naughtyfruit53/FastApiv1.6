import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar
} from '@mui/material';
import {
  CameraAlt,
  Upload,
  Visibility,
  Edit,
  Delete,
  Event,
  BusinessCenter,
  Email,
  Analytics,
  FileUpload,
  QrCodeScanner,
  ContactMail,
  TrendingUp
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
interface ExhibitionEvent {
  id: number;
  name: string;
  description?: string;
  location?: string;
  venue?: string;
  start_date?: string;
  end_date?: string;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  is_active: boolean;
  auto_send_intro_email: boolean;
  created_at: string;
  card_scan_count?: number;
  prospect_count?: number;
}
interface BusinessCardScan {
  id: number;
  scan_id: string;
  exhibition_event_id: number;
  full_name?: string;
  company_name?: string;
  designation?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: string;
  confidence_score?: number;
  validation_status: 'pending' | 'validated' | 'rejected';
  processing_status: 'scanned' | 'processed' | 'converted' | 'failed';
  prospect_created: boolean;
  intro_email_sent: boolean;
  created_at: string;
}
interface ExhibitionProspect {
  id: number;
  exhibition_event_id: number;
  card_scan_id?: number;
  full_name: string;
  company_name: string;
  designation?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: string;
  lead_score?: number;
  qualification_status: 'unqualified' | 'qualified' | 'hot' | 'cold';
  interest_level?: 'high' | 'medium' | 'low';
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost';
  conversion_status: 'prospect' | 'lead' | 'customer';
  created_at: string;
  intro_email_sent_at?: string;
  contact_attempts: number;
}
// Mock API service - would be replaced with actual API calls
const exhibitionAPI = {
  getEvents: () => Promise.resolve([
    {
      id: 1,
      name: "Tech Expo 2024",
      description: "Annual technology exhibition",
      location: "Convention Center",
      venue: "Hall A",
      start_date: "2024-03-15",
      end_date: "2024-03-17",
      status: "active" as const,
      is_active: true,
      auto_send_intro_email: true,
      created_at: "2024-02-01T10:00:00Z",
      card_scan_count: 25,
      prospect_count: 18
    },
    {
      id: 2,
      name: "Business Summit 2024",
      description: "Corporate networking event",
      location: "Downtown Hotel",
      venue: "Ballroom",
      start_date: "2024-04-10",
      end_date: "2024-04-11",
      status: "planned" as const,
      is_active: true,
      auto_send_intro_email: true,
      created_at: "2024-02-15T09:00:00Z",
      card_scan_count: 0,
      prospect_count: 0
    }
  ] as ExhibitionEvent[]),
  getCardScans: (eventId: number) => Promise.resolve([
    {
      id: 1,
      scan_id: "scan_001",
      exhibition_event_id: eventId,
      full_name: "John Smith",
      company_name: "TechCorp Solutions",
      designation: "CEO",
      email: "john.smith@techcorp.com",
      phone: "+1-555-0123",
      mobile: "+1-555-0124",
      website: "https://techcorp.com",
      address: "123 Business Ave, Tech City",
      confidence_score: 0.95,
      validation_status: "validated" as const,
      processing_status: "converted" as const,
      prospect_created: true,
      intro_email_sent: true,
      created_at: "2024-02-20T14:30:00Z"
    },
    {
      id: 2,
      scan_id: "scan_002",
      exhibition_event_id: eventId,
      full_name: "Sarah Johnson",
      company_name: "Innovation Labs",
      designation: "CTO",
      email: "sarah.j@innovationlabs.com",
      phone: "+1-555-0125",
      confidence_score: 0.87,
      validation_status: "pending" as const,
      processing_status: "processed" as const,
      prospect_created: false,
      intro_email_sent: false,
      created_at: "2024-02-21T09:15:00Z"
    }
  ] as BusinessCardScan[]),
  getProspects: (eventId: number) => Promise.resolve([
    {
      id: 1,
      exhibition_event_id: eventId,
      card_scan_id: 1,
      full_name: "John Smith",
      company_name: "TechCorp Solutions",
      designation: "CEO",
      email: "john.smith@techcorp.com",
      phone: "+1-555-0123",
      lead_score: 85,
      qualification_status: "qualified" as const,
      interest_level: "high" as const,
      status: "contacted" as const,
      conversion_status: "lead" as const,
      created_at: "2024-02-20T14:30:00Z",
      intro_email_sent_at: "2024-02-20T15:00:00Z",
      contact_attempts: 2
    }
  ] as ExhibitionProspect[])
};
const ExhibitionMode: React.FC = () => {
  const [selectedEvent, setSelectedEvent] = useState<ExhibitionEvent | null>(null);
  const [activeTab, setActiveTab] = useState<'events' | 'scans' | 'prospects' | 'analytics'>('events');
  const [scanModalOpen, setScanModalOpen] = useState(false);
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const queryClient = useQueryClient();
  // Queries
  const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ['exhibition-events'],
    queryFn: exhibitionAPI.getEvents
  });
  const { data: cardScans, isLoading: scansLoading } = useQuery({
    queryKey: ['card-scans', selectedEvent?.id],
    queryFn: () => selectedEvent ? exhibitionAPI.getCardScans(selectedEvent.id) : Promise.resolve([]),
    enabled: !!selectedEvent
  });
  const { data: prospects, isLoading: prospectsLoading } = useQuery({
    queryKey: ['prospects', selectedEvent?.id],
    queryFn: () => selectedEvent ? exhibitionAPI.getProspects(selectedEvent.id) : Promise.resolve([]),
    enabled: !!selectedEvent
  });
  // Mock scan mutation
  const scanMutation = useMutation({
    mutationFn: async (file: File) => {
      setScanning(true);
      // Simulate OCR processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      setScanning(false);
      return {
        id: Date.now(),
        scan_id: `scan_${Date.now()}`,
        exhibition_event_id: selectedEvent?.id || 0,
        full_name: "Demo Contact",
        company_name: "Demo Company",
        confidence_score: 0.9,
        validation_status: "pending" as const,
        processing_status: "processed" as const,
        prospect_created: false,
        intro_email_sent: false,
        created_at: new Date().toISOString()
      };
    },
    onSuccess: () => {
      toast.success('Business card scanned successfully!');
      setScanModalOpen(false);
      setSelectedFile(null);
      queryClient.invalidateQueries({ queryKey: ['card-scans'] });
    },
    onError: () => {
      setScanning(false);
      toast.error('Failed to scan business card');
    }
  });
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
    } else {
      toast.error('Please select a valid image file');
    }
  };
  const handleScanCard = () => {
    if (selectedFile) {
      scanMutation.mutate(selectedFile);
    }
  };
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'planned': return 'info';
      case 'completed': return 'default';
      case 'cancelled': return 'error';
      case 'validated': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'qualified': return 'success';
      case 'hot': return 'error';
      case 'converted': return 'success';
      default: return 'default';
    }
  };
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  if (eventsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Exhibition Mode
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Scan business cards, manage prospects, and track leads from exhibition events
      </Typography>
      {/* Tab Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Box display="flex" gap={2}>
          {[
            { key: 'events', label: 'Events', icon: <Event /> },
            { key: 'scans', label: 'Card Scans', icon: <QrCodeScanner /> },
            { key: 'prospects', label: 'Prospects', icon: <ContactMail /> },
            { key: 'analytics', label: 'Analytics', icon: <TrendingUp /> }
          ].map(tab => (
            <Button
              key={tab.key}
              variant={activeTab === tab.key ? 'contained' : 'text'}
              startIcon={tab.icon}
              onClick={() => setActiveTab(tab.key as any)}
              sx={{ mb: 1 }}
            >
              {tab.label}
            </Button>
          ))}
        </Box>
      </Box>
      {/* Events Tab */}
      {activeTab === 'events' && (
        <Box>
          <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
            <Typography variant="h6">Exhibition Events</Typography>
            <Button
              variant="contained"
              startIcon={<Event />}
              onClick={() => setEventModalOpen(true)}
            >
              Create Event
            </Button>
          </Box>
          <Grid container spacing={3}>
            {events?.map(event => (
              <Grid item xs={12} md={6} lg={4} key={event.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: selectedEvent?.id === event.id ? 2 : 0,
                    borderColor: 'primary.main'
                  }}
                  onClick={() => setSelectedEvent(event)}
                >
                  <CardContent>
                    <Box display="flex" justifyContent="between" alignItems="start" mb={2}>
                      <Typography variant="h6" noWrap>
                        {event.name}
                      </Typography>
                      <Chip 
                        label={event.status} 
                        color={getStatusColor(event.status) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {event.description}
                    </Typography>
                    <Box display="flex" gap={2} mb={2}>
                      <Typography variant="body2">
                        📍 {event.location}
                      </Typography>
                    </Box>
                    {event.start_date && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {formatDate(event.start_date)} - {event.end_date ? formatDate(event.end_date) : 'Ongoing'}
                      </Typography>
                    )}
                    <Box display="flex" justifyContent="between" alignItems="center">
                      <Box display="flex" gap={2}>
                        <Chip 
                          label={`${event.card_scan_count || 0} Scans`} 
                          size="small" 
                          variant="outlined"
                        />
                        <Chip 
                          label={`${event.prospect_count || 0} Prospects`} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                      {event.status === 'active' && (
                        <Button
                          size="small"
                          variant="contained"
                          startIcon={<CameraAlt />}
                          onClick={(e) => {
                            e.stopPropagation();
                            setScanModalOpen(true);
                          }}
                        >
                          Scan Card
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      {/* Card Scans Tab */}
      {activeTab === 'scans' && selectedEvent && (
        <Box>
          <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
            <Typography variant="h6">
              Card Scans - {selectedEvent.name}
            </Typography>
            <Button
              variant="contained"
              startIcon={<CameraAlt />}
              onClick={() => setScanModalOpen(true)}
            >
              Scan New Card
            </Button>
          </Box>
          {scansLoading ? (
            <CircularProgress />
          ) : (
            <List>
              {cardScans?.map(scan => (
                <ListItem key={scan.id} divider>
                  <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                    <BusinessCenter />
                  </Avatar>
                  <ListItemText
                    primary={`${scan.full_name || 'Unknown'} - ${scan.company_name || 'Unknown Company'}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {scan.designation} • {scan.email}
                        </Typography>
                        <Box display="flex" gap={1} mt={1}>
                          <Chip 
                            label={scan.validation_status} 
                            size="small" 
                            color={getStatusColor(scan.validation_status) as any}
                          />
                          <Chip 
                            label={`${Math.round((scan.confidence_score || 0) * 100)}% confidence`} 
                            size="small" 
                            variant="outlined"
                          />
                          {scan.prospect_created && (
                            <Chip label="Prospect Created" size="small" color="success" />
                          )}
                          {scan.intro_email_sent && (
                            <Chip label="Email Sent" size="small" color="info" />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}
      {/* Prospects Tab */}
      {activeTab === 'prospects' && selectedEvent && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Prospects - {selectedEvent.name}
          </Typography>
          {prospectsLoading ? (
            <CircularProgress />
          ) : (
            <List>
              {prospects?.map(prospect => (
                <ListItem key={prospect.id} divider>
                  <Avatar sx={{ mr: 2, bgcolor: 'secondary.main' }}>
                    <ContactMail />
                  </Avatar>
                  <ListItemText
                    primary={`${prospect.full_name} - ${prospect.company_name}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {prospect.designation} • Score: {prospect.lead_score || 0}
                        </Typography>
                        <Box display="flex" gap={1} mt={1}>
                          <Chip 
                            label={prospect.qualification_status} 
                            size="small" 
                            color={getStatusColor(prospect.qualification_status) as any}
                          />
                          <Chip 
                            label={prospect.status} 
                            size="small" 
                            variant="outlined"
                          />
                          {prospect.interest_level && (
                            <Chip 
                              label={`${prospect.interest_level} interest`} 
                              size="small" 
                              color={prospect.interest_level === 'high' ? 'success' : 'default'}
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <Email />
                    </IconButton>
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      )}
      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Exhibition Analytics
          </Typography>
          <Alert severity="info">
            Analytics dashboard will show conversion rates, lead quality metrics, 
            and performance comparisons across events.
          </Alert>
        </Box>
      )}
      {/* Card Scan Modal */}
      <Dialog open={scanModalOpen} onClose={() => setScanModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Scan Business Card</DialogTitle>
        <DialogContent>
          {scanning ? (
            <Box display="flex" flexDirection="column" alignItems="center" py={4}>
              <CircularProgress size={60} sx={{ mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Processing Business Card...
              </Typography>
              <Typography color="text.secondary">
                Extracting contact information using OCR
              </Typography>
              <LinearProgress sx={{ width: '100%', mt: 2 }} />
            </Box>
          ) : (
            <Box>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Upload an image of a business card to extract contact information automatically.
              </Typography>
              <Box 
                border={2} 
                borderColor={selectedFile ? 'primary.main' : 'grey.300'}
                borderStyle="dashed"
                borderRadius={2}
                p={4}
                textAlign="center"
                sx={{ mb: 3 }}
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <IconButton component="span" size="large">
                    <Upload fontSize="large" />
                  </IconButton>
                </label>
                <Typography variant="h6" gutterBottom>
                  {selectedFile ? selectedFile.name : 'Click to upload business card image'}
                </Typography>
                <Typography color="text.secondary">
                  Supports JPG, PNG, and other image formats
                </Typography>
              </Box>
              {selectedFile && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Business card image selected: {selectedFile.name}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScanModalOpen(false)} disabled={scanning}>
            Cancel
          </Button>
          <Button 
            onClick={handleScanCard} 
            variant="contained" 
            disabled={!selectedFile || scanning}
          >
            {scanning ? 'Processing...' : 'Scan Card'}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Event Creation Modal - Placeholder */}
      <Dialog open={eventModalOpen} onClose={() => setEventModalOpen(false)}>
        <DialogTitle>Create Exhibition Event</DialogTitle>
        <DialogContent>
          <Alert severity="info">
            Event creation form would be implemented here with fields for name, dates, location, etc.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEventModalOpen(false)}>Cancel</Button>
          <Button variant="contained">Create Event</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default ExhibitionMode;