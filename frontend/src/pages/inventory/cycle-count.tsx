import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
import { ProtectedPage } from '@/components/ProtectedPage';
  Add,
  Edit,
  Visibility,
  CheckCircle,
  Schedule,
  Assignment,
  TrendingUp,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`cycle-count-tabpanel-${index}`}
      aria-labelledby={`cycle-count-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CycleCountPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [addDialog, setAddDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedCount, setSelectedCount] = useState<any>(null);
  const [formData, setFormData] = useState({
    count_name: '',
    location_id: '',
    count_type: 'full',
    scheduled_date: '',
    assigned_to: '',
    notes: '',
  });

  // Empty arrays - to be loaded from API
  const cycleCounts: any[] = [];
  const locations: any[] = [];
  const users: any[] = [];

  const countTypes = [
    { value: 'full', label: 'Full Count' },
    { value: 'partial', label: 'Partial Count' },
    { value: 'spot', label: 'Spot Check' },
    { value: 'abc', label: 'ABC Analysis' },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const resetForm = () => {
    setFormData({
      count_name: '',
      location_id: '',
      count_type: 'full',
      scheduled_date: '',
      assigned_to: '',
      notes: '',
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleViewClick = (count: any) => {
    setSelectedCount(count);
    setViewDialog(true);
  };

  const handleSubmit = () => {
    // TODO: Implement create functionality
    console.log('Create cycle count:', formData);
    setAddDialog(false);
  };

  const pendingCounts = cycleCounts.filter((c) => c.status === 'pending');
  const inProgressCounts = cycleCounts.filter((c) => c.status === 'in_progress');
  const completedCounts = cycleCounts.filter((c) => c.status === 'completed');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'in_progress':
        return 'info';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  return (


    <ProtectedPage moduleKey="inventory" action="read">
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography variant="h4" component="h1">
            Cycle Count Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Schedule Count
          </Button>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Schedule and manage cycle counts to maintain inventory accuracy. Regular
          cycle counting helps identify discrepancies and improve stock control.
        </Alert>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Counts
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {cycleCounts.length}
                    </Typography>
                  </Box>
                  <Assignment sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Pending
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {pendingCounts.length}
                    </Typography>
                  </Box>
                  <Schedule sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      In Progress
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {inProgressCounts.length}
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Completed
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {completedCounts.length}
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Pending" />
              <Tab label="In Progress" />
              <Tab label="Completed" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Count Name</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Scheduled Date</TableCell>
                    <TableCell>Assigned To</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingCounts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                          No pending cycle counts.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    pendingCounts.map((count) => (
                      <TableRow key={count.id}>
                        <TableCell>{count.count_name}</TableCell>
                        <TableCell>{count.location_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={count.count_type}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{count.scheduled_date}</TableCell>
                        <TableCell>{count.assigned_user_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={count.status}
                            size="small"
                            color={getStatusColor(count.status)}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            size="small"
                            onClick={() => handleViewClick(count)}
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Count Name</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Started Date</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {inProgressCounts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                          No cycle counts in progress.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    inProgressCounts.map((count) => (
                      <TableRow key={count.id}>
                        <TableCell>{count.count_name}</TableCell>
                        <TableCell>{count.location_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={count.count_type}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{count.started_date}</TableCell>
                        <TableCell>{count.progress}%</TableCell>
                        <TableCell>
                          <Chip
                            label={count.status}
                            size="small"
                            color={getStatusColor(count.status)}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            size="small"
                            onClick={() => handleViewClick(count)}
                          >
                            <Visibility />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Count Name</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Completed Date</TableCell>
                    <TableCell>Variance</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {completedCounts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                          No completed cycle counts.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    completedCounts.map((count) => (
                      <TableRow key={count.id}>
                        <TableCell>{count.count_name}</TableCell>
                        <TableCell>{count.location_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={count.count_type}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{count.completed_date}</TableCell>
                        <TableCell>
                          {count.variance > 0 ? (
                            <Chip
                              label={`+${count.variance}`}
                              size="small"
                              color="success"
                            />
                          ) : count.variance < 0 ? (
                            <Chip
                              label={count.variance}
                              size="small"
                              color="error"
                            />
                          ) : (
                            <Chip label="0" size="small" color="default" />
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={count.status}
                            size="small"
                            color={getStatusColor(count.status)}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            size="small"
                            onClick={() => handleViewClick(count)}
                          >
                            <Visibility />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </Paper>
      </Box>

      {/* Add Dialog */}
      <Dialog
        open={addDialog}
        onClose={() => setAddDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Schedule Cycle Count</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Count Name"
                value={formData.count_name}
                onChange={(e) =>
                  setFormData({ ...formData, count_name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Location</InputLabel>
                <Select
                  value={formData.location_id}
                  label="Location"
                  onChange={(e) =>
                    setFormData({ ...formData, location_id: e.target.value })
                  }
                >
                  {locations.length === 0 ? (
                    <MenuItem value="" disabled>
                      No locations available
                    </MenuItem>
                  ) : (
                    locations.map((location) => (
                      <MenuItem key={location.id} value={location.id}>
                        {location.location_name}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Count Type</InputLabel>
                <Select
                  value={formData.count_type}
                  label="Count Type"
                  onChange={(e) =>
                    setFormData({ ...formData, count_type: e.target.value })
                  }
                >
                  {countTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scheduled Date"
                type="date"
                value={formData.scheduled_date}
                onChange={(e) =>
                  setFormData({ ...formData, scheduled_date: e.target.value })
                }
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Assign To</InputLabel>
                <Select
                  value={formData.assigned_to}
                  label="Assign To"
                  onChange={(e) =>
                    setFormData({ ...formData, assigned_to: e.target.value })
                  }
                >
                  {users.length === 0 ? (
                    <MenuItem value="" disabled>
                      No users available
                    </MenuItem>
                  ) : (
                    users.map((user) => (
                      <MenuItem key={user.id} value={user.id}>
                        {user.name}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                multiline
                rows={3}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Schedule
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Dialog */}
      <Dialog
        open={viewDialog}
        onClose={() => setViewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Cycle Count Details</DialogTitle>
        <DialogContent>
          {selectedCount && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Count Name: {selectedCount.count_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Location: {selectedCount.location_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Type: {selectedCount.count_type}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Status: {selectedCount.status}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>


    </ProtectedPage>


  
  );
};

export default CycleCountPage;
