"use client";

import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
  Tooltip,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
} from "@mui/icons-material";
import { useRouter } from "next/router";

interface Customer {
  id: number;
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  status: "active" | "inactive" | "prospect";
  created_at: string;
}

const SalesCustomerDatabase: React.FC = () => {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Define logout function
  const logout = () => {
    localStorage.removeItem("access_token");
    router.push("/login");
  };

  // Fetch customers from master data API
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    const fetchCustomers = async () => {
      if (!token) {
        setError("No authentication token found. Please log in.");
        setLoading(false);
        router.push("/login");
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch with Authorization header
        const response = await fetch("/api/v1/customers", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error("API Error:", response.status, response.statusText, errorText);
          if (response.status === 401) {
            setError("Session expired. Please log in again.");
            logout();
            return;
          }
          throw new Error(`Failed to fetch customers: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();

        // Map master customer data to sales customer format
        const mappedCustomers: Customer[] = data.map((customer: any) => ({
          id: customer.id,
          name: customer.name || customer.customer_name || "Unknown",
          contact_person: customer.contact_person || customer.contact_name || "",
          email: customer.email || customer.contact_email || "",
          phone: customer.phone || customer.contact_number || "",
          address: customer.address || customer.address1 || "",
          city: customer.city || "",
          state: customer.state || "",
          status: customer.is_active ? "active" : "inactive",
          created_at: customer.created_at || new Date().toISOString(),
        }));

        setCustomers(mappedCustomers);
      } catch (err: any) {
        console.error("Error fetching customers:", err);
        setError(`Failed to load customers: ${err.message}. Please check your connection or try logging in again.`);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, [router]); // Depend on router only, as token is checked within useEffect

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.contact_person
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "prospect":
        return "primary";
      case "inactive":
        return "default";
      default:
        return "default";
    }
  };

  const handleGoToMasterCustomers = () => {
    router.push("/masters/customers");
  };

  const handleViewCustomerAnalytics = (customerId: number) => {
    router.push(`/analytics/customer?id=${customerId}`);
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button variant="contained" onClick={() => router.push("/login")} sx={{ mt: 2 }}>
          Go to Login
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Customer Database
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Customers
              </Typography>
              <Typography variant="h4">{customers.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Customers
              </Typography>
              <Typography variant="h4" color="success.main">
                {customers.filter((c) => c.status === "active").length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Prospects
              </Typography>
              <Typography variant="h4" color="primary.main">
                {customers.filter((c) => c.status === "prospect").length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                This Month
              </Typography>
              <Typography variant="h4">
                {
                  customers.filter(
                    (c) =>
                      new Date(c.created_at).getMonth() ===
                      new Date().getMonth(),
                  ).length
                }
              </Typography>
              <Typography variant="body2" color="textSecondary">
                New customers
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Bar */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <TextField
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => router.push("/sales/customer-analytics")}
          >
            View Analytics
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleGoToMasterCustomers}
          >
            Add Customer
          </Button>
        </Box>
      </Box>

      {/* Customers Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer Name</TableCell>
              <TableCell>Contact Person</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Customer Since</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredCustomers.map((customer) => (
              <TableRow key={customer.id} hover>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <BusinessIcon sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="subtitle2">{customer.name}</Typography>
                  </Box>
                </TableCell>
                <TableCell>{customer.contact_person}</TableCell>
                <TableCell>{customer.email}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>
                  {customer.city}, {customer.state}
                </TableCell>
                <TableCell>
                  <Chip
                    label={customer.status}
                    color={getStatusColor(customer.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(customer.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      onClick={() =>
                        router.push(`/masters/customers?action=view&id=${customer.id}`)
                      }
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit Customer">
                    <IconButton
                      size="small"
                      onClick={() =>
                        router.push(`/masters/customers?action=edit&id=${customer.id}`)
                      }
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Customer Analytics">
                    <IconButton
                      size="small"
                      onClick={() => handleViewCustomerAnalytics(customer.id)}
                    >
                      <AnalyticsIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Integration Footer */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: "grey.50", borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary">
          <strong>Note:</strong> This customer database is integrated with the
          Master Data management system. All customer records are synchronized
          and any changes made here will be reflected in master data and vice
          versa.
        </Typography>
      </Box>
    </Container>
  );
};

export default SalesCustomerDatabase;