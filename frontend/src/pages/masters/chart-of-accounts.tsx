import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  Card,
  CardContent,
  CircularProgress,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Search,
  AccountBalance,
  AccountTree,
} from "@mui/icons-material";
import api from "../../lib/api";  // Assuming corrected import from previous
import AddEditAccountModal from "../../components/AddEditAccountModal";
import ViewAccountModal from "../../components/ViewAccountModal";

const ChartOfAccountsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<any>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    account_code: "",
    account_name: "",
    account_type: "asset",
    parent_account_id: "",
    is_group: false,
    opening_balance: 0,
    can_post: true,
    is_reconcilable: false,
    description: "",
    notes: "",
    is_active: true,
  });
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const accountTypes = [
    { value: "ASSET", label: "Asset", color: "success" },
    { value: "LIABILITY", label: "Liability", color: "error" },
    { value: "EQUITY", label: "Equity", color: "primary" },
    { value: "INCOME", label: "Income", color: "info" },
    { value: "EXPENSE", label: "Expense", color: "warning" },
    { value: "BANK", label: "Bank", color: "secondary" },
    { value: "CASH", label: "Cash", color: "default" },
  ];

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get("/chart-of-accounts");
      setAccounts(response.data.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch chart of accounts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const resetForm = () => {
    setFormData({
      account_code: "",
      account_name: "",
      account_type: "ASSET",
      parent_account_id: "",
      is_group: false,
      opening_balance: 0,
      can_post: true,
      is_reconcilable: false,
      description: "",
      notes: "",
      is_active: true,
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (account: any) => {
    setSelectedAccount(account);
    setFormData({
      account_code: account.account_code || "",
      account_name: account.account_name || "",
      account_type: account.account_type || "ASSET",
      parent_account_id: account.parent_account_id || "",
      is_group: account.is_group,
      opening_balance: parseFloat(account.opening_balance) || 0,
      can_post: account.can_post,
      is_reconcilable: account.is_reconcilable,
      description: account.description || "",
      notes: account.notes || "",
      is_active: account.is_active,
    });
    setEditDialog(true);
  };

  const handleViewClick = (account: any) => {
    setSelectedAccount(account);
    setViewDialog(true);
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      setSuccessMessage(null);
      let response;
      const payload = { ...formData };
      payload.account_type = payload.account_type.toUpperCase();
      if (selectedAccount) {
        // Update existing account
        response = await api.put(
          `/chart-of-accounts/${selectedAccount.id}`,
          payload,
        );
        setSuccessMessage("Account updated successfully");
      } else {
        // Create new account
        response = await api.post(
          "/chart-of-accounts",
          payload,
        );
        setSuccessMessage("Account created successfully");
      }
      // Refresh accounts list
      fetchAccounts();
      setAddDialog(false);
      setEditDialog(false);
    } catch (err: any) {
      let errorMessage = "Failed to save account";
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Handle Pydantic validation errors (list of dicts)
          errorMessage = detail.map((e: any) => `${e.loc.join(".")}: ${e.msg}`).join("\n");
        } else if (typeof detail === "object") {
          // Handle other object errors
          errorMessage = JSON.stringify(detail);
        }
      }
      setError(errorMessage);
    }
  };

  const handleClose = () => {
    setAddDialog(false);
    setEditDialog(false);
    setViewDialog(false);
  };

  const handleDeleteClick = async (accountId: number) => {
    if (!window.confirm("Are you sure you want to delete this account?")) return;
    try {
      setError(null);
      setSuccessMessage(null);
      await api.delete(`/chart-of-accounts/${accountId}`);
      setSuccessMessage("Account deleted successfully");
      // Refresh accounts list
      fetchAccounts();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete account");
    }
  };

  const handleTypeClick = (type: string) => {
    setSelectedType(selectedType === type ? null : type);
  };

  const filteredAccounts = accounts.filter(
    (account: any) =>
      (selectedType ? account.account_type === selectedType : true) &&
      (account.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_type?.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getAccountTypeColor = (type: string) => {
    const accountType = accountTypes.find((t) => t.value === type);
    return accountType?.color || "default";
  };

  const getTotalByType = (type: string) => {
    return accounts
      .filter((account: any) => account.account_type === type)
      .reduce((sum: number, account: any) => sum + (parseFloat(account.current_balance) || 0), 0);
  };

  const formatCurrency = (value: number) => {
    return value.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4" component="h1">
            Chart of Accounts
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Account
          </Button>
        </Box>
        {/* Account Type Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {accountTypes.map((type) => (
            <Grid item xs={12} sm={6} md={2.4} key={type.value}>
              <Card
                onClick={() => handleTypeClick(type.value)}
                sx={{ cursor: 'pointer' }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <Box>
                      <Typography
                        color="textSecondary"
                        gutterBottom
                        variant="body2"
                      >
                        {type.label}
                      </Typography>
                      <Typography variant="h6" component="h2">
                        ₹{formatCurrency(getTotalByType(type.value))}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {
                          accounts.filter(
                            (acc: any) => acc.account_type === type.value,
                          ).length
                        }{" "}
                        accounts
                      </Typography>
                    </Box>
                    <AccountBalance
                      sx={{ fontSize: 32, color: `${type.color}.main` }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search accounts by name, code, or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: "action.active" }} />,
            }}
          />
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {successMessage}
          </Alert>
        )}
        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Account Code</TableCell>
                  <TableCell>Account Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Balance</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredAccounts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Box sx={{ py: 3 }}>
                        <AccountBalance
                          sx={{ fontSize: 48, color: "action.disabled", mb: 2 }}
                        />
                        <Typography variant="h6" color="textSecondary">
                          No accounts found
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Add your first account to start building your chart of
                          accounts
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredAccounts.map((account: any) => (
                    <TableRow 
                      key={account.id}
                      onClick={() => handleViewClick(account)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {account.account_code}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          <AccountTree sx={{ mr: 2, color: "primary.main" }} />
                          <Typography variant="body1">
                            {account.account_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={
                            account.account_type.charAt(0).toUpperCase() +
                            account.account_type.slice(1)
                          }
                          size="small"
                          color={getAccountTypeColor(account.account_type)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          ₹{formatCurrency(parseFloat(account.current_balance) || 0)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={account.is_active ? "Active" : "Inactive"}
                          color={account.is_active ? "success" : "default"}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditClick(account);
                          }}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteClick(account.id);
                          }}
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <AddEditAccountModal
          open={addDialog || editDialog}
          onClose={handleClose}
          formData={formData}
          setFormData={setFormData}
          accounts={accounts}
          accountTypes={accountTypes}
          selectedAccount={selectedAccount}
          handleSubmit={handleSubmit}
        />
        <ViewAccountModal
          open={viewDialog}
          onClose={handleClose}
          account={selectedAccount}
        />
      </Box>
    </Container>
  );
};
export default ChartOfAccountsPage;