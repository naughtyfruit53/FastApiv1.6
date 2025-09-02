"use client";
// frontend/src/pages/demo.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Switch,
  FormControlLabel,
  Grid,
} from "@mui/material";
import {
  Receipt,
  Inventory,
  People,
  Business,
  Warning,
  ExitToApp,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
// Mock/Sample data for demo mode
const _mockData = {
  stats: [
    {
      title: "Purchase Vouchers",
      value: 15,
      icon: <Receipt />,
      color: "#1976D2",
    },
    {
      title: "Sales Vouchers",
      value: 23,
      icon: <Receipt />,
      color: "#2E7D32",
    },
    {
      title: "Low Stock Items",
      value: 5,
      icon: <Warning />,
      color: "#F57C00",
    },
    {
      title: "Active Products",
      value: 148,
      icon: <People />,
      color: "#7B1FA2",
    },
  ],
  purchaseVouchers: [
    {
      id: 1,
      voucher_number: "PV-2024-001",
      date: "2024-01-15",
      total_amount: 15750.0,
      status: "confirmed",
      vendor: "ABC Suppliers",
    },
    {
      id: 2,
      voucher_number: "PV-2024-002",
      date: "2024-01-16",
      total_amount: 8950.0,
      status: "pending",
      vendor: "XYZ Materials",
    },
    {
      id: 3,
      voucher_number: "PV-2024-003",
      date: "2024-01-17",
      total_amount: 22100.0,
      status: "confirmed",
      vendor: "Best Parts Inc",
    },
  ],
  salesVouchers: [
    {
      id: 1,
      voucher_number: "SV-2024-001",
      date: "2024-01-15",
      total_amount: 25600.0,
      status: "confirmed",
      customer: "Tech Solutions Ltd",
    },
    {
      id: 2,
      voucher_number: "SV-2024-002",
      date: "2024-01-16",
      total_amount: 18750.0,
      status: "pending",
      customer: "Modern Industries",
    },
    {
      id: 3,
      voucher_number: "SV-2024-003",
      date: "2024-01-17",
      total_amount: 31200.0,
      status: "confirmed",
      customer: "Global Corp",
    },
  ],
  companyInfo: {
    name: "Demo Manufacturing Company",
    address: "123 Demo Street, Sample City",
    phone: "+91-9876543210",
    email: "demo@example.com",
    gst: "24AAACC1206D1ZV",
  },
};
export default function DemoPage() {
  const _router = useRouter();
  const [demoMode, setDemoMode] = useState(true);
  const [isDemoTempUser, setIsDemoTempUser] = useState(false);
  useEffect(() => {
    // Set demo mode flag
    localStorage.setItem("demoMode", demoMode.toString());
    // Check if this is a temporary demo user
    const _tempUser = localStorage.getItem("isDemoTempUser");
    setIsDemoTempUser(tempUser === "true");
  }, [demoMode]);
  const _handleExitDemo = () => {
    localStorage.removeItem("demoMode");
    localStorage.removeItem("isDemoTempUser");
    // If this was a temporary demo user, redirect to login
    if (isDemoTempUser) {
      localStorage.removeItem("token");
      localStorage.removeItem("user_role");
      router.push("/login");
    } else {
      // Regular user, go back to dashboard
      router.push("/dashboard");
    }
  };
  const _handleToggleDemo = () => {
    setDemoMode(!demoMode);
    if (!demoMode) {
      localStorage.setItem("demoMode", "true");
    } else {
      localStorage.removeItem("demoMode");
    }
  };
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Demo Mode Alert */}
        <Alert
          severity="info"
          sx={{ mb: 3 }}
          action={
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={demoMode}
                    onChange={handleToggleDemo}
                    color="primary"
                  />
                }
                label="Demo Mode"
              />
              <Button
                color="inherit"
                size="small"
                onClick={handleExitDemo}
                startIcon={<ExitToApp />}
              >
                {isDemoTempUser ? "End Demo Session" : "Exit Demo"}
              </Button>
            </Box>
          }
        >
          <Typography variant="h6" component="div">
            🎭 Demo Mode Active {isDemoTempUser && "(Temporary User)"}
          </Typography>
          <Typography variant="body2">
            You are viewing the organization dashboard with sample data. This is
            not real business data. All functionality is simulated for
            demonstration purposes.
            {isDemoTempUser &&
              " Your temporary session will end when you logout or close the browser."}
          </Typography>
        </Alert>
        {/* Additional alert for temporary demo users */}
        {isDemoTempUser && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Temporary Demo Account:</strong> You are using a temporary
              demo account that was created for this session only. No real user
              account has been created in the system. When you end this session,
              all temporary data will be cleared.
            </Typography>
          </Alert>
        )}
        <Typography variant="h4" component="h1" gutterBottom>
          Organization Dashboard - Demo Mode
        </Typography>
        {/* Company Info Card */}
        <Paper
          sx={{
            p: 2,
            mb: 3,
            bgcolor: "primary.light",
            color: "primary.contrastText",
          }}
        >
          <Typography variant="h6" gutterBottom>
            {mockData.companyInfo.name}
          </Typography>
          <Typography variant="body2">
            {mockData.companyInfo.address} • {mockData.companyInfo.phone} •{" "}
            {mockData.companyInfo.email}
          </Typography>
          <Typography variant="body2">
            GST: {mockData.companyInfo.gst}
          </Typography>
        </Paper>
        <Grid container spacing={3}>
          {/* Statistics Cards */}
          {mockData.stats.map((_stat, _index) => (
            <Grid
              key={index}
              size={{
                xs: 12,
                sm: 6,
                md: 3,
              }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <Box sx={{ color: stat.color, mr: 2 }}>{stat.icon}</Box>
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        {stat.title}
                      </Typography>
                      <Typography variant="h4" component="h2">
                        {stat.value}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {/* Recent Purchase Vouchers */}
          <Grid
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Purchase Vouchers (Sample Data)
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockData.purchaseVouchers.map((_voucher) => (
                      <TableRow key={voucher.id}>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>
                          {new Date(voucher.date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          ₹{voucher.total_amount.toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={voucher.status}
                            color={
                              voucher.status === "confirmed"
                                ? "success"
                                : "default"
                            }
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          {/* Recent Sales Vouchers */}
          <Grid
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Sales Vouchers (Sample Data)
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockData.salesVouchers.map((_voucher) => (
                      <TableRow key={voucher.id}>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>
                          {new Date(voucher.date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          ₹{voucher.total_amount.toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={voucher.status}
                            color={
                              voucher.status === "confirmed"
                                ? "success"
                                : "default"
                            }
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          {/* Demo Features - Comprehensive Feature Showcase */}
          <Grid size={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
                🎯 Complete Feature Showcase - All Live Features Available
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Explore all features of the TRITIQ ERP system with sample data.
                This demo provides access to every module and functionality.
              </Typography>
              {/* Master Data Section */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                👥 Master Data Management
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/masters/vendors")}
                  >
                    Vendors Management
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Business />}
                    onClick={() => router.push("/masters/customers")}
                  >
                    Customers Management
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Inventory />}
                    onClick={() => router.push("/masters/products")}
                  >
                    Products Catalog
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Business />}
                    onClick={() => router.push("/masters?tab=company")}
                  >
                    Company Details
                  </Button>
                </Grid>
              </Grid>
              {/* Inventory Management */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                📦 Inventory Management
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Inventory />}
                    onClick={() => router.push("/inventory/stock")}
                  >
                    Current Stock
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/inventory/movements")}
                  >
                    Stock Movements
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Warning />}
                    onClick={() => router.push("/inventory/low-stock")}
                  >
                    Low Stock Report
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<ExitToApp />}
                    onClick={() => router.push("/inventory/bulk-import")}
                  >
                    Bulk Import Tools
                  </Button>
                </Grid>
              </Grid>
              {/* Voucher System */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                🧾 Complete Voucher System
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() =>
                      router.push("/vouchers/Purchase-Vouchers/purchase-order")
                    }
                  >
                    Purchase Orders
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() =>
                      router.push("/vouchers/Sales-Vouchers/sales-voucher")
                    }
                  >
                    Sales Vouchers
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() =>
                      router.push(
                        "/vouchers/Financial-Vouchers/payment-voucher",
                      )
                    }
                  >
                    Financial Vouchers
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() =>
                      router.push(
                        "/vouchers/Manufacturing-Vouchers/production-order",
                      )
                    }
                  >
                    Manufacturing Orders
                  </Button>
                </Grid>
              </Grid>
              {/* Analytics & Reports */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                📊 Business Intelligence & Analytics
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/analytics/customer")}
                  >
                    Customer Analytics
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/analytics/sales")}
                  >
                    Sales Analytics
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/analytics/purchase")}
                  >
                    Purchase Analytics
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/analytics/service")}
                  >
                    Service Analytics
                  </Button>
                </Grid>
              </Grid>
              {/* Service CRM Features */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                🔧 Service CRM & Operations
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/service/dashboard")}
                  >
                    Service Dashboard
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/service/dispatch")}
                  >
                    Dispatch Management
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/service/feedback")}
                  >
                    Feedback Workflow
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/sla")}
                  >
                    SLA Management
                  </Button>
                </Grid>
              </Grid>
              {/* Reports & Financial */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                📈 Reports & Financial Analysis
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/reports/ledgers")}
                  >
                    Ledger Reports
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/reports/trial-balance")}
                  >
                    Trial Balance
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/reports/profit-loss")}
                  >
                    Profit & Loss
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Inventory />}
                    onClick={() => router.push("/reports/stock")}
                  >
                    Stock Reports
                  </Button>
                </Grid>
              </Grid>
              {/* Administration Features */}
              <Typography
                variant="h6"
                gutterBottom
                sx={{ mt: 3, mb: 2, color: "primary.main" }}
              >
                ⚙️ Administration & Management
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/admin/rbac")}
                  >
                    Role Management
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/admin/audit-logs")}
                  >
                    Audit Logs
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => router.push("/admin/notifications")}
                  >
                    Notifications
                  </Button>
                </Grid>
                <Grid>
                  <Button
                    variant="outlined"
                    startIcon={<People />}
                    onClick={() => router.push("/settings")}
                  >
                    System Settings
                  </Button>
                </Grid>
              </Grid>
              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  <strong>✨ Full Feature Parity:</strong> This demo showcases
                  all live features of the TRITIQ ERP system. Every module,
                  report, and functionality is accessible with sample data for
                  comprehensive testing and evaluation.
                </Typography>
              </Alert>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
