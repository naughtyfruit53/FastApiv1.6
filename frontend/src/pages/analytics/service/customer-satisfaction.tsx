// pages/analytics/service/customer-satisfaction.tsx
// Customer Satisfaction Analytics

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
import { Feedback } from "@mui/icons-material";
import { useAuth } from "../../../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import CustomerSatisfactionChart from "../../../components/ServiceAnalytics/CustomerSatisfactionChart";
import { ProtectedPage } from '../../../components/ProtectedPage';
import {
  rbacService,
  SERVICE_PERMISSIONS,
} from "../../../services/rbacService";

const CustomerSatisfactionAnalyticsPage: NextPage = () => {
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
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Alert severity="error">
            Access Denied: Service Reports Read permission required.
          </Alert>
        </Container>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage moduleKey="service" action="read">
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{ display: "flex", alignItems: "center", gap: 2 }}
          >
            <Feedback color="primary" />
            Customer Satisfaction Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Analyze customer satisfaction scores, feedback trends, and service
            quality metrics to improve customer experience.
          </Typography>
        </Box>

        <Card>
          <CardContent>
            <CustomerSatisfactionChart />
          </CardContent>
        </Card>
      </Container>
    </ProtectedPage>
  );
};
export default CustomerSatisfactionAnalyticsPage;
