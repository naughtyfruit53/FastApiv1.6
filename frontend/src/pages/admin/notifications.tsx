// pages/admin/notifications.tsx
// Notification Management page

import React from "react";
import { NextPage } from "next";
import { Box, Container, Typography, Alert } from "@mui/material";
import { NotificationsActive } from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import NotificationTemplates from "../../components/NotificationTemplates";
import { canManageUsers } from "../../types/user.types";

const NotificationManagementPage: NextPage = () => {
  const { user } = useAuth();

  const canManageNotifications = canManageUsers(user);

  if (!user || !canManageNotifications) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to manage notifications.
          Contact your administrator for access.
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
          <NotificationsActive color="primary" />
          Notification Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage notification templates, configure notification settings, and
          send notifications to users.
        </Typography>
      </Box>

      <NotificationTemplates />
    </Container>
  );
};

export default NotificationManagementPage;
