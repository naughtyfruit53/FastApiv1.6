'use client';

import React from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Grid,
  Button
} from '@mui/material';
import { MonetizationOn, TrendingUp, People, Assessment } from '@mui/icons-material';

const SalesDashboard: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sales CRM Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage your sales pipeline, leads, and customer relationships
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <MonetizationOn color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Revenue</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  $0
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This month
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUp color="success.main" sx={{ mr: 1 }} />
                  <Typography variant="h6">Opportunities</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  0
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active opportunities
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <People color="info.main" sx={{ mr: 1 }} />
                  <Typography variant="h6">Leads</Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  0
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  New leads
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Assessment color="warning.main" sx={{ mr: 1 }} />
                  <Typography variant="h6">Conversion</Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  0%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Lead to customer
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales CRM Module
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                This module is currently under development. Contact your administrator to enable full functionality.
              </Typography>
              <Button variant="outlined" disabled>
                Configure Sales CRM
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  );
};

export default SalesDashboard;