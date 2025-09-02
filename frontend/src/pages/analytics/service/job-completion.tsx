// pages/analytics/service/job-completion.tsx
// Job Completion Analytics

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
import { Assignment } from "@mui/icons-material";
import { useAuth } from "../../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import JobCompletionChart from "../../../components/ServiceAnalytics/JobCompletionChart";
import {
  rbacService,
  SERVICE_PERMISSIONS,
} from "../../../services/rbacService";

const JobCompletionAnalyticsPage: NextPage = () => {
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
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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
          <Assignment color="primary" />
          Job Completion Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track job completion rates, trends, and performance metrics across
          your service operations.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <JobCompletionChart />
        </CardContent>
      </Card>
    </Container>
  );
};

export default JobCompletionAnalyticsPage;
