// pages/receipt-vouchers.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert
} from '@mui/material';
import { 
  MonetizationOn
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const ReceiptVouchersPage: React.FC = () => {
  return (
    <DashboardLayout
      title="Receipt Vouchers"
      subtitle="Record payments from customers"
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            This receipt vouchers module is under development. Core functionality will be available soon.
          </Alert>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center', 
                minHeight: 400,
                textAlign: 'center'
              }}>
                <MonetizationOn sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" gutterBottom>
                  Receipt Vouchers
                </Typography>
                <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                  Record payments from customers
                </Typography>
                <Button variant="contained" disabled>
                  Feature Coming Soon
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default ReceiptVouchersPage;