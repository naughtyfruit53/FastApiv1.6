import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { BarChart, TrendingUp, Assessment } from '@mui/icons-material';

const QualityReportsPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Quality Reports
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Analyze quality metrics and inspection data.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Quality Reports provide insights into quality trends, rejection rates,
          and inspection performance across your manufacturing operations.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <BarChart color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Quality Trends
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track quality metrics over time and identify improvement areas.
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
                    Rejection Analysis
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Analyze rejection patterns and root causes for quality issues.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Assessment color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Compliance Reports
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Generate compliance reports for audits and certifications.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default QualityReportsPage;
