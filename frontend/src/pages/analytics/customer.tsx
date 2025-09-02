// pages/analytics/customer.tsx
// Customer Analytics page - Business intelligence and customer insights
import React from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
} from "@mui/material";
import { Analytics, TrendingUp, People, Assessment } from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import CustomerAnalytics from "../../components/CustomerAnalytics";
import { canManageUsers } from "../../types/user.types";
const CustomerAnalyticsPage: NextPage = () => {
  const { user } = useAuth();
  if (!user || !canManageUsers(user)) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view customer
          analytics.
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
          Customer Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Business intelligence and customer insights to help you understand
          your customer base and improve business decisions.
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <People color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Customer Insights</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Analyze customer behavior patterns
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <TrendingUp color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Purchase Trends</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Track purchasing patterns over time
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Assessment color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Performance Metrics</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Key performance indicators
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        {/* Main Analytics Component */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <CustomerAnalytics />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};
export default CustomerAnalyticsPage;
