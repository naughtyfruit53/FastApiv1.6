import React from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid } from '@mui/material';
import { Inventory, CheckCircle, LocalShipping } from '@mui/icons-material';

const JobworkReceiptPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Jobwork Receipt
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Record receipt of finished goods from jobwork processing.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Jobwork Receipt allows you to record the receipt of processed materials back
          into your inventory. Update stock levels and track quality inspection results.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Inventory color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Receive Goods
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Record the receipt of finished goods from vendors or delivery of processed goods to customers.
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
                    Quality Check
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Perform quality inspection and record acceptance or rejection of received goods.
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
                    Stock Update
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Automatically update inventory levels upon receipt confirmation.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default JobworkReceiptPage;
