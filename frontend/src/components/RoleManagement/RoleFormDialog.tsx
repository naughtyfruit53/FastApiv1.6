'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Typography,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormGroup,
  Alert
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import {
  ServiceRole,
  ServiceRoleWithPermissions,
  ServicePermission,
  ServiceRoleCreate,
  ServiceRoleUpdate,
  ServiceRoleType,
  SERVICE_ROLE_DEFAULTS,
  MODULE_DISPLAY_NAMES,
  ServiceModule
} from '../../types/rbac.types';

interface RoleFormDialogProps {
  open: boolean;
  onClose: () => void;
  role?: ServiceRoleWithPermissions | null;
  permissions: ServicePermission[];
  organizationId: number;
  onSubmit: (data: ServiceRoleCreate | ServiceRoleUpdate) => void;
}

const RoleFormDialog: React.FC<RoleFormDialogProps> = ({
  open,
  onClose,
  role,
  permissions,
  organizationId,
  onSubmit
}) => {
  const [formData, setFormData] = useState({
    name: ServiceRoleType.VIEWER,
    display_name: '',
    description: '',
    is_active: true,
    permission_ids: [] as number[]
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [expandedModule, setExpandedModule] = useState<string | false>(false);

  useEffect(() => {
    if (role) {
      // Editing existing role
      setFormData({
        name: role.name,
        display_name: role.display_name,
        description: role.description || '',
        is_active: role.is_active,
        permission_ids: role.permissions.map(p => p.id)
      });
    } else {
      // Creating new role - use defaults
      setFormData({
        name: ServiceRoleType.VIEWER,
        display_name: SERVICE_ROLE_DEFAULTS[ServiceRoleType.VIEWER].display_name || '',
        description: SERVICE_ROLE_DEFAULTS[ServiceRoleType.VIEWER].description || '',
        is_active: true,
        permission_ids: []
      });
    }
    setErrors({});
  }, [role, open]);

  const handleRoleTypeChange = (roleType: ServiceRoleType) => {
    const defaults = SERVICE_ROLE_DEFAULTS[roleType];
    setFormData(prev => ({
      ...prev,
      name: roleType,
      display_name: defaults.display_name || '',
      description: defaults.description || ''
    }));
  };

  const handlePermissionToggle = (permissionId: number) => {
    setFormData(prev => ({
      ...prev,
      permission_ids: prev.permission_ids.includes(permissionId)
        ? prev.permission_ids.filter(id => id !== permissionId)
        : [...prev.permission_ids, permissionId]
    }));
  };

  const handleModuleToggle = (module: ServiceModule) => {
    const modulePermissions = permissions
      .filter(p => p.module === module)
      .map(p => p.id);
    
    const allSelected = modulePermissions.every(id => 
      formData.permission_ids.includes(id)
    );
    
    if (allSelected) {
      // Deselect all module permissions
      setFormData(prev => ({
        ...prev,
        permission_ids: prev.permission_ids.filter(id => 
          !modulePermissions.includes(id)
        )
      }));
    } else {
      // Select all module permissions
      setFormData(prev => ({
        ...prev,
        permission_ids: [
          ...prev.permission_ids.filter(id => !modulePermissions.includes(id)),
          ...modulePermissions
        ]
      }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.display_name.trim()) {
      newErrors.display_name = 'Display name is required';
    }
    
    if (formData.permission_ids.length === 0) {
      newErrors.permissions = 'At least one permission must be selected';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;
    
    if (role) {
      // Updating existing role
      const updateData: ServiceRoleUpdate = {
        display_name: formData.display_name,
        description: formData.description || undefined,
        is_active: formData.is_active,
        permission_ids: formData.permission_ids
      };
      onSubmit(updateData);
    } else {
      // Creating new role
      const createData: ServiceRoleCreate = {
        name: formData.name,
        display_name: formData.display_name,
        description: formData.description || undefined,
        organization_id: organizationId,
        is_active: formData.is_active,
        permission_ids: formData.permission_ids
      };
      onSubmit(createData);
    }
  };

  // Group permissions by module
  const permissionsByModule = permissions.reduce((acc, permission) => {
    if (!acc[permission.module]) {
      acc[permission.module] = [];
    }
    acc[permission.module].push(permission);
    return acc;
  }, {} as Record<string, ServicePermission[]>);

  const getModuleSelectionStatus = (module: ServiceModule) => {
    const modulePermissions = permissionsByModule[module] || [];
    const selectedCount = modulePermissions.filter(p => 
      formData.permission_ids.includes(p.id)
    ).length;
    
    if (selectedCount === 0) return 'none';
    if (selectedCount === modulePermissions.length) return 'all';
    return 'partial';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {role ? 'Edit Service Role' : 'Create Service Role'}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
          {/* Basic Information */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Basic Information
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl fullWidth disabled={!!role}>
                <InputLabel>Role Type</InputLabel>
                <Select
                  value={formData.name}
                  onChange={(e) => handleRoleTypeChange(e.target.value as ServiceRoleType)}
                  label="Role Type"
                >
                  {Object.values(ServiceRoleType).map(roleType => (
                    <MenuItem key={roleType} value={roleType}>
                      {roleType.charAt(0).toUpperCase() + roleType.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => setFormData(prev => ({ ...prev, display_name: e.target.value }))}
                error={!!errors.display_name}
                helperText={errors.display_name}
                required
              />
              
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                multiline
                rows={2}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                  />
                }
                label="Active"
              />
            </Box>
          </Box>
          
          {/* Permissions */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Permissions ({formData.permission_ids.length} selected)
            </Typography>
            
            {errors.permissions && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errors.permissions}
              </Alert>
            )}
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Select permissions for this role. Permissions are organized by module.
              </Typography>
            </Box>
            
            {Object.entries(permissionsByModule).map(([module, modulePermissions]) => {
              const selectionStatus = getModuleSelectionStatus(module as ServiceModule);
              
              return (
                <Accordion
                  key={module}
                  expanded={expandedModule === module}
                  onChange={(_, isExpanded) => setExpandedModule(isExpanded ? module : false)}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={selectionStatus === 'all'}
                            indeterminate={selectionStatus === 'partial'}
                            onChange={() => handleModuleToggle(module as ServiceModule)}
                            onClick={(e) => e.stopPropagation()}
                          />
                        }
                        label=""
                        sx={{ mr: 0 }}
                      />
                      <Typography sx={{ flexGrow: 1 }}>
                        {MODULE_DISPLAY_NAMES[module as ServiceModule] || module}
                      </Typography>
                      <Chip
                        label={`${modulePermissions.filter(p => formData.permission_ids.includes(p.id)).length}/${modulePermissions.length}`}
                        size="small"
                        color={selectionStatus === 'all' ? 'primary' : selectionStatus === 'partial' ? 'warning' : 'default'}
                      />
                    </Box>
                  </AccordionSummary>
                  
                  <AccordionDetails>
                    <FormGroup>
                      {modulePermissions.map((permission) => (
                        <FormControlLabel
                          key={permission.id}
                          control={
                            <Checkbox
                              checked={formData.permission_ids.includes(permission.id)}
                              onChange={() => handlePermissionToggle(permission.id)}
                            />
                          }
                          label={
                            <Box>
                              <Typography variant="body2">
                                {permission.display_name}
                              </Typography>
                              {permission.description && (
                                <Typography variant="caption" color="text.secondary">
                                  {permission.description}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      ))}
                    </FormGroup>
                  </AccordionDetails>
                </Accordion>
              );
            })}
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained">
          {role ? 'Update Role' : 'Create Role'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RoleFormDialog;