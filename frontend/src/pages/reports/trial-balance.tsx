// pages/reports/trial-balance.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider
} from '@mui/material';
import { 
  Download, 
  Print,
  AccountBalance
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const TrialBalancePage: React.FC = () => {
  const trialBalanceData = [
    { account: 'Cash in Hand', debit: 45000, credit: 0 },
    { account: 'Bank Account', debit: 125000, credit: 0 },
    { account: 'Accounts Receivable', debit: 85000, credit: 0 },
    { account: 'Inventory', debit: 150000, credit: 0 },
    { account: 'Office Equipment', debit: 75000, credit: 0 },
    { account: 'Accounts Payable', debit: 0, credit: 65000 },
    { account: 'Sales Revenue', debit: 0, credit: 450000 },
    { account: 'Purchase Expenses', debit: 200000, credit: 0 },
    { account: 'Office Expenses', debit: 25000, credit: 0 },
    { account: 'Salary Expenses', debit: 180000, credit: 0 },
    { account: 'Owner\'s Equity', debit: 0, credit: 370000 },
  ];

  const totalDebit = trialBalanceData.reduce((sum, item) => sum + item.debit, 0);
  const totalCredit = trialBalanceData.reduce((sum, item) => sum + item.credit, 0);

  return (
    <DashboardLayout
      title="Trial Balance"
      subtitle="Verify that total debits equal total credits"
      actions={
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant="outlined" 
            startIcon={<Download />}
          >
            Export
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<Print />}
          >
            Print
          </Button>
        </Box>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity={totalDebit === totalCredit ? "success" : "error"} sx={{ mb: 3 }}>
            {totalDebit === totalCredit 
              ? "Trial Balance is balanced! Debits equal Credits." 
              : `Trial Balance is NOT balanced! Difference: $${Math.abs(totalDebit - totalCredit).toLocaleString()}`
            }
          </Alert>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error.main">
                Total Debits
              </Typography>
              <Typography variant="h3" color="error.main">
                ${totalDebit.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="success.main">
                Total Credits
              </Typography>
              <Typography variant="h3" color="success.main">
                ${totalCredit.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trial Balance Report
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                As of {new Date().toLocaleDateString()}
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Account Name</strong></TableCell>
                      <TableCell align="right"><strong>Debit</strong></TableCell>
                      <TableCell align="right"><strong>Credit</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {trialBalanceData.map((row, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <AccountBalance sx={{ mr: 1, fontSize: 16 }} />
                            {row.account}
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          {row.debit > 0 ? `$${row.debit.toLocaleString()}` : '-'}
                        </TableCell>
                        <TableCell align="right">
                          {row.credit > 0 ? `$${row.credit.toLocaleString()}` : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={3}>
                        <Divider />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>TOTALS</strong></TableCell>
                      <TableCell align="right">
                        <strong>${totalDebit.toLocaleString()}</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>${totalCredit.toLocaleString()}</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/reports/ledgers">
                  View Ledgers
                </Button>
                <Button variant="outlined" href="/reports/balance-sheet">
                  Balance Sheet
                </Button>
                <Button variant="outlined" href="/reports/profit-loss">
                  P&L Statement
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default TrialBalancePage;