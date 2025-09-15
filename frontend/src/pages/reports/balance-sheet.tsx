// pages/reports/balance-sheet.tsx
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
  Assessment, 
  Download, 
  Print,
  AccountBalance
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const BalanceSheetPage: React.FC = () => {
  const assets = {
    currentAssets: [
      { name: 'Cash in Hand', amount: 45000 },
      { name: 'Bank Account', amount: 125000 },
      { name: 'Accounts Receivable', amount: 85000 },
      { name: 'Inventory', amount: 150000 },
    ],
    fixedAssets: [
      { name: 'Office Equipment', amount: 75000 },
      { name: 'Computer Systems', amount: 50000 },
      { name: 'Furniture & Fixtures', amount: 25000 },
    ]
  };

  const liabilities = {
    currentLiabilities: [
      { name: 'Accounts Payable', amount: 65000 },
      { name: 'Accrued Expenses', amount: 15000 },
      { name: 'Short-term Loans', amount: 25000 },
    ],
    longTermLiabilities: [
      { name: 'Long-term Debt', amount: 100000 },
    ]
  };

  const equity = [
    { name: 'Owner\'s Capital', amount: 300000 },
    { name: 'Retained Earnings', amount: 70000 },
  ];

  const totalCurrentAssets = assets.currentAssets.reduce((sum, item) => sum + item.amount, 0);
  const totalFixedAssets = assets.fixedAssets.reduce((sum, item) => sum + item.amount, 0);
  const totalAssets = totalCurrentAssets + totalFixedAssets;

  const totalCurrentLiabilities = liabilities.currentLiabilities.reduce((sum, item) => sum + item.amount, 0);
  const totalLongTermLiabilities = liabilities.longTermLiabilities.reduce((sum, item) => sum + item.amount, 0);
  const totalLiabilities = totalCurrentLiabilities + totalLongTermLiabilities;

  const totalEquity = equity.reduce((sum, item) => sum + item.amount, 0);
  const totalLiabilitiesAndEquity = totalLiabilities + totalEquity;

  return (
    <DashboardLayout
      title="Balance Sheet"
      subtitle="Statement of financial position"
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
          <Alert severity={totalAssets === totalLiabilitiesAndEquity ? "success" : "error"} sx={{ mb: 3 }}>
            {totalAssets === totalLiabilitiesAndEquity 
              ? "Balance Sheet is balanced! Assets = Liabilities + Equity" 
              : "Balance Sheet is NOT balanced! Please review the entries."
            }
          </Alert>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ASSETS
              </Typography>

              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
                Current Assets
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {assets.currentAssets.map((asset, index) => (
                      <TableRow key={index}>
                        <TableCell>{asset.name}</TableCell>
                        <TableCell align="right">${asset.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell><strong>Total Current Assets</strong></TableCell>
                      <TableCell align="right"><strong>${totalCurrentAssets.toLocaleString()}</strong></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              <Typography variant="subtitle1" sx={{ mt: 3, mb: 1, fontWeight: 'bold' }}>
                Fixed Assets
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {assets.fixedAssets.map((asset, index) => (
                      <TableRow key={index}>
                        <TableCell>{asset.name}</TableCell>
                        <TableCell align="right">${asset.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell><strong>Total Fixed Assets</strong></TableCell>
                      <TableCell align="right"><strong>${totalFixedAssets.toLocaleString()}</strong></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">TOTAL ASSETS</Typography>
                <Typography variant="h6" color="primary.main">
                  ${totalAssets.toLocaleString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                LIABILITIES & EQUITY
              </Typography>

              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
                Current Liabilities
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {liabilities.currentLiabilities.map((liability, index) => (
                      <TableRow key={index}>
                        <TableCell>{liability.name}</TableCell>
                        <TableCell align="right">${liability.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell><strong>Total Current Liabilities</strong></TableCell>
                      <TableCell align="right"><strong>${totalCurrentLiabilities.toLocaleString()}</strong></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              <Typography variant="subtitle1" sx={{ mt: 3, mb: 1, fontWeight: 'bold' }}>
                Long-term Liabilities
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {liabilities.longTermLiabilities.map((liability, index) => (
                      <TableRow key={index}>
                        <TableCell>{liability.name}</TableCell>
                        <TableCell align="right">${liability.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell><strong>Total Long-term Liabilities</strong></TableCell>
                      <TableCell align="right"><strong>${totalLongTermLiabilities.toLocaleString()}</strong></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              <Typography variant="subtitle1" sx={{ mt: 3, mb: 1, fontWeight: 'bold' }}>
                Equity
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {equity.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell align="right">${item.amount.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell><strong>Total Equity</strong></TableCell>
                      <TableCell align="right"><strong>${totalEquity.toLocaleString()}</strong></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">TOTAL LIABILITIES & EQUITY</Typography>
                <Typography variant="h6" color="primary.main">
                  ${totalLiabilitiesAndEquity.toLocaleString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Ratios
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">Current Ratio</Typography>
                  <Typography variant="h6">
                    {(totalCurrentAssets / totalCurrentLiabilities).toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">Debt-to-Equity Ratio</Typography>
                  <Typography variant="h6">
                    {(totalLiabilities / totalEquity).toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">Equity Ratio</Typography>
                  <Typography variant="h6">
                    {((totalEquity / totalAssets) * 100).toFixed(1)}%
                  </Typography>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/reports/profit-loss">
                  P&L Statement
                </Button>
                <Button variant="outlined" href="/reports/trial-balance">
                  Trial Balance
                </Button>
                <Button variant="outlined" href="/reports/cash-flow">
                  Cash Flow
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default BalanceSheetPage;