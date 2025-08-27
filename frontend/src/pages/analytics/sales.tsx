// pages/analytics/sales.tsx
// Sales Analytics page

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Alert,
} from '@mui/material';
import { BarChart, TrendingUp, Assessment, ShoppingCart } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';

const SalesAnalyticsPage: NextPage = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Please log in to access sales analytics.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <BarChart color="primary" />
          Sales Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze sales performance, trends, and key metrics to optimize your sales strategy.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUp color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Sales Trends</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Track sales performance over time
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Assessment color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Performance Metrics</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Key sales performance indicators
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <ShoppingCart color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Product Analysis</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Best performing products and categories
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
              Sales Analytics Dashboard
            </Typography>
            <Alert severity="info">
              This is a placeholder for the Sales Analytics Dashboard. The actual implementation would include:
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                <li>Sales performance charts and graphs</li>
                <li>Revenue trends and forecasting</li>
                <li>Product-wise sales analysis</li>
                <li>Customer segment analysis</li>
                <li>Sales team performance metrics</li>
                <li>Comparative analysis tools</li>
              </ul>
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SalesAnalyticsPage;