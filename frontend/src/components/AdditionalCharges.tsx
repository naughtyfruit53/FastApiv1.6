// src/components/AdditionalCharges.tsx
// Reusable component for managing additional charges in vouchers
import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Checkbox,
  FormControlLabel,
  Divider,
  Paper,
} from '@mui/material';

export interface AdditionalCharge {
  type: string;
  label: string;
  amount: number;
  enabled: boolean;
}

export interface AdditionalChargesData {
  freight: number;
  installation: number;
  packing: number;
  insurance: number;
  loading: number;
  unloading: number;
  miscellaneous: number;
  [key: string]: number;
}

interface AdditionalChargesProps {
  charges: AdditionalChargesData;
  onChange: (charges: AdditionalChargesData) => void;
  mode?: 'view' | 'edit' | 'create';
}

const CHARGE_TYPES = [
  { key: 'freight', label: 'Freight Charges' },
  { key: 'installation', label: 'Installation Charges' },
  { key: 'packing', label: 'Packing Charges' },
  { key: 'insurance', label: 'Insurance Charges' },
  { key: 'loading', label: 'Loading Charges' },
  { key: 'unloading', label: 'Unloading Charges' },
  { key: 'miscellaneous', label: 'Miscellaneous Charges' },
];

const AdditionalCharges: React.FC<AdditionalChargesProps> = ({
  charges,
  onChange,
  mode = 'edit',
}) => {
  const [enabledCharges, setEnabledCharges] = useState<{ [key: string]: boolean }>(() => {
    const initial: { [key: string]: boolean } = {};
    CHARGE_TYPES.forEach(({ key }) => {
      initial[key] = (charges[key] || 0) > 0;
    });
    return initial;
  });

  const handleToggleCharge = (key: string, enabled: boolean) => {
    setEnabledCharges({ ...enabledCharges, [key]: enabled });
    if (!enabled) {
      onChange({ ...charges, [key]: 0 });
    }
  };

  const handleAmountChange = (key: string, value: number) => {
    onChange({ ...charges, [key]: value });
  };

  const getTotalAdditionalCharges = () => {
    return CHARGE_TYPES.reduce((total, { key }) => {
      return total + (charges[key] || 0);
    }, 0);
  };

  if (mode === 'view') {
    const activeCharges = CHARGE_TYPES.filter(({ key }) => (charges[key] || 0) > 0);
    if (activeCharges.length === 0) {
      return null;
    }

    return (
      <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Additional Charges
        </Typography>
        <Divider sx={{ mb: 1 }} />
        {activeCharges.map(({ key, label }) => (
          <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">{label}:</Typography>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              ₹{(charges[key] || 0).toLocaleString()}
            </Typography>
          </Box>
        ))}
        <Divider sx={{ my: 1 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            Total Additional Charges:
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
            ₹{getTotalAdditionalCharges().toLocaleString()}
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
        Additional Charges
      </Typography>
      <Typography variant="caption" color="text.secondary" gutterBottom display="block">
        These charges will be added to the taxable amount before GST calculation
      </Typography>
      <Divider sx={{ mb: 2 }} />

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {CHARGE_TYPES.map(({ key, label }) => (
          <Box key={key}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={enabledCharges[key] || false}
                  onChange={(e) => handleToggleCharge(key, e.target.checked)}
                  size="small"
                />
              }
              label={label}
              sx={{ mb: 0.5 }}
            />
            {enabledCharges[key] && (
              <TextField
                type="number"
                value={charges[key] || 0}
                onChange={(e) => handleAmountChange(key, parseFloat(e.target.value) || 0)}
                size="small"
                fullWidth
                inputProps={{ min: 0, step: 0.01 }}
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>₹</Typography>,
                }}
                sx={{ ml: 4 }}
              />
            )}
          </Box>
        ))}
      </Box>

      <Divider sx={{ my: 2 }} />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
          Total Additional Charges:
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          ₹{getTotalAdditionalCharges().toLocaleString()}
        </Typography>
      </Box>
    </Paper>
  );
};

export default AdditionalCharges;