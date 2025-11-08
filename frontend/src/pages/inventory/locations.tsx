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
} from '@mui/material';
import { ProtectedPage } from '@/components/ProtectedPage';
import {
  Add,
  Edit,
  Delete,
  Search,
  LocationOn,
  Warehouse,
} from '@mui/icons-material';

const LocationsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<any>(null);
  const [formData, setFormData] = useState({
    location_code: '',
    location_name: '',
    location_type: 'warehouse',
    parent_location_id: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    is_active: true,
  });

  // Empty locations array - to be loaded from API
  const locations: any[] = [];

  const locationTypes = [
    { value: 'warehouse', label: 'Warehouse' },
    { value: 'store', label: 'Store' },
    { value: 'showroom', label: 'Showroom' },
    { value: 'factory', label: 'Factory' },
    { value: 'office', label: 'Office' },
  ];

  const resetForm = () => {
    setFormData({
      location_code: '',
      location_name: '',
      location_type: 'warehouse',
      parent_location_id: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      is_active: true,
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (location: any) => {
    setSelectedLocation(location);
    setFormData({
      location_code: location.location_code || '',
      location_name: location.location_name || '',
      location_type: location.location_type || 'warehouse',
      parent_location_id: location.parent_location_id || '',
      address: location.address || '',
      city: location.city || '',
      state: location.state || '',
      pincode: location.pincode || '',
      is_active: location.is_active,
    });
    setEditDialog(true);
  };

  const handleSubmit = () => {
    if (selectedLocation) {
      // TODO: Implement update functionality
      console.log('Update location:', selectedLocation.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create location:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };

  const handleDeleteClick = (location: any) => {
    // TODO: Implement delete functionality
    console.log('Delete location:', location.id);
  };

  const filteredLocations = locations.filter(
    (location) =>
      location.location_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      location.location_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      location.city?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            Warehouse Locations
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Location
          </Button>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Manage your warehouse locations, stores, and facilities. Define location
          hierarchy and track inventory across multiple sites.
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
                      Total Locations
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {locations.length}
                    </Typography>
                  </Box>
                  <LocationOn sx={{ fontSize: 40, color: 'primary.main' }} />
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
                      Active Locations
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {locations.filter((l) => l.is_active).length}
                    </Typography>
                  </Box>
                  <Warehouse sx={{ fontSize: 40, color: 'success.main' }} />
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
                      Warehouses
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {locations.filter((l) => l.location_type === 'warehouse').length}
                    </Typography>
                  </Box>
                  <Warehouse sx={{ fontSize: 40, color: 'info.main' }} />
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
                      Stores
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {locations.filter((l) => l.location_type === 'store').length}
                    </Typography>
                  </Box>
                  <LocationOn sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Search */}
        <TextField
          fullWidth
          label="Search Locations"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 3 }}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />,
          }}
        />

        {/* Locations Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Location Code</TableCell>
                <TableCell>Location Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>City</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLocations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                      No locations found. Click "Add Location" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredLocations.map((location) => (
                  <TableRow key={location.id}>
                    <TableCell>{location.location_code}</TableCell>
                    <TableCell>{location.location_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={location.location_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{location.city}</TableCell>
                    <TableCell>{location.state}</TableCell>
                    <TableCell>
                      <Chip
                        label={location.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={location.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleEditClick(location)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(location)}
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      {/* Add/Edit Dialog */}
      <Dialog
        open={addDialog || editDialog}
        onClose={() => {
          setAddDialog(false);
          setEditDialog(false);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedLocation ? 'Edit Location' : 'Add New Location'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location Code"
                value={formData.location_code}
                onChange={(e) =>
                  setFormData({ ...formData, location_code: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location Name"
                value={formData.location_name}
                onChange={(e) =>
                  setFormData({ ...formData, location_name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Location Type</InputLabel>
                <Select
                  value={formData.location_type}
                  label="Location Type"
                  onChange={(e) =>
                    setFormData({ ...formData, location_type: e.target.value })
                  }
                >
                  {locationTypes.map((type) => (
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
                label="Address"
                value={formData.address}
                onChange={(e) =>
                  setFormData({ ...formData, address: e.target.value })
                }
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="City"
                value={formData.city}
                onChange={(e) =>
                  setFormData({ ...formData, city: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="State"
                value={formData.state}
                onChange={(e) =>
                  setFormData({ ...formData, state: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Pincode"
                value={formData.pincode}
                onChange={(e) =>
                  setFormData({ ...formData, pincode: e.target.value })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setAddDialog(false);
              setEditDialog(false);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedLocation ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
    </ProtectedPage>
  );
};

export default LocationsPage;
