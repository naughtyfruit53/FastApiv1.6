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
  FormControlLabel
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Receipt,
  Percent
} from '@mui/icons-material';

const TaxCodesPage: React.FC = () => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedTaxCode, setSelectedTaxCode] = useState<any>(null);
  const [formData, setFormData] = useState({
    tax_code: '',
    tax_name: '',
    tax_rate: 0,
    tax_type: 'GST',
    description: '',
    is_default: false,
    is_active: true
  });

  // Mock data for demonstration
  const taxCodes = [
    {
      id: 1,
      tax_code: 'GST_0',
      tax_name: 'GST 0%',
      tax_rate: 0,
      tax_type: 'GST',
      description: 'Nil GST rate for exempt items',
      is_default: false,
      is_active: true,
      usage_count: 5
    },
    {
      id: 2,
      tax_code: 'GST_5',
      tax_name: 'GST 5%',
      tax_rate: 5,
      tax_type: 'GST',
      description: 'GST at 5% for essential items',
      is_default: false,
      is_active: true,
      usage_count: 12
    },
    {
      id: 3,
      tax_code: 'GST_12',
      tax_name: 'GST 12%',
      tax_rate: 12,
      tax_type: 'GST',
      description: 'GST at 12% for standard items',
      is_default: false,
      is_active: true,
      usage_count: 25
    },
    {
      id: 4,
      tax_code: 'GST_18',
      tax_name: 'GST 18%',
      tax_rate: 18,
      tax_type: 'GST',
      description: 'GST at 18% for most items',
      is_default: true,
      is_active: true,
      usage_count: 45
    },
    {
      id: 5,
      tax_code: 'GST_28',
      tax_name: 'GST 28%',
      tax_rate: 28,
      tax_type: 'GST',
      description: 'GST at 28% for luxury items',
      is_default: false,
      is_active: true,
      usage_count: 8
    },
    {
      id: 6,
      tax_code: 'IGST_18',
      tax_name: 'IGST 18%',
      tax_rate: 18,
      tax_type: 'IGST',
      description: 'Integrated GST at 18% for interstate sales',
      is_default: false,
      is_active: true,
      usage_count: 15
    }
  ];

  const taxTypes = [
    { value: 'GST', label: 'GST (Goods and Services Tax)' },
    { value: 'IGST', label: 'IGST (Integrated GST)' },
    { value: 'CGST', label: 'CGST (Central GST)' },
    { value: 'SGST', label: 'SGST (State GST)' },
    { value: 'CESS', label: 'CESS' },
    { value: 'VAT', label: 'VAT (Value Added Tax)' },
    { value: 'OTHER', label: 'Other Tax' }
  ];

  const resetForm = () => {
    setFormData({
      tax_code: '',
      tax_name: '',
      tax_rate: 0,
      tax_type: 'GST',
      description: '',
      is_default: false,
      is_active: true
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (taxCode: any) => {
    setSelectedTaxCode(taxCode);
    setFormData({
      tax_code: taxCode.tax_code || '',
      tax_name: taxCode.tax_name || '',
      tax_rate: taxCode.tax_rate || 0,
      tax_type: taxCode.tax_type || 'GST',
      description: taxCode.description || '',
      is_default: taxCode.is_default || false,
      is_active: taxCode.is_active
    });
    setEditDialog(true);
  };

  const handleSubmit = () => {
    if (selectedTaxCode) {
      // TODO: Implement update functionality
      console.log('Update tax code:', selectedTaxCode.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create tax code:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };

  const handleDeleteClick = (taxCode: any) => {
    // TODO: Implement delete functionality
    console.log('Delete tax code:', taxCode.id);
  };

  const filteredTaxCodes = taxCodes.filter((taxCode: any) =>
    taxCode.tax_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    taxCode.tax_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    taxCode.tax_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTotalUsage = () => {
    return taxCodes.reduce((sum, taxCode) => sum + taxCode.usage_count, 0);
  };

  const getAverageRate = () => {
    const activeTaxCodes = taxCodes.filter(tc => tc.is_active && tc.tax_rate > 0);
    if (activeTaxCodes.length === 0) return 0;
    const total = activeTaxCodes.reduce((sum, tc) => sum + tc.tax_rate, 0);
    return (total / activeTaxCodes.length).toFixed(1);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Tax Codes
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Tax Code
          </Button>
        </Box>

        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          Configure tax codes for different tax rates and types. These will be used automatically 
          in invoices, purchase orders, and financial calculations.
        </Alert>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Tax Codes
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {taxCodes.length}
                    </Typography>
                  </Box>
                  <Receipt sx={{ fontSize: 40, color: 'primary.main' }} />
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
                      Active Tax Codes
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {taxCodes.filter(tc => tc.is_active).length}
                    </Typography>
                  </Box>
                  <Receipt sx={{ fontSize: 40, color: 'success.main' }} />
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
                      Average Rate
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {getAverageRate()}%
                    </Typography>
                  </Box>
                  <Percent sx={{ fontSize: 40, color: 'warning.main' }} />
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
                      Total Usage
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {getTotalUsage()}
                    </Typography>
                  </Box>
                  <Receipt sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search tax codes by name, code, or type..."
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
                <TableCell>Tax Code</TableCell>
                <TableCell>Tax Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Rate (%)</TableCell>
                <TableCell>Usage</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredTaxCodes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Box sx={{ py: 3 }}>
                      <Receipt sx={{ fontSize: 48, color: 'action.disabled', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary">
                        No tax codes found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first tax code to configure tax calculations
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTaxCodes.map((taxCode: any) => (
                  <TableRow key={taxCode.id}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {taxCode.tax_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Receipt sx={{ mr: 2, color: 'primary.main' }} />
                        <Box>
                          <Typography variant="body1">
                            {taxCode.tax_name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {taxCode.description}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={taxCode.tax_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="h6" color="secondary">
                        {taxCode.tax_rate}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${taxCode.usage_count} times`}
                        size="small"
                        color="info"
                      />
                    </TableCell>
                    <TableCell>
                      {taxCode.is_default && (
                        <Chip
                          label="Default"
                          size="small"
                          color="warning"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={taxCode.is_active ? 'Active' : 'Inactive'}
                        color={taxCode.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" color="primary" onClick={() => handleEditClick(taxCode)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDeleteClick(taxCode)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Add/Edit Tax Code Dialog */}
        <Dialog 
          open={addDialog || editDialog} 
          onClose={() => { setAddDialog(false); setEditDialog(false); }}
          maxWidth="sm" 
          fullWidth
        >
          <DialogTitle>
            {selectedTaxCode ? 'Edit Tax Code' : 'Add New Tax Code'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Tax Code *"
                  value={formData.tax_code}
                  onChange={(e) => setFormData(prev => ({ ...prev, tax_code: e.target.value }))}
                  placeholder="e.g., GST_18"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Tax Rate (%) *"
                  type="number"
                  value={formData.tax_rate}
                  onChange={(e) => setFormData(prev => ({ ...prev, tax_rate: parseFloat(e.target.value) || 0 }))}
                  InputProps={{ inputProps: { min: 0, max: 100, step: 0.01 } }}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Tax Name *"
                  value={formData.tax_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, tax_name: e.target.value }))}
                  placeholder="e.g., GST 18%"
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FormControl fullWidth>
                  <InputLabel>Tax Type</InputLabel>
                  <Select
                    value={formData.tax_type}
                    label="Tax Type"
                    onChange={(e) => setFormData(prev => ({ ...prev, tax_type: e.target.value }))}
                  >
                    {taxTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_default}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_default: e.target.checked }))}
                    />
                  }
                  label="Set as Default Tax Code"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setAddDialog(false); setEditDialog(false); }}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedTaxCode ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default TaxCodesPage;