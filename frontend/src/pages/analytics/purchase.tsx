// frontend/src/pages/analytics/purchase.tsx
// Purchase Analytics page

import React from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Alert,
} from "@mui/material";
import {
  ShoppingCart,
  TrendingDown,
  Assessment,
  LocalShipping,
} from "@mui/icons-material";
import { useAuth } from "../../context/AuthContext";
import { ProtectedPage } from "../../components/ProtectedPage";

const PurchaseAnalyticsPage: NextPage = () => {
  const { user } = useAuth();

  return (
    <ProtectedPage moduleKey="analytics" action="read">
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <ShoppingCart color="primary" />
          Purchase Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor and analyze procurement activities, vendor performance, and
          cost optimization opportunities.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <TrendingDown color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Cost Trends</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Track procurement costs over time
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
                  <Typography variant="h6">Vendor Performance</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supplier reliability and quality metrics
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
                <LocalShipping color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Procurement Efficiency</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Order fulfillment and delivery metrics
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Purchase Analytics Dashboard
            </Typography>
            <Alert severity="info">
              This is a placeholder for the Purchase Analytics Dashboard. The
              actual implementation would include:
              <ul style={{ marginTop: "8px", marginBottom: 0 }}>
                <li>Purchase volume and cost analysis</li>
                <li>Vendor performance scorecards</li>
                <li>Category-wise spending analysis</li>
                <li>Cost savings and optimization opportunities</li>
                <li>Purchase order cycle time metrics</li>
                <li>Budget vs. actual spending comparisons</li>
              </ul>
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
    </ProtectedPage>
  );
};

export default PurchaseAnalyticsPage;
