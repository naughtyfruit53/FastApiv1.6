'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  Alert,
  Divider,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  LocalShipping as DispatchIcon
} from '@mui/icons-material';
import { dispatchService, DispatchOrderInDB, DispatchOrderCreate, DispatchOrderUpdate, DispatchItemCreate } from '../../services/dispatchService';
import { DISPATCH_ORDER_STATUSES } from '../../types/dispatch.types';

interface DispatchOrderDialogProps {
  open: boolean;
  onClose: () => void;
  dispatchOrder?: DispatchOrderInDB | null;
  editMode: boolean;
  onSave: () => void;
}

const DispatchOrderDialog: React.FC<DispatchOrderDialogProps> = ({
  open,
  onClose,
  dispatchOrder,
  editMode,
  onSave
}) => {
  const [formData, setFormData] = useState({
    customer_id: '',
    ticket_id: '',
    status: 'pending' as keyof typeof DISPATCH_ORDER_STATUSES,
    delivery_address: '',
    delivery_contact_person: '',
    delivery_contact_number: '',
    expected_delivery_date: '',
    notes: '',
    tracking_number: '',
    courier_name: ''
  });

  const [items, setItems] = useState<DispatchItemCreate[]>([{
    product_id: 0,
    quantity: 1,
    unit: 'PCS',
    description: '',
    status: 'pending'
  }]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (dispatchOrder && editMode) {
      setFormData({
        customer_id: dispatchOrder.customer_id.toString(),
        ticket_id: dispatchOrder.ticket_id?.toString() || '',
        status: dispatchOrder.status,
        delivery_address: dispatchOrder.delivery_address,
        delivery_contact_person: dispatchOrder.delivery_contact_person || '',
        delivery_contact_number: dispatchOrder.delivery_contact_number || '',
        expected_delivery_date: dispatchOrder.expected_delivery_date || '',
        notes: dispatchOrder.notes || '',
        tracking_number: dispatchOrder.tracking_number || '',
        courier_name: dispatchOrder.courier_name || ''
      });
      setItems(dispatchOrder.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit: item.unit,
        description: item.description || '',
        status: item.status
      })));
    }
  }, [dispatchOrder, editMode]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addItem = () => {
    setItems(prev => [...prev, {
      product_id: 0,
      quantity: 1,
      unit: 'PCS',
      description: '',
      status: 'pending'
    }]);
  };

  const removeItem = (index: number) => {
    setItems(prev => prev.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    setItems(prev => prev.map((item, i) => 
      i === index ? { ...item, [field]: value } : item
    ));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!formData.customer_id || !formData.delivery_address) {
        setError('Customer and delivery address are required');
        return;
      }

      if (items.length === 0 || items.some(item => !item.product_id)) {
        setError('At least one valid item is required');
        return;
      }

      if (editMode && dispatchOrder) {
        const updateData: DispatchOrderUpdate = {
          customer_id: parseInt(formData.customer_id),
          ticket_id: formData.ticket_id ? parseInt(formData.ticket_id) : null,
          status: formData.status,
          delivery_address: formData.delivery_address,
          delivery_contact_person: formData.delivery_contact_person || null,
          delivery_contact_number: formData.delivery_contact_number || null,
          expected_delivery_date: formData.expected_delivery_date || null,
          notes: formData.notes || null,
          tracking_number: formData.tracking_number || null,
          courier_name: formData.courier_name || null
        };

        await dispatchService.updateDispatchOrder(dispatchOrder.id, updateData);
      } else {
        const createData: DispatchOrderCreate = {
          customer_id: parseInt(formData.customer_id),
          ticket_id: formData.ticket_id ? parseInt(formData.ticket_id) : null,
          status: formData.status,
          delivery_address: formData.delivery_address,
          delivery_contact_person: formData.delivery_contact_person || null,
          delivery_contact_number: formData.delivery_contact_number || null,
          expected_delivery_date: formData.expected_delivery_date || null,
          notes: formData.notes || null,
          tracking_number: formData.tracking_number || null,
          courier_name: formData.courier_name || null,
          items: items.filter(item => item.product_id > 0)
        };

        await dispatchService.createDispatchOrder(createData);
      }

      onSave();
      onClose();
    } catch (err: any) {
      console.error('Error saving dispatch order:', err);
      setError(err.message || 'Failed to save dispatch order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <DispatchIcon color="primary" />
          <Typography variant="h6">
            {editMode ? 'Edit Dispatch Order' : 'Create Dispatch Order'}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Customer ID"
              value={formData.customer_id}
              onChange={(e) => handleInputChange('customer_id', e.target.value)}
              type="number"
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Ticket ID"
              value={formData.ticket_id}
              onChange={(e) => handleInputChange('ticket_id', e.target.value)}
              type="number"
              helperText="Optional: Link to support ticket"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                label="Status"
              >
                {Object.entries(DISPATCH_ORDER_STATUSES).map(([key, value]) => (
                  <MenuItem key={key} value={value}>
                    {value.charAt(0).toUpperCase() + value.slice(1).replace('_', ' ')}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Expected Delivery Date"
              type="datetime-local"
              value={formData.expected_delivery_date}
              onChange={(e) => handleInputChange('expected_delivery_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Delivery Address"
              value={formData.delivery_address}
              onChange={(e) => handleInputChange('delivery_address', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Contact Person"
              value={formData.delivery_contact_person}
              onChange={(e) => handleInputChange('delivery_contact_person', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Contact Number"
              value={formData.delivery_contact_number}
              onChange={(e) => handleInputChange('delivery_contact_number', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tracking Number"
              value={formData.tracking_number}
              onChange={(e) => handleInputChange('tracking_number', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Courier Name"
              value={formData.courier_name}
              onChange={(e) => handleInputChange('courier_name', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Items</Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={addItem}
            variant="outlined"
            size="small"
          >
            Add Item
          </Button>
        </Box>

        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Product ID</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Unit</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={item.product_id || ''}
                      onChange={(e) => updateItem(index, 'product_id', parseInt(e.target.value) || 0)}
                      required
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0.1, step: 0.1 }}
                      required
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      value={item.unit}
                      onChange={(e) => updateItem(index, 'unit', e.target.value)}
                      required
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      value={item.description}
                      onChange={(e) => updateItem(index, 'description', e.target.value)}
                      placeholder="Item description"
                    />
                  </TableCell>
                  <TableCell>
                    {items.length > 1 && (
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => removeItem(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? 'Saving...' : editMode ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DispatchOrderDialog;