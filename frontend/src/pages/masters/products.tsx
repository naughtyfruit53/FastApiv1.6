// Standalone Products Page - Extract from masters/index.tsx
import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  InputLabel,
  FormControl
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Inventory,
  Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { masterDataService } from '../../services/authService';
import ExcelImportExport from '../../components/ExcelImportExport';
import { bulkImportProducts } from '../../services/masterService';
import Grid from '@mui/material/Grid';
import { useAuth } from '../../context/AuthContext';

const ProductsPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isOrgContextReady } = useAuth();
  const [itemDialog, setItemDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [formData, setFormData] = useState({
    product_name: '',
    hsn_code: '',
    part_number: '',
    unit: '',
    unit_price: '',
    gst_rate: '',
    is_gst_inclusive: false,
    reorder_level: '',
    description: '',
    is_manufactured: false,
    is_active: true
  });
  const queryClient = useQueryClient();

  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => masterDataService.getProducts(),
    enabled: isOrgContextReady,
  });

  const createItemMutation = useMutation({
    mutationFn: (data: any) => masterDataService.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setItemDialog(false);
      setSelectedItem(null);
      setFormData({
        product_name: '',
        hsn_code: '',
        part_number: '',
        unit: '',
        unit_price: '',
        gst_rate: '',
        is_gst_inclusive: false,
        reorder_level: '',
        description: '',
        is_manufactured: false,
        is_active: true
      });
    },
    onError: (error: any) => {
      console.error('Error creating product:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to create product');
    }
  });

  const updateItemMutation = useMutation({
    mutationFn: (data: any) => masterDataService.updateProduct(data.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setItemDialog(false);
      setSelectedItem(null);
      setFormData({
        product_name: '',
        hsn_code: '',
        part_number: '',
        unit: '',
        unit_price: '',
        gst_rate: '',
        is_gst_inclusive: false,
        reorder_level: '',
        description: '',
        is_manufactured: false,
        is_active: true
      });
    },
    onError: (error: any) => {
      console.error('Error updating product:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to update product');
    }
  });

  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error: any) => {
      console.error('Error deleting product:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to delete product');
    }
  });

  const openItemDialog = useCallback((item: any = null) => {
    setSelectedItem(item);
    if (item) {
      setFormData({ ...item, product_name: item.product_name || item.name || '' });
    } else {
      setFormData({
        product_name: '',
        hsn_code: '',
        part_number: '',
        unit: '',
        unit_price: '',
        gst_rate: '',
        is_gst_inclusive: false,
        reorder_level: '',
        description: '',
        is_manufactured: false,
        is_active: true
      });
    }
    setErrorMessage('');
    setItemDialog(true);
  }, []);

  const handleSubmit = () => {
    const data = { 
      ...formData, 
      name: formData.product_name // Map back to 'name' for backend compatibility
    };
    
    // Convert string numbers to actual numbers
    if (data.unit_price) (data as any).unit_price = parseFloat(data.unit_price as string);
    if (data.gst_rate) (data as any).gst_rate = parseFloat(data.gst_rate as string);
    if (data.reorder_level) (data as any).reorder_level = parseInt(data.reorder_level as string);
    
    if (selectedItem) {
      updateItemMutation.mutate({ ...selectedItem, ...data });
    } else {
      createItemMutation.mutate(data);
    }
  };

  // Auto-open add dialog if action=add in URL
  React.useEffect(() => {
    if (action === 'add') {
      openItemDialog(null);
    }
  }, [action, openItemDialog]);

  if (!isOrgContextReady) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Product Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => openItemDialog()}
            sx={{ ml: 2 }}
          >
            Add Product
          </Button>
        </Box>

        {/* Products Table */}
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">All Products</Typography>
            <ExcelImportExport
              data={products || []}
              entity="Products"
              onImport={bulkImportProducts}
            />
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>HSN Code</TableCell>
                  <TableCell>Part Number</TableCell>
                  <TableCell>Unit</TableCell>
                  <TableCell>Unit Price</TableCell>
                  <TableCell>GST Rate</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {products?.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {item.product_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {item.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{item.hsn_code || 'N/A'}</TableCell>
                    <TableCell>{item.part_number || 'N/A'}</TableCell>
                    <TableCell>{item.unit}</TableCell>
                    <TableCell>₹{item.unit_price}</TableCell>
                    <TableCell>{item.gst_rate}%</TableCell>
                    <TableCell>
                      <Chip
                        label={item.is_manufactured ? 'Manufactured' : 'Purchased'}
                        color={item.is_manufactured ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={item.is_active ? 'Active' : 'Inactive'}
                        color={item.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => openItemDialog(item)} size="small">
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => deleteItemMutation.mutate(item.id)} size="small" color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Add/Edit Dialog */}
        <Dialog open={itemDialog} onClose={() => setItemDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>{selectedItem ? 'Edit Product' : 'Add New Product'}</DialogTitle>
          <DialogContent>
            {errorMessage && <Alert severity="error" sx={{ mb: 2 }}>{errorMessage}</Alert>}
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Product Name"
                  value={formData.product_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, product_name: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="HSN Code"
                  value={formData.hsn_code}
                  onChange={(e) => setFormData(prev => ({ ...prev, hsn_code: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Part Number"
                  value={formData.part_number}
                  onChange={(e) => setFormData(prev => ({ ...prev, part_number: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit"
                  value={formData.unit}
                  onChange={(e) => setFormData(prev => ({ ...prev, unit: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit Price"
                  type="number"
                  value={formData.unit_price}
                  onChange={(e) => setFormData(prev => ({ ...prev, unit_price: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="GST Rate (%)"
                  type="number"
                  value={formData.gst_rate}
                  onChange={(e) => setFormData(prev => ({ ...prev, gst_rate: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Reorder Level"
                  type="number"
                  value={formData.reorder_level}
                  onChange={(e) => setFormData(prev => ({ ...prev, reorder_level: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_gst_inclusive}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_gst_inclusive: e.target.checked }))}
                    />
                  }
                  label="GST Inclusive Pricing"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_manufactured}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_manufactured: e.target.checked }))}
                    />
                  }
                  label="Manufactured Product"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_active}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    />
                  }
                  label="Active"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setItemDialog(false)}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">Save</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default ProductsPage;