import React from 'react';
import { Container, Typography, Grid, Card, CardContent, CardActionArea, Box } from '@mui/material';
import { useRouter } from 'next/router';
import PaymentIcon from '@mui/icons-material/Payment';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';

const FinancialVouchers: React.FC = () => {
  const router = useRouter();

  const voucherTypes = [
    {
      title: 'Payment Voucher',
      description: 'Record payments made to vendors and suppliers',
      icon: <PaymentIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      path: '/vouchers/Financial-Vouchers/payment-voucher'
    },
    {
      title: 'Receipt Voucher',
      description: 'Record receipts from customers and other sources',
      icon: <ReceiptIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      path: '/vouchers/Financial-Vouchers/receipt-voucher'
    },
    {
      title: 'Journal Voucher',
      description: 'Record general journal entries and adjustments',
      icon: <AccountBalanceIcon sx={{ fontSize: 40, color: 'info.main' }} />,
      path: '/vouchers/Financial-Vouchers/journal-voucher'
    },
    {
      title: 'Contra Voucher',
      description: 'Record transfers between bank and cash accounts',
      icon: <SwapHorizIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      path: '/vouchers/Financial-Vouchers/contra-voucher'
    },
    {
      title: 'Non-Sales Credit Note',
      description: 'Issue credit notes for non-sales related adjustments',
      icon: <CreditCardIcon sx={{ fontSize: 40, color: 'error.main' }} />,
      path: '/vouchers/Financial-Vouchers/non-sales-credit-note'
    },
    {
      title: 'Credit Note',
      description: 'Issue credit notes for financial adjustments',
      icon: <CreditCardIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      path: '/vouchers/Financial-Vouchers/credit-note'
    },
    {
      title: 'Debit Note',
      description: 'Issue debit notes for financial adjustments',
      icon: <RemoveCircleIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      path: '/vouchers/Financial-Vouchers/debit-note'
    }
  ];

  const handleVoucherClick = (path: string) => {
    router.push(path);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        Financial Vouchers
      </Typography>
      <Typography variant="body1" paragraph align="center" color="textSecondary">
        Manage all your financial transactions and accounting entries
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {voucherTypes.map((voucher, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                '&:hover': {
                  boxShadow: 6,
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s ease-in-out'
                }
              }}
            >
              <CardActionArea 
                onClick={() => handleVoucherClick(voucher.path)}
                sx={{ height: '100%', p: 2 }}
              >
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ mb: 2 }}>
                    {voucher.icon}
                  </Box>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {voucher.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {voucher.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default FinancialVouchers;