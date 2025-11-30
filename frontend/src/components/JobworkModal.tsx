/**
 * Reusable Jobwork Modal Component
 * Single-column stacked layout for both Inward and Outward jobwork
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  Autocomplete,
  CircularProgress,
  Alert,
  Divider,
  Stack,
  FormHelperText,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  AttachFile as AttachFileIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { getProducts, getVendors, getCustomers } from '../../services/masterService';

interface JobworkItem {
  product_id: number | null;
  quantity: number;
  unit: string;
  remarks: string;
}

interface JobworkFormData {
  jobwork_order_no: string;
  party_id: number | null; // vendor_id for inward, customer_id for outward
  date: string;
  expected_return_date: string;
  purpose: string;
  notes: string;
  items: JobworkItem[];
  attachments: File[];
}

interface JobworkModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: JobworkFormData) => Promise<void>;
  direction: 'inward' | 'outward';
  title?: string;
  initialData?: Partial<JobworkFormData>;
}

const emptyItem: JobworkItem = {
  product_id: null,
  quantity: 1,
  unit: 'PCS',
  remarks: '',
};

const JobworkModal: React.FC<JobworkModalProps> = ({
  open,
  onClose,
  onSubmit,
  direction,
  title,
  initialData,
}) => {
  const [formData, setFormData] = useState<JobworkFormData>({
    jobwork_order_no: '',
    party_id: null,
    date: new Date().toISOString().split('T')[0],
    expected_return_date: '',
    purpose: '',
    notes: '',
    items: [{ ...emptyItem }],
    attachments: [],
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (open) {
      if (initialData) {
        setFormData({
          ...formData,
          ...initialData,
          items: initialData.items?.length ? initialData.items : [{ ...emptyItem }],
        });
      } else {
        setFormData({
          jobwork_order_no: '',
          party_id: null,
          date: new Date().toISOString().split('T')[0],
          expected_return_date: '',
          purpose: '',
          notes: '',
          items: [{ ...emptyItem }],
          attachments: [],
        });
      }
      setErrors({});
      setSubmitError(null);
    }
  }, [open, initialData]);

  // Fetch vendors for inward, customers for outward
  const { data: vendorList = [], isLoading: vendorsLoading } = useQuery({
    queryKey: ['vendors'],
    queryFn: getVendors,
    enabled: open && direction === 'inward',
  });

  const { data: customerList = [], isLoading: customersLoading } = useQuery({
    queryKey: ['customers'],
    queryFn: getCustomers,
    enabled: open && direction === 'outward',
  });

  // Fetch products
  const { data: productList = [], isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
    enabled: open,
  });

  const parties = direction === 'inward' ? vendorList : customerList;
  const partiesLoading = direction === 'inward' ? vendorsLoading : customersLoading;
  const partyLabel = direction === 'inward' ? 'Vendor' : 'Customer';

  // Validation
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.party_id) {
      newErrors.party_id = `${partyLabel} is required`;
    }

    if (!formData.date) {
      newErrors.date = 'Date is required';
    }

    if (formData.items.length === 0) {
      newErrors.items = 'At least one item is required';
    }

    formData.items.forEach((item, index) => {
      if (!item.product_id) {
        newErrors[`item_${index}_product`] = 'Product is required';
      }
      if (item.quantity <= 0) {
        newErrors[`item_${index}_quantity`] = 'Quantity must be positive';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit(formData);
      onClose();
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to create jobwork order');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { ...emptyItem }],
    });
  };

  const handleRemoveItem = (index: number) => {
    if (formData.items.length === 1) return; // Keep at least one item
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const handleItemChange = (index: number, field: keyof JobworkItem, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
    // Clear error for this field
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[`item_${index}_${field}`];
      return newErrors;
    });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      setFormData({
        ...formData,
        attachments: [...formData.attachments, ...Array.from(files)],
      });
    }
  };

  const handleRemoveAttachment = (index: number) => {
    const newAttachments = formData.attachments.filter((_, i) => i !== index);
    setFormData({ ...formData, attachments: newAttachments });
  };

  const modalTitle = title || (direction === 'inward' 
    ? 'Create Inward Jobwork Order' 
    : 'Create Outward Jobwork Order');

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { maxHeight: '90vh' } }}
    >
      <DialogTitle>{modalTitle}</DialogTitle>
      <DialogContent dividers>
        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSubmitError(null)}>
            {submitError}
          </Alert>
        )}

        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Party Selection (Vendor/Customer) */}
          <Autocomplete
            options={parties}
            getOptionLabel={(option: any) => option.name || ''}
            value={parties.find((p: any) => p.id === formData.party_id) || null}
            onChange={(_, newValue) => {
              setFormData({ ...formData, party_id: newValue?.id || null });
              setErrors((prev) => ({ ...prev, party_id: '' }));
            }}
            loading={partiesLoading}
            renderInput={(params) => (
              <TextField
                {...params}
                label={partyLabel}
                required
                error={!!errors.party_id}
                helperText={errors.party_id}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {partiesLoading ? <CircularProgress size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
          />

          {/* Items Section */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1" fontWeight="medium">
                Items
              </Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                onClick={handleAddItem}
              >
                Add Row
              </Button>
            </Box>
            {errors.items && (
              <FormHelperText error>{errors.items}</FormHelperText>
            )}
            
            <Stack spacing={2}>
              {formData.items.map((item, index) => (
                <Paper key={index} variant="outlined" sx={{ p: 2 }}>
                  <Stack spacing={2}>
                    <Autocomplete
                      options={productList}
                      getOptionLabel={(option: any) => option.name || ''}
                      value={productList.find((p: any) => p.id === item.product_id) || null}
                      onChange={(_, newValue) => handleItemChange(index, 'product_id', newValue?.id || null)}
                      loading={productsLoading}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Product"
                          required
                          size="small"
                          error={!!errors[`item_${index}_product`]}
                          helperText={errors[`item_${index}_product`]}
                        />
                      )}
                    />
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <TextField
                        type="number"
                        label="Quantity"
                        required
                        size="small"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                        error={!!errors[`item_${index}_quantity`]}
                        helperText={errors[`item_${index}_quantity`]}
                        sx={{ flex: 1 }}
                        inputProps={{ min: 0.01, step: 0.01 }}
                      />
                      <TextField
                        label="Unit"
                        size="small"
                        value={item.unit}
                        onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                        sx={{ width: 100 }}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                      <TextField
                        label="Remarks"
                        size="small"
                        value={item.remarks}
                        onChange={(e) => handleItemChange(index, 'remarks', e.target.value)}
                        fullWidth
                      />
                      {formData.items.length > 1 && (
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleRemoveItem(index)}
                          sx={{ mt: 0.5 }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Stack>
                </Paper>
              ))}
            </Stack>
          </Box>

          <Divider />

          {/* Due Date */}
          <TextField
            label="Due Date"
            type="date"
            value={formData.expected_return_date}
            onChange={(e) => setFormData({ ...formData, expected_return_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />

          {/* Documents/Attachments */}
          <Box>
            <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 1 }}>
              Documents/Attachments
            </Typography>
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadIcon />}
              size="small"
            >
              Upload Files
              <input
                type="file"
                hidden
                multiple
                onChange={handleFileChange}
              />
            </Button>
            {formData.attachments.length > 0 && (
              <Stack spacing={1} sx={{ mt: 1 }}>
                {formData.attachments.map((file, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      p: 1,
                      bgcolor: 'grey.50',
                      borderRadius: 1,
                    }}
                  >
                    <AttachFileIcon fontSize="small" />
                    <Typography variant="body2" sx={{ flex: 1 }}>
                      {file.name}
                    </Typography>
                    <IconButton size="small" onClick={() => handleRemoveAttachment(index)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                ))}
              </Stack>
            )}
          </Box>

          {/* Notes */}
          <TextField
            label="Notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            multiline
            rows={3}
            fullWidth
          />
        </Stack>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? <CircularProgress size={24} /> : 'Create Order'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default JobworkModal;
