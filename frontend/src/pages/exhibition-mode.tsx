import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  TextField,
  FormControlLabel,
  Switch,
  Paper,
} from "@mui/material";
import {
  CameraAlt,
  Upload,
  Visibility,
  Edit,
  Event,
  BusinessCenter,
  Email,
  QrCodeScanner,
  ContactMail,
  TrendingUp,
  Add,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import exhibitionService, {
  ExhibitionEvent,
  ExhibitionAnalytics,
} from "../services/exhibitionService";

interface EventFormData {
  name: string;
  description: string;
  location: string;
  venue: string;
  start_date: string;
  end_date: string;
  status: "planned" | "active" | "completed" | "cancelled";
  auto_send_intro_email: boolean;
}

const ExhibitionMode: React.FC = () => {
  const [selectedEvent, setSelectedEvent] = useState<ExhibitionEvent | null>(
    null,
  );
  const [activeTab, setActiveTab] = useState<
    "events" | "scans" | "prospects" | "analytics"
  >("events");
  const [scanModalOpen, setScanModalOpen] = useState(false);
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [eventFormData, setEventFormData] = useState<EventFormData>({
    name: "",
    description: "",
    location: "",
    venue: "",
    start_date: "",
    end_date: "",
    status: "planned",
    auto_send_intro_email: true,
  });
  const queryClient = useQueryClient();

  // Queries
  const { data: events = [], isLoading: eventsLoading } = useQuery({
    queryKey: ["exhibition-events"],
    queryFn: () => exhibitionService.getEvents(),
  });

  const { data: cardScans = [], isLoading: scansLoading } = useQuery({
    queryKey: ["card-scans", selectedEvent?.id],
    queryFn: () =>
      selectedEvent
        ? exhibitionService.getCardScans(selectedEvent.id)
        : Promise.resolve([]),
    enabled: !!selectedEvent,
  });

  const { data: prospects = [], isLoading: prospectsLoading } = useQuery({
    queryKey: ["prospects", selectedEvent?.id],
    queryFn: () =>
      selectedEvent
        ? exhibitionService.getProspects(selectedEvent.id)
        : Promise.resolve([]),
    enabled: !!selectedEvent,
  });

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ["exhibition-analytics", selectedEvent?.id],
    queryFn: () => exhibitionService.getAnalytics(selectedEvent?.id ? { event_id: selectedEvent.id } : undefined),
    enabled: activeTab === "analytics",
  });

  // Create event mutation
  const createEventMutation = useMutation({
    mutationFn: async (data: EventFormData) => {
      return exhibitionService.createEvent({
        name: data.name,
        description: data.description || undefined,
        location: data.location || undefined,
        venue: data.venue || undefined,
        start_date: data.start_date || undefined,
        end_date: data.end_date || undefined,
        status: data.status,
        auto_send_intro_email: data.auto_send_intro_email,
      });
    },
    onSuccess: (newEvent) => {
      toast.success("Exhibition event created successfully!");
      setEventModalOpen(false);
      setEventFormData({
        name: "",
        description: "",
        location: "",
        venue: "",
        start_date: "",
        end_date: "",
        status: "planned",
        auto_send_intro_email: true,
      });
      queryClient.invalidateQueries({ queryKey: ["exhibition-events"] });
      setSelectedEvent(newEvent);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Failed to create event");
    },
  });

  // Real scan mutation using backend API
  const scanMutation = useMutation({
    mutationFn: async (file: File) => {
      if (!selectedEvent) {
        throw new Error("No event selected");
      }
      setScanning(true);
      const result = await exhibitionService.scanBusinessCard(selectedEvent.id, file);
      setScanning(false);
      return result;
    },
    onSuccess: () => {
      toast.success("Business card scanned successfully!");
      setScanModalOpen(false);
      setSelectedFile(null);
      queryClient.invalidateQueries({ queryKey: ["card-scans"] });
      queryClient.invalidateQueries({ queryKey: ["exhibition-events"] });
    },
    onError: (error: any) => {
      setScanning(false);
      toast.error(error?.response?.data?.detail || "Failed to scan business card");
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
    } else {
      toast.error("Please select a valid image file");
    }
  };

  const handleScanCard = () => {
    if (selectedFile) {
      scanMutation.mutate(selectedFile);
    }
  };

  const handleCreateEvent = () => {
    if (!eventFormData.name.trim()) {
      toast.error("Event name is required");
      return;
    }
    createEventMutation.mutate(eventFormData);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "planned":
        return "info";
      case "completed":
        return "default";
      case "cancelled":
        return "error";
      case "validated":
        return "success";
      case "pending":
        return "warning";
      case "rejected":
        return "error";
      case "qualified":
        return "success";
      case "hot":
        return "error";
      case "converted":
        return "success";
      default:
        return "default";
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (eventsLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
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
        Scan business cards, manage prospects, and track leads from exhibition
        events
      </Typography>
      {/* Tab Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Box display="flex" gap={2}>
          {[
            { key: "events", label: "Events", icon: <Event /> },
            { key: "scans", label: "Card Scans", icon: <QrCodeScanner /> },
            { key: "prospects", label: "Prospects", icon: <ContactMail /> },
            { key: "analytics", label: "Analytics", icon: <TrendingUp /> },
          ].map((tab) => (
            <Button
              key={tab.key}
              variant={activeTab === tab.key ? "contained" : "text"}
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
      {activeTab === "events" && (
        <Box>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={3}
          >
            <Typography variant="h6">Exhibition Events</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setEventModalOpen(true)}
            >
              Create Event
            </Button>
          </Box>
          {events.length === 0 ? (
            <Card>
              <CardContent>
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  py={6}
                >
                  <Event sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No Exhibition Events
                  </Typography>
                  <Typography color="text.secondary" align="center" sx={{ mb: 3 }}>
                    Create your first exhibition event to start tracking business cards and prospects.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setEventModalOpen(true)}
                  >
                    Create First Event
                  </Button>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Grid container spacing={3}>
              {events.map((event) => (
                <Grid item xs={12} md={6} lg={4} key={event.id}>
                  <Card
                    sx={{
                      cursor: "pointer",
                      border: selectedEvent?.id === event.id ? 2 : 0,
                      borderColor: "primary.main",
                    }}
                    onClick={() => setSelectedEvent(event)}
                  >
                    <CardContent>
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="start"
                        mb={2}
                      >
                        <Typography variant="h6" noWrap>
                          {event.name}
                        </Typography>
                        <Chip
                          label={event.status}
                          color={getStatusColor(event.status) as any}
                          size="small"
                        />
                      </Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                      >
                        {event.description}
                      </Typography>
                      <Box display="flex" gap={2} mb={2}>
                        <Typography variant="body2">
                          📍 {event.location || "No location"}
                        </Typography>
                      </Box>
                      {event.start_date && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 2 }}
                        >
                          {formatDate(event.start_date)} -{" "}
                          {event.end_date
                            ? formatDate(event.end_date)
                            : "Ongoing"}
                        </Typography>
                      )}
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                      >
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
                        {event.status === "active" && (
                          <Button
                            size="small"
                            variant="contained"
                            startIcon={<CameraAlt />}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedEvent(event);
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
          )}
        </Box>
      )}
      {/* Card Scans Tab */}
      {activeTab === "scans" && (
        <Box>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={3}
          >
            <Typography variant="h6">
              Card Scans {selectedEvent ? `- ${selectedEvent.name}` : "(All Events)"}
            </Typography>
            {selectedEvent && (
              <Button
                variant="contained"
                startIcon={<CameraAlt />}
                onClick={() => setScanModalOpen(true)}
              >
                Scan New Card
              </Button>
            )}
          </Box>
          {!selectedEvent && (
            <Alert severity="info" sx={{ mb: 3 }}>
              Select an event from the Events tab to view and scan cards for that specific event.
            </Alert>
          )}
          {scansLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : cardScans.length === 0 ? (
            <Card>
              <CardContent>
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  py={6}
                >
                  <QrCodeScanner sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No Card Scans Yet
                  </Typography>
                  <Typography color="text.secondary" align="center" sx={{ mb: 3 }}>
                    {selectedEvent 
                      ? "Start scanning business cards to capture leads from this exhibition event."
                      : "Select an event first, then start scanning business cards."}
                  </Typography>
                  {selectedEvent && (
                    <Button
                      variant="contained"
                      startIcon={<CameraAlt />}
                      onClick={() => setScanModalOpen(true)}
                    >
                      Scan First Card
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          ) : (
            <List>
              {cardScans.map((scan) => (
                <ListItem key={scan.id} divider>
                  <Avatar sx={{ mr: 2, bgcolor: "primary.main" }}>
                    <BusinessCenter />
                  </Avatar>
                  <ListItemText
                    primary={`${scan.full_name || "Unknown"} - ${scan.company_name || "Unknown Company"}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {scan.designation} • {scan.email}
                        </Typography>
                        <Box display="flex" gap={1} mt={1}>
                          <Chip
                            label={scan.validation_status}
                            size="small"
                            color={
                              getStatusColor(scan.validation_status) as any
                            }
                          />
                          <Chip
                            label={`${Math.round((scan.confidence_score || 0) * 100)}% confidence`}
                            size="small"
                            variant="outlined"
                          />
                          {scan.prospect_created && (
                            <Chip
                              label="Prospect Created"
                              size="small"
                              color="success"
                            />
                          )}
                          {scan.intro_email_sent && (
                            <Chip
                              label="Email Sent"
                              size="small"
                              color="info"
                            />
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
      {activeTab === "prospects" && (
        <Box>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={3}
          >
            <Typography variant="h6">
              Prospects {selectedEvent ? `- ${selectedEvent.name}` : "(All Events)"}
            </Typography>
            {selectedEvent && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setScanModalOpen(true)}
              >
                Add Prospect
              </Button>
            )}
          </Box>
          {!selectedEvent && (
            <Alert severity="info" sx={{ mb: 3 }}>
              Select an event from the Events tab to view prospects for that specific event.
            </Alert>
          )}
          {prospectsLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : prospects.length === 0 ? (
            <Card>
              <CardContent>
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  py={6}
                >
                  <ContactMail sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No Prospects Yet
                  </Typography>
                  <Typography color="text.secondary" align="center" sx={{ mb: 3 }}>
                    {selectedEvent
                      ? "Scan business cards or manually add prospects to start tracking potential leads from this event."
                      : "Select an event first to view and manage prospects."}
                  </Typography>
                  {selectedEvent && (
                    <Button
                      variant="contained"
                      startIcon={<CameraAlt />}
                      onClick={() => setScanModalOpen(true)}
                    >
                      Scan Business Card
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          ) : (
            <List>
              {prospects.map((prospect) => (
                <ListItem key={prospect.id} divider>
                  <Avatar sx={{ mr: 2, bgcolor: "secondary.main" }}>
                    <ContactMail />
                  </Avatar>
                  <ListItemText
                    primary={`${prospect.full_name} - ${prospect.company_name}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {prospect.designation} • Score:{" "}
                          {prospect.lead_score || 0}
                        </Typography>
                        <Box display="flex" gap={1} mt={1}>
                          <Chip
                            label={prospect.qualification_status}
                            size="small"
                            color={
                              getStatusColor(
                                prospect.qualification_status,
                              ) as any
                            }
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
                              color={
                                prospect.interest_level === "high"
                                  ? "success"
                                  : "default"
                              }
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
      {activeTab === "analytics" && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Exhibition Analytics {selectedEvent ? `- ${selectedEvent.name}` : "(Overall)"}
          </Typography>
          {analyticsLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : analytics ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 3, textAlign: "center" }}>
                  <Typography variant="h3" color="primary">
                    {analytics.total_events}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Events
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 3, textAlign: "center" }}>
                  <Typography variant="h3" color="success.main">
                    {analytics.total_scans}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Scans
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 3, textAlign: "center" }}>
                  <Typography variant="h3" color="info.main">
                    {analytics.total_prospects}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Prospects
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 3, textAlign: "center" }}>
                  <Typography variant="h3" color="warning.main">
                    {analytics.conversion_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Conversion Rate
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Top Companies
                  </Typography>
                  {analytics.top_companies && analytics.top_companies.length > 0 ? (
                    <List dense>
                      {analytics.top_companies.slice(0, 5).map((company: any, index: number) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={company.name}
                            secondary={`${company.count} prospects`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No data available</Typography>
                  )}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Lead Quality Distribution
                  </Typography>
                  {analytics.lead_quality_distribution && Object.keys(analytics.lead_quality_distribution).length > 0 ? (
                    <Box display="flex" gap={2} flexWrap="wrap">
                      {Object.entries(analytics.lead_quality_distribution).map(([status, count]) => (
                        <Chip
                          key={status}
                          label={`${status}: ${count}`}
                          color={getStatusColor(status) as any}
                        />
                      ))}
                    </Box>
                  ) : (
                    <Typography color="text.secondary">No data available</Typography>
                  )}
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">
              No analytics data available yet. Start by creating events and scanning business cards.
            </Alert>
          )}
        </Box>
      )}
      {/* Card Scan Modal */}
      <Dialog
        open={scanModalOpen}
        onClose={() => setScanModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Scan Business Card</DialogTitle>
        <DialogContent>
          {!selectedEvent ? (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Please select an event first before scanning a business card.
            </Alert>
          ) : scanning ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              py={4}
            >
              <CircularProgress size={60} sx={{ mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Processing Business Card...
              </Typography>
              <Typography color="text.secondary">
                Extracting contact information using OCR
              </Typography>
              <LinearProgress sx={{ width: "100%", mt: 2 }} />
            </Box>
          ) : (
            <Box>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Upload an image of a business card to extract contact
                information automatically.
              </Typography>
              <Box
                border={2}
                borderColor={selectedFile ? "primary.main" : "grey.300"}
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
                  style={{ display: "none" }}
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <IconButton component="span" size="large">
                    <Upload fontSize="large" />
                  </IconButton>
                </label>
                <Typography variant="h6" gutterBottom>
                  {selectedFile
                    ? selectedFile.name
                    : "Click to upload business card image"}
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
            disabled={!selectedFile || scanning || !selectedEvent}
          >
            {scanning ? "Processing..." : "Scan Card"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Event Creation Modal */}
      <Dialog 
        open={eventModalOpen} 
        onClose={() => setEventModalOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Exhibition Event</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField
              label="Event Name"
              fullWidth
              required
              value={eventFormData.name}
              onChange={(e) => setEventFormData({ ...eventFormData, name: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={eventFormData.description}
              onChange={(e) => setEventFormData({ ...eventFormData, description: e.target.value })}
            />
            <TextField
              label="Location"
              fullWidth
              value={eventFormData.location}
              onChange={(e) => setEventFormData({ ...eventFormData, location: e.target.value })}
            />
            <TextField
              label="Venue"
              fullWidth
              value={eventFormData.venue}
              onChange={(e) => setEventFormData({ ...eventFormData, venue: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Start Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={eventFormData.start_date}
                  onChange={(e) => setEventFormData({ ...eventFormData, start_date: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="End Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={eventFormData.end_date}
                  onChange={(e) => setEventFormData({ ...eventFormData, end_date: e.target.value })}
                />
              </Grid>
            </Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={eventFormData.auto_send_intro_email}
                  onChange={(e) => setEventFormData({ ...eventFormData, auto_send_intro_email: e.target.checked })}
                />
              }
              label="Auto-send intro email to prospects"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEventModalOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreateEvent}
            disabled={createEventMutation.isPending}
          >
            {createEventMutation.isPending ? "Creating..." : "Create Event"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default ExhibitionMode;
