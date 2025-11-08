// frontend/src/pages/admin/rbac.tsx
// RBAC Management page

import React, { useState } from "react";
import { NextPage } from "next";
import { Box, Container, Typography, Alert, FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import { SupervisorAccount } from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import RoleManagement from "../../components/RoleManagement/RoleManagement";
import { rbacService, PERMISSIONS } from "../../services/rbacService";
import { isOrgSuperAdmin, isAppSuperAdmin } from "../../types/user.types";
import { organizationService } from "../../services/organizationService";

import { ProtectedPage } from '@/components/ProtectedPage';
const RBACManagementPage: NextPage = () => {
  const { user } = useAuth();
  const [selectedOrgId, setSelectedOrgId] = useState<number | null>(null);

  // Move all hooks to the top
  const { data: userPermissions = [] } = useQuery({
    queryKey: ["userPermissions"],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const { data: organizations = [] } = useQuery({
    queryKey: ["organizations"],
    queryFn: organizationService.getAllOrganizations,
    enabled: !!user && isAppSuperAdmin(user),
  });

  const hasAdminPermission = userPermissions.includes(
    PERMISSIONS.ADMIN,
  );
  const canAccessRBAC = hasAdminPermission || isOrgSuperAdmin(user) || isAppSuperAdmin(user);

  if (!user || !canAccessRBAC) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to manage roles
          and permissions. Contact your administrator to request Admin
          permissions.
        </Alert>
      </Container>
    );
  }

  // Get organization ID for role management
  const organizationId = user?.organization_id || selectedOrgId;

  if (!organizationId) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Error: Unable to determine organization context. Please select an organization or contact support.
        </Alert>
      </Container>
    );
  }

  return (


    <ProtectedPage moduleKey="admin" action="read">
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <SupervisorAccount color="primary" />
          Role Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage roles, permissions across all modules, and user assignments for your
          organization.
        </Typography>
      </Box>

      {!!user && isAppSuperAdmin(user) && (
        <Box sx={{ mb: 4 }}>
          <FormControl fullWidth>
            <InputLabel>Select Organization</InputLabel>
            <Select
              value={selectedOrgId || ''}
              onChange={(e) => setSelectedOrgId(Number(e.target.value))}
            >
              {organizations.map((org: any) => (
                <MenuItem key={org.id} value={org.id}>
                  {org.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}

      <RoleManagement organizationId={organizationId} />
    </Container>


    </ProtectedPage>


  
  );
};

export default RBACManagementPage;