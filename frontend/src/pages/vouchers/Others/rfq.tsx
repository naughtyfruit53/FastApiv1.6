// frontend/src/pages/vouchers/Others/rfq.tsx
// Request for Quotation (RFQ) Page
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Grid,
} from '@mui/material';
import {
  Add,
  Remove,
  Visibility,
  Edit,
  Delete,
  Send,
  Assignment,
  Search,
  FilterList,
  Download,
  Upload
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import VoucherLayout from '../../../components/VoucherLayout';
import { procurementService } from '../../../services/procurementService';
interface RFQItem {
  item_code: string;
  item_name: string;
  item_description: string;
  quantity: number;
  unit: string;
  specifications: any;
  expected_price: number;
}
interface RFQFormData {
  rfq_title: string;
  rfq_description: string;
  issue_date: string;
  submission_deadline: string;
  validity_period: number;
  terms_and_conditions: string;
  delivery_requirements: string;
  payment_terms: string;
  is_public: boolean;
  requires_samples: boolean;
  allow_partial_quotes: boolean;
  rfq_items: RFQItem[];
}
const RFQPage: React.FC = () => {
  const [mode, setMode] = useState<'create' | 'view' | 'edit'>('view');
  const [selectedRFQ, setSelectedRFQ] = useState<any>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [formData, setFormData] = useState<RFQFormData>({
    rfq_title: '',
    rfq_description: '',
    issue_date: new Date().toISOString().split('T')[0],
    submission_deadline: '',
    validity_period: 30,
    terms_and_conditions: '',
    delivery_requirements: '',
    payment_terms: '',
    is_public: false,
    requires_samples: false,
    allow_partial_quotes: true,
    rfq_items: []
  });
  const queryClient = useQueryClient();
  // Fetch RFQs
  const { data: rfqs = [], isLoading, error } = useQuery({
    queryKey: ['rfqs', searchTerm, statusFilter],
    queryFn: () => procurementService.getRFQs({
      search: searchTerm || undefined,
      status: statusFilter || undefined
    })
  });
  // Create RFQ mutation
  const createRFQMutation = useMutation({
    mutationFn: procurementService.createRFQ,
    onSuccess: () => {
      toast.success('RFQ created successfully');
      queryClient.invalidateQueries({ queryKey: ['rfqs'] });
      handleDialogClose();
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create RFQ');
    }
  });
  // Update RFQ mutation
  const updateRFQMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      procurementService.updateRFQ(id, data),
    onSuccess: () => {
      toast.success('RFQ updated successfully');
      queryClient.invalidateQueries({ queryKey: ['rfqs'] });
      handleDialogClose();
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update RFQ');
    }
  });
  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedRFQ(null);
    setMode('view');
    setFormData({
      rfq_title: '',
      rfq_description: '',
      issue_date: new Date().toISOString().split('T')[0],
      submission_deadline: '',
      validity_period: 30,
      terms_and_conditions: '',
      delivery_requirements: '',
      payment_terms: '',
      is_public: false,
      requires_samples: false,
      allow_partial_quotes: true,
      rfq_items: []
    });
  };
  const handleCreateNew = () => {
    setMode('create');
    setSelectedRFQ(null);
    setIsDialogOpen(true);
  };
  const handleEdit = (rfq: any) => {
    setMode('edit');
    setSelectedRFQ(rfq);
    setFormData({
      rfq_title: rfq.rfq_title || '',
      rfq_description: rfq.rfq_description || '',
      issue_date: rfq.issue_date || '',
      submission_deadline: rfq.submission_deadline || '',
      validity_period: rfq.validity_period || 30,
      terms_and_conditions: rfq.terms_and_conditions || '',
      delivery_requirements: rfq.delivery_requirements || '',
      payment_terms: rfq.payment_terms || '',
      is_public: rfq.is_public || false,
      requires_samples: rfq.requires_samples || false,
      allow_partial_quotes: rfq.allow_partial_quotes || true,
      rfq_items: rfq.rfq_items || []
    });
    setIsDialogOpen(true);
  };
  const handleView = (rfq: any) => {
    setMode('view');
    setSelectedRFQ(rfq);
    setFormData({
      rfq_title: rfq.rfq_title || '',
      rfq_description: rfq.rfq_description || '',
      issue_date: rfq.issue_date || '',
      submission_deadline: rfq.submission_deadline || '',
      validity_period: rfq.validity_period || 30,
      terms_and_conditions: rfq.terms_and_conditions || '',
      delivery_requirements: rfq.delivery_requirements || '',
      payment_terms: rfq.payment_terms || '',
      is_public: rfq.is_public || false,
      requires_samples: rfq.requires_samples || false,
      allow_partial_quotes: rfq.allow_partial_quotes || true,
      rfq_items: rfq.rfq_items || []
    });
    setIsDialogOpen(true);
  };
  const handleSubmit = () => {
    if (mode === 'create') {
      createRFQMutation.mutate(formData);
    } else if (mode === 'edit' && selectedRFQ) {
      updateRFQMutation.mutate({ id: selectedRFQ.id, data: formData });
    }
  };
  const addRFQItem = () => {
    setFormData(prev => ({
      ...prev,
      rfq_items: [...prev.rfq_items, {
        item_code: '',
        item_name: '',
        item_description: '',
        quantity: 1,
        unit: 'PCS',
        specifications: {},
        expected_price: 0
      }]
    }));
  };
  const removeRFQItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      rfq_items: prev.rfq_items.filter((_, i) => i !== index)
    }));
  };
  const updateRFQItem = (index: number, field: keyof RFQItem, value: any) => {
    setFormData(prev => ({
      ...prev,
      rfq_items: prev.rfq_items.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };
  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'draft': return 'default';
      case 'sent': return 'primary';
      case 'responded': return 'info';
      case 'evaluated': return 'warning';
      case 'awarded': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };
  return (
    <VoucherLayout
      title="Request for Quotation (RFQ)"
      description="Manage procurement requests and vendor quotations"
    >
      <Container maxWidth="xl">
        {/* Header Actions */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Search RFQs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="sent">Sent</MenuItem>
                <MenuItem value="responded">Responded</MenuItem>
                <MenuItem value="evaluated">Evaluated</MenuItem>
                <MenuItem value="awarded">Awarded</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateNew}
          >
            Create RFQ
          </Button>
        </Box>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Failed to load RFQs
          </Alert>
        )}
        {/* Loading */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}
        {/* RFQ Cards */}
        <Grid container spacing={3}>
          {rfqs.map((rfq: any) => (
            <Grid item xs={12} md={6} lg={4} key={rfq.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div" noWrap>
                      {rfq.rfq_number}
                    </Typography>
                    <Chip
                      label={rfq.status}
                      color={getStatusColor(rfq.status) as any}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body1" sx={{ fontWeight: 500, mb: 1 }}>
                    {rfq.rfq_title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {rfq.rfq_description}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Issue Date:</strong> {rfq.issue_date}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Deadline:</strong> {rfq.submission_deadline}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Items:</strong> {rfq.rfq_items?.length || 0}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => handleView(rfq)}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => handleEdit(rfq)}
                  >
                    Edit
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
        {/* RFQ Dialog */}
        <Dialog open={isDialogOpen} onClose={handleDialogClose} maxWidth="lg" fullWidth>
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Assignment />
              {mode === 'create' && 'Create New RFQ'}
              {mode === 'edit' && 'Edit RFQ'}
              {mode === 'view' && 'View RFQ'}
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="RFQ Title"
                  value={formData.rfq_title}
                  onChange={(e) => setFormData(prev => ({ ...prev, rfq_title: e.target.value }))}
                  disabled={mode === 'view'}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Validity Period (Days)"
                  type="number"
                  value={formData.validity_period}
                  onChange={(e) => setFormData(prev => ({ ...prev, validity_period: parseInt(e.target.value) || 0 }))}
                  disabled={mode === 'view'}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Issue Date"
                  type="date"
                  value={formData.issue_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, issue_date: e.target.value }))}
                  disabled={mode === 'view'}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Submission Deadline"
                  type="date"
                  value={formData.submission_deadline}
                  onChange={(e) => setFormData(prev => ({ ...prev, submission_deadline: e.target.value }))}
                  disabled={mode === 'view'}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="RFQ Description"
                  multiline
                  rows={3}
                  value={formData.rfq_description}
                  onChange={(e) => setFormData(prev => ({ ...prev, rfq_description: e.target.value }))}
                  disabled={mode === 'view'}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Terms and Conditions"
                  multiline
                  rows={3}
                  value={formData.terms_and_conditions}
                  onChange={(e) => setFormData(prev => ({ ...prev, terms_and_conditions: e.target.value }))}
                  disabled={mode === 'view'}
                />
              </Grid>
            </Grid>
            {/* RFQ Items */}
            <Box sx={{ mt: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">RFQ Items</Typography>
                {mode !== 'view' && (
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={addRFQItem}
                    size="small"
                  >
                    Add Item
                  </Button>
                )}
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item Code</TableCell>
                      <TableCell>Item Name</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Expected Price</TableCell>
                      {mode !== 'view' && <TableCell>Actions</TableCell>}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formData.rfq_items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <TextField
                            size="small"
                            value={item.item_code}
                            onChange={(e) => updateRFQItem(index, 'item_code', e.target.value)}
                            disabled={mode === 'view'}
                            placeholder="Item code"
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={item.item_name}
                            onChange={(e) => updateRFQItem(index, 'item_name', e.target.value)}
                            disabled={mode === 'view'}
                            placeholder="Item name"
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={item.quantity}
                            onChange={(e) => updateRFQItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                            disabled={mode === 'view'}
                            inputProps={{ min: 0, step: 0.1 }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={item.unit}
                            onChange={(e) => updateRFQItem(index, 'unit', e.target.value)}
                            disabled={mode === 'view'}
                            placeholder="Unit"
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={item.expected_price}
                            onChange={(e) => updateRFQItem(index, 'expected_price', parseFloat(e.target.value) || 0)}
                            disabled={mode === 'view'}
                            inputProps={{ min: 0, step: 0.01 }}
                          />
                        </TableCell>
                        {mode !== 'view' && (
                          <TableCell>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => removeRFQItem(index)}
                            >
                              <Remove />
                            </IconButton>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose}>
              {mode === 'view' ? 'Close' : 'Cancel'}
            </Button>
            {mode !== 'view' && (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={createRFQMutation.isPending || updateRFQMutation.isPending}
              >
                {mode === 'create' ? 'Create RFQ' : 'Update RFQ'}
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Container>
    </VoucherLayout>
  );
};
export default RFQPage;