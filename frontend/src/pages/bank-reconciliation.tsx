// frontend/src/pages/bank-reconciliation.tsx
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
  AccountBalance
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';

import { ProtectedPage } from '../components/ProtectedPage';
const BankReconciliationPage: React.FC = () => {
  return (
    <ProtectedPage moduleKey="finance" action="read">
      <DashboardLayout
        title="Bank Reconciliation"
        subtitle="Reconcile bank statements with accounting records"
      >
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 3 }}>
              This bank reconciliation module is under development. Core functionality will be available soon.
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
                  <AccountBalance sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h4" gutterBottom>
                    Bank Reconciliation
                  </Typography>
                  <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                    Reconcile bank statements with accounting records
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
    </ProtectedPage>
  );
};
export default BankReconciliationPage;
