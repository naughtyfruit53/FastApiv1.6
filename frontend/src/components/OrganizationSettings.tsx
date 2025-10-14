// frontend/src/components/OrganizationSettings.tsx

import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControl,
  FormControlLabel,
  FormGroup,
  Divider,
  Alert,
  CircularProgress,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { ExpandMore, Email, Security, Settings, Sync, IntegrationInstructions, Description, Download, Upload } from "@mui/icons-material";
import { organizationService } from "../services/organizationService";
import { useAuth } from "../context/AuthContext";
import api from "../lib/api";

interface OrganizationSettingsData {
  id?: number;
  organization_id: number;
  mail_1_level_up_enabled: boolean;
  auto_send_notifications: boolean;
  custom_settings?: any;
  created_at?: string;
  updated_at?: string;
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

interface TallyConfig {
  enabled: boolean;
  host: string;
  port: number;
  company_name: string;
  sync_frequency: string;
  last_sync?: string;
}

const OrganizationSettings: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<OrganizationSettingsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Tally integration state
  const [tallyConfig, setTallyConfig] = useState<TallyConfig>({
    enabled: false,
    host: "localhost",
    port: 9000,
    company_name: "",
    sync_frequency: "manual",
  });
  const [tallyDialogOpen, setTallyDialogOpen] = useState(false);
  const [tallyTesting, setTallyTesting] = useState(false);
  const [tallySyncing, setTallySyncing] = useState(false);

