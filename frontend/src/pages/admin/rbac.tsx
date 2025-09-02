// pages/admin/rbac.tsx
// RBAC Management page

import React from "react";
import { NextPage } from "next";
import { Box, Container, Typography, Alert } from "@mui/material";
import { SupervisorAccount } from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import RoleManagement from "../../components/RoleManagement/RoleManagement";
import { rbacService, SERVICE_PERMISSIONS } from "../../services/rbacService";
import { isOrgSuperAdmin } from "../../types/user.types";

const RBACManagementPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ["userServicePermissions"],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasCRMAdminPermission = userPermissions.includes(
    SERVICE_PERMISSIONS.CRM_ADMIN,
  );
  const canAccessRBAC = hasCRMAdminPermission || isOrgSuperAdmin(user);

  if (!user || !canAccessRBAC) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to manage service roles
          and permissions. Contact your administrator to request CRM Admin
          permissions.
        </Alert>
      </Container>
    );
  }

  // Get organization ID for role management
  const organizationId = user?.organization_id;

  if (!organizationId) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Error: Unable to determine organization context. Please contact
          support.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <SupervisorAccount color="primary" />
          Service Role Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage service CRM roles, permissions, and user assignments for your
          organization.
        </Typography>
      </Box>

      <RoleManagement organizationId={organizationId} />
    </Container>
  );
};

export default RBACManagementPage;
