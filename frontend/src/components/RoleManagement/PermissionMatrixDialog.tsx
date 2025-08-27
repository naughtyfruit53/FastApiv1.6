'use client';

import React, { useState, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import {
  ServiceRole,
  ServiceRoleWithPermissions,
  ServicePermission,
  ServiceModule,
  MODULE_DISPLAY_NAMES,
  ROLE_BADGE_COLORS
} from '../../types/rbac.types';

interface PermissionMatrixDialogProps {
  open: boolean;
  onClose: () => void;
  roles: ServiceRoleWithPermissions[];
  permissions: ServicePermission[];
}

const PermissionMatrixDialog: React.FC<PermissionMatrixDialogProps> = ({
  open,
  onClose,
  roles,
  permissions
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModule, setSelectedModule] = useState<ServiceModule | 'all'>('all');
  const [showMatrixView, setShowMatrixView] = useState(true);
  const [expandedRole, setExpandedRole] = useState<string | false>(false);

  // Group permissions by module
  const permissionsByModule = useMemo(() => {
    return permissions.reduce((acc, permission) => {
      if (!acc[permission.module]) {
        acc[permission.module] = [];
      }
      acc[permission.module].push(permission);
      return acc;
    }, {} as Record<string, ServicePermission[]>);
  }, [permissions]);

  // Filter permissions based on search and module selection
  const filteredPermissions = useMemo(() => {
    let filtered = permissions;
    
    if (selectedModule !== 'all') {
      filtered = filtered.filter(p => p.module === selectedModule);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(p => 
        p.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  }, [permissions, selectedModule, searchTerm]);

  // Check if a role has a specific permission
  const roleHasPermission = (role: ServiceRoleWithPermissions, permissionId: number) => {
    return role.permissions.some(p => p.id === permissionId);
  };

  // Get permission statistics for a role
  const getRoleStats = (role: ServiceRoleWithPermissions) => {
    const total = permissions.length;
    const granted = role.permissions.length;
    const percentage = total > 0 ? Math.round((granted / total) * 100) : 0;
    
    return { total, granted, percentage };
  };

  // Get module statistics for a role
  const getModuleStats = (role: ServiceRoleWithPermissions, module: ServiceModule) => {
    const modulePermissions = permissionsByModule[module] || [];
    const grantedInModule = role.permissions.filter(p => p.module === module).length;
    const totalInModule = modulePermissions.length;
    
    return {
      granted: grantedInModule,
      total: totalInModule,
      percentage: totalInModule > 0 ? Math.round((grantedInModule / totalInModule) * 100) : 0
    };
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SecurityIcon />
          <Typography variant="h6">Permission Matrix</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
          {/* Filters and Controls */}
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <TextField
              size="small"
              placeholder="Search permissions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 250 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Filter by Module</InputLabel>
              <Select
                value={selectedModule}
                onChange={(e) => setSelectedModule(e.target.value as ServiceModule | 'all')}
                label="Filter by Module"
              >
                <MenuItem value="all">All Modules</MenuItem>
                {Object.keys(permissionsByModule).map(module => (
                  <MenuItem key={module} value={module}>
                    {MODULE_DISPLAY_NAMES[module as ServiceModule] || module}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControlLabel
              control={
                <Switch
                  checked={showMatrixView}
                  onChange={(e) => setShowMatrixView(e.target.checked)}
                />
              }
              label="Matrix View"
            />
          </Box>
          
          {showMatrixView ? (
            /* Matrix View */
            <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ minWidth: 250, position: 'sticky', left: 0, bgcolor: 'background.paper', zIndex: 1 }}>
                      Permission
                    </TableCell>
                    {roles.map((role) => (
                      <TableCell key={role.id} align="center" sx={{ minWidth: 120 }}>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={role.name}
                            size="small"
                            color={ROLE_BADGE_COLORS[role.name] as any}
                          />
                          <Typography variant="caption">
                            {getRoleStats(role).granted}/{getRoleStats(role).total}
                          </Typography>
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredPermissions.map((permission) => (
                    <TableRow key={permission.id} hover>
                      <TableCell sx={{ position: 'sticky', left: 0, bgcolor: 'background.paper', zIndex: 1 }}>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {permission.display_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {MODULE_DISPLAY_NAMES[permission.module]} • {permission.action}
                          </Typography>
                          {permission.description && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                              {permission.description}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      {roles.map((role) => (
                        <TableCell key={role.id} align="center">
                          <Checkbox
                            checked={roleHasPermission(role, permission.id)}
                            disabled
                            size="small"
                          />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            /* Role-based View */
            <Box>
              {roles.map((role) => {
                const stats = getRoleStats(role);
                
                return (
                  <Accordion
                    key={role.id}
                    expanded={expandedRole === role.id.toString()}
                    onChange={(_, isExpanded) => setExpandedRole(isExpanded ? role.id.toString() : false)}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                        <Chip
                          label={role.name}
                          color={ROLE_BADGE_COLORS[role.name] as any}
                          size="small"
                        />
                        <Typography sx={{ flexGrow: 1 }}>
                          {role.display_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {stats.granted}/{stats.total} permissions ({stats.percentage}%)
                        </Typography>
                      </Box>
                    </AccordionSummary>
                    
                    <AccordionDetails>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {/* Module breakdown */}
                        <Box>
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>
                            Permissions by Module
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {Object.keys(permissionsByModule).map(module => {
                              const moduleStats = getModuleStats(role, module as ServiceModule);
                              return (
                                <Chip
                                  key={module}
                                  label={`${MODULE_DISPLAY_NAMES[module as ServiceModule]}: ${moduleStats.granted}/${moduleStats.total}`}
                                  size="small"
                                  variant="outlined"
                                  color={moduleStats.percentage === 100 ? 'primary' : moduleStats.percentage > 0 ? 'warning' : 'default'}
                                />
                              );
                            })}
                          </Box>
                        </Box>
                        
                        {/* Detailed permissions */}
                        <Box>
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>
                            Granted Permissions
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {role.permissions
                              .filter(p => selectedModule === 'all' || p.module === selectedModule)
                              .filter(p => !searchTerm || 
                                p.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                p.name.toLowerCase().includes(searchTerm.toLowerCase())
                              )
                              .map(permission => (
                                <Chip
                                  key={permission.id}
                                  label={permission.display_name}
                                  size="small"
                                  variant="outlined"
                                />
                              ))}
                          </Box>
                        </Box>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                );
              })}
            </Box>
          )}
          
          {filteredPermissions.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No permissions found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your search criteria.
              </Typography>
            </Box>
          )}
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

export default PermissionMatrixDialog;