// frontend/src/components/VoucherReferenceDropdown.tsx
// Reference column dropdown component for voucher types

import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { getReferenceVoucherOptions, getVoucherConfig } from '../utils/voucherUtils';
import api from '../lib/api';

interface VoucherReferenceDropdownProps {
  voucherType: string;
  value?: {
    referenceType?: string;
    referenceId?: number;
    referenceNumber?: string;
  };
  onChange: (reference: {
    referenceType?: string;
    referenceId?: number;
    referenceNumber?: string;
  }) => void;
  disabled?: boolean;
  onReferenceSelected?: (referenceData: any) => void;
}

const VoucherReferenceDropdown: React.FC<VoucherReferenceDropdownProps> = ({
  voucherType,
  value = {},
  onChange,
  disabled = false,
  onReferenceSelected
}) => {
  const [referenceOptions, setReferenceOptions] = useState<any[]>([]);
  const [loadingReferences, setLoadingReferences] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = getVoucherConfig(voucherType as any);
  const allowedTypes = getReferenceVoucherOptions(voucherType as any);

  // Fetch reference documents when reference type changes
  useEffect(() => {
    if (value.referenceType && config.referenceConfig) {
      fetchReferenceDocuments(value.referenceType);
    }
  }, [value.referenceType, config.referenceConfig]);

  // If this voucher type doesn't support references, don't render
  if (!config.referenceConfig) {
    return null;
  }

  const fetchReferenceDocuments = async (referenceType: string) => {
    setLoadingReferences(true);
    setError(null);
    
    try {
      const typeConfig = getVoucherConfig(referenceType as any);
      const response = await api.get(`${typeConfig.endpoint}?limit=100&sort=desc`);
      
      if (response.data) {
        const documents = Array.isArray(response.data) ? response.data : [response.data];
        setReferenceOptions(documents.map((doc: any) => ({
          id: doc.id,
          label: `${doc.voucher_number || doc.number}`,
          value: doc.id,
          data: doc
        })));
      }
    } catch (err) {
      console.error('Error fetching reference documents:', err);
      setError('Failed to load reference documents');
      setReferenceOptions([]);
    } finally {
      setLoadingReferences(false);
    }
  };

  const handleTypeChange = (newType: string) => {
    onChange({
      referenceType: newType,
      referenceId: undefined,
      referenceNumber: undefined
    });
    setReferenceOptions([]);
  };

  const handleDocumentChange = (selectedOption: any) => {
    if (selectedOption) {
      const newReference = {
        referenceType: value.referenceType,
        referenceId: selectedOption.value,
        referenceNumber: selectedOption.data.voucher_number || selectedOption.data.number
      };
      
      onChange(newReference);
      
      // Call callback with full reference data for auto-population
      if (onReferenceSelected) {
        onReferenceSelected(selectedOption.data);
      }
    } else {
      onChange({
        referenceType: value.referenceType,
        referenceId: undefined,
        referenceNumber: undefined
      });
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={2}>
        {/* Reference Type Selection */}
        <Grid size={{ xs: 12, md: 6 }}>
          <FormControl fullWidth size="small">
            <InputLabel 
              id="reference-type-label"
              style={{ fontSize: 12 }}
              shrink
            >
              Reference Type
            </InputLabel>
            <Select
              labelId="reference-type-label"
              value={value.referenceType || ''}
              onChange={(e) => handleTypeChange(e.target.value)}
              disabled={disabled}
              label="Reference Type"
              sx={{ 
                height: 27,
                '& .MuiSelect-select': { 
                  fontSize: 14,
                  textAlign: 'center'
                }
              }}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {allowedTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Reference Document Selection */}
        {value.referenceType && (
          <Grid size={{ xs: 12, md: 6 }}>
            <Autocomplete
              size="small"
              options={referenceOptions}
              value={referenceOptions.find(opt => opt.value === value.referenceId) || null}
              onChange={(_, newValue) => handleDocumentChange(newValue)}
              disabled={disabled || loadingReferences}
              loading={loadingReferences}
              getOptionLabel={(option) => option.label || ''}
              isOptionEqualToValue={(option, value) => option.value === value.value}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={config.referenceConfig?.label || 'Reference Document'}
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ 
                    ...params.inputProps,
                    style: { fontSize: 14, textAlign: 'center' }
                  }}
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loadingReferences ? <CircularProgress color="inherit" size={20} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
              renderOption={(props, option) => (
                <Box component="li" {...props} key={option.value}>
                  <Typography variant="body2" sx={{ fontSize: 13 }}>
                    {option.label}
                  </Typography>
                </Box>
              )}
              noOptionsText={
                value.referenceType 
                  ? `No ${allowedTypes.find(t => t.value === value.referenceType)?.label || 'documents'} found`
                  : 'Select reference type first'
              }
            />
          </Grid>
        )}
      </Grid>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 1, fontSize: 12 }}>
          {error}
        </Alert>
      )}

      {/* Selected Reference Info */}
      {value.referenceId && value.referenceNumber && (
        <Typography 
          variant="body2" 
          sx={{ 
            mt: 1, 
            fontSize: 12, 
            textAlign: 'center',
            color: 'primary.main',
            fontWeight: 'medium'
          }}
        >
          Referenced: {value.referenceNumber}
        </Typography>
      )}
    </Box>
  );
};

export default VoucherReferenceDropdown;