import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { ReceiptLong, LocalShipping, Description } from '@mui/icons-material';

const JobworkChallanPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Jobwork Challan
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Generate and manage delivery challans for jobwork materials.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Jobwork Challan feature allows you to create delivery documents for materials
          sent out for jobwork or received from customers. This ensures proper tracking
          and compliance.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <ReceiptLong color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Delivery Challan
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Create delivery challans for materials sent to vendors or customers for jobwork processing.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <LocalShipping color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Material Tracking
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track materials sent out and received back with proper documentation and audit trail.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Description color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Compliance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Generate GST-compliant delivery challans as per statutory requirements.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default JobworkChallanPage;
