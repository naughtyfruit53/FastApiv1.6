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
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Search,
  Payment,
  AccessTime,
} from "@mui/icons-material";
import { ProtectedPage } from "../../components/ProtectedPage";

const PaymentTermsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedTerm, setSelectedTerm] = useState<any>(null);
  const [formData, setFormData] = useState({
    term_name: "",
    term_code: "",
    description: "",
    payment_type: "net_days",
    due_days: 30,
    discount_days: 0,
    discount_percentage: 0,
    is_default: false,
    is_active: true,
  });
  // Mock data for demonstration
  const paymentTerms = [
    {
      id: 1,
      term_code: "NET30",
      term_name: "Net 30 Days",
      description: "Payment due within 30 days of invoice date",
      payment_type: "net_days",
      due_days: 30,
      discount_days: 0,
      discount_percentage: 0,
      is_default: true,
      is_active: true,
      usage_count: 25,
    },
    {
      id: 2,
      term_code: "NET15",
      term_name: "Net 15 Days",
      description: "Payment due within 15 days of invoice date",
      payment_type: "net_days",
      due_days: 15,
      discount_days: 0,
      discount_percentage: 0,
      is_default: false,
      is_active: true,
      usage_count: 12,
    },
    {
      id: 3,
      term_code: "2_10_NET30",
      term_name: "2/10 Net 30",
      description:
        "2% discount if paid within 10 days, otherwise due in 30 days",
      payment_type: "net_days",
      due_days: 30,
      discount_days: 10,
      discount_percentage: 2,
      is_default: false,
      is_active: true,
      usage_count: 8,
    },
    {
      id: 4,
      term_code: "COD",
      term_name: "Cash on Delivery",
      description: "Payment due upon delivery",
      payment_type: "immediate",
      due_days: 0,
      discount_days: 0,
      discount_percentage: 0,
      is_default: false,
      is_active: true,
      usage_count: 15,
    },
    {
      id: 5,
      term_code: "ADVANCE",
      term_name: "Advance Payment",
      description: "Payment required before delivery",
      payment_type: "advance",
      due_days: 0,
      discount_days: 0,
      discount_percentage: 0,
      is_default: false,
      is_active: true,
      usage_count: 18,
    },
    {
      id: 6,
      term_code: "NET60",
      term_name: "Net 60 Days",
      description: "Payment due within 60 days of invoice date",
      payment_type: "net_days",
      due_days: 60,
      discount_days: 0,
      discount_percentage: 0,
      is_default: false,
      is_active: true,
      usage_count: 5,
    },
  ];
  const paymentTypes = [
    { value: "immediate", label: "Immediate Payment" },
    { value: "advance", label: "Advance Payment" },
    { value: "net_days", label: "Net Days" },
    { value: "eom", label: "End of Month" },
    { value: "custom", label: "Custom Terms" },
  ];
  const resetForm = () => {
    setFormData({
      term_name: "",
      term_code: "",
      description: "",
      payment_type: "net_days",
      due_days: 30,
      discount_days: 0,
      discount_percentage: 0,
      is_default: false,
      is_active: true,
    });
  };
  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };
  const handleEditClick = (term: any) => {
    setSelectedTerm(term);
    setFormData({
      term_name: term.term_name || "",
      term_code: term.term_code || "",
      description: term.description || "",
      payment_type: term.payment_type || "net_days",
      due_days: term.due_days || 30,
      discount_days: term.discount_days || 0,
      discount_percentage: term.discount_percentage || 0,
      is_default: term.is_default || false,
      is_active: term.is_active,
    });
    setEditDialog(true);
  };
  const handleSubmit = () => {
    if (selectedTerm) {
      // TODO: Implement update functionality
      console.log("Update payment term:", selectedTerm.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log("Create payment term:", formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };
  const handleDeleteClick = (term: any) => {
    // TODO: Implement delete functionality
    console.log("Delete payment term:", term.id);
  };
  const filteredTerms = paymentTerms.filter(
    (term: any) =>
      term.term_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      term.term_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      term.description?.toLowerCase().includes(searchTerm.toLowerCase()),
  );
  const getTotalUsage = () => {
    return paymentTerms.reduce((sum, term) => sum + term.usage_count, 0);
  };
  const getAverageDays = () => {
    const netDaysTerms = paymentTerms.filter(
      (term) => term.payment_type === "net_days" && term.is_active,
    );
    if (netDaysTerms.length === 0) {
      return 0;
    }
    const total = netDaysTerms.reduce((sum, term) => sum + term.due_days, 0);
    return Math.round(total / netDaysTerms.length);
  };
  const getTermDisplay = (term: any) => {
    if (term.payment_type === "immediate") {
      return "Immediate";
    }
    if (term.payment_type === "advance") {
      return "Advance";
    }
    if (term.discount_percentage > 0) {
      return `${term.discount_percentage}/${term.discount_days} Net ${term.due_days}`;
    }
    return `Net ${term.due_days} days`;
  };
  return (
    <ProtectedPage moduleKey="masters" action="read">
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
            Payment Terms
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Payment Term
          </Button>
        </Box>
        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          Configure payment terms to automatically set payment due dates and
          discount conditions in your invoices and purchase orders.
        </Alert>
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
                      Total Terms
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {paymentTerms.length}
                    </Typography>
                  </Box>
                  <Payment sx={{ fontSize: 40, color: "primary.main" }} />
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
                      Active Terms
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {paymentTerms.filter((term) => term.is_active).length}
                    </Typography>
                  </Box>
                  <Payment sx={{ fontSize: 40, color: "success.main" }} />
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
                      Avg. Days
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {getAverageDays()}
                    </Typography>
                  </Box>
                  <AccessTime sx={{ fontSize: 40, color: "warning.main" }} />
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
                      Total Usage
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {getTotalUsage()}
                    </Typography>
                  </Box>
                  <Payment sx={{ fontSize: 40, color: "info.main" }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search payment terms by name, code, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: "action.active" }} />,
            }}
          />
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Term Code</TableCell>
                <TableCell>Term Name</TableCell>
                <TableCell>Payment Type</TableCell>
                <TableCell>Terms</TableCell>
                <TableCell>Usage</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredTerms.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Box sx={{ py: 3 }}>
                      <Payment
                        sx={{ fontSize: 48, color: "action.disabled", mb: 2 }}
                      />
                      <Typography variant="h6" color="textSecondary">
                        No payment terms found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first payment term to configure payment
                        conditions
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTerms.map((term: any) => (
                  <TableRow key={term.id}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {term.term_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Payment sx={{ mr: 2, color: "primary.main" }} />
                        <Box>
                          <Typography variant="body1">
                            {term.term_name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {term.description}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={
                          paymentTypes.find(
                            (pt) => pt.value === term.payment_type,
                          )?.label || term.payment_type
                        }
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {getTermDisplay(term)}
                      </Typography>
                      {term.discount_percentage > 0 && (
                        <Typography variant="body2" color="success.main">
                          {term.discount_percentage}% discount available
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${term.usage_count} times`}
                        size="small"
                        color="info"
                      />
                    </TableCell>
                    <TableCell>
                      {term.is_default && (
                        <Chip label="Default" size="small" color="warning" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={term.is_active ? "Active" : "Inactive"}
                        color={term.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditClick(term)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(term)}
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
        {/* Add/Edit Payment Term Dialog */}
        <Dialog
          open={addDialog || editDialog}
          onClose={() => {
            setAddDialog(false);
            setEditDialog(false);
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {selectedTerm ? "Edit Payment Term" : "Add New Payment Term"}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Term Code *"
                  value={formData.term_code}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      term_code: e.target.value,
                    }))
                  }
                  placeholder="e.g., NET30"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Payment Type</InputLabel>
                  <Select
                    value={formData.payment_type}
                    label="Payment Type"
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        payment_type: e.target.value,
                      }))
                    }
                  >
                    {paymentTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Term Name *"
                  value={formData.term_name}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      term_name: e.target.value,
                    }))
                  }
                  placeholder="e.g., Net 30 Days"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={2}
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                />
              </Grid>
              {formData.payment_type === "net_days" && (
                <>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Due Days *"
                      type="number"
                      value={formData.due_days}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          due_days: parseInt(e.target.value) || 0,
                        }))
                      }
                      InputProps={{ inputProps: { min: 0 } }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Discount Days"
                      type="number"
                      value={formData.discount_days}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          discount_days: parseInt(e.target.value) || 0,
                        }))
                      }
                      InputProps={{ inputProps: { min: 0 } }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Discount Percentage (%)"
                      type="number"
                      value={formData.discount_percentage}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          discount_percentage: parseFloat(e.target.value) || 0,
                        }))
                      }
                      InputProps={{
                        inputProps: { min: 0, max: 100, step: 0.01 },
                      }}
                    />
                  </Grid>
                </>
              )}
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_default}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          is_default: e.target.checked,
                        }))
                      }
                    />
                  }
                  label="Set as Default Payment Term"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => {
                setAddDialog(false);
                setEditDialog(false);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedTerm ? "Update" : "Create"}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
    </ProtectedPage>
  );
};
export default PaymentTermsPage;
