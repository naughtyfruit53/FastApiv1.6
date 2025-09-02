// pages/analytics/service.tsx
// Service Analytics Dashboard - Comprehensive service analytics suite

import React from "react";
import { NextPage } from "next";
import { Box, Container, Typography, Alert } from "@mui/material";
import { Analytics } from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import ServiceAnalyticsDashboard from "../../components/ServiceAnalytics/ServiceAnalyticsDashboard";
import { rbacService, SERVICE_PERMISSIONS } from "../../services/rbacService";

const ServiceAnalyticsPage: NextPage = () => {
  const { user } = useAuth();

  // Check if user has service analytics permissions
  const { data: userPermissions = [] } = useQuery({
    queryKey: ["userServicePermissions"],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const hasServiceReportsPermission = userPermissions.includes(
    SERVICE_PERMISSIONS.SERVICE_REPORTS_READ,
  );

  if (!user || !hasServiceReportsPermission) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view service
          analytics. Contact your administrator to request the &quot;Service
          Reports Read&quot; permission.
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
          <Analytics color="primary" />
          Service Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive service analytics including job completion, technician
          performance, customer satisfaction, and SLA compliance metrics.
        </Typography>
      </Box>

      <ServiceAnalyticsDashboard />
    </Container>
  );
};

export default ServiceAnalyticsPage;
