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
import {
  Add,
  Edit,
  Delete,
  Search,
  Storage,
  Inventory,
} from '@mui/icons-material';

const BinManagementPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedBin, setSelectedBin] = useState<any>(null);
  const [formData, setFormData] = useState({
    bin_code: '',
    bin_name: '',
    location_id: '',
    aisle: '',
    rack: '',
    shelf: '',
    bin_type: 'storage',
    capacity: '',
    is_active: true,
  });

  // Empty bins array - to be loaded from API
  const bins: any[] = [];
  const locations: any[] = []; // To be loaded from API

  const binTypes = [
    { value: 'storage', label: 'Storage' },
    { value: 'picking', label: 'Picking' },
    { value: 'staging', label: 'Staging' },
    { value: 'receiving', label: 'Receiving' },
    { value: 'shipping', label: 'Shipping' },
    { value: 'quarantine', label: 'Quarantine' },
  ];

  const resetForm = () => {
    setFormData({
      bin_code: '',
      bin_name: '',
      location_id: '',
      aisle: '',
      rack: '',
      shelf: '',
      bin_type: 'storage',
      capacity: '',
      is_active: true,
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (bin: any) => {
    setSelectedBin(bin);
    setFormData({
      bin_code: bin.bin_code || '',
      bin_name: bin.bin_name || '',
      location_id: bin.location_id || '',
      aisle: bin.aisle || '',
      rack: bin.rack || '',
      shelf: bin.shelf || '',
      bin_type: bin.bin_type || 'storage',
      capacity: bin.capacity || '',
      is_active: bin.is_active,
    });
    setEditDialog(true);
  };

  const handleSubmit = () => {
    if (selectedBin) {
      // TODO: Implement update functionality
      console.log('Update bin:', selectedBin.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create bin:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };

  const handleDeleteClick = (bin: any) => {
    // TODO: Implement delete functionality
    console.log('Delete bin:', bin.id);
  };

  const filteredBins = bins.filter(
    (bin) =>
      bin.bin_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bin.bin_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bin.aisle?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
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
            Bin Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Bin
          </Button>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Organize your warehouse with bin locations. Define aisles, racks, and
          shelves for efficient inventory storage and picking operations.
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
                      Total Bins
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {bins.length}
                    </Typography>
                  </Box>
                  <Storage sx={{ fontSize: 40, color: 'primary.main' }} />
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
                      Active Bins
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {bins.filter((b) => b.is_active).length}
                    </Typography>
                  </Box>
                  <Inventory sx={{ fontSize: 40, color: 'success.main' }} />
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
                      Storage Bins
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {bins.filter((b) => b.bin_type === 'storage').length}
                    </Typography>
                  </Box>
                  <Storage sx={{ fontSize: 40, color: 'info.main' }} />
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
                      Picking Bins
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {bins.filter((b) => b.bin_type === 'picking').length}
                    </Typography>
                  </Box>
                  <Inventory sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Search */}
        <TextField
          fullWidth
          label="Search Bins"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 3 }}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />,
          }}
        />

        {/* Bins Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Bin Code</TableCell>
                <TableCell>Bin Name</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Aisle</TableCell>
                <TableCell>Rack</TableCell>
                <TableCell>Shelf</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredBins.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                      No bins found. Click "Add Bin" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredBins.map((bin) => (
                  <TableRow key={bin.id}>
                    <TableCell>{bin.bin_code}</TableCell>
                    <TableCell>{bin.bin_name}</TableCell>
                    <TableCell>{bin.location_name}</TableCell>
                    <TableCell>{bin.aisle}</TableCell>
                    <TableCell>{bin.rack}</TableCell>
                    <TableCell>{bin.shelf}</TableCell>
                    <TableCell>
                      <Chip
                        label={bin.bin_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={bin.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={bin.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleEditClick(bin)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(bin)}
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
          {selectedBin ? 'Edit Bin' : 'Add New Bin'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Bin Code"
                value={formData.bin_code}
                onChange={(e) =>
                  setFormData({ ...formData, bin_code: e.target.value })
                }
                required
                helperText="e.g., A-01-01-01"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Bin Name"
                value={formData.bin_name}
                onChange={(e) =>
                  setFormData({ ...formData, bin_name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
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
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Bin Type</InputLabel>
                <Select
                  value={formData.bin_type}
                  label="Bin Type"
                  onChange={(e) =>
                    setFormData({ ...formData, bin_type: e.target.value })
                  }
                >
                  {binTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Aisle"
                value={formData.aisle}
                onChange={(e) =>
                  setFormData({ ...formData, aisle: e.target.value })
                }
                helperText="e.g., A, B, C"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Rack"
                value={formData.rack}
                onChange={(e) =>
                  setFormData({ ...formData, rack: e.target.value })
                }
                helperText="e.g., 01, 02, 03"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Shelf"
                value={formData.shelf}
                onChange={(e) =>
                  setFormData({ ...formData, shelf: e.target.value })
                }
                helperText="e.g., 01, 02, 03"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Capacity"
                value={formData.capacity}
                onChange={(e) =>
                  setFormData({ ...formData, capacity: e.target.value })
                }
                helperText="Maximum capacity (optional)"
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
            {selectedBin ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BinManagementPage;
