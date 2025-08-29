// frontend/src/pages/settings/UserPreferences.tsx

import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  FormControlLabel,
  Switch,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import {
  StickyNote2,
  PersonOutline
} from '@mui/icons-material';
import useStickyNotes from '../../hooks/useStickyNotes';

const UserPreferences: React.FC = () => {
  const { userSettings, toggleStickyNotes, refreshSettings } = useStickyNotes();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleStickyNotesToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const enabled = event.target.checked;
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await toggleStickyNotes(enabled);
      setSuccess(enabled ? 'Sticky notes enabled' : 'Sticky notes disabled');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Error updating sticky notes setting:', err);
      setError('Failed to update sticky notes setting');
      
      // Refresh settings to ensure UI is in sync
      await refreshSettings();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <PersonOutline sx={{ mr: 1 }} />
        User Preferences
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Customize your dashboard experience and personal settings.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Dashboard Settings */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
          Dashboard Settings
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={userSettings.sticky_notes_enabled}
              onChange={handleStickyNotesToggle}
              disabled={loading}
              color="primary"
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <StickyNote2 sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  Enable Sticky Notes
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Show sticky notes panel on your dashboard
                </Typography>
              </Box>
            </Box>
          }
          sx={{ 
            alignItems: 'flex-start',
            ml: 0,
            '& .MuiFormControlLabel-label': {
              ml: 1
            }
          }}
        />
        
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, ml: 4 }}>
            <CircularProgress size={16} sx={{ mr: 1 }} />
            <Typography variant="caption" color="text.secondary">
              Updating preferences...
            </Typography>
          </Box>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Future preferences can be added here */}
      <Box>
        <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
          More customization options will be available in future updates.
        </Typography>
      </Box>
    </Paper>
  );
};

export default UserPreferences;