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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Assignment as AssignmentIcon,
} from "@mui/icons-material";
import { formatCurrency } from "../../utils/currencyUtils";
import { ProtectedPage } from "../../components/ProtectedPage";
interface Account {
  id: number;
  name: string;
  type: "customer" | "prospect" | "partner" | "vendor";
  industry: string;
  size: "small" | "medium" | "large" | "enterprise";
  revenue: number;
  employees: number;
  website: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  status: "active" | "inactive" | "prospect";
  parentAccount: string | null;
  accountManager: string;
  source: string;
  created_at: string;
  lastActivity: string;
  description: string;
  totalContracts: number;
  totalRevenue: number;
  primaryContact: string;
}
const AccountManagement: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [editedAccount, setEditedAccount] = useState<Account | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<"view" | "edit" | "create">(
    "view",
  );
  const [tabValue, setTabValue] = useState(0);
  
  // Fetch accounts from backend
  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/v1/accounts", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      } else {
        setError("Failed to load accounts");
      }
    } catch (err) {
      setError("Failed to load accounts");
      console.error("Error fetching accounts:", err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchAccounts();
  }, []);
  const filteredAccounts = accounts.filter((account) => {
    const matchesSearch =
      account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.accountManager.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || account.type === filterType;
    const matchesStatus =
      filterStatus === "all" || account.status === filterStatus;
    return matchesSearch && matchesType && matchesStatus;
  });
  const handleViewAccount = (account: Account) => {
    setEditedAccount(account);
    setDialogMode("view");
    setDialogOpen(true);
  };
  const handleEditAccount = (account: Account) => {
    setEditedAccount(account);
    setDialogMode("edit");
    setDialogOpen(true);
  };
  const handleCreateAccount = () => {
    setEditedAccount({
      id: 0,
      name: "",
      type: "customer",
      industry: "",
      size: "small",
      revenue: 0,
      employees: 0,
      website: "",
      phone: "",
      email: "",
      address: "",
      city: "",
      state: "",
      zipCode: "",
      country: "",
      status: "active",
      parentAccount: null,
      accountManager: "",
      source: "",
      created_at: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
      description: "",
      totalContracts: 0,
      totalRevenue: 0,
      primaryContact: "",
    });
    setDialogMode("create");
    setDialogOpen(true);
  };
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditedAccount(null);
    setTabValue(0);
  };
  const handleSave = async () => {
    if (!editedAccount) return;
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const url = dialogMode === "create" ? "/api/v1/accounts" : `/api/v1/accounts/${editedAccount.id}`;
      const method = dialogMode === "create" ? "POST" : "PUT";
      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(editedAccount),
      });
      if (response.ok) {
        fetchAccounts();
        handleCloseDialog();
      } else {
        setError("Failed to save account");
      }
    } catch (err) {
      setError("Error saving account");
    } finally {
      setLoading(false);
    }
  };
  const getTypeColor = (type: string) => {
    switch (type) {
      case "customer":
        return "success";
      case "prospect":
        return "primary";
      case "partner":
        return "warning";
      case "vendor":
        return "info";
      default:
        return "default";
    }
  };
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
  const getSizeColor = (size: string) => {
    switch (size) {
      case "enterprise":
        return "error";
      case "large":
        return "warning";
      case "medium":
        return "primary";
      case "small":
        return "success";
      default:
        return "default";
    }
  };
  const accountStats = {
    total: accounts.length,
    customers: accounts.filter((a) => a.type === "customer").length,
    prospects: accounts.filter((a) => a.type === "prospect").length,
    totalRevenue: accounts.reduce((sum, a) => sum + a.totalRevenue, 0),
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
      </Container>
    );
  }
  return (
    <ProtectedPage moduleKey="sales" action="read">
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Account Management
      </Typography>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Accounts
              </Typography>
              <Typography variant="h4">{accountStats.total}</Typography>
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
                {accountStats.customers}
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
                {accountStats.prospects}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h4" color="success.main">
                {formatCurrency(accountStats.totalRevenue)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Filters and Actions */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
          flexWrap: "wrap",
          gap: 2,
        }}
      >
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          <TextField
            placeholder="Search accounts..."
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
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filterType}
              label="Type"
              onChange={(e) => setFilterType(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
              <MenuItem value="prospect">Prospect</MenuItem>
              <MenuItem value="partner">Partner</MenuItem>
              <MenuItem value="vendor">Vendor</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              label="Status"
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="prospect">Prospect</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateAccount}
        >
          Add Account
        </Button>
      </Box>
      {/* Accounts Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Account Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Industry</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Revenue</TableCell>
              <TableCell>Account Manager</TableCell>
              <TableCell>Last Activity</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAccounts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 8 }}>
                  <Box>
                    <Typography variant="h6" color="textSecondary" gutterBottom>
                      No accounts found
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      {searchTerm || filterType !== "all" || filterStatus !== "all"
                        ? "Try adjusting your filters"
                        : "Get started by adding your first account"}
                    </Typography>
                    {!searchTerm && filterType === "all" && filterStatus === "all" && (
                      <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleCreateAccount}
                      >
                        Add Account
                      </Button>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              filteredAccounts.map((account) => (
              <TableRow key={account.id} hover>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
                      {account.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {account.city}, {account.state}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={account.type}
                    color={getTypeColor(account.type) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{account.industry}</TableCell>
                <TableCell>
                  <Chip
                    label={account.size}
                    color={getSizeColor(account.size) as any}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={account.status}
                    color={getStatusColor(account.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(account.totalRevenue)}
                </TableCell>
                <TableCell>{account.accountManager}</TableCell>
                <TableCell>
                  {new Date(account.lastActivity).toLocaleDateString()}
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={() => handleViewAccount(account)}
                    title="View Details"
                  >
                    <ViewIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleEditAccount(account)}
                    title="Edit Account"
                  >
                    <EditIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {/* Account Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === "create"
            ? "Add New Account"
            : dialogMode === "edit"
              ? "Edit Account"
              : "Account Details"}
        </DialogTitle>
        <DialogContent>
          {editedAccount && (
            <Box sx={{ mt: 2 }}>
              <Tabs
                value={tabValue}
                onChange={(e, newValue) => setTabValue(newValue)}
              >
                <Tab label="General Information" />
                <Tab label="Contact Details" />
                <Tab label="Business Information" />
                <Tab label="Activity & Notes" />
              </Tabs>
              {tabValue === 0 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account Name"
                      value={editedAccount.name}
                      onChange={(e) => setEditedAccount({...editedAccount, name: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === "view"}>
                      <InputLabel>Account Type</InputLabel>
                      <Select 
                        value={editedAccount.type} 
                        label="Account Type"
                        onChange={(e) => setEditedAccount({...editedAccount, type: e.target.value as "customer" | "prospect" | "partner" | "vendor"})}
                      >
                        <MenuItem value="customer">Customer</MenuItem>
                        <MenuItem value="prospect">Prospect</MenuItem>
                        <MenuItem value="partner">Partner</MenuItem>
                        <MenuItem value="vendor">Vendor</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Industry"
                      value={editedAccount.industry}
                      onChange={(e) => setEditedAccount({...editedAccount, industry: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === "view"}>
                      <InputLabel>Company Size</InputLabel>
                      <Select 
                        value={editedAccount.size} 
                        label="Company Size"
                        onChange={(e) => setEditedAccount({...editedAccount, size: e.target.value as "small" | "medium" | "large" | "enterprise"})}
                      >
                        <MenuItem value="small">Small (1-50)</MenuItem>
                        <MenuItem value="medium">Medium (51-500)</MenuItem>
                        <MenuItem value="large">Large (501-5000)</MenuItem>
                        <MenuItem value="enterprise">
                          Enterprise (5000+)
                        </MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === "view"}>
                      <InputLabel>Status</InputLabel>
                      <Select 
                        value={editedAccount.status} 
                        label="Status"
                        onChange={(e) => setEditedAccount({...editedAccount, status: e.target.value as "active" | "inactive" | "prospect"})}
                      >
                        <MenuItem value="active">Active</MenuItem>
                        <MenuItem value="prospect">Prospect</MenuItem>
                        <MenuItem value="inactive">Inactive</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account Manager"
                      value={editedAccount.accountManager}
                      onChange={(e) => setEditedAccount({...editedAccount, accountManager: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Parent Account"
                      value={editedAccount.parentAccount || ""}
                      onChange={(e) => setEditedAccount({...editedAccount, parentAccount: e.target.value || null})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                </Grid>
              )}
              {tabValue === 1 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={editedAccount.phone}
                      onChange={(e) => setEditedAccount({...editedAccount, phone: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={editedAccount.email}
                      onChange={(e) => setEditedAccount({...editedAccount, email: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Website"
                      value={editedAccount.website}
                      onChange={(e) => setEditedAccount({...editedAccount, website: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Primary Contact"
                      value={editedAccount.primaryContact}
                      onChange={(e) => setEditedAccount({...editedAccount, primaryContact: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      value={editedAccount.address}
                      onChange={(e) => setEditedAccount({...editedAccount, address: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="City"
                      value={editedAccount.city}
                      onChange={(e) => setEditedAccount({...editedAccount, city: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="State"
                      value={editedAccount.state}
                      onChange={(e) => setEditedAccount({...editedAccount, state: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Zip Code"
                      value={editedAccount.zipCode}
                      onChange={(e) => setEditedAccount({...editedAccount, zipCode: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Country"
                      value={editedAccount.country}
                      onChange={(e) => setEditedAccount({...editedAccount, country: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                </Grid>
              )}
              {tabValue === 2 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Annual Revenue"
                      type="number"
                      value={editedAccount.revenue}
                      onChange={(e) => setEditedAccount({...editedAccount, revenue: parseFloat(e.target.value) || 0})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Number of Employees"
                      type="number"
                      value={editedAccount.employees}
                      onChange={(e) => setEditedAccount({...editedAccount, employees: parseFloat(e.target.value) || 0})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Total Contracts"
                      type="number"
                      value={editedAccount.totalContracts}
                      onChange={(e) => setEditedAccount({...editedAccount, totalContracts: parseFloat(e.target.value) || 0})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Total Revenue with Us"
                      type="number"
                      value={editedAccount.totalRevenue}
                      onChange={(e) => setEditedAccount({...editedAccount, totalRevenue: parseFloat(e.target.value) || 0})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Description"
                      multiline
                      rows={4}
                      value={editedAccount.description}
                      onChange={(e) => setEditedAccount({...editedAccount, description: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                </Grid>
              )}
              {tabValue === 3 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Source"
                      value={editedAccount.source}
                      onChange={(e) => setEditedAccount({...editedAccount, source: e.target.value})}
                      disabled={dialogMode === "view"}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Last Activity Date"
                      type="date"
                      value={editedAccount.lastActivity.split('T')[0]}
                      onChange={(e) => setEditedAccount({...editedAccount, lastActivity: new Date(e.target.value).toISOString()})}
                      disabled={dialogMode === "view"}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Recent Activities
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <AssignmentIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Contract Renewal Discussion"
                          secondary="Meeting scheduled with decision makers - Jan 20, 2024"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <EmailIcon color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Proposal Sent"
                          secondary="Detailed proposal sent for Q2 implementation - Jan 15, 2024"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <PhoneIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Follow-up Call"
                          secondary="Discussed technical requirements - Jan 10, 2024"
                        />
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === "view" ? "Close" : "Cancel"}
          </Button>
          {dialogMode !== "view" && (
            <Button variant="contained" onClick={handleSave} disabled={loading}>
              {dialogMode === "create" ? "Create" : "Save"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
    </ProtectedPage>
  );
};
export default AccountManagement;