import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { Assessment, TrendingUp, Build } from '@mui/icons-material';

const ProductionSummaryPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Production Summary
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Overview of production activities and performance metrics.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Production Summary provides a comprehensive view of your manufacturing
          operations, including production volumes, efficiency, and capacity utilization.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Assessment color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Production Volume
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track production quantities across different products and time periods.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Efficiency Metrics
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor production efficiency and compare against targets.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Build color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Capacity Utilization
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Analyze equipment and labor capacity utilization rates.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ProductionSummaryPage;
