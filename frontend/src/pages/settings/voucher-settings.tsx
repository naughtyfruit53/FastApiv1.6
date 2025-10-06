// frontend/src/pages/settings/voucher-settings.tsx

/**
 * Voucher Settings Page
 * Organization-level settings for voucher numbering and formatting
 * Requirements 5, 6, 7
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
  Switch,
  Button,
  Grid,
  Alert,
  Snackbar,
  MenuItem,
  Select,
  InputLabel,
  Paper,
  Divider,
  Chip
} from '@mui/material';
import {
  Save as SaveIcon,
  Preview as PreviewIcon
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../lib/api';

interface VoucherSettings {
  voucher_prefix: string;
  voucher_prefix_enabled: boolean;
  voucher_counter_reset_period: 'never' | 'monthly' | 'quarterly' | 'annually';
  voucher_format_template_id: number | null;
}

interface VoucherFormatTemplate {
  id: number;
  name: string;
  description: string;
  preview_image_url?: string;
  is_system_template: boolean;
}

const VoucherSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<VoucherSettings>({
    voucher_prefix: '',
    voucher_prefix_enabled: false,
    voucher_counter_reset_period: 'annually',
    voucher_format_template_id: null
  });
  const [templates, setTemplates] = useState<VoucherFormatTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [previewNumber, setPreviewNumber] = useState('');

  useEffect(() => {
    fetchSettings();
    fetchTemplates();
  }, []);

  useEffect(() => {
    // Generate preview number when settings change
    generatePreviewNumber();
  }, [settings]);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/organizations/settings');
      if (response.data) {
        setSettings({
          voucher_prefix: response.data.voucher_prefix || '',
          voucher_prefix_enabled: response.data.voucher_prefix_enabled || false,
          voucher_counter_reset_period: response.data.voucher_counter_reset_period || 'annually',
          voucher_format_template_id: response.data.voucher_format_template_id || null
        });
      }
    } catch (err: any) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/voucher-format-templates');
      setTemplates(response.data || []);
    } catch (err) {
      console.error('Error fetching templates:', err);
    }
  };

  const generatePreviewNumber = () => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;
    const fiscalYear = currentMonth > 3 
      ? `${String(currentYear).slice(-2)}${String(currentYear + 1).slice(-2)}`
      : `${String(currentYear - 1).slice(-2)}${String(currentYear).slice(-2)}`;

    let prefix = 'PO';
    if (settings.voucher_prefix_enabled && settings.voucher_prefix) {
      prefix = `${settings.voucher_prefix}-PO`;
    }

    let periodSegment = '';
    if (settings.voucher_counter_reset_period === 'monthly') {
      const monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                         'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
      periodSegment = `/${monthNames[currentMonth - 1]}`;
    } else if (settings.voucher_counter_reset_period === 'quarterly') {
      const quarter = Math.floor((currentMonth - 1) / 3) + 1;
      periodSegment = `/Q${quarter}`;
    }

    const preview = `${prefix}/${fiscalYear}${periodSegment}/00001`;
    setPreviewNumber(preview);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await api.put('/organizations/settings', settings);
      setSuccess('Settings saved successfully!');
    } catch (err: any) {
      console.error('Error saving settings:', err);
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handlePrefixChange = (value: string) => {
    // Limit to 5 characters and uppercase
    const sanitized = value.toUpperCase().slice(0, 5);
    setSettings({ ...settings, voucher_prefix: sanitized });
  };

  if (loading) {
    return (
      <DashboardLayout title="Voucher Settings" subtitle="Configure voucher numbering and formatting">
        <Box sx={{ p: 3 }}>
          <Typography>Loading...</Typography>
        </Box>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout 
      title="Voucher Settings" 
      subtitle="Configure voucher numbering and formatting"
    >
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Voucher Prefix Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Voucher Number Prefix
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Add a custom prefix (up to 5 characters) to all voucher numbers
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.voucher_prefix_enabled}
                      onChange={(e) => setSettings({ 
                        ...settings, 
                        voucher_prefix_enabled: e.target.checked 
                      })}
                    />
                  }
                  label="Enable Prefix"
                  sx={{ mb: 2 }}
                />

                <TextField
                  label="Prefix"
                  value={settings.voucher_prefix}
                  onChange={(e) => handlePrefixChange(e.target.value)}
                  disabled={!settings.voucher_prefix_enabled}
                  fullWidth
                  helperText="Max 5 characters, will be converted to uppercase"
                  inputProps={{ maxLength: 5 }}
                  sx={{ mb: 2 }}
                />

                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                    Preview:
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {previewNumber}
                  </Typography>
                </Paper>
              </CardContent>
            </Card>
          </Grid>

          {/* Counter Reset Period */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Counter Reset Period
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Choose how often voucher numbers reset
                </Typography>

                <FormControl component="fieldset" fullWidth>
                  <RadioGroup
                    value={settings.voucher_counter_reset_period}
                    onChange={(e) => setSettings({ 
                      ...settings, 
                      voucher_counter_reset_period: e.target.value as any
                    })}
                  >
                    <FormControlLabel 
                      value="never" 
                      control={<Radio />} 
                      label={
                        <Box>
                          <Typography>Never</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Continuous numbering (e.g., PO/2526/00001)
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel 
                      value="annually" 
                      control={<Radio />} 
                      label={
                        <Box>
                          <Typography>Annually</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Reset every fiscal year (e.g., PO/2526/00001)
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel 
                      value="quarterly" 
                      control={<Radio />} 
                      label={
                        <Box>
                          <Typography>Quarterly</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Reset every quarter (e.g., PO/2526/Q1/00001)
                          </Typography>
                        </Box>
                      }
                    />
                    <FormControlLabel 
                      value="monthly" 
                      control={<Radio />} 
                      label={
                        <Box>
                          <Typography>Monthly</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Reset every month (e.g., PO/2526/JAN/00001)
                          </Typography>
                        </Box>
                      }
                    />
                  </RadioGroup>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          {/* Voucher Format Template */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Voucher Format Template
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Select a template for voucher PDF and email formatting
                </Typography>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Template</InputLabel>
                  <Select
                    value={settings.voucher_format_template_id || ''}
                    onChange={(e) => setSettings({ 
                      ...settings, 
                      voucher_format_template_id: e.target.value ? Number(e.target.value) : null
                    })}
                    label="Template"
                  >
                    <MenuItem value="">
                      <em>Default Template</em>
                    </MenuItem>
                    {templates.map((template) => (
                      <MenuItem key={template.id} value={template.id}>
                        {template.name}
                        {template.is_system_template && (
                          <Chip 
                            label="System" 
                            size="small" 
                            sx={{ ml: 1 }} 
                          />
                        )}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {settings.voucher_format_template_id && (
                  <Button
                    startIcon={<PreviewIcon />}
                    variant="outlined"
                    size="small"
                  >
                    Preview Template
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Save Button */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Success/Error Snackbar */}
        <Snackbar
          open={!!success}
          autoHideDuration={6000}
          onClose={() => setSuccess(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="success" onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </DashboardLayout>
  );
};

export default VoucherSettingsPage;