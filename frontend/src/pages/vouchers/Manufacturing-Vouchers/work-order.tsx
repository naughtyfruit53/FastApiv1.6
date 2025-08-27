import React from 'react';
import { Typography, Container, Box, Button, Grid, Card, CardContent } from '@mui/material';
import { Engineering, Inventory, Assignment, Build } from '@mui/icons-material';
import { useRouter } from 'next/router';

const WorkOrder: React.FC = () => {
  const router = useRouter();

  const workOrderTypes = [
    {
      title: 'Production Entry',
      description: 'Record production output and quality metrics',
      icon: <Build />,
      route: '/vouchers/Manufacturing-Vouchers/production-entry'
    },
    {
      title: 'Quality Control',
      description: 'Quality inspection and approval workflow',
      icon: <Assignment />,
      route: '/vouchers/Manufacturing-Vouchers/quality-control'
    },
    {
      title: 'Machine Maintenance',
      description: 'Schedule and track maintenance activities',
      icon: <Engineering />,
      route: '/vouchers/Manufacturing-Vouchers/maintenance'
    },
    {
      title: 'Inventory Adjustment',
      description: 'Adjust inventory for production variances',
      icon: <Inventory />,
      route: '/vouchers/Manufacturing-Vouchers/inventory-adjustment'
    }
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" gutterBottom>
          Work Order Management
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage production work orders, quality control, and manufacturing operations.
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          {workOrderTypes.map((type, index) => (
            <Grid size={{ xs: 12, sm: 6 }} md={6} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  cursor: 'pointer',
                  '&:hover': {
                    boxShadow: 6,
                    transform: 'translateY(-2px)',
                    transition: 'all 0.3s ease-in-out'
                  }
                }}
                onClick={() => router.push(type.route)}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 2, color: 'primary.main' }}>
                    {React.cloneElement(type.icon, { sx: { fontSize: 48 } })}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {type.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {type.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
            <Button 
              variant="contained" 
              onClick={() => router.push('/vouchers/Manufacturing-Vouchers/production-order')}
            >
              New Production Order
            </Button>
            <Button 
              variant="outlined"
              onClick={() => router.push('/vouchers/Manufacturing-Vouchers/material-requisition')}
            >
              Material Requisition
            </Button>
            <Button 
              variant="outlined"
              onClick={() => router.push('/masters/bom')}
            >
              Manage BOMs
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default WorkOrder;