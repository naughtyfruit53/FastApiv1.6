import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { Assessment, CheckCircle, Warning } from '@mui/icons-material';

const QualityInspectionPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Quality Inspection
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Conduct quality inspections for manufactured goods and jobwork items.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Quality Inspection module helps maintain quality standards by enabling
          systematic inspection of raw materials, work-in-progress, and finished goods.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Assessment color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Inspection Plans
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Define inspection criteria and quality parameters for different product types.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <CheckCircle color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Acceptance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Record inspection results and approve or reject batches based on quality standards.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Warning color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Non-Conformance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track and manage non-conformance issues and corrective actions.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default QualityInspectionPage;
