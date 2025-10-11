import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { TrendingUp, Speed, Timer } from '@mui/icons-material';

const ManufacturingEfficiencyPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Manufacturing Efficiency Report
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Monitor and analyze manufacturing efficiency metrics.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Manufacturing Efficiency Report provides insights into productivity,
          cycle times, and overall equipment effectiveness (OEE).
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    OEE Analysis
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Calculate Overall Equipment Effectiveness (OEE) and identify improvement areas.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Speed color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Throughput Rate
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor production throughput and compare against capacity.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Timer color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Cycle Time
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track production cycle times and identify bottlenecks.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ManufacturingEfficiencyPage;
