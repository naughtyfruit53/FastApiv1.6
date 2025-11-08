// pages/analytics/service/technician-performance.tsx
// Technician Performance Analytics

import React from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Alert,
  Card,
  CardContent,
} from "@mui/material";
import { Engineering } from "@mui/icons-material";
import { useAuth } from "../../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import TechnicianPerformanceChart from "../../../components/ServiceAnalytics/TechnicianPerformanceChart";
import { ProtectedPage } from '../../../components/ProtectedPage';
import {
  rbacService,
  SERVICE_PERMISSIONS,
} from "../../../services/rbacService";

const TechnicianPerformanceAnalyticsPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ["userServicePermissions"],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasPermission = userPermissions.includes(
    SERVICE_PERMISSIONS.SERVICE_REPORTS_READ,
  );

  if (!user || !hasPermission) {
    return (
      <ProtectedPage moduleKey="service" action="read">
      ontainer maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: Service Reports Read permission required.
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
          <Engineering color="primary" />
          Technician Performance Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor and analyze technician performance metrics, efficiency, and
          productivity across your service team.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <TechnicianPerformanceChart />
        </CardContent>
      </Card>
    </Container>
    </ProtectedPage>
  );
};
export default TechnicianPerformanceAnalyticsPage;
