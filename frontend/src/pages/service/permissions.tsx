// frontend/src/pages/service/permissions.tsx
"use client";
import React from "react";
import {
  Container,
  Typography,
  Paper,
  Alert,
} from "@mui/material";
import { Security } from "@mui/icons-material";
import DashboardLayout from "../../components/DashboardLayout";
import { useAuth } from "../../context/AuthContext";
import RoleManagement from "../../components/RoleManagement/RoleManagement";

export default function ServicePermissions() {
  const { user } = useAuth();

  // Debug logging
  console.log("ServicePermissions.tsx - Current user:", JSON.stringify(user, null, 2));
  console.log("ServicePermissions.tsx - User role:", user?.role);

  // Restrict to org_admin
  if (user?.role !== "org_admin") {
    return (
      <DashboardLayout
        title="Service Permissions"
        subtitle="Manage permissions for Service CRM"
      >
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography color="error">
              Only organization administrators can manage Service CRM permissions.
            </Typography>
          </Paper>
        </Container>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Service Permissions"
      subtitle="Manage permissions for Service CRM"
    >
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <Security sx={{ mr: 2 }} />
          Service Permissions
        </Typography>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="body1">
            <strong>Current Role:</strong> {user?.role}
          </Typography>
        </Paper>
        <RoleManagement />
      </Container>
    </DashboardLayout>
  );
}