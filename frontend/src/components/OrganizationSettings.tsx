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
} from "@mui/material";
import { ExpandMore, Email, Security, Settings } from "@mui/icons-material";
import { organizationService } from "../services/organizationService";
import { useAuth } from "../context/AuthContext";

interface OrganizationSettingsData {
  id?: number;
  organization_id: number;
  mail_1_level_up_enabled: boolean;
  auto_send_notifications: boolean;
  custom_settings?: any;
  created_at?: string;
  updated_at?: string;
}

const OrganizationSettings: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<OrganizationSettingsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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
    </Paper>
  );
};

export default OrganizationSettings;