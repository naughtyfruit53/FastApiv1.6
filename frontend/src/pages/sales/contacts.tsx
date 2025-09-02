"use client";
import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Avatar,
  Tooltip,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
} from "@mui/icons-material";
interface Contact {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  jobTitle: string;
  company: string;
  department: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  source: string;
  status: "active" | "inactive" | "lead";
  tags: string[];
  lastContact: string;
  created_at: string;
  assignedTo: string;
  notes: string;
}
const ContactManagement: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<"view" | "edit" | "create">(
    "view",
  );
  const [tabValue, setTabValue] = useState(0);
  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchContacts = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const mockData: Contact[] = [
          {
            id: 1,
            firstName: "John",
            lastName: "Smith",
            email: "john.smith@techcorp.com",
            phone: "+1-555-0123",
            jobTitle: "CTO",
            company: "TechCorp Ltd",
            department: "Technology",
            address: "123 Tech Street",
            city: "San Francisco",
            state: "CA",
            zipCode: "94105",
            country: "USA",
            source: "Website",
            status: "active",
            tags: ["decision-maker", "technical"],
            lastContact: "2024-01-20",
            created_at: "2023-08-15",
            assignedTo: "Sarah Johnson",
            notes:
              "Primary technical contact. Interested in enterprise solutions.",
          },
          {
            id: 2,
            firstName: "Mike",
            lastName: "Wilson",
            email: "mike.wilson@globalsystems.com",
            phone: "+1-555-0124",
            jobTitle: "VP of Operations",
            company: "Global Systems Inc",
            department: "Operations",
            address: "456 Business Ave",
            city: "New York",
            state: "NY",
            zipCode: "10001",
            country: "USA",
            source: "Referral",
            status: "active",
            tags: ["decision-maker", "operations"],
            lastContact: "2024-01-18",
            created_at: "2023-06-20",
            assignedTo: "David Brown",
            notes: "Responsible for operational efficiency initiatives.",
          },
          {
            id: 3,
            firstName: "Lisa",
            lastName: "Davis",
            email: "lisa.davis@manufacturing.com",
            phone: "+1-555-0125",
            jobTitle: "IT Manager",
            company: "Manufacturing Co",
            department: "IT",
            address: "789 Industrial Blvd",
            city: "Detroit",
            state: "MI",
            zipCode: "48201",
            country: "USA",
            source: "Cold Call",
            status: "lead",
            tags: ["technical", "evaluating"],
            lastContact: "2024-01-15",
            created_at: "2024-01-10",
            assignedTo: "Sarah Johnson",
            notes: "Evaluating ERP solutions for manufacturing operations.",
          },
          {
            id: 4,
            firstName: "Robert",
            lastName: "Chen",
            email: "robert.chen@retailcorp.com",
            phone: "+1-555-0126",
            jobTitle: "Director of Finance",
            company: "Retail Corp",
            department: "Finance",
            address: "321 Commerce St",
            city: "Los Angeles",
            state: "CA",
            zipCode: "90210",
            country: "USA",
            source: "Trade Show",
            status: "inactive",
            tags: ["finance", "budget-holder"],
            lastContact: "2023-12-08",
            created_at: "2023-05-12",
            assignedTo: "Mike Wilson",
            notes: "Budget approved for Q2. Need to reconnect.",
          },
          {
            id: 5,
            firstName: "Emily",
            lastName: "Rodriguez",
            email: "emily.rodriguez@datasolutions.com",
            phone: "+1-555-0127",
            jobTitle: "Data Science Lead",
            company: "Data Solutions Ltd",
            department: "Analytics",
            address: "654 Data Drive",
            city: "Austin",
            state: "TX",
            zipCode: "73301",
            country: "USA",
            source: "LinkedIn",
            status: "active",
            tags: ["technical", "analytics"],
            lastContact: "2024-01-22",
            created_at: "2023-11-08",
            assignedTo: "Lisa Thompson",
            notes: "Interested in analytics and reporting capabilities.",
          },
        ];
        setContacts(mockData);
      } catch (err) {
        setError("Failed to load contacts");
        console.error("Error fetching contacts:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchContacts();
  }, []);
  const filteredContacts = contacts.filter((contact) => {
    const matchesSearch =
      contact.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.jobTitle.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      filterStatus === "all" || contact.status === filterStatus;
    return matchesSearch && matchesStatus;
  });
  const handleViewContact = (contact: Contact) => {
    setSelectedContact(contact);
    setDialogMode("view");
    setDialogOpen(true);
  };
  const handleEditContact = (contact: Contact) => {
    setSelectedContact(contact);
    setDialogMode("edit");
    setDialogOpen(true);
  };
  const handleCreateContact = () => {
    setSelectedContact(null);
    setDialogMode("create");
    setDialogOpen(true);
  };
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedContact(null);
    setTabValue(0);
  };
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "lead":
        return "primary";
      case "inactive":
        return "default";
      default:
        return "default";
    }
  };
  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };
  const contactStats = {
    total: contacts.length,
    active: contacts.filter((c) => c.status === "active").length,
    leads: contacts.filter((c) => c.status === "lead").length,
    inactive: contacts.filter((c) => c.status === "inactive").length,
  };
  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }
  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Contact Management
      </Typography>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Contacts
              </Typography>
              <Typography variant="h4">{contactStats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Contacts
              </Typography>
              <Typography variant="h4" color="success.main">
                {contactStats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Leads
              </Typography>
              <Typography variant="h4" color="primary.main">
                {contactStats.leads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Inactive
              </Typography>
              <Typography variant="h4" color="text.secondary">
                {contactStats.inactive}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Filters and Actions */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box sx={{ display: "flex", gap: 2 }}>
          <TextField
            placeholder="Search contacts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300 }}
          />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              label="Status"
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="lead">Lead</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateContact}
        >
          Add Contact
        </Button>
      </Box>
      {/* Contacts Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Contact</TableCell>
              <TableCell>Company & Title</TableCell>
              <TableCell>Contact Info</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Last Contact</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredContacts.map((contact) => (
              <TableRow key={contact.id} hover>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <Avatar sx={{ mr: 2, bgcolor: "primary.main" }}>
                      {getInitials(contact.firstName, contact.lastName)}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2">
                        {contact.firstName} {contact.lastName}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        ID: {contact.id}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{contact.company}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {contact.jobTitle}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {contact.department}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box>
                    <Box
                      sx={{ display: "flex", alignItems: "center", mb: 0.5 }}
                    >
                      <EmailIcon
                        sx={{ fontSize: 16, mr: 1, color: "text.secondary" }}
                      />
                      <Typography variant="body2">{contact.email}</Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <PhoneIcon
                        sx={{ fontSize: 16, mr: 1, color: "text.secondary" }}
                      />
                      <Typography variant="body2">{contact.phone}</Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={contact.status}
                    color={getStatusColor(contact.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                    {contact.tags.slice(0, 2).map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {contact.tags.length > 2 && (
                      <Chip
                        label={`+${contact.tags.length - 2}`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </TableCell>
                <TableCell>{contact.assignedTo}</TableCell>
                <TableCell>
                  {new Date(contact.lastContact).toLocaleDateString()}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      onClick={() => handleViewContact(contact)}
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit Contact">
                    <IconButton
                      size="small"
                      onClick={() => handleEditContact(contact)}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {/* Contact Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === "create"
            ? "Add New Contact"
            : dialogMode === "edit"
              ? "Edit Contact"
              : "Contact Details"}
        </DialogTitle>
        <DialogContent>
          {selectedContact && (
            <Box sx={{ mt: 2 }}>
              <Tabs
                value={tabValue}
                onChange={(e, newValue) => setTabValue(newValue)}
              >
                <Tab label="Personal Information" />
                <Tab label="Contact Details" />
                <Tab label="Notes & Activity" />
              </Tabs>
              {tabValue === 0 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      value={selectedContact.firstName}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      value={selectedContact.lastName}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Job Title"
                      value={selectedContact.jobTitle}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Department"
                      value={selectedContact.department}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Company"
                      value={selectedContact.company}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === "view"}>
                      <InputLabel>Status</InputLabel>
                      <Select value={selectedContact.status} label="Status">
                        <MenuItem value="active">Active</MenuItem>
                        <MenuItem value="lead">Lead</MenuItem>
                        <MenuItem value="inactive">Inactive</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Source"
                      value={selectedContact.source}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                </Grid>
              )}
              {tabValue === 1 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={selectedContact.email}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={selectedContact.phone}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      value={selectedContact.address}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="City"
                      value={selectedContact.city}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="State"
                      value={selectedContact.state}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Zip Code"
                      value={selectedContact.zipCode}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Country"
                      value={selectedContact.country}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                </Grid>
              )}
              {tabValue === 2 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Notes"
                      multiline
                      rows={4}
                      value={selectedContact.notes}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Assigned To"
                      value={selectedContact.assignedTo}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Last Contact Date"
                      type="date"
                      value={selectedContact.lastContact}
                      disabled={dialogMode === "view"}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Activity Timeline
                    </Typography>
                    <Typography color="textSecondary">
                      Activity tracking will be implemented with backend
                      integration.
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === "view" ? "Close" : "Cancel"}
          </Button>
          {dialogMode !== "view" && (
            <Button variant="contained" onClick={handleCloseDialog}>
              {dialogMode === "create" ? "Create" : "Save"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};
export default ContactManagement;
