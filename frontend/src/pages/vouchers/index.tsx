// revised fastapi_migration/frontend/src/pages/vouchers/index.tsx

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
  Paper,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { voucherService, reportsService } from '../../services/authService';
import { voucherService as voucherApi } from '../../services/vouchersService';
import { generateVoucherPDF, getVoucherPdfConfig } from '../../utils/pdfUtils';
import MegaMenu from '../../components/MegaMenu';
import VoucherContextMenu from '../../components/VoucherContextMenu';
import VoucherListModal from '../../components/VoucherListModal';
import Grid from '@mui/material/Grid';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`voucher-tabpanel-${index}`}
      aria-labelledby={`voucher-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const VoucherManagement: React.FC = () => {
  const router = useRouter();
  const [user] = useState({ email: 'demo@example.com', role: 'admin' });
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; voucher: any; type: string } | null>(null);
  const [showAllModal, setShowAllModal] = useState(false);
  const [modalVoucherType, setModalVoucherType] = useState('');
  const [modalVouchers, setModalVouchers] = useState<any[]>([]);

  // Get tab from URL parameter
  const getInitialTab = () => {
    const { tab } = router.query;
    switch (tab) {
      case 'purchase': return 0;
      case 'sales': return 1;
      case 'financial': return 2;
      case 'internal': return 3;
      default: return 0;
    }
  };

  const [tabValue, setTabValue] = useState(getInitialTab());

  // Update tab when URL changes
  useEffect(() => {
    setTabValue(getInitialTab());
   
  }, [router.query.tab]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    // Update URL without full navigation
    const tabNames = ['purchase', 'sales', 'financial', 'internal'];
    router.replace(`/vouchers?tab=${tabNames[newValue]}`, undefined, { shallow: true });
  };

  const handleShowAll = (type: string, vouchers: any[]) => {
    setModalVoucherType(type);
    setModalVouchers(vouchers);
    setShowAllModal(true);
  };

  const handleCloseModal = () => {
    setShowAllModal(false);
    setModalVoucherType('');
    setModalVouchers([]);
  };

  const handleLogout = () => {
    // Handle logout
  };

  const handleCreateVoucher = (tabIndex: number) => {
    const tabNames = ['purchase', 'sales', 'financial', 'internal'];
    router.push(`/vouchers/${tabNames[tabIndex]}`);
  };

  const handleViewVoucher = (type: string, id: number) => {
    router.push(`/vouchers/${type.toLowerCase()}/view/${id}`);
  };

  const handleEditVoucher = (type: string, id: number) => {
    router.push(`/vouchers/${type.toLowerCase()}/edit/${id}`);
  };

  const handlePrintVoucher = async (type: string, id: number) => {
    try {
      // Map display type to API type
      const voucherType = type === 'Purchase' ? 'purchase-vouchers' : 
                         type === 'Sales' ? 'sales-vouchers' : 
                         type.toLowerCase().replace(' ', '-');
      
      // Fetch voucher data
      const voucherData = await voucherApi.getVoucherById(voucherType, id);
      
      // Generate PDF using the existing PDF utility
      const pdfConfig = getVoucherPdfConfig(voucherType);
      await generateVoucherPDF(voucherData, pdfConfig);
    } catch (error: any) {
      console.error('Error generating PDF:', error);
      alert(`Error generating PDF: ${error.message || 'Unknown error'}`);
    }
  };

  const handleEmailVoucher = async (type: string, id: number) => {
    const voucherType = type === 'Purchase' ? 'purchase-vouchers' : (type === 'Sales' ? 'sales-vouchers' : '');
    if (!voucherType) return alert('Email not supported for this type');

    try {
      await voucherService.sendVoucherEmail(voucherType, id);
      alert('Email sent successfully');
    } catch (error: any) {
      alert(`Error sending email: ${error.message || 'Unknown error'}`);
    }
  };

  const handleDeleteVoucher = async (type: string, id: number) => {
    if (window.confirm(`Are you sure you want to delete this ${type} voucher?`)) {
      try {
        // Map display type to API type
        const voucherType = type === 'Purchase' ? 'purchase-vouchers' : 
                           type === 'Sales' ? 'sales-vouchers' : 
                           type.toLowerCase().replace(' ', '-');
        
        await voucherApi.deleteVoucher(voucherType, id);
        
        // Refresh the appropriate voucher data
        if (type === 'Purchase') {
          refetchPurchaseVouchers();
        } else if (type === 'Sales') {
          refetchSalesVouchers();
        } else if (type === 'Financial') {
          refetchFinancialVouchers();
        } else if (type === 'Internal') {
          refetchInternalVouchers();
        }
        
        alert('Voucher deleted successfully');
      } catch (error: any) {
        console.error('Error deleting voucher:', error);
        alert(`Error deleting voucher: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
      }
    }
  };

  const handleContextMenu = (event: React.MouseEvent, voucher: any, voucherType: string) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX + 2,
      mouseY: event.clientY - 6,
      voucher,
      type: voucherType
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  // Fetch real data from APIs
  const { data: dashboardStats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: reportsService.getDashboardStats
  });
  const { data: purchaseVouchers, isLoading: purchaseLoading, refetch: refetchPurchaseVouchers } = useQuery({
    queryKey: ['purchaseVouchers'],
    queryFn: () => voucherService.getVouchers('purchase-vouchers'),
    enabled: tabValue === 0
  });
  const { data: salesVouchers, isLoading: salesLoading, refetch: refetchSalesVouchers } = useQuery({
    queryKey: ['salesVouchers'],
    queryFn: () => voucherService.getVouchers('sales-vouchers'),
    enabled: tabValue === 1
  });
  
  // Financial vouchers queries
  const { data: financialVouchers, isLoading: financialLoading, refetch: refetchFinancialVouchers } = useQuery({
    queryKey: ['financialVouchers'],
    queryFn: async () => {
      const [payments, receipts, journals, contras] = await Promise.all([
        voucherService.getVouchers('payment-vouchers').catch(() => []),
        voucherService.getVouchers('receipt-vouchers').catch(() => []),
        voucherService.getVouchers('journal-vouchers').catch(() => []),
        voucherService.getVouchers('contra-vouchers').catch(() => [])
      ]);
      return [...payments, ...receipts, ...journals, ...contras];
    },
    enabled: tabValue === 2
  });
  
  // Internal vouchers queries  
  const { data: internalVouchers, isLoading: internalLoading, refetch: refetchInternalVouchers } = useQuery({
    queryKey: ['internalVouchers'],
    queryFn: async () => {
      const [manufacturing, stock] = await Promise.all([
        voucherService.getVouchers('manufacturing-journals').catch(() => []),
        voucherService.getVouchers('stock-journals').catch(() => [])
      ]);
      return [...manufacturing, ...stock];
    },
    enabled: tabValue === 3
  });

  // Voucher types with real data
  const voucherTypes = [
    {
      title: 'Purchase Vouchers',
      description: 'Manage purchase transactions, orders, and returns',
      count: dashboardStats?.vouchers?.purchase_vouchers || 0,
      color: '#1976D2',
      vouchers: purchaseVouchers || []
    },
    {
      title: 'Sales Vouchers',
      description: 'Manage sales transactions, orders, and returns',
      count: dashboardStats?.vouchers?.sales_vouchers || 0,
      color: '#2E7D32',
      vouchers: salesVouchers || []
    },
    {
      title: 'Financial Vouchers',
      description: 'Manage payments, receipts, and journal entries',
      count: (financialVouchers || []).length,
      color: '#7B1FA2',
      vouchers: financialVouchers || []
    },
    {
      title: 'Internal Vouchers',
      description: 'Manage internal transfers and adjustments',
      count: (internalVouchers || []).length,
      color: '#F57C00',
      vouchers: internalVouchers || []
    }
  ];

  const renderVoucherTable = (vouchers: any[], type: string, isLoading: boolean = false) => {
    if (isLoading) {
      return <Typography>Loading {type} vouchers...</Typography>;
    }
    
    if (!vouchers || vouchers.length === 0) {
      return <Typography>No {type} vouchers found.</Typography>;
    }

    // Show only latest 5 vouchers in the table
    const latestVouchers = vouchers.slice(0, 5);

    return (
      <Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Index</TableCell>
                <TableCell>Voucher #</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>{type === 'Purchase' ? 'Vendor' : type === 'Sales' ? 'Customer' : 'Type'}</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {latestVouchers.map((voucher, index) => (
                <TableRow 
                  key={voucher.id}
                  onContextMenu={(e) => handleContextMenu(e, voucher, type)}
                  sx={{ 
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    }
                  }}
                >
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{voucher.voucher_number}</TableCell>
                  <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {voucher.vendor?.name || voucher.customer?.name || voucher.type || 'N/A'}
                  </TableCell>
                  <TableCell>
                    {voucher.total_amount > 0 ? `₹${voucher.total_amount.toLocaleString()}` : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={voucher.status}
                      color={
                        voucher.status === 'approved' || voucher.status === 'confirmed' || voucher.status === 'processed'
                          ? 'success'
                          : voucher.status === 'pending'
                          ? 'warning'
                          : 'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType={type}
                      onView={(id) => handleViewVoucher(type, id)}
                      onEdit={(id) => handleEditVoucher(type, id)}
                      onDelete={(id) => handleDeleteVoucher(type, id)}
                      onPrint={(id) => handlePrintVoucher(type, id)}
                      onEmail={(id) => handleEmailVoucher(type, id)}
                      showKebab={true}
                      open={false}
                      onClose={() => {}}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {vouchers.length > 5 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button
              variant="outlined"
              onClick={() => handleShowAll(type, vouchers)}
              sx={{ textTransform: 'none' }}
            >
              Show All ({vouchers.length} total)
            </Button>
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <MegaMenu user={user} onLogout={handleLogout} />

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Voucher Management System
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          Comprehensive management of all voucher types in your ERP system
        </Typography>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {voucherTypes.map((voucherType, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        {voucherType.title}
                      </Typography>
                      <Typography variant="h4" component="h2">
                        {voucherType.count}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {voucherType.description}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Voucher Tabs */}
        <Paper sx={{ mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="voucher tabs">
              <Tab label="Purchase Vouchers" />
              <Tab label="Sales Vouchers" />
              <Tab label="Financial Vouchers" />
              <Tab label="Internal Vouchers" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6">Purchase Vouchers</Typography>
            </Box>
            {renderVoucherTable(voucherTypes[0].vouchers, 'Purchase', purchaseLoading)}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6">Sales Vouchers</Typography>
            </Box>
            {renderVoucherTable(voucherTypes[1].vouchers, 'Sales', salesLoading)}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6">Financial Vouchers</Typography>
            </Box>
            {renderVoucherTable(voucherTypes[2].vouchers, 'Financial', false)}
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6">Internal Vouchers</Typography>
            </Box>
            {renderVoucherTable(voucherTypes[3].vouchers, 'Internal', false)}
          </TabPanel>
        </Paper>

        {/* Summary */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Voucher System Features
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="body1" paragraph>
                ✅ <strong>4 Voucher Categories:</strong> Purchase, Sales, Financial, and Internal vouchers
              </Typography>
              <Typography variant="body1" paragraph>
                ✅ <strong>Complete CRUD Operations:</strong> Create, Read, Update, Delete vouchers
              </Typography>
              <Typography variant="body1" paragraph>
                ✅ <strong>Status Management:</strong> Draft, Pending, Approved, Confirmed workflows
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="body1" paragraph>
                ✅ <strong>Email Integration:</strong> Send vouchers to vendors/customers
              </Typography>
              <Typography variant="body1" paragraph>
                ✅ <strong>Print Support:</strong> Generate PDF vouchers for printing
              </Typography>
              <Typography variant="body1" paragraph>
                ✅ <strong>Audit Trail:</strong> Track all voucher changes and approvals
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Container>

      {/* Global Context Menu for Right-Click */}
      {contextMenu && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType={contextMenu.type}
          onView={(id) => handleViewVoucher(contextMenu.type, id)}
          onEdit={(id) => handleEditVoucher(contextMenu.type, id)}
          onDelete={(id) => handleDeleteVoucher(contextMenu.type, id)}
          onPrint={(id) => handlePrintVoucher(contextMenu.type, id)}
          onEmail={(id) => handleEmailVoucher(contextMenu.type, id)}
          showKebab={false}
          anchorPosition={{ left: contextMenu.mouseX, top: contextMenu.mouseY }}
          open={!!contextMenu}
          onClose={handleCloseContextMenu}
        />
      )}

      {/* Show All Modal */}
      {showAllModal && (
        <VoucherListModal
          open={showAllModal}
          onClose={handleCloseModal}
          vouchers={modalVouchers}
          voucherType={modalVoucherType}
          onVoucherClick={(voucher) => handleViewVoucher(modalVoucherType, voucher.id)}
          onView={(id) => handleViewVoucher(modalVoucherType, id)}
          onEdit={(id) => handleEditVoucher(modalVoucherType, id)}
          onDelete={(id) => handleDeleteVoucher(modalVoucherType, id)}
          onGeneratePDF={(voucher) => handlePrintVoucher(modalVoucherType, voucher.id)}
        />
      )}
    </Box>
  );
};

export default VoucherManagement;