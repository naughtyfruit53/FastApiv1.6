import React from 'react';
import { Typography, Container, Box, Alert, Grid, Card, CardContent, Chip, LinearProgress } from '@mui/material';
import { CheckCircle, Schedule, Build, Inventory } from '@mui/icons-material';

const FinishedGoodsReceipt: React.FC = () => {
  // Mock data for demonstration
  const recentProduction = [
    {
      id: 1,
      productionOrder: 'MO/2425/00000001',
      bomName: 'Laptop Assembly v1.0',
      plannedQty: 50,
      producedQty: 45,
      goodQty: 42,
      rejectQty: 3,
      status: 'completed',
      completionDate: '2024-08-14'
    },
    {
      id: 2,
      productionOrder: 'MO/2425/00000002',
      bomName: 'Desktop PC v2.1',
      plannedQty: 30,
      producedQty: 28,
      goodQty: 25,
      rejectQty: 3,
      status: 'in_progress',
      completionDate: null
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'quality_check': return 'info';
      default: return 'default';
    }
  };

  const getCompletionPercentage = (produced: number, planned: number) => {
    return Math.min((produced / planned) * 100, 100);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" gutterBottom>
          Finished Goods Receipt
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Track and receive finished goods from production orders.
        </Typography>

        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            This module shows completed production orders ready for finished goods receipt.
            Integrate with your production workflow to automatically update inventory.
          </Typography>
        </Alert>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Recent Production Orders
        </Typography>

        <Grid container spacing={3}>
          {recentProduction.map((order) => (
            <Grid size={{ xs: 12, md: 6 }} key={order.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {order.productionOrder}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {order.bomName}
                      </Typography>
                    </Box>
                    <Chip 
                      label={order.status.replace('_', ' ')} 
                      color={getStatusColor(order.status)}
                      size="small"
                    /> */}
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        Production Progress
                      </Typography>
                      <Typography variant="body2">
                        {order.producedQty}/{order.plannedQty}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={getCompletionPercentage(order.producedQty, order.plannedQty)}
                      sx={{ height: 8, borderRadius: 4 }}
                    /> */}
                  </Box>

                  <Grid container spacing={2}>
                    <Grid size={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircle color="success" fontSize="small" />
                        <Typography variant="body2">
                          Good: {order.goodQty}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid size={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Build color="error" fontSize="small" />
                        <Typography variant="body2">
                          Reject: {order.rejectQty}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  {order.completionDate && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Completed on: {order.completionDate}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Integration Points
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Inventory color="primary" />
                    <Typography variant="subtitle1">
                      Inventory Update
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Automatically update finished goods inventory upon receipt confirmation.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Schedule color="primary" />
                    <Typography variant="subtitle1">
                      Quality Control
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Route goods through quality control before final inventory receipt.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Build color="primary" />
                    <Typography variant="subtitle1">
                      Cost Calculation
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Calculate actual production costs vs. planned costs for analysis.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  );
};

export default FinishedGoodsReceipt;