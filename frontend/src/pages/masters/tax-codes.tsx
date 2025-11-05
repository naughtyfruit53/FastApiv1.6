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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  CircularProgress,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Search,
  Receipt,
  Percent,
} from "@mui/icons-material";
import { getTaxCodes, toggleTaxCodeStatus, TaxCode } from "../../services/masterService";
import { toast } from "react-toastify";
import { ProtectedPage } from "../../components/ProtectedPage";

const TaxCodesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedTaxCode, setSelectedTaxCode] = useState<any>(null);
  const [taxCodes, setTaxCodes] = useState<TaxCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    tax_code: "",
    tax_name: "",
    tax_rate: 0,
    tax_type: "GST",
    description: "",
    is_default: false,
    is_active: true,
  });

  // Fetch tax codes from API
  useEffect(() => {
    const fetchTaxCodes = async () => {
      try {
        setLoading(true);
        const data = await getTaxCodes();
        setTaxCodes(data);
        setError(null);
      } catch (err: any) {
        console.error("Error fetching tax codes:", err);
        setError(err?.response?.data?.detail || "Failed to load tax codes");
      } finally {
        setLoading(false);
      }
    };
    fetchTaxCodes();
  }, []);

  // Toggle tax code active status
  const handleToggleStatus = async (taxCodeId: number, currentStatus: boolean) => {
    try {
      const newStatus = !currentStatus;
      await toggleTaxCodeStatus(taxCodeId, newStatus);
      // Update local state
      setTaxCodes(prevCodes =>
        prevCodes.map(code =>
          code.id === taxCodeId ? { ...code, is_active: newStatus } : code
        )
      );
      toast.success(`Tax code ${newStatus ? "activated" : "deactivated"} successfully`);
    } catch (err: any) {
      console.error("Error toggling tax code status:", err);
      toast.error(err?.response?.data?.detail || "Failed to update tax code status");
    }
  };

  // NOTE: The hardcoded tax codes array has been removed. 
  // Tax codes are now loaded from the backend API via getTaxCodes()
  // Keeping the mock data structure below for reference only
  const _mockTaxCodes = [
    // GST Tax Codes (Goods and Services Tax)
    {
      id: 1,
      tax_code: "GST_0",
      tax_name: "GST 0%",
      tax_rate: 0,
      tax_type: "GST",
      description: "Nil GST rate for exempt items as per GST Act",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 2,
      tax_code: "GST_0.25",
      tax_name: "GST 0.25%",
      tax_rate: 0.25,
      tax_type: "GST",
      description: "GST at 0.25% for precious stones (rough diamonds)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 3,
      tax_code: "GST_3",
      tax_name: "GST 3%",
      tax_rate: 3,
      tax_type: "GST",
      description: "GST at 3% for gold, silver and gold ornaments",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 4,
      tax_code: "GST_5",
      tax_name: "GST 5%",
      tax_rate: 5,
      tax_type: "GST",
      description: "GST at 5% for essential items (household necessities, certain food items)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 5,
      tax_code: "GST_12",
      tax_name: "GST 12%",
      tax_rate: 12,
      tax_type: "GST",
      description: "GST at 12% for standard items (processed food, computers)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 6,
      tax_code: "GST_18",
      tax_name: "GST 18%",
      tax_rate: 18,
      tax_type: "GST",
      description: "GST at 18% for most goods and services",
      is_default: true,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 7,
      tax_code: "GST_28",
      tax_name: "GST 28%",
      tax_rate: 28,
      tax_type: "GST",
      description: "GST at 28% for luxury items, sin goods, and automobiles",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    // IGST Tax Codes (Integrated GST for interstate transactions)
    {
      id: 8,
      tax_code: "IGST_0",
      tax_name: "IGST 0%",
      tax_rate: 0,
      tax_type: "IGST",
      description: "Integrated GST at 0% for exempt items (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 9,
      tax_code: "IGST_0.25",
      tax_name: "IGST 0.25%",
      tax_rate: 0.25,
      tax_type: "IGST",
      description: "Integrated GST at 0.25% for precious stones (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 10,
      tax_code: "IGST_3",
      tax_name: "IGST 3%",
      tax_rate: 3,
      tax_type: "IGST",
      description: "Integrated GST at 3% for gold and precious metals (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 11,
      tax_code: "IGST_5",
      tax_name: "IGST 5%",
      tax_rate: 5,
      tax_type: "IGST",
      description: "Integrated GST at 5% for essential items (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 12,
      tax_code: "IGST_12",
      tax_name: "IGST 12%",
      tax_rate: 12,
      tax_type: "IGST",
      description: "Integrated GST at 12% for standard items (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 13,
      tax_code: "IGST_18",
      tax_name: "IGST 18%",
      tax_rate: 18,
      tax_type: "IGST",
      description: "Integrated GST at 18% for most items (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 14,
      tax_code: "IGST_28",
      tax_name: "IGST 28%",
      tax_rate: 28,
      tax_type: "IGST",
      description: "Integrated GST at 28% for luxury items (interstate)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    // TDS Tax Codes (Tax Deducted at Source)
    {
      id: 15,
      tax_code: "TDS_194C",
      tax_name: "TDS 194C - Contractor",
      tax_rate: 1,
      tax_type: "TDS",
      description: "TDS on payments to contractors (individual/HUF): 1%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 16,
      tax_code: "TDS_194C_2",
      tax_name: "TDS 194C - Contractor (Others)",
      tax_rate: 2,
      tax_type: "TDS",
      description: "TDS on payments to contractors (others): 2%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 17,
      tax_code: "TDS_194H",
      tax_name: "TDS 194H - Commission/Brokerage",
      tax_rate: 5,
      tax_type: "TDS",
      description: "TDS on commission or brokerage: 5%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 18,
      tax_code: "TDS_194I",
      tax_name: "TDS 194I - Rent",
      tax_rate: 10,
      tax_type: "TDS",
      description: "TDS on rent of plant/machinery/equipment: 2%, land/building: 10%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 19,
      tax_code: "TDS_194J",
      tax_name: "TDS 194J - Professional Fees",
      tax_rate: 10,
      tax_type: "TDS",
      description: "TDS on professional or technical services: 10%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 20,
      tax_code: "TDS_194Q",
      tax_name: "TDS 194Q - Purchase of Goods",
      tax_rate: 0.1,
      tax_type: "TDS",
      description: "TDS on purchase of goods exceeding ₹50 lakhs: 0.1%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 21,
      tax_code: "TDS_194O",
      tax_name: "TDS 194O - E-commerce",
      tax_rate: 1,
      tax_type: "TDS",
      description: "TDS on e-commerce participants: 1%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    // TCS Tax Codes (Tax Collected at Source)
    {
      id: 22,
      tax_code: "TCS_206C_1H",
      tax_name: "TCS 206C(1H) - Sale of Goods",
      tax_rate: 0.1,
      tax_type: "TCS",
      description: "TCS on sale of goods exceeding ₹50 lakhs: 0.1%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 23,
      tax_code: "TCS_206C_1F",
      tax_name: "TCS 206C(1F) - Overseas Remittance",
      tax_rate: 5,
      tax_type: "TCS",
      description: "TCS on remittance under LRS: 5% (education/medical: 0.5%)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 24,
      tax_code: "TCS_206C_1G",
      tax_name: "TCS 206C(1G) - Overseas Tour Package",
      tax_rate: 5,
      tax_type: "TCS",
      description: "TCS on sale of overseas tour package: 5% (up to ₹7 lakhs: 5%, above: 10%)",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    // GST Compensation Cess
    {
      id: 25,
      tax_code: "CESS_COAL",
      tax_name: "Compensation Cess - Coal",
      tax_rate: 400,
      tax_type: "CESS",
      description: "GST Compensation Cess on coal: ₹400 per tonne",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 26,
      tax_code: "CESS_TOBACCO",
      tax_name: "Compensation Cess - Tobacco",
      tax_rate: 5,
      tax_type: "CESS",
      description: "GST Compensation Cess on tobacco products: 5% to 290%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
    {
      id: 27,
      tax_code: "CESS_AERATED",
      tax_name: "Compensation Cess - Aerated Drinks",
      tax_rate: 12,
      tax_type: "CESS",
      description: "GST Compensation Cess on aerated waters: 12%",
      is_default: false,
      is_active: true,
      usage_count: 0,
    },
  ];
  // End of mock data - only used if API fails or for reference

  const taxTypes = [
    { value: "GST", label: "GST (Goods and Services Tax)" },
    { value: "IGST", label: "IGST (Integrated GST)" },
    { value: "CGST", label: "CGST (Central GST)" },
    { value: "SGST", label: "SGST (State GST)" },
    { value: "TDS", label: "TDS (Tax Deducted at Source)" },
    { value: "TCS", label: "TCS (Tax Collected at Source)" },
    { value: "CESS", label: "Compensation Cess" },
    { value: "OTHER", label: "Other Tax" },
  ];
  const resetForm = () => {
    setFormData({
      tax_code: "",
      tax_name: "",
      tax_rate: 0,
      tax_type: "GST",
      description: "",
      is_default: false,
      is_active: true,
    });
  };
  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };
  const handleEditClick = (taxCode: any) => {
    setSelectedTaxCode(taxCode);
    setFormData({
      tax_code: taxCode.tax_code || "",
      tax_name: taxCode.tax_name || "",
      tax_rate: taxCode.tax_rate || 0,
      tax_type: taxCode.tax_type || "GST",
      description: taxCode.description || "",
      is_default: taxCode.is_default || false,
      is_active: taxCode.is_active,
    });
    setEditDialog(true);
  };
  const handleSubmit = () => {
    if (selectedTaxCode) {
      // TODO: Implement update functionality
      console.log("Update tax code:", selectedTaxCode.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log("Create tax code:", formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };
  const handleDeleteClick = (taxCode: any) => {
    // TODO: Implement delete functionality
    console.log("Delete tax code:", taxCode.id);
  };
  const filteredTaxCodes = taxCodes.filter(
    (taxCode: any) =>
      taxCode.tax_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      taxCode.tax_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      taxCode.tax_type?.toLowerCase().includes(searchTerm.toLowerCase()),
  );
  const getTotalUsage = () => {
    return taxCodes.reduce((sum, taxCode) => sum + (taxCode.usage_count || 0), 0);
  };
  const getAverageRate = () => {
    const activeTaxCodes = taxCodes.filter(
      (tc) => tc.is_active && tc.tax_rate > 0,
    );
    if (activeTaxCodes.length === 0) {
      return 0;
    }
    const total = activeTaxCodes.reduce((sum, tc) => sum + tc.tax_rate, 0);
    return (total / activeTaxCodes.length).toFixed(1);
  };

  // Show loading state
  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 3, display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

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
            Tax Codes
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Tax Code
          </Button>
        </Box>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          Configure tax codes for different tax rates and types. These will be
          used automatically in invoices, purchase orders, and financial
          calculations. Toggle the switch to activate/deactivate tax codes.
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
                      Total Tax Codes
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {taxCodes.length}
                    </Typography>
                  </Box>
                  <Receipt sx={{ fontSize: 40, color: "primary.main" }} />
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
                      Active Tax Codes
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {taxCodes.filter((tc) => tc.is_active).length}
                    </Typography>
                  </Box>
                  <Receipt sx={{ fontSize: 40, color: "success.main" }} />
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
                      Average Rate
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {getAverageRate()}%
                    </Typography>
                  </Box>
                  <Percent sx={{ fontSize: 40, color: "warning.main" }} />
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
                  <Receipt sx={{ fontSize: 40, color: "info.main" }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search tax codes by name, code, or type..."
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
                <TableCell>Tax Code</TableCell>
                <TableCell>Tax Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Rate (%)</TableCell>
                <TableCell>Usage</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredTaxCodes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Box sx={{ py: 3 }}>
                      <Receipt
                        sx={{ fontSize: 48, color: "action.disabled", mb: 2 }}
                      />
                      <Typography variant="h6" color="textSecondary">
                        No tax codes found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first tax code to configure tax calculations
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTaxCodes.map((taxCode: any) => (
                  <TableRow key={taxCode.id}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {taxCode.tax_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Receipt sx={{ mr: 2, color: "primary.main" }} />
                        <Box>
                          <Typography variant="body1">
                            {taxCode.tax_name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {taxCode.description}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={taxCode.tax_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="h6" color="secondary">
                        {taxCode.tax_rate}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${taxCode.usage_count} times`}
                        size="small"
                        color="info"
                      />
                    </TableCell>
                    <TableCell>
                      {taxCode.is_default && (
                        <Chip label="Default" size="small" color="warning" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <Switch
                          checked={taxCode.is_active}
                          onChange={() => handleToggleStatus(taxCode.id, taxCode.is_active)}
                          color="success"
                          size="small"
                        />
                        <Typography variant="body2" color={taxCode.is_active ? "success.main" : "text.secondary"}>
                          {taxCode.is_active ? "Active" : "Inactive"}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditClick(taxCode)}
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(taxCode)}
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
        {/* Add/Edit Tax Code Dialog */}
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
            {selectedTaxCode ? "Edit Tax Code" : "Add New Tax Code"}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tax Code *"
                  value={formData.tax_code}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      tax_code: e.target.value,
                    }))
                  }
                  placeholder="e.g., GST_18"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tax Rate (%) *"
                  type="number"
                  value={formData.tax_rate}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      tax_rate: parseFloat(e.target.value) || 0,
                    }))
                  }
                  InputProps={{ inputProps: { min: 0, max: 100, step: 0.01 } }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Tax Name *"
                  value={formData.tax_name}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      tax_name: e.target.value,
                    }))
                  }
                  placeholder="e.g., GST 18%"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Tax Type</InputLabel>
                  <Select
                    value={formData.tax_type}
                    label="Tax Type"
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        tax_type: e.target.value,
                      }))
                    }
                  >
                    {taxTypes.map((type) => (
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
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                />
              </Grid>
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
                  label="Set as Default Tax Code"
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
              {selectedTaxCode ? "Update" : "Create"}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
    </ProtectedPage>
  );
};
export default TaxCodesPage;