  // Load organization settings on component mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await organizationService.getOrganizationSettings();
      setSettings(data);
    } catch (err: any) {
      setError(err.message || "Failed to load organization settings");
      // Set default settings if none exist
      setSettings({
        organization_id: user?.organization_id || 0,
        mail_1_level_up_enabled: false,
        auto_send_notifications: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (updatedSettings: Partial<OrganizationSettingsData>) => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const newSettings = { ...settings, ...updatedSettings };
      const result = await organizationService.updateOrganizationSettings(updatedSettings);
      
      setSettings(result);
      setSuccess("Settings updated successfully!");
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to update settings");
    } finally {
      setSaving(false);
    }
  };

  const handleMail1LevelUpChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    updateSettings({ mail_1_level_up_enabled: enabled });
  };

  const handleAutoNotificationsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    updateSettings({ auto_send_notifications: enabled });
  };

  const handleTermsChange = (field: keyof OrganizationSettingsData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    updateSettings({ [field]: value });
  };

  // Tally Integration Handlers
  const loadTallyConfig = async () => {
    try {
      const response = await api.get("/tally/configuration");
      if (response.data) {
        setTallyConfig(response.data);
      }
    } catch (err: any) {
      // If no config exists, use defaults
      console.log("No Tally config found, using defaults");
    }
  };

  const saveTallyConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      const response = await api.post("/tally/configuration", tallyConfig);
      setTallyConfig(response.data);
      setSuccess("Tally configuration saved successfully!");
      setTimeout(() => setSuccess(null), 3000);
      setTallyDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to save Tally configuration");
    } finally {
      setSaving(false);
    }
  };

  const testTallyConnection = async () => {
    try {
      setTallyTesting(true);
      setError(null);
      const response = await api.post("/tally/test-connection", {
        host: tallyConfig.host,
        port: tallyConfig.port,
        company_name: tallyConfig.company_name,
      });
      
      if (response.data.success) {
        setSuccess("Tally connection successful!");
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.data.message || "Connection test failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to connect to Tally");
    } finally {
      setTallyTesting(false);
    }
  };

  const syncWithTally = async () => {
    try {
      setTallySyncing(true);
      setError(null);
      const response = await api.post("/tally/sync", {
        sync_type: "full",
      });
      
      setSuccess(`Tally sync completed! Synced ${response.data.items_synced || 0} items.`);
      setTimeout(() => setSuccess(null), 5000);
      
      // Reload config to get updated last_sync time
      await loadTallyConfig();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to sync with Tally");
    } finally {
      setTallySyncing(false);
    }
  };

  // Load Tally config on mount
  useEffect(() => {
    if (user?.is_super_admin) {
      loadTallyConfig();
    }
  }, [user]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading organization settings...</Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ display: "flex", alignItems: "center", mb: 2 }}
      >
        <Settings sx={{ mr: 1 }} />
        Organization Settings
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <FormGroup>
        {/* Email Settings Section */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: "flex", alignItems: "center", width: "100%" }}>
              <Email sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Email Settings</Typography>
              <Box sx={{ ml: "auto" }}>
                {settings?.mail_1_level_up_enabled && (
                  <Chip label="Mail 1 Level Up: ON" color="primary" size="small" />
                )}
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={settings?.mail_1_level_up_enabled || false}
                  onChange={handleMail1LevelUpChange}
                  disabled={saving}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Mail 1 Level Up</Typography>
                  <Typography variant="body2" color="text.secondary">
                    When enabled, emails sent by users will automatically BCC one level up:
                    <br />
                    • Executive emails → BCC their assigned Manager
                    <br />
                    • Manager emails → BCC Management users
                    <br />
                    • Management emails → No BCC (top level)
                  </Typography>
                </Box>
              }
            />
          </AccordionDetails>
        </Accordion>

        {/* Notification Settings Section */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Security sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Notification Settings</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={settings?.auto_send_notifications || false}
                  onChange={handleAutoNotificationsChange}
                  disabled={saving}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Auto Send Notifications</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Automatically send system notifications for important events
                  </Typography>
                </Box>
              }
            />
          </AccordionDetails>
        </Accordion>

        {/* Voucher Terms & Conditions Section */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <Description sx={{ mr: 1 }} />
              <Typography variant="subtitle1">Voucher Terms & Conditions</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
              <TextField
                label="Purchase Order Terms"
                value={settings?.purchase_order_terms || ""}
                onChange={handleTermsChange("purchase_order_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for purchase orders (up to 2000 characters)"
              />
              <TextField
                label="Purchase Voucher Terms"
                value={settings?.purchase_voucher_terms || ""}
                onChange={handleTermsChange("purchase_voucher_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for purchase vouchers (up to 2000 characters)"
              />
              <TextField
                label="Sales Order Terms"
                value={settings?.sales_order_terms || ""}
                onChange={handleTermsChange("sales_order_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for sales orders (up to 2000 characters)"
              />
              <TextField
                label="Sales Voucher Terms"
                value={settings?.sales_voucher_terms || ""}
                onChange={handleTermsChange("sales_voucher_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for sales vouchers (up to 2000 characters)"
              />
              <TextField
                label="Quotation Terms"
                value={settings?.quotation_terms || ""}
                onChange={handleTermsChange("quotation_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for quotations (up to 2000 characters)"
              />
              <TextField
                label="Proforma Invoice Terms"
                value={settings?.proforma_invoice_terms || ""}
                onChange={handleTermsChange("proforma_invoice_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for proforma invoices (up to 2000 characters)"
              />
              <TextField
                label="Delivery Challan Terms"
                value={settings?.delivery_challan_terms || ""}
                onChange={handleTermsChange("delivery_challan_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for delivery challans (up to 2000 characters)"
              />
              <TextField
                label="Goods Receipt Note Terms"
                value={settings?.grn_terms || ""}
                onChange={handleTermsChange("grn_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for GRNs (up to 2000 characters)"
              />
              <TextField
                label="Manufacturing Terms"
                value={settings?.manufacturing_terms || ""}
                onChange={handleTermsChange("manufacturing_terms")}
                multiline
                rows={4}
                fullWidth
                helperText="Terms for manufacturing vouchers (up to 2000 characters)"
              />
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Tally Integration Section - Only for App Super Admin */}
        {user?.is_super_admin && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: "flex", alignItems: "center", width: "100%" }}>
                <IntegrationInstructions sx={{ mr: 1 }} />
                <Typography variant="subtitle1">Tally Integration</Typography>
                <Box sx={{ ml: "auto", mr: 2 }}>
                  {tallyConfig.enabled && (
                    <Chip label="Enabled" color="success" size="small" />
                  )}
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={tallyConfig.enabled}
                      onChange={(e) => setTallyConfig({ ...tallyConfig, enabled: e.target.checked })}
                      disabled={saving}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body1">Enable Tally Sync</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Integrate with Tally for real-time data synchronization
                      </Typography>
                    </Box>
                  }
                />

                {tallyConfig.enabled && (
                  <>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      Connect to Tally ERP 9 running on your local network. Ensure Tally is configured to accept external connections (F12 → Configure → Enable ODBC Server).
                    </Alert>

                    <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                      <Button
                        variant="outlined"
                        startIcon={<Settings />}
                        onClick={() => setTallyDialogOpen(true)}
                        size="small"
                      >
                        Configure Connection
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Sync />}
                        onClick={syncWithTally}
                        disabled={tallySyncing || !tallyConfig.company_name}
                        size="small"
                        color="primary"
                      >
                        {tallySyncing ? "Syncing..." : "Sync Now"}
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Download />}
                        onClick={async () => {
                          try {
                            await api.post('/tally/import');
                            alert('Import from Tally initiated. This may take a few minutes.');
                          } catch (error) {
                            alert('Failed to import from Tally');
                          }
                        }}
                        disabled={!tallyConfig.company_name}
                        size="small"
                        color="success"
                      >
                        Import from Tally
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Upload />}
                        onClick={async () => {
                          try {
                            await api.post('/tally/export');
                            alert('Export to Tally initiated.');
                          } catch (error) {
                            alert('Failed to export to Tally');
                          }
                        }}
                        disabled={!tallyConfig.company_name}
                        size="small"
                        color="warning"
                      >
                        Export to Tally
                      </Button>
                    </Box>

                    {tallyConfig.last_sync && (
                      <Typography variant="caption" color="text.secondary">
                        Last synced: {new Date(tallyConfig.last_sync).toLocaleString()}
                      </Typography>
                    )}

                    <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Tally Integration Features:
                      </Typography>
                      <Box component="ul" sx={{ mt: 1, pl: 2, mb: 0 }}>
                        <li><Typography variant="body2">✓ Two-way sync with Tally ERP 9</Typography></li>
                        <li><Typography variant="body2">✓ Import ledgers, vouchers, and items</Typography></li>
                        <li><Typography variant="body2">✓ Export sales and purchase data</Typography></li>
                        <li><Typography variant="body2">✓ Real-time inventory synchronization</Typography></li>
                        <li><Typography variant="body2">✓ Automatic data mapping and validation</Typography></li>
                      </Box>
                    </Box>
                  </>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        )}
      </FormGroup>

      {saving && (
        <Box display="flex" justifyContent="center" alignItems="center" sx={{ mt: 2 }}>
          <CircularProgress size={20} />
          <Typography sx={{ ml: 1 }}>Saving...</Typography>
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="body2" color="text.secondary">
          Organization settings apply to all users in your organization
        </Typography>
        <Button
          variant="outlined"
          onClick={loadSettings}
          disabled={loading || saving}
          size="small"
        >
          Refresh
        </Button>
      </Box>

      {/* Tally Configuration Dialog */}
      <Dialog open={tallyDialogOpen} onClose={() => setTallyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Tally Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
            <TextField
              label="Tally Server Host"
              value={tallyConfig.host}
              onChange={(e) => setTallyConfig({ ...tallyConfig, host: e.target.value })}
              fullWidth
              helperText="e.g., localhost or IP address"
            />
            <TextField
              label="Port"
              type="number"
              value={tallyConfig.port}
              onChange={(e) => setTallyConfig({ ...tallyConfig, port: parseInt(e.target.value) })}
              fullWidth
              helperText="Default Tally port is 9000"
            />
            <TextField
              label="Company Name"
              value={tallyConfig.company_name}
              onChange={(e) => setTallyConfig({ ...tallyConfig, company_name: e.target.value })}
              fullWidth
              helperText="Exact company name as configured in Tally"
            />
            <FormControl fullWidth>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Sync Frequency
              </Typography>
              <Button
                variant={tallyConfig.sync_frequency === "manual" ? "contained" : "outlined"}
                onClick={() => setTallyConfig({ ...tallyConfig, sync_frequency: "manual" })}
                fullWidth
              >
                Manual
              </Button>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTallyDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={testTallyConnection}
            disabled={tallyTesting}
            variant="outlined"
          >
            {tallyTesting ? "Testing..." : "Test Connection"}
          </Button>
          <Button onClick={saveTallyConfig} disabled={saving} variant="contained">
            {saving ? "Saving..." : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default OrganizationSettings;