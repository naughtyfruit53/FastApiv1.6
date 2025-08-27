'use client';

import React, { useState } from 'react';
import '../styles/print.css';
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Alert
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Assessment,
  TrendingUp,
  TrendingDown,
  Download,
  Print,
  Refresh,
  Business,
  Person,
  Inventory,
  Warning,
  AccountBalance
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { reportsService } from '../services/authService';
import MegaMenu from '../components/MegaMenu';
import ExportPrintToolbar from '../components/ExportPrintToolbar';
import { canAccessLedger } from '../types/user.types';

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
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
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

const ReportsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [user] = useState({ id: 1, email: 'demo@example.com', role: 'admin' });
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0], // First day of current month
    end: new Date().toISOString().split('T')[0]
  });

  const [salesFilters, setSalesFilters] = useState({
    customer_id: '',
    search: ''
  });
  const [purchaseFilters, setPurchaseFilters] = useState({
    vendor_id: '',
    search: ''
  });
  const [inventoryFilters, setInventoryFilters] = useState({
    include_zero_stock: false,
    search: ''
  });
  const [pendingOrdersFilters, setPendingOrdersFilters] = useState({
    order_type: 'all',
    search: ''
  });

  // Ledger specific state
  const [ledgerType, setLedgerType] = useState<'complete' | 'outstanding'>('complete');
  const [ledgerFilters, setLedgerFilters] = useState({
    start_date: dateRange.start,
    end_date: dateRange.end,
    account_type: 'all',
    account_id: '',
    voucher_type: 'all'
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleLogout = () => {
    // Handle logout
  };

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    setDateRange(prev => ({ ...prev, [field]: value }));
  };

  // Fetch dashboard statistics
  const { data: dashboardStats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: reportsService.getDashboardStats,
    enabled: true,
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  // Fetch sales report
  const { data: salesReport, isLoading: salesLoading, refetch: refetchSales } = useQuery({
    queryKey: ['salesReport', dateRange.start, dateRange.end, salesFilters],
    queryFn: () => reportsService.getSalesReport({
      start_date: dateRange.start,
      end_date: dateRange.end,
      customer_id: salesFilters.customer_id || undefined,
      search: salesFilters.search || undefined
    }),
    enabled: tabValue === 1
  });

  // Fetch purchase report
  const { data: purchaseReport, isLoading: purchaseLoading, refetch: refetchPurchase } = useQuery({
    queryKey: ['purchaseReport', dateRange.start, dateRange.end, purchaseFilters],
    queryFn: () => reportsService.getPurchaseReport({
      start_date: dateRange.start,
      end_date: dateRange.end,
      vendor_id: purchaseFilters.vendor_id || undefined,
      search: purchaseFilters.search || undefined
    }),
    enabled: tabValue === 2
  });

  // Fetch inventory report
  const { data: inventoryReport, isLoading: inventoryLoading, refetch: refetchInventory } = useQuery({
    queryKey: ['inventoryReport', inventoryFilters],
    queryFn: () => reportsService.getInventoryReport(inventoryFilters.include_zero_stock),
    enabled: tabValue === 3
  });

  // Fetch pending orders
  const { data: pendingOrders, isLoading: ordersLoading, refetch: refetchOrders } = useQuery({
    queryKey: ['pendingOrders', pendingOrdersFilters],
    queryFn: () => reportsService.getPendingOrders(pendingOrdersFilters.order_type),
    enabled: tabValue === 4
  });

  // Fetch complete ledger
  const { data: completeLedger, isLoading: completeLedgerLoading, refetch: refetchCompleteLedger } = useQuery({
    queryKey: ['completeLedger', ledgerFilters],
    queryFn: () => reportsService.getCompleteLedger(ledgerFilters),
    enabled: tabValue === 5 && ledgerType === 'complete' && canAccessLedger(user)
  });

  // Fetch outstanding ledger  
  const { data: outstandingLedger, isLoading: outstandingLedgerLoading, refetch: refetchOutstandingLedger } = useQuery({
    queryKey: ['outstandingLedger', ledgerFilters],
    queryFn: () => reportsService.getOutstandingLedger(ledgerFilters),
    enabled: tabValue === 5 && ledgerType === 'outstanding' && canAccessLedger(user)
  });

  const handleLedgerFilterChange = (field: string, value: string) => {
    setLedgerFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleLedgerTypeChange = (type: 'complete' | 'outstanding') => {
    setLedgerType(type);
  };

  const renderSummaryCards = () => {
    if (statsLoading || !dashboardStats) {
      return <Typography>Loading statistics...</Typography>;
    }

    const cards = [
      {
        title: 'Vendors',
        value: dashboardStats.masters?.vendors || 0,
        color: '#1976D2',
        icon: <Business />
      },
      {
        title: 'Customers', 
        value: dashboardStats.masters?.customers || 0,
        color: '#2E7D32',
        icon: <Person />
      },
      {
        title: 'Products',
        value: dashboardStats.masters?.products || 0,
        color: '#7B1FA2',
        icon: <Inventory />
      },
      {
        title: 'Low Stock Items',
        value: dashboardStats.inventory?.low_stock_items || 0,
        color: '#F57C00',
        icon: <Warning />
      }
    ];

    return (
      <Grid container spacing={3}>
        {cards.map((card, index) => (
          <Grid
            key={index}
            size={{
              xs: 12,
              sm: 6,
              md: 3
            }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  const renderVoucherTable = (vouchers: any[], title: string, reportType: string, filters?: any) => {
    const getExportHandler = () => {
      switch (reportType) {
        case 'sales':
          return () => reportsService.exportSalesReportExcel({
            start_date: dateRange.start,
            end_date: dateRange.end,
            ...filters
          });
        case 'purchase':
          return () => reportsService.exportPurchaseReportExcel({
            start_date: dateRange.start,
            end_date: dateRange.end,
            ...filters
          });
        case 'pending-orders':
          return () => reportsService.exportPendingOrdersExcel(filters);
        default:
          return undefined;
      }
    };

    return (
      <TableContainer component={Paper}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">{title}</Typography>
          <ExportPrintToolbar
            onExportExcel={getExportHandler()}
            filename={`${reportType.replace('-', '_')}_report`}
            showCSV={false}
            onPrint={() => window.print()}
          />
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Voucher #</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Party</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>GST</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {vouchers?.map((voucher) => (
              <TableRow key={voucher.id}>
                <TableCell>{voucher.voucher_number}</TableCell>
                <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                <TableCell>{voucher.vendor_name || voucher.customer_name}</TableCell>
                <TableCell>₹{voucher.total_amount.toLocaleString()}</TableCell>
                <TableCell>₹{voucher.gst_amount.toLocaleString()}</TableCell>
                <TableCell>
                  <Chip
                    label={voucher.status}
                    color={voucher.status === 'confirmed' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <MegaMenu user={user} onLogout={handleLogout} />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Reports & Analytics
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          Comprehensive business reports and data analytics
        </Typography>

        {/* Summary Cards */}
        <Box sx={{ mb: 4 }}>
          {renderSummaryCards()}
        </Box>

        {/* Reports Tabs */}
        <Paper sx={{ mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="reports tabs">
              <Tab label="Overview" />
              <Tab label="Sales Report" />
              <Tab label="Purchase Report" />
              <Tab label="Inventory Report" />
              <Tab label="Pending Orders" />
              <Tab label="Ledger" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Typography variant="h6" gutterBottom>
              Business Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid
                size={{
                  xs: 12,
                  md: 6
                }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Sales Performance
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TrendingUp sx={{ color: 'green', mr: 1 }} />
                      <Typography variant="body1">
                        Total Sales Vouchers: {dashboardStats?.vouchers?.sales_vouchers || 0}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid
                size={{
                  xs: 12,
                  md: 6
                }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Purchase Performance
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TrendingDown sx={{ color: 'orange', mr: 1 }} />
                      <Typography variant="body1">
                        Total Purchase Vouchers: {dashboardStats?.vouchers?.purchase_vouchers || 0}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <TextField
                label="Start Date"
                type="date"
                value={dateRange.start}
                onChange={(e) => handleDateChange('start', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
              <TextField
                label="End Date"
                type="date"
                value={dateRange.end}
                onChange={(e) => handleDateChange('end', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
              <TextField
                label="Search"
                placeholder="Search vouchers..."
                value={salesFilters.search}
                onChange={(e) => setSalesFilters(prev => ({ ...prev, search: e.target.value }))}
                size="small"
                sx={{ minWidth: 200 }}
              />
              <Button variant="contained" startIcon={<Refresh />} onClick={() => refetchSales()}>
                Refresh
              </Button>
            </Box>
            
            {salesLoading ? (
              <Typography>Loading sales report...</Typography>
            ) : salesReport ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6">Summary</Typography>
                  <Typography>Total Vouchers: {salesReport.summary?.total_vouchers || 0}</Typography>
                  <Typography>Total Sales: ₹{salesReport.summary?.total_sales?.toLocaleString() || 0}</Typography>
                  <Typography>Total GST: ₹{salesReport.summary?.total_gst?.toLocaleString() || 0}</Typography>
                </Box>
                {renderVoucherTable(salesReport.vouchers || [], 'Sales Vouchers', 'sales', {
                  customer_id: salesFilters.customer_id,
                  search: salesFilters.search
                })}
              </>
            ) : (
              <Typography>No sales data available</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <TextField
                label="Start Date"
                type="date"
                value={dateRange.start}
                onChange={(e) => handleDateChange('start', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
              <TextField
                label="End Date"
                type="date"
                value={dateRange.end}
                onChange={(e) => handleDateChange('end', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
              <TextField
                label="Search"
                placeholder="Search vouchers..."
                value={purchaseFilters.search}
                onChange={(e) => setPurchaseFilters(prev => ({ ...prev, search: e.target.value }))}
                size="small"
                sx={{ minWidth: 200 }}
              />
              <Button variant="contained" startIcon={<Refresh />} onClick={() => refetchPurchase()}>
                Refresh
              </Button>
            </Box>
            
            {purchaseLoading ? (
              <Typography>Loading purchase report...</Typography>
            ) : purchaseReport ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6">Summary</Typography>
                  <Typography>Total Vouchers: {purchaseReport.summary?.total_vouchers || 0}</Typography>
                  <Typography>Total Purchases: ₹{purchaseReport.summary?.total_purchases?.toLocaleString() || 0}</Typography>
                  <Typography>Total GST: ₹{purchaseReport.summary?.total_gst?.toLocaleString() || 0}</Typography>
                </Box>
                {renderVoucherTable(purchaseReport.vouchers || [], 'Purchase Vouchers', 'purchase', {
                  vendor_id: purchaseFilters.vendor_id,
                  search: purchaseFilters.search
                })}
              </>
            ) : (
              <Typography>No purchase data available</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <Typography variant="h6">Inventory Status</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={inventoryFilters.include_zero_stock}
                    onChange={(e) => setInventoryFilters(prev => ({ ...prev, include_zero_stock: e.target.checked }))}
                  />
                }
                label="Include Zero Stock"
              />
              <TextField
                label="Search Products"
                placeholder="Search products..."
                value={inventoryFilters.search}
                onChange={(e) => setInventoryFilters(prev => ({ ...prev, search: e.target.value }))}
                size="small"
                sx={{ minWidth: 200 }}
              />
              <Button variant="contained" startIcon={<Refresh />} onClick={() => refetchInventory()}>
                Refresh
              </Button>
            </Box>
            
            {inventoryLoading ? (
              <Typography>Loading inventory report...</Typography>
            ) : inventoryReport ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <Typography>Total Items: {inventoryReport.summary?.total_items || 0}</Typography>
                  <Typography>Total Value: ₹{inventoryReport.summary?.total_value?.toLocaleString() || 0}</Typography>
                  <Typography>Low Stock Items: {inventoryReport.summary?.low_stock_items || 0}</Typography>
                </Box>
                <TableContainer component={Paper}>
                  <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Inventory Items</Typography>
                    <ExportPrintToolbar
                      onExportExcel={() => reportsService.exportInventoryReportExcel({
                        include_zero_stock: inventoryFilters.include_zero_stock
                      })}
                      filename="inventory_report"
                      showCSV={false}
                      onPrint={() => window.print()}
                    />
                  </Box>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Unit</TableCell>
                        <TableCell>Unit Price</TableCell>
                        <TableCell>Total Value</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {inventoryReport.items?.map((item: any) => (
                        <TableRow key={item.product_id}>
                          <TableCell>{item.product_name}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>{item.unit}</TableCell>
                          <TableCell>₹{item.unit_price.toLocaleString()}</TableCell>
                          <TableCell>₹{item.total_value.toLocaleString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={item.is_low_stock ? 'Low Stock' : 'Normal'}
                              color={item.is_low_stock ? 'warning' : 'success'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : (
              <Typography>No inventory data available</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <Typography variant="h6">Pending Orders</Typography>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Order Type</InputLabel>
                <Select
                  value={pendingOrdersFilters.order_type}
                  label="Order Type"
                  onChange={(e) => setPendingOrdersFilters(prev => ({ ...prev, order_type: e.target.value }))}
                >
                  <MenuItem value="all">All Orders</MenuItem>
                  <MenuItem value="purchase">Purchase Orders</MenuItem>
                  <MenuItem value="sales">Sales Orders</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Search Orders"
                placeholder="Search orders..."
                value={pendingOrdersFilters.search}
                onChange={(e) => setPendingOrdersFilters(prev => ({ ...prev, search: e.target.value }))}
                size="small"
                sx={{ minWidth: 200 }}
              />
              <Button variant="contained" startIcon={<Refresh />} onClick={() => refetchOrders()}>
                Refresh
              </Button>
            </Box>
            
            {ordersLoading ? (
              <Typography>Loading pending orders...</Typography>
            ) : pendingOrders ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <Typography>Total Orders: {pendingOrders.summary?.total_orders || 0}</Typography>
                  <Typography>Total Value: ₹{pendingOrders.summary?.total_value?.toLocaleString() || 0}</Typography>
                </Box>
                <TableContainer component={Paper}>
                  <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Pending Orders</Typography>
                    <ExportPrintToolbar
                      onExportExcel={() => reportsService.exportPendingOrdersExcel({
                        order_type: pendingOrdersFilters.order_type
                      })}
                      filename="pending_orders_report"
                      showCSV={false}
                      onPrint={() => window.print()}
                    />
                  </Box>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Order #</TableCell>
                        <TableCell>Date</TableCell>
                        <TableCell>Party</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingOrders.orders?.map((order: any) => (
                        <TableRow key={`${order.type}-${order.id}`}>
                          <TableCell>{order.type}</TableCell>
                          <TableCell>{order.number}</TableCell>
                          <TableCell>{new Date(order.date).toLocaleDateString()}</TableCell>
                          <TableCell>{order.party}</TableCell>
                          <TableCell>₹{order.amount.toLocaleString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={order.status}
                              color={order.status === 'pending' ? 'warning' : 'default'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : (
              <Typography>No pending orders</Typography>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={5}>
            {!canAccessLedger(user) ? (
              <Alert severity="warning">
                You don't have permission to access the Ledger report. Contact your administrator for access.
              </Alert>
            ) : (
              <>
                <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                  <Typography variant="h6" sx={{ mr: 2 }}>
                    Ledger Report
                  </Typography>
                  
                  {/* Ledger Type Toggle */}
                  <FormControlLabel
                    control={
                      <Switch
                        checked={ledgerType === 'outstanding'}
                        onChange={(e) => handleLedgerTypeChange(e.target.checked ? 'outstanding' : 'complete')}
                        color="primary"
                      />
                    }
                    label={ledgerType === 'complete' ? 'Complete Ledger' : 'Outstanding Ledger'}
                    sx={{ mr: 2 }}
                  />

                  {/* Date Range Filters */}
                  <TextField
                    label="Start Date"
                    type="date"
                    value={ledgerFilters.start_date}
                    onChange={(e) => handleLedgerFilterChange('start_date', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    size="small"
                    sx={{ minWidth: 140 }}
                  />
                  <TextField
                    label="End Date"
                    type="date"
                    value={ledgerFilters.end_date}
                    onChange={(e) => handleLedgerFilterChange('end_date', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    size="small"
                    sx={{ minWidth: 140 }}
                  />

                  {/* Account Type Filter */}
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Account Type</InputLabel>
                    <Select
                      value={ledgerFilters.account_type}
                      label="Account Type"
                      onChange={(e) => handleLedgerFilterChange('account_type', e.target.value)}
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="vendor">Vendors</MenuItem>
                      <MenuItem value="customer">Customers</MenuItem>
                    </Select>
                  </FormControl>

                  {/* Voucher Type Filter */}
                  <FormControl size="small" sx={{ minWidth: 140 }}>
                    <InputLabel>Voucher Type</InputLabel>
                    <Select
                      value={ledgerFilters.voucher_type}
                      label="Voucher Type"
                      onChange={(e) => handleLedgerFilterChange('voucher_type', e.target.value)}
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="purchase_voucher">Purchase</MenuItem>
                      <MenuItem value="sales_voucher">Sales</MenuItem>
                      <MenuItem value="payment_voucher">Payment</MenuItem>
                      <MenuItem value="receipt_voucher">Receipt</MenuItem>
                      <MenuItem value="debit_note">Debit Note</MenuItem>
                      <MenuItem value="credit_note">Credit Note</MenuItem>
                    </Select>
                  </FormControl>

                  <Button 
                    variant="contained" 
                    startIcon={<Refresh />} 
                    onClick={() => ledgerType === 'complete' ? refetchCompleteLedger() : refetchOutstandingLedger()}
                  >
                    Refresh
                  </Button>
                </Box>

                {/* Complete Ledger View */}
                {ledgerType === 'complete' && (
                  <>
                    {completeLedgerLoading ? (
                      <Typography>Loading complete ledger...</Typography>
                    ) : completeLedger ? (
                      <>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="h6">Summary</Typography>
                          <Typography>Total Transactions: {completeLedger.summary?.transaction_count || 0}</Typography>
                          <Typography>Total Debit: ₹{Number(completeLedger.total_debit || 0).toLocaleString()}</Typography>
                          <Typography>Total Credit: ₹{Number(completeLedger.total_credit || 0).toLocaleString()}</Typography>
                          <Typography>Net Balance: ₹{Number(completeLedger.net_balance || 0).toLocaleString()}</Typography>
                        </Box>
                        <TableContainer component={Paper}>
                          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="h6">Complete Ledger Transactions</Typography>
                            <ExportPrintToolbar
                              onExportExcel={() => reportsService.exportCompleteLedgerExcel(ledgerFilters)}
                              filename="complete_ledger_report"
                              showCSV={false}
                              onPrint={() => window.print()}
                            />
                          </Box>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Date</TableCell>
                                <TableCell>Voucher Type</TableCell>
                                <TableCell>Voucher #</TableCell>
                                <TableCell>Account</TableCell>
                                <TableCell>Debit</TableCell>
                                <TableCell>Credit</TableCell>
                                <TableCell>Balance</TableCell>
                                <TableCell>Status</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {completeLedger.transactions?.map((transaction: any) => (
                                <TableRow key={`${transaction.voucher_type}-${transaction.id}`}>
                                  <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                                  <TableCell>{transaction.voucher_type.replace('_', ' ').toUpperCase()}</TableCell>
                                  <TableCell>{transaction.voucher_number}</TableCell>
                                  <TableCell>{transaction.account_name}</TableCell>
                                  <TableCell>₹{Number(transaction.debit_amount || 0).toLocaleString()}</TableCell>
                                  <TableCell>₹{Number(transaction.credit_amount || 0).toLocaleString()}</TableCell>
                                  <TableCell>₹{Number(transaction.balance || 0).toLocaleString()}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={transaction.status}
                                      color={transaction.status === 'confirmed' ? 'success' : 'default'}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </>
                    ) : (
                      <Typography>No complete ledger data available</Typography>
                    )}
                  </>
                )}

                {/* Outstanding Ledger View */}
                {ledgerType === 'outstanding' && (
                  <>
                    {outstandingLedgerLoading ? (
                      <Typography>Loading outstanding ledger...</Typography>
                    ) : outstandingLedger ? (
                      <>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="h6">Outstanding Balances Summary</Typography>
                          <Typography>Total Accounts: {outstandingLedger.summary?.total_accounts || 0}</Typography>
                          <Typography color="error">
                            Total Payable: ₹{Math.abs(Number(outstandingLedger.total_payable || 0)).toLocaleString()} 
                            (Amount owed to vendors)
                          </Typography>
                          <Typography color="success.main">
                            Total Receivable: ₹{Number(outstandingLedger.total_receivable || 0).toLocaleString()} 
                            (Amount owed by customers)
                          </Typography>
                          <Typography>
                            Net Outstanding: ₹{Number(outstandingLedger.net_outstanding || 0).toLocaleString()}
                          </Typography>
                        </Box>
                        <TableContainer component={Paper}>
                          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="h6">Outstanding Balances</Typography>
                            <ExportPrintToolbar
                              onExportExcel={() => reportsService.exportOutstandingLedgerExcel(ledgerFilters)}
                              filename="outstanding_ledger_report"
                              showCSV={false}
                              onPrint={() => window.print()}
                            />
                          </Box>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Account Type</TableCell>
                                <TableCell>Account Name</TableCell>
                                <TableCell>Outstanding Amount</TableCell>
                                <TableCell>Last Transaction</TableCell>
                                <TableCell>Transaction Count</TableCell>
                                <TableCell>Contact</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {outstandingLedger.outstanding_balances?.map((balance: any) => (
                                <TableRow key={`${balance.account_type}-${balance.account_id}`}>
                                  <TableCell>
                                    <Chip
                                      label={balance.account_type.toUpperCase()}
                                      color={balance.account_type === 'vendor' ? 'warning' : 'info'}
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell>{balance.account_name}</TableCell>
                                  <TableCell>
                                    <Typography 
                                      color={balance.outstanding_amount < 0 ? 'error' : 'success.main'}
                                      fontWeight="bold"
                                    >
                                      ₹{Math.abs(Number(balance.outstanding_amount || 0)).toLocaleString()}
                                      {balance.outstanding_amount < 0 && ' (Payable)'}
                                      {balance.outstanding_amount > 0 && ' (Receivable)'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    {balance.last_transaction_date 
                                      ? new Date(balance.last_transaction_date).toLocaleDateString()
                                      : 'N/A'
                                    }
                                  </TableCell>
                                  <TableCell>{balance.transaction_count || 0}</TableCell>
                                  <TableCell>{balance.contact_info || 'N/A'}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </>
                    ) : (
                      <Typography>No outstanding ledger data available</Typography>
                    )}
                  </>
                )}
              </>
            )}
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
};

export default ReportsPage;