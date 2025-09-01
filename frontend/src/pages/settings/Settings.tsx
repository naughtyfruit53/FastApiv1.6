// Revised: v1/frontend/src/pages/settings/Settings.tsx
import React from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Divider
} from '@mui/material';
import {
  Person,
  PersonAdd,
  Settings as SettingsIcon,
  Security,
  Integration,
  CloudUpload,
  Timeline,
  StickyNote2
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import FactoryReset from './FactoryReset';
import { useAuth } from '../../context/AuthContext';
import { getDisplayRole, canAccessAdvancedSettings, isOrgSuperAdmin, canManageUsers } from '../../types/user.types';
import Grid from '@mui/material/Grid';
import UserPreferences from './UserPreferences';
const Settings: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const displayRole = getDisplayRole(user?.role || 'unknown', user?.is_super_admin);
  const isAuthorized = canAccessAdvancedSettings(user);
  const isOrgAdmin = isOrgSuperAdmin(user);
  const canManage = canManageUsers(user);
  console.log('Current user in Settings:', JSON.stringify(user, null, 2));
  console.log('Display Role:', displayRole);
  console.log('Is Authorized:', isAuthorized);
  console.log('Is Org Admin:', isOrgAdmin);
  console.log('Can Manage Users:', canManage);
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <SettingsIcon sx={{ mr: 2 }} />
        Settings
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Account Information</Typography>
        <Typography variant="body2" color="text.secondary">
          Current Role: <strong>{displayRole}</strong>
        </Typography>
      </Paper>
      <Grid container spacing={3}>
        {/* User Preferences - Available to all users */}
        <Grid size={{ xs: 12, md: isOrgAdmin && canManage ? 4 : (isOrgAdmin ? 6 : 12) }}>
          <UserPreferences />
        </Grid>
        {/* User Management - Only for Organization Super Admins */}
        {isOrgAdmin && canManage && (
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Person sx={{ mr: 1 }} />
                User Management
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Manage users within your organization. Add new users, edit existing ones, 
                and control their access permissions.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                <Button
                  variant="contained"
                  startIcon={<Person />}
                  onClick={() => router.push('/settings/user-management')}
                  fullWidth
                >
                  Manage Users
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<PersonAdd />}
                  onClick={() => router.push('/settings/add-user')}
                  fullWidth
                >
                  Add New User
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
        {/* Integration Management - For Super Admins */}
        {isOrgAdmin && (
          <Grid size={{ xs: 12, md: canManage ? 6 : 12 }}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Integration sx={{ mr: 1 }} />
                Integration Management
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Manage external integrations like Tally, Zoho, email services, and data migration.
                Configure connections and monitor integration health.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
                <Button
                  variant="contained"
                  startIcon={<Timeline />}
                  onClick={() => router.push('/migration/management')}
                  fullWidth
                >
                  Migration & Integrations
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CloudUpload />}
                  onClick={() => router.push('/migration/management')}
                  fullWidth
                >
                  Data Import Wizard
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
        {/* Advanced Settings - For authorized users */}
        {isAuthorized && (
          <Grid size={{ xs: 12, md: isOrgAdmin ? (canManage ? 4 : 6) : 12 }}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Security sx={{ mr: 1 }} />
                Advanced Options
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Advanced reset and recovery options. Use with caution as these actions 
                cannot be undone.
              </Typography>
              <FactoryReset />
            </Paper>
          </Grid>
        )}
        {/* Message for users without advanced access */}
        {!isAuthorized && !canManage && (
          <Grid size={{ xs: 12 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="body1" color="text.secondary">
                Advanced options and user management are not available for your role: <strong>{displayRole}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Contact your organization administrator if you need access to additional features.
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};
export default Settings;