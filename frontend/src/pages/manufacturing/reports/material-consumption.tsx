import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { BarChart, Inventory, TrendingDown } from '@mui/icons-material';

const MaterialConsumptionPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Material Consumption Report
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Track and analyze material usage in manufacturing processes.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Material Consumption Report helps you monitor material usage patterns,
          identify waste, and optimize inventory planning for production.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <BarChart color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Consumption Analysis
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Detailed analysis of material consumption by product, process, or time period.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Inventory color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    BOM Variance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Compare actual material consumption against Bill of Materials standards.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingDown color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Waste Analysis
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Identify and track material waste to improve efficiency.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default MaterialConsumptionPage;
