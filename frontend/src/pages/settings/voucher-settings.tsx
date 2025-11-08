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
  RadioGroup,
  Radio,
  Switch,
  Button,
  Grid,
  Alert,
  Snackbar,
  Paper,
  Chip,
  Tooltip
} from '@mui/material';
import {
  Save as SaveIcon,
  Preview as PreviewIcon
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { ProtectedPage } from '../../components/ProtectedPage';

interface VoucherSettings {
  voucher_prefix: string;
  voucher_prefix_enabled: boolean;
  voucher_counter_reset_period: 'never' | 'monthly' | 'quarterly' | 'annually';
  voucher_format_template_id: number | null;
  // Terms & Conditions for different voucher types
  purchase_order_terms?: string;
  purchase_voucher_terms?: string;
  sales_order_terms?: string;
  sales_voucher_terms?: string;
  quotation_terms?: string;
  proforma_invoice_terms?: string;
  delivery_challan_terms?: string;
  grn_terms?: string;
  manufacturing_terms?: string;
}

interface VoucherFormatTemplate {
  id: number;
  name: string;
  description: string;
  preview_image_url?: string;
  is_system_template: boolean;
}

const VoucherSettingsPage: React.FC = () => {
  const { user } = useAuth();
  const isOrgAdmin = user?.role?.toLowerCase() === 'org_admin' || user?.is_super_admin;
  
  const [settings, setSettings] = useState<VoucherSettings>({
    voucher_prefix: '',
    voucher_prefix_enabled: false,
    voucher_counter_reset_period: 'annually',
    voucher_format_template_id: null,
    purchase_order_terms: '',
    purchase_voucher_terms: '',
    sales_order_terms: '',
    sales_voucher_terms: '',
    quotation_terms: '',
    proforma_invoice_terms: '',
    delivery_challan_terms: '',
    grn_terms: '',
    manufacturing_terms: ''
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
    <ProtectedPage moduleKey="settings" action="update">
      <DashboardLayout 
        title="Voucher Settings" 
        subtitle="Configure voucher numbering and formatting"
      >
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Voucher Prefix Settings - org_admin only */}
          {isOrgAdmin ? (
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
          ) : (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Voucher Number Prefix
                  </Typography>
                  <Alert severity="info">
                    This setting can only be modified by Organization Administrators.
                    {settings.voucher_prefix_enabled && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2">
                          Current prefix: <strong>{settings.voucher_prefix || '(none)'}</strong>
                        </Typography>
                      </Box>
                    )}
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Counter Reset Period - org_admin only */}
          {isOrgAdmin ? (
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
          ) : (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Counter Reset Period
                  </Typography>
                  <Alert severity="info">
                    This setting can only be modified by Organization Administrators.
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        Current period: <strong>{settings.voucher_counter_reset_period}</strong>
                      </Typography>
                    </Box>
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Voucher Format Template */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Voucher PDF Template Style
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Choose a professional template style for all your voucher PDFs. Choose a professional template style for all your voucher PDFs. Each template includes bank details and terms & conditions.
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {templates.map((template) => (
                    <Grid item xs={12} sm={6} md={3} key={template.id}>
                      <Card 
                        sx={{ 
                          cursor: 'pointer',
                          border: settings.voucher_format_template_id === template.id ? 3 : 1,
                          borderColor: settings.voucher_format_template_id === template.id ? 'primary.main' : 'grey.300',
                          transition: 'all 0.2s',
                          '&:hover': {
                            boxShadow: 4,
                            transform: 'translateY(-4px)'
                          }
                        }}
                        onClick={() => setSettings({ 
                          ...settings, 
                          voucher_format_template_id: template.id 
                        })}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="h6" component="div">
                              {template.name}
                            </Typography>
                            {settings.voucher_format_template_id === template.id && (
                              <Chip 
                                label="Selected" 
                                color="primary" 
                                size="small" 
                              />
                            )}
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 80 }}>
                            {template.description}
                          </Typography>
                          <Button
                            startIcon={<PreviewIcon />}
                            variant="outlined"
                            size="small"
                            fullWidth
                            onClick={(e) => {
                              e.stopPropagation();
                              window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/voucher-format-templates/${template.id}/preview`, '_blank');
                            }}
                          >
                            Preview PDF
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>

                {!settings.voucher_format_template_id && templates.length > 0 && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    No template selected. The default "Standard" template will be used for all vouchers.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Terms & Conditions Section */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Terms & Conditions
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure default terms & conditions for each voucher type. These will appear in PDFs.
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Purchase Order Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.purchase_order_terms || ''}
                      onChange={(e) => setSettings({ ...settings, purchase_order_terms: e.target.value })}
                      placeholder="Enter default terms for Purchase Orders..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Purchase Voucher Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.purchase_voucher_terms || ''}
                      onChange={(e) => setSettings({ ...settings, purchase_voucher_terms: e.target.value })}
                      placeholder="Enter default terms for Purchase Vouchers..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Sales Order Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.sales_order_terms || ''}
                      onChange={(e) => setSettings({ ...settings, sales_order_terms: e.target.value })}
                      placeholder="Enter default terms for Sales Orders..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Sales Voucher Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.sales_voucher_terms || ''}
                      onChange={(e) => setSettings({ ...settings, sales_voucher_terms: e.target.value })}
                      placeholder="Enter default terms for Sales Vouchers..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Quotation Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.quotation_terms || ''}
                      onChange={(e) => setSettings({ ...settings, quotation_terms: e.target.value })}
                      placeholder="Enter default terms for Quotations..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Proforma Invoice Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.proforma_invoice_terms || ''}
                      onChange={(e) => setSettings({ ...settings, proforma_invoice_terms: e.target.value })}
                      placeholder="Enter default terms for Proforma Invoices..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Delivery Challan Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.delivery_challan_terms || ''}
                      onChange={(e) => setSettings({ ...settings, delivery_challan_terms: e.target.value })}
                      placeholder="Enter default terms for Delivery Challans..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="GRN Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.grn_terms || ''}
                      onChange={(e) => setSettings({ ...settings, grn_terms: e.target.value })}
                      placeholder="Enter default terms for Goods Receipt Notes..."
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Manufacturing Terms"
                      multiline
                      rows={3}
                      fullWidth
                      value={settings.manufacturing_terms || ''}
                      onChange={(e) => setSettings({ ...settings, manufacturing_terms: e.target.value })}
                      placeholder="Enter default terms for Manufacturing Vouchers..."
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
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
    </ProtectedPage>
  );
};

export default VoucherSettingsPage;