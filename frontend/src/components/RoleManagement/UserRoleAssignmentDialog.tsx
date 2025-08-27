'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Checkbox,
  ListItemText,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText as MuiListItemText,
  Divider,
  Alert
} from '@mui/material';
import {
  Close as CloseIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import {
  ServiceRole,
  UserWithServiceRoles,
  ROLE_BADGE_COLORS
} from '../../types/rbac.types';

interface UserRoleAssignmentDialogProps {
  open: boolean;
  onClose: () => void;
  user: UserWithServiceRoles;
  availableRoles: ServiceRole[];
  onAssign: (userId: number, roleIds: number[]) => void;
  onRemove: (userId: number, roleId: number) => void;
}

const UserRoleAssignmentDialog: React.FC<UserRoleAssignmentDialogProps> = ({
  open,
  onClose,
  user,
  availableRoles,
  onAssign,
  onRemove
}) => {
  const [selectedRoleIds, setSelectedRoleIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSelectedRoleIds([]);
  }, [user, open]);

  const handleAssignRoles = async () => {
    if (selectedRoleIds.length === 0) return;
    
    setLoading(true);
    try {
      await onAssign(user.id, selectedRoleIds);
      setSelectedRoleIds([]);
    } catch (error) {
      console.error('Failed to assign roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveRole = async (roleId: number) => {
    setLoading(true);
    try {
      await onRemove(user.id, roleId);
    } catch (error) {
      console.error('Failed to remove role:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSelectionChange = (event: any) => {
    const value = event.target.value;
    setSelectedRoleIds(typeof value === 'string' ? value.split(',').map(Number) : value);
  };

  // Filter out roles that the user already has
  const assignableRoles = availableRoles.filter(role => 
    !user.service_roles.some(userRole => userRole.id === role.id)
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <PersonIcon />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6">
              Manage Service Roles
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user.full_name || user.email}
            </Typography>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Current Roles */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Current Service Roles
            </Typography>
            
            {user.service_roles.length === 0 ? (
              <Alert severity="info">
                This user has no service roles assigned.
              </Alert>
            ) : (
              <List dense>
                {user.service_roles.map((role) => (
                  <ListItem
                    key={role.id}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => handleRemoveRole(role.id)}
                        disabled={loading}
                        color="error"
                      >
                        <CloseIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      <Chip
                        label={role.name}
                        size="small"
                        color={ROLE_BADGE_COLORS[role.name] as any}
                      />
                    </ListItemIcon>
                    <MuiListItemText
                      primary={role.display_name}
                      secondary={role.description}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
          
          <Divider />
          
          {/* Assign New Roles */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Assign New Roles
            </Typography>
            
            {assignableRoles.length === 0 ? (
              <Alert severity="warning">
                No additional roles available for assignment.
              </Alert>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Select Roles to Assign</InputLabel>
                  <Select
                    multiple
                    value={selectedRoleIds}
                    onChange={handleRoleSelectionChange}
                    input={<OutlinedInput label="Select Roles to Assign" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(selected as number[]).map((roleId) => {
                          const role = assignableRoles.find(r => r.id === roleId);
                          return role ? (
                            <Chip
                              key={roleId}
                              label={role.display_name}
                              size="small"
                              color={ROLE_BADGE_COLORS[role.name] as any}
                            />
                          ) : null;
                        })}
                      </Box>
                    )}
                  >
                    {assignableRoles.map((role) => (
                      <MenuItem key={role.id} value={role.id}>
                        <Checkbox checked={selectedRoleIds.indexOf(role.id) > -1} />
                        <ListItemText
                          primary={role.display_name}
                          secondary={role.description}
                        />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <Button
                  variant="contained"
                  onClick={handleAssignRoles}
                  disabled={selectedRoleIds.length === 0 || loading}
                  fullWidth
                >
                  Assign Selected Roles ({selectedRoleIds.length})
                </Button>
              </Box>
            )}
          </Box>
          
          {/* User Info */}
          <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              User Information
            </Typography>
            <Typography variant="body2">
              <strong>Email:</strong> {user.email}
            </Typography>
            <Typography variant="body2">
              <strong>System Role:</strong> {user.role}
            </Typography>
            <Typography variant="body2">
              <strong>Status:</strong> {user.is_active ? 'Active' : 'Inactive'}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserRoleAssignmentDialog;