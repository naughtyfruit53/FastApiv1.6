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
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import exhibitionService, {
  ExhibitionEvent,
} from "../services/exhibitionService";
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
            justifyContent="between"
            alignItems="center"
            mb={3}
          >
            <Typography variant="h6">Exhibition Events</Typography>
            <Button
              variant="contained"
              startIcon={<Event />}
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
                    startIcon={<Event />}
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
                        justifyContent="between"
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
                          📍 {event.location}
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
                        justifyContent="between"
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
      {activeTab === "scans" && selectedEvent && (
        <Box>
          <Box
            display="flex"
            justifyContent="between"
            alignItems="center"
            mb={3}
          >
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
                    Start scanning business cards to capture leads from this exhibition event.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<CameraAlt />}
                    onClick={() => setScanModalOpen(true)}
                  >
                    Scan First Card
                  </Button>
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
      {activeTab === "prospects" && selectedEvent && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Prospects - {selectedEvent.name}
          </Typography>
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
                    Scan business cards or manually add prospects to start tracking potential leads from this event.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<CameraAlt />}
                    onClick={() => setScanModalOpen(true)}
                  >
                    Scan Business Card
                  </Button>
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
            Exhibition Analytics
          </Typography>
          <Alert severity="info">
            Analytics dashboard will show conversion rates, lead quality
            metrics, and performance comparisons across events.
          </Alert>
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
          {scanning ? (
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
            disabled={!selectedFile || scanning}
          >
            {scanning ? "Processing..." : "Scan Card"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Event Creation Modal - Placeholder */}
      <Dialog open={eventModalOpen} onClose={() => setEventModalOpen(false)}>
        <DialogTitle>Create Exhibition Event</DialogTitle>
        <DialogContent>
          <Alert severity="info">
            Event creation form would be implemented here with fields for name,
            dates, location, etc.
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
