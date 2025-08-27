'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Alert,
  CircularProgress,
  Box,
  Chip,
  TextField,
  Grid
} from '@mui/material';
import { Add, Email, Person } from '@mui/icons-material';
import { organizationService } from '../services/organizationService';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  username: string;
}

interface OrganizationMembersDialogProps {
  open: boolean;
  onClose: () => void;
  organizationId: number;
  organizationName: string;
  canInvite?: boolean;
}

const OrganizationMembersDialog: React.FC<OrganizationMembersDialogProps> = ({
  open,
  onClose,
  organizationId,
  organizationName,
  canInvite = false
}) => {
  const [members, setMembers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteData, setInviteData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    role: 'standard_user'
  });
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    if (open && organizationId) {
      fetchMembers();
    }
  }, [open, organizationId]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      const membersData = await organizationService.getOrganizationMembers(organizationId);
      setMembers(membersData);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteSubmit = async () => {
    try {
      setInviting(true);
      setError(null);
      
      await organizationService.inviteUserToOrganization(organizationId, inviteData);
      
      // Reset form and refresh members
      setInviteData({
        email: '',
        username: '',
        full_name: '',
        password: '',
        role: 'standard_user'
      });
      setShowInviteForm(false);
      await fetchMembers();
      
    } catch (error: any) {
      setError(error.message);
    } finally {
      setInviting(false);
    }
  };

  const getRoleColor = (role: string): 'error' | 'warning' | 'info' | 'default' => {
    switch (role) {
      case 'super_admin':
        return 'error';
      case 'org_admin':
        return 'warning';
      case 'admin':
        return 'info';
      default:
        return 'default';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'Super Admin';
      case 'org_admin':
        return 'Org Admin';
      case 'admin':
        return 'Admin';
      case 'standard_user':
        return 'User';
      default:
        return role;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {organizationName} - Members
          </Typography>
          {canInvite && (
            <Button
              startIcon={<Add />}
              variant="outlined"
              size="small"
              onClick={() => setShowInviteForm(!showInviteForm)}
            >
              Invite User
            </Button>
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {showInviteForm && (
          <Box sx={{ mb: 3, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Invite New User
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={inviteData.email}
                  onChange={(e) => setInviteData(prev => ({ ...prev, email: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Username"
                  value={inviteData.username}
                  onChange={(e) => setInviteData(prev => ({ ...prev, username: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={inviteData.full_name}
                  onChange={(e) => setInviteData(prev => ({ ...prev, full_name: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Temporary Password"
                  type="password"
                  value={inviteData.password}
                  onChange={(e) => setInviteData(prev => ({ ...prev, password: e.target.value }))}
                  required
                />
              </Grid>
              <Grid size={12}>
                <Box display="flex" gap={1} justifyContent="flex-end">
                  <Button
                    onClick={() => setShowInviteForm(false)}
                    disabled={inviting}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleInviteSubmit}
                    disabled={inviting || !inviteData.email || !inviteData.username || !inviteData.password}
                  >
                    {inviting ? <CircularProgress size={20} /> : 'Send Invitation'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <List>
            {members.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="No members found"
                  secondary="This organization has no active members"
                />
              </ListItem>
            ) : (
              members.map((member) => (
                <ListItem key={member.id} divider>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Person fontSize="small" color="action" />
                        <Typography variant="body1">
                          {member.full_name}
                        </Typography>
                        <Chip
                          label={getRoleLabel(member.role)}
                          size="small"
                          color={getRoleColor(member.role)}
                          variant="outlined"
                        />
                        {!member.is_active && (
                          <Chip label="Inactive" size="small" color="default" />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          <Email fontSize="small" sx={{ mr: 0.5, verticalAlign: 'text-bottom' }} />
                          {member.email}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Username: {member.username}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))
            )}
          </List>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default OrganizationMembersDialog;