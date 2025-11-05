import React, { useState } from "react";
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  FormControlLabel,
  Checkbox,
  Autocomplete,
  Menu,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Search,
  AccountBalance,
  TrendingUp,
  Folder,
  MoreVert,
  FileUpload,
  FileDownload,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../lib/api";
import { useSnackbar } from "notistack";
import BulkImportExportProgressBar from "../../components/BulkImportExportProgressBar";
import { ProtectedPage } from "../../components/ProtectedPage";

interface ExpenseAccount {
  id?: number;
  account_code: string;
  account_name: string;
  parent_account_id?: number | null;
  category?: string;
  sub_category?: string;
  opening_balance?: number;
  current_balance?: number;
  budgeted_amount?: number;
  is_active: boolean;
  is_group: boolean;
  can_post: boolean;
  requires_approval: boolean;
  coa_account_id?: number | null;
  description?: string;
  notes?: string;
  tags?: string;
}

const ExpenseAccountsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<ExpenseAccount | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [importExportState, setImportExportState] = useState({
    isProcessing: false,
    progress: 0,
    type: 'import' as 'import' | 'export',
    status: 'idle' as 'idle' | 'processing' | 'success' | 'error',
    message: '',
    error: '',
    fileName: '',
  });
  const [formData, setFormData] = useState<Partial<ExpenseAccount>>({
    account_code: "",
    account_name: "",
    parent_account_id: null,
    category: "",
    sub_category: "",
    opening_balance: 0,
    budgeted_amount: 0,
    is_active: true,
    is_group: false,
    can_post: true,
    requires_approval: false,
    description: "",
    notes: "",
    tags: "",
  });

  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  // Fetch expense accounts
  const { data: accountsData, isLoading } = useQuery({
    queryKey: ["expense-accounts"],
    queryFn: async () => {
      const response = await api.get("/v1/expense-accounts?per_page=1000");
      return response.data;
    },
  });

  const accounts = accountsData?.items || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: Partial<ExpenseAccount>) =>
      api.post("/v1/expense-accounts", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expense-accounts"] });
      enqueueSnackbar("Expense account created successfully", { variant: "success" });
      setAddDialog(false);
      resetForm();
    },
    onError: (error: any) => {
      enqueueSnackbar(
        error.response?.data?.detail || "Failed to create expense account",
        { variant: "error" }
      );
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ExpenseAccount> }) =>
      api.put(`/v1/expense-accounts/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expense-accounts"] });
      enqueueSnackbar("Expense account updated successfully", { variant: "success" });
      setEditDialog(false);
      resetForm();
    },
    onError: (error: any) => {
      enqueueSnackbar(
        error.response?.data?.detail || "Failed to update expense account",
        { variant: "error" }
      );
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/v1/expense-accounts/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expense-accounts"] });
      enqueueSnackbar("Expense account deleted successfully", { variant: "success" });
    },
    onError: (error: any) => {
      enqueueSnackbar(
        error.response?.data?.detail || "Failed to delete expense account",
        { variant: "error" }
      );
    },
  });

  const resetForm = () => {
    setFormData({
      account_code: "",
      account_name: "",
      parent_account_id: null,
      category: "",
      sub_category: "",
      opening_balance: 0,
      budgeted_amount: 0,
      is_active: true,
      is_group: false,
      can_post: true,
      requires_approval: false,
      description: "",
      notes: "",
      tags: "",
    });
    setSelectedAccount(null);
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (account: ExpenseAccount) => {
    setSelectedAccount(account);
    setFormData({
      account_code: account.account_code,
      account_name: account.account_name,
      parent_account_id: account.parent_account_id,
      category: account.category || "",
      sub_category: account.sub_category || "",
      opening_balance: account.opening_balance || 0,
      budgeted_amount: account.budgeted_amount || 0,
      is_active: account.is_active,
      is_group: account.is_group,
      can_post: account.can_post,
      requires_approval: account.requires_approval,
      description: account.description || "",
      notes: account.notes || "",
      tags: account.tags || "",
    });
    setEditDialog(true);
  };

  const handleSubmit = () => {
    if (selectedAccount?.id) {
      updateMutation.mutate({ id: selectedAccount.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDeleteClick = (account: ExpenseAccount) => {
    if (confirm(`Are you sure you want to delete expense account "${account.account_name}"?`)) {
      deleteMutation.mutate(account.id!);
    }
  };

  const handleImportClick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.xlsx';
    input.onchange = async (e: any) => {
      const file = e.target.files?.[0];
      if (file) {
        setImportExportState({
          isProcessing: true,
          progress: 0,
          type: 'import',
          status: 'processing',
          message: '',
          error: '',
          fileName: file.name,
        });

        try {
          const formData = new FormData();
          formData.append('file', file);

          // Simulate progress
          const progressInterval = setInterval(() => {
            setImportExportState((prev) => ({
              ...prev,
              progress: Math.min(prev.progress + 10, 90),
            }));
          }, 500);

          const response = await api.post('/v1/expense-accounts/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          clearInterval(progressInterval);
          
          setImportExportState({
            isProcessing: false,
            progress: 100,
            type: 'import',
            status: 'success',
            message: `Successfully imported ${response.data.count || 0} expense accounts`,
            error: '',
            fileName: file.name,
          });

          queryClient.invalidateQueries({ queryKey: ['expense-accounts'] });
          
          setTimeout(() => {
            setImportExportState((prev) => ({ ...prev, status: 'idle' }));
          }, 5000);
        } catch (error: any) {
          setImportExportState({
            isProcessing: false,
            progress: 0,
            type: 'import',
            status: 'error',
            message: '',
            error: error.response?.data?.detail || 'Failed to import expense accounts',
            fileName: file.name,
          });
        }
      }
    };
    input.click();
  };

  const handleExportClick = async () => {
    setImportExportState({
      isProcessing: true,
      progress: 0,
      type: 'export',
      status: 'processing',
      message: '',
      error: '',
      fileName: 'expense-accounts.csv',
    });

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setImportExportState((prev) => ({
          ...prev,
          progress: Math.min(prev.progress + 10, 90),
        }));
      }, 500);

      const response = await api.get('/v1/expense-accounts/export', {
        responseType: 'blob',
      });

      clearInterval(progressInterval);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'expense-accounts.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();

      setImportExportState({
        isProcessing: false,
        progress: 100,
        type: 'export',
        status: 'success',
        message: 'Successfully exported expense accounts',
        error: '',
        fileName: 'expense-accounts.csv',
      });

      setTimeout(() => {
        setImportExportState((prev) => ({ ...prev, status: 'idle' }));
      }, 5000);
    } catch (error: any) {
      setImportExportState({
        isProcessing: false,
        progress: 0,
        type: 'export',
        status: 'error',
        message: '',
        error: error.response?.data?.detail || 'Failed to export expense accounts',
        fileName: 'expense-accounts.csv',
      });
    }
  };

  const filteredAccounts = accounts.filter(
    (account: ExpenseAccount) =>
      account.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.account_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categoryOptions = [
    "Operating",
    "Administrative",
    "Manufacturing",
    "Sales & Marketing",
    "Financial",
    "Other",
  ];

  const parentAccounts = accounts.filter((a: ExpenseAccount) => a.is_group);

  return (
    <ProtectedPage moduleKey="masters" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Expense Accounts
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Manage and categorize business expense accounts
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
              <MoreVert />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={() => setAnchorEl(null)}
            >
              <MenuItem onClick={() => {
                handleImportClick();
                setAnchorEl(null);
              }}>
                <ListItemIcon>
                  <FileUpload fontSize="small" />
                </ListItemIcon>
                <ListItemText>Import Accounts</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => {
                handleExportClick();
                setAnchorEl(null);
              }}>
                <ListItemIcon>
                  <FileDownload fontSize="small" />
                </ListItemIcon>
                <ListItemText>Export Accounts</ListItemText>
              </MenuItem>
            </Menu>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddClick}
            >
              Add Expense Account
            </Button>
          </Box>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Expense accounts help track and categorize business expenses for better
          financial management and reporting. Group accounts can have sub-accounts
          for hierarchical organization.
        </Alert>

        {/* Bulk Import/Export Progress Bar */}
        <BulkImportExportProgressBar
          isProcessing={importExportState.isProcessing}
          progress={importExportState.progress}
          type={importExportState.type}
          status={importExportState.status}
          message={importExportState.message}
          error={importExportState.error}
          fileName={importExportState.fileName}
        />

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Accounts
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {accounts.length}
                    </Typography>
                  </Box>
                  <AccountBalance sx={{ fontSize: 40, color: "primary.main" }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Active Accounts
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {accounts.filter((a: ExpenseAccount) => a.is_active).length}
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 40, color: "success.main" }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Group Accounts
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {accounts.filter((a: ExpenseAccount) => a.is_group).length}
                    </Typography>
                  </Box>
                  <Folder sx={{ fontSize: 40, color: "info.main" }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Search */}
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Search by name, code, or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: "text.secondary" }} />,
            }}
          />
        </Box>

        {/* Expense Accounts Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Current Balance</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : filteredAccounts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                      No expense accounts found. Click "Add Expense Account" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredAccounts.map((account: ExpenseAccount) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {account.account_code}
                      </Typography>
                    </TableCell>
                    <TableCell>{account.account_name}</TableCell>
                    <TableCell>
                      {account.category && (
                        <Chip label={account.category} size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {account.is_group ? (
                        <Chip label="Group" size="small" color="primary" />
                      ) : (
                        <Chip label="Account" size="small" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      ₹{(account.current_balance || 0).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={account.is_active ? "Active" : "Inactive"}
                        size="small"
                        color={account.is_active ? "success" : "default"}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleEditClick(account)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(account)}
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
      </Box>

      {/* Add/Edit Dialog */}
      <Dialog
        open={addDialog || editDialog}
        onClose={() => {
          setAddDialog(false);
          setEditDialog(false);
          resetForm();
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedAccount ? "Edit Expense Account" : "Add Expense Account"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Account Code"
                value={formData.account_code}
                onChange={(e) =>
                  setFormData({ ...formData, account_code: e.target.value })
                }
                required
                disabled={!!selectedAccount}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Account Name"
                value={formData.account_name}
                onChange={(e) =>
                  setFormData({ ...formData, account_name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                >
                  {categoryOptions.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Sub Category"
                value={formData.sub_category}
                onChange={(e) =>
                  setFormData({ ...formData, sub_category: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Autocomplete
                options={parentAccounts}
                getOptionLabel={(option: ExpenseAccount) =>
                  `${option.account_code} - ${option.account_name}`
                }
                value={
                  parentAccounts.find(
                    (a: ExpenseAccount) => a.id === formData.parent_account_id
                  ) || null
                }
                onChange={(_, newValue) =>
                  setFormData({
                    ...formData,
                    parent_account_id: newValue?.id || null,
                  })
                }
                renderInput={(params) => (
                  <TextField {...params} label="Parent Account (Optional)" />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Opening Balance"
                type="number"
                value={formData.opening_balance}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    opening_balance: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Budgeted Amount"
                type="number"
                value={formData.budgeted_amount}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    budgeted_amount: parseFloat(e.target.value) || 0,
                  })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_group}
                    onChange={(e) =>
                      setFormData({ ...formData, is_group: e.target.checked })
                    }
                  />
                }
                label="Is Group Account"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.can_post}
                    onChange={(e) =>
                      setFormData({ ...formData, can_post: e.target.checked })
                    }
                  />
                }
                label="Can Post Transactions"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.requires_approval}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        requires_approval: e.target.checked,
                      })
                    }
                  />
                }
                label="Requires Approval"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setAddDialog(false);
              setEditDialog(false);
              resetForm();
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !formData.account_code ||
              !formData.account_name ||
              createMutation.isPending ||
              updateMutation.isPending
            }
          >
            {selectedAccount ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
    </ProtectedPage>
  );
};

export default ExpenseAccountsPage;
