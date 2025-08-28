// pages/transport.tsx
// Transport and Freight Management page

import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
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
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocalShipping as LocalShippingIcon,
  Route as RouteIcon,
  AttachMoney as AttachMoneyIcon,
  TrackChanges as TrackChangesIcon,
  Assessment as AssessmentIcon,
  CompareArrows as CompareArrowsIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transportService } from '../services/transportService';

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
      id={`transport-tabpanel-${index}`}
      aria-labelledby={`transport-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const TransportManagementPage: NextPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState<'carrier' | 'route' | 'rate' | 'shipment' | null>(null);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [rateComparisonData, setRateComparisonData] = useState({
    origin_city: '',
    destination_city: '',
    weight_kg: 0,
    volume_cbm: 0,
  });

  // Fetch dashboard summary
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['transportDashboard'],
    queryFn: transportService.getDashboardSummary,
    enabled: !!user,
  });

  // Fetch carriers
  const { data: carriers, isLoading: carriersLoading } = useQuery({
    queryKey: ['carriers'],
    queryFn: () => transportService.getCarriers(),
    enabled: !!user,
  });

  // Fetch routes
  const { data: routes, isLoading: routesLoading } = useQuery({
    queryKey: ['routes'],
    queryFn: () => transportService.getRoutes(),
    enabled: !!user,
  });

  // Fetch freight rates
  const { data: freightRates, isLoading: ratesLoading } = useQuery({
    queryKey: ['freightRates'],
    queryFn: () => transportService.getFreightRates(),
    enabled: !!user,
  });

  // Fetch shipments
  const { data: shipments, isLoading: shipmentsLoading } = useQuery({
    queryKey: ['shipments'],
    queryFn: () => transportService.getShipments(),
    enabled: !!user,
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'success';
      case 'booked': return 'info';
      case 'in_transit': return 'warning';
      case 'delivered': return 'success';
      case 'cancelled': return 'error';
      case 'delayed': return 'error';
      default: return 'default';
    }
  };

  const getCarrierTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'road': return '🚛';
      case 'rail': return '🚂';
      case 'air': return '✈️';
      case 'sea': return '🚢';
      case 'courier': return '📦';
      default: return '🚚';
    }
  };

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Please log in to access Transport Management.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LocalShippingIcon color="primary" />
          Transport & Freight Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage carriers, routes, freight rates, shipments, and logistics operations
        </Typography>
      </Box>

      {/* Dashboard Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Carriers
                  </Typography>
                  <Typography variant="h4">
                    {dashboardLoading ? <CircularProgress size={24} /> : dashboardData?.total_carriers || 0}
                  </Typography>
                </Box>
                <LocalShippingIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Shipments
                  </Typography>
                  <Typography variant="h4">
                    {dashboardLoading ? <CircularProgress size={24} /> : dashboardData?.active_shipments || 0}
                  </Typography>
                </Box>
                <TrackChangesIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Delivered This Month
                  </Typography>
                  <Typography variant="h4">
                    {dashboardLoading ? <CircularProgress size={24} /> : dashboardData?.delivered_this_month || 0}
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Freight Cost MTD
                  </Typography>
                  <Typography variant="h6">
                    {dashboardLoading ? <CircularProgress size={24} /> : 
                     `$${(dashboardData?.total_freight_cost_this_month || 0).toLocaleString()}`}
                  </Typography>
                </Box>
                <AttachMoneyIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Carriers" />
          <Tab label="Routes" />
          <Tab label="Freight Rates" />
          <Tab label="Shipments" />
          <Tab label="Rate Comparison" />
          <Tab label="Analytics" />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {/* Carriers */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Carrier Management</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog('carrier')}
          >
            Add Carrier
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Carrier Code</TableCell>
                <TableCell>Carrier Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Contact</TableCell>
                <TableCell>Rating</TableCell>
                <TableCell>On-Time %</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Preferred</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {carriersLoading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                carriers?.map((carrier: any) => (
                  <TableRow key={carrier.id}>
                    <TableCell>{carrier.carrier_code}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <span>{getCarrierTypeIcon(carrier.carrier_type)}</span>
                        {carrier.carrier_name}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={carrier.carrier_type}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{carrier.phone || carrier.email || '-'}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        ⭐ {carrier.rating.toFixed(1)}
                      </Box>
                    </TableCell>
                    <TableCell>{carrier.on_time_percentage.toFixed(1)}%</TableCell>
                    <TableCell>
                      <Chip
                        label={carrier.is_active ? 'Active' : 'Inactive'}
                        color={carrier.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {carrier.is_preferred && (
                        <Chip label="Preferred" color="primary" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedItem(carrier);
                            setOpenDialog('carrier');
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {/* Routes */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Route Management</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog('route')}
          >
            Add Route
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Route Code</TableCell>
                <TableCell>Route Name</TableCell>
                <TableCell>Carrier</TableCell>
                <TableCell>Origin</TableCell>
                <TableCell>Destination</TableCell>
                <TableCell>Distance</TableCell>
                <TableCell>Transit Time</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {routesLoading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                routes?.map((route: any) => (
                  <TableRow key={route.id}>
                    <TableCell>{route.route_code}</TableCell>
                    <TableCell>{route.route_name}</TableCell>
                    <TableCell>{route.carrier_id}</TableCell>
                    <TableCell>{route.origin_city}</TableCell>
                    <TableCell>{route.destination_city}</TableCell>
                    <TableCell>
                      {route.distance_km ? `${route.distance_km} km` : '-'}
                    </TableCell>
                    <TableCell>
                      {route.estimated_transit_time_hours ? 
                        `${route.estimated_transit_time_hours}h` : '-'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={route.status}
                        color={getStatusColor(route.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedItem(route);
                            setOpenDialog('route');
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {/* Freight Rates */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Freight Rate Management</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog('rate')}
          >
            Add Rate
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rate Code</TableCell>
                <TableCell>Carrier</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Rate Basis</TableCell>
                <TableCell>Minimum Charge</TableCell>
                <TableCell>Effective Date</TableCell>
                <TableCell>Expiry Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ratesLoading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                freightRates?.map((rate: any) => (
                  <TableRow key={rate.id}>
                    <TableCell>{rate.rate_code}</TableCell>
                    <TableCell>{rate.carrier_id}</TableCell>
                    <TableCell>
                      <Chip
                        label={rate.freight_mode}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{rate.rate_basis}</TableCell>
                    <TableCell>${rate.minimum_charge}</TableCell>
                    <TableCell>
                      {new Date(rate.effective_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {rate.expiry_date ? 
                        new Date(rate.expiry_date).toLocaleDateString() : 'No Expiry'}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={rate.is_active ? 'Active' : 'Inactive'}
                        color={rate.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedItem(rate);
                            setOpenDialog('rate');
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        {/* Shipments */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Shipment Tracking</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog('shipment')}
          >
            Create Shipment
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Shipment #</TableCell>
                <TableCell>Carrier</TableCell>
                <TableCell>Origin</TableCell>
                <TableCell>Destination</TableCell>
                <TableCell>Weight</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Pickup Date</TableCell>
                <TableCell>Expected Delivery</TableCell>
                <TableCell>Total Charges</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {shipmentsLoading ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                shipments?.map((shipment: any) => (
                  <TableRow key={shipment.id}>
                    <TableCell>{shipment.shipment_number}</TableCell>
                    <TableCell>{shipment.carrier_id}</TableCell>
                    <TableCell>{shipment.origin_city}</TableCell>
                    <TableCell>{shipment.destination_city}</TableCell>
                    <TableCell>{shipment.total_weight_kg} kg</TableCell>
                    <TableCell>
                      <Chip
                        label={shipment.status}
                        color={getStatusColor(shipment.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {shipment.pickup_date ? 
                        new Date(shipment.pickup_date).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      {shipment.expected_delivery_date ? 
                        new Date(shipment.expected_delivery_date).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>${shipment.total_charges}</TableCell>
                    <TableCell>
                      <Tooltip title="Track">
                        <IconButton size="small">
                          <TrackChangesIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        {/* Rate Comparison */}
        <Typography variant="h6" sx={{ mb: 3 }}>Freight Rate Comparison</Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="Origin City"
                value={rateComparisonData.origin_city}
                onChange={(e) => setRateComparisonData(prev => ({
                  ...prev,
                  origin_city: e.target.value
                }))}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="Destination City"
                value={rateComparisonData.destination_city}
                onChange={(e) => setRateComparisonData(prev => ({
                  ...prev,
                  destination_city: e.target.value
                }))}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 2 }}>
              <TextField
                fullWidth
                label="Weight (kg)"
                type="number"
                value={rateComparisonData.weight_kg}
                onChange={(e) => setRateComparisonData(prev => ({
                  ...prev,
                  weight_kg: parseFloat(e.target.value) || 0
                }))}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 2 }}>
              <TextField
                fullWidth
                label="Volume (cbm)"
                type="number"
                value={rateComparisonData.volume_cbm}
                onChange={(e) => setRateComparisonData(prev => ({
                  ...prev,
                  volume_cbm: parseFloat(e.target.value) || 0
                }))}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 2 }}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<CompareArrowsIcon />}
              >
                Compare Rates
              </Button>
            </Grid>
          </Grid>
        </Paper>

        <Typography variant="body2" color="text.secondary">
          Enter shipment details above to compare freight rates across carriers and routes.
        </Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        {/* Analytics */}
        <Typography variant="h6" sx={{ mb: 3 }}>Transport Analytics</Typography>
        
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Carrier Performance Report
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Compare carrier performance metrics
                </Typography>
                <Button variant="outlined">Generate Report</Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Freight Cost Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Analyze freight costs and optimization opportunities
                </Typography>
                <Button variant="outlined">Generate Report</Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Container>
  );
};

export default TransportManagementPage;