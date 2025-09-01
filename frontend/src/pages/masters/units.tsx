import React, { useState } from 'react';
import { useRouter } from 'next/router';
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
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Scale,
  SwapHoriz,
  ExpandMore
} from '@mui/icons-material';
const UnitsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    symbol: '',
    description: '',
    unit_type: 'weight', // weight, length, volume, quantity, etc.
    base_unit: false,
    conversion_factor: 1,
    alternate_units: []
  });
  // Mock data for demonstration
  const units = [
    {
      id: 1,
      name: 'Kilogram',
      symbol: 'kg',
      description: 'Standard unit of mass',
      unit_type: 'weight',
      base_unit: true,
      conversion_factor: 1,
      alternate_units: [
        { unit: 'Gram', symbol: 'g', conversion_factor: 1000 },
        { unit: 'Pound', symbol: 'lb', conversion_factor: 2.205 }
      ],
      is_active: true
    },
    {
      id: 2,
      name: 'Meter',
      symbol: 'm',
      description: 'Standard unit of length',
      unit_type: 'length',
      base_unit: true,
      conversion_factor: 1,
      alternate_units: [
        { unit: 'Centimeter', symbol: 'cm', conversion_factor: 100 },
        { unit: 'Millimeter', symbol: 'mm', conversion_factor: 1000 },
        { unit: 'Inch', symbol: 'in', conversion_factor: 39.37 }
      ],
      is_active: true
    },
    {
      id: 3,
      name: 'Liter',
      symbol: 'L',
      description: 'Standard unit of volume',
      unit_type: 'volume',
      base_unit: true,
      conversion_factor: 1,
      alternate_units: [
        { unit: 'Milliliter', symbol: 'ml', conversion_factor: 1000 },
        { unit: 'Gallon', symbol: 'gal', conversion_factor: 0.264 }
      ],
      is_active: true
    },
    {
      id: 4,
      name: 'Piece',
      symbol: 'pcs',
      description: 'Count unit for discrete items',
      unit_type: 'quantity',
      base_unit: true,
      conversion_factor: 1,
      alternate_units: [
        { unit: 'Dozen', symbol: 'doz', conversion_factor: 0.083 },
        { unit: 'Pair', symbol: 'pr', conversion_factor: 0.5 }
      ],
      is_active: true
    }
  ];
  const unitTypes = [
    { value: 'weight', label: 'Weight/Mass' },
    { value: 'length', label: 'Length/Distance' },
    { value: 'volume', label: 'Volume/Capacity' },
    { value: 'quantity', label: 'Quantity/Count' },
    { value: 'area', label: 'Area' },
    { value: 'time', label: 'Time' },
    { value: 'temperature', label: 'Temperature' },
    { value: 'other', label: 'Other' }
  ];
  const resetForm = () => {
    setFormData({
      name: '',
      symbol: '',
      description: '',
      unit_type: 'weight',
      base_unit: false,
      conversion_factor: 1,
      alternate_units: []
    });
  };
  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };
  const handleEditClick = (unit: any) => {
    setSelectedUnit(unit);
    setFormData({
      name: unit.name || '',
      symbol: unit.symbol || '',
      description: unit.description || '',
      unit_type: unit.unit_type || 'weight',
      base_unit: unit.base_unit || false,
      conversion_factor: unit.conversion_factor || 1,
      alternate_units: unit.alternate_units || []
    });
    setEditDialog(true);
  };
  const handleSubmit = () => {
    if (selectedUnit) {
      // TODO: Implement update functionality
      console.log('Update unit:', selectedUnit.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create unit:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };
  const handleDeleteClick = (unit: any) => {
    // TODO: Implement delete functionality
    console.log('Delete unit:', unit.id);
  };
  const addAlternateUnit = () => {
    setFormData(prev => ({
      ...prev,
      alternate_units: [
        ...prev.alternate_units,
        { unit: '', symbol: '', conversion_factor: 1 }
      ]
    }));
  };
  const removeAlternateUnit = (index: number) => {
    setFormData(prev => ({
      ...prev,
      alternate_units: prev.alternate_units.filter((_, i) => i !== index)
    }));
  };
  const updateAlternateUnit = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      alternate_units: prev.alternate_units.map((unit, i) => 
        i === index ? { ...unit, [field]: value } : unit
      )
    }));
  };
  const filteredUnits = units.filter((unit: any) =>
    unit.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    unit.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    unit.unit_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Units of Measurement
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Unit
          </Button>
        </Box>
        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          Define units of measurement for your inventory items. Set up alternate unit relations 
          to automatically convert between different units (e.g., kg to grams, meters to centimeters).
        </Alert>
        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Units
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {units.length}
                    </Typography>
                  </Box>
                  <Scale sx={{ fontSize: 40, color: 'primary.main' }} />
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
                      Base Units
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {units.filter(unit => unit.base_unit).length}
                    </Typography>
                  </Box>
                  <Scale sx={{ fontSize: 40, color: 'success.main' }} />
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
                      Unit Types
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {new Set(units.map(unit => unit.unit_type)).size}
                    </Typography>
                  </Box>
                  <Scale sx={{ fontSize: 40, color: 'warning.main' }} />
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
                      Alternate Units
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {units.reduce((sum, unit) => sum + unit.alternate_units.length, 0)}
                    </Typography>
                  </Box>
                  <SwapHoriz sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search units by name, symbol, or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Unit Name</TableCell>
                <TableCell>Symbol</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Base Unit</TableCell>
                <TableCell>Alternate Units</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUnits.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Box sx={{ py: 3 }}>
                      <Scale sx={{ fontSize: 48, color: 'action.disabled', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary">
                        No units found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first unit of measurement
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredUnits.map((unit: any) => (
                  <TableRow key={unit.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Scale sx={{ mr: 2, color: 'primary.main' }} />
                        <Box>
                          <Typography variant="body1" fontWeight="medium">
                            {unit.name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {unit.description}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={unit.symbol}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={unit.unit_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={unit.base_unit ? 'Base' : 'Derived'}
                        size="small"
                        color={unit.base_unit ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${unit.alternate_units.length} units`}
                        size="small"
                        color="info"
                        icon={<SwapHoriz />}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={unit.is_active ? 'Active' : 'Inactive'}
                        color={unit.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" color="primary" onClick={() => handleEditClick(unit)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDeleteClick(unit)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {/* Add/Edit Unit Dialog */}
        <Dialog 
          open={addDialog || editDialog} 
          onClose={() => { setAddDialog(false); setEditDialog(false); }}
          maxWidth="md" 
          fullWidth
        >
          <DialogTitle>
            {selectedUnit ? 'Edit Unit' : 'Add New Unit'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Unit Name *"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Symbol *"
                  value={formData.symbol}
                  onChange={(e) => setFormData(prev => ({ ...prev, symbol: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Unit Type</InputLabel>
                  <Select
                    value={formData.unit_type}
                    label="Unit Type"
                    onChange={(e) => setFormData(prev => ({ ...prev, unit_type: e.target.value }))}
                  >
                    {unitTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.base_unit}
                      onChange={(e) => setFormData(prev => ({ ...prev, base_unit: e.target.checked }))}
                    />
                  }
                  label="Base Unit"
                />
              </Grid>
              {/* Alternate Units Section */}
              <Grid item xs={12}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">
                      Alternate Unit Relations ({formData.alternate_units.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ mb: 2 }}>
                      <Button
                        variant="outlined"
                        startIcon={<Add />}
                        onClick={addAlternateUnit}
                        size="small"
                      >
                        Add Alternate Unit
                      </Button>
                    </Box>
                    {formData.alternate_units.map((altUnit: any, index: number) => (
                      <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
                        <Grid item xs={4}>
                          <TextField
                            fullWidth
                            label="Unit Name"
                            value={altUnit.unit}
                            onChange={(e) => updateAlternateUnit(index, 'unit', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            label="Symbol"
                            value={altUnit.symbol}
                            onChange={(e) => updateAlternateUnit(index, 'symbol', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            label="Conversion Factor"
                            type="number"
                            value={altUnit.conversion_factor}
                            onChange={(e) => updateAlternateUnit(index, 'conversion_factor', parseFloat(e.target.value))}
                            size="small"
                            helperText={`1 ${formData.symbol} = ${altUnit.conversion_factor} ${altUnit.symbol}`}
                          />
                        </Grid>
                        <Grid item xs={2}>
                          <IconButton
                            color="error"
                            onClick={() => removeAlternateUnit(index)}
                            size="small"
                          >
                            <Delete />
                          </IconButton>
                        </Grid>
                      </Grid>
                    ))}
                    {formData.alternate_units.length === 0 && (
                      <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
                        No alternate units defined. Click "Add Alternate Unit" to create unit conversions.
                      </Typography>
                    )}
                  </AccordionDetails>
                </Accordion>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setAddDialog(false); setEditDialog(false); }}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedUnit ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};
export default UnitsPage;