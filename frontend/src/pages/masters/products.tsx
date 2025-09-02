// frontend/src/pages/masters/products.tsx
// Standalone Products Page - Extract from masters/index.tsx
import React, { useState, useCallback, useMemo } from "react";
import { useRouter } from "next/router";
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  FormControlLabel,
  Checkbox,
  TableSortLabel,
  InputAdornment,
  Autocomplete,
  CircularProgress,
} from "@mui/material";
import { Add, Edit, Delete, Search } from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { masterDataService } from "../../services/authService";
import ExcelImportExport from "../../components/ExcelImportExport";
import { bulkImportProducts } from "../../services/masterService";
import Grid from "@mui/material/Grid";
import { useAuth } from "../../context/AuthContext";
// Utility function to get product display name
const getProductDisplayName = (product: any): string => {
  return product.product_name || product.name || "";
};
const ProductsPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isOrgContextReady } = useAuth();
  const [itemDialog, setItemDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [formData, setFormData] = useState({
    product_name: "",
    hsn_code: "",
    part_number: "",
    unit: "",
    unit_price: "",
    gst_rate: "",
    is_gst_inclusive: false,
    reorder_level: "",
    description: "",
    is_manufactured: false,
    is_active: true,
  });
  const queryClient = useQueryClient();
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ["products"],
    queryFn: () => masterDataService.getProducts(),
    enabled: isOrgContextReady,
  });
  // Normalize products to ensure consistent product_name property
  const normalizedProducts = useMemo(() => {
    if (!products) {
      return [];
    }
    return products.map((product: any) => ({
      ...product,
      product_name: product.product_name || product.name || "",
    }));
  }, [products]);
  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    if (!normalizedProducts) {
      return [];
    }
    // Filter products based on search term
    const filtered = normalizedProducts.filter((product: any) => {
      const searchLower = searchTerm.toLowerCase();
      return (
        (product.product_name || "").toLowerCase().includes(searchLower) ||
        (product.hsn_code || "").toLowerCase().includes(searchLower) ||
        (product.part_number || "").toLowerCase().includes(searchLower)
      );
    });
    // Sort products by name
    filtered.sort((a: any, b: any) => {
      const nameA = (a.product_name || "").toLowerCase();
      const nameB = (b.product_name || "").toLowerCase();
      if (sortOrder === "asc") {
        return nameA.localeCompare(nameB);
      } else {
        return nameB.localeCompare(nameA);
      }
    });
    return filtered;
  }, [normalizedProducts, searchTerm, sortOrder]);
  const handleSortToggle = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };
  const createItemMutation = useMutation({
    mutationFn: (data: any) => masterDataService.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setItemDialog(false);
      setSelectedItem(null);
      setFormData({
        product_name: "",
        hsn_code: "",
        part_number: "",
        unit: "",
        unit_price: "",
        gst_rate: "",
        is_gst_inclusive: false,
        reorder_level: "",
        description: "",
        is_manufactured: false,
        is_active: true,
      });
    },
    onError: (error: any) => {
      console.error(msg, err);
      setErrorMessage(
        error.response?.data?.detail || "Failed to create product",
      );
    },
  });
  const updateItemMutation = useMutation({
    mutationFn: (data: any) => masterDataService.updateProduct(data.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setItemDialog(false);
      setSelectedItem(null);
      setFormData({
        product_name: "",
        hsn_code: "",
        part_number: "",
        unit: "",
        unit_price: "",
        gst_rate: "",
        is_gst_inclusive: false,
        reorder_level: "",
        description: "",
        is_manufactured: false,
        is_active: true,
      });
    },
    onError: (error: any) => {
      console.error(msg, err);
      setErrorMessage(
        error.response?.data?.detail || "Failed to update product",
      );
    },
  });
  // HSN/Product bidirectional search functionality
  const uniqueHsnCodes = useMemo(() => {
    const hsnSet = new Set<string>();
    normalizedProducts.forEach((product: any) => {
      if (product.hsn_code && product.hsn_code.trim()) {
        hsnSet.add(product.hsn_code.trim());
      }
    });
    return Array.from(hsnSet).sort();
  }, [normalizedProducts]);
  const getProductsByHsn = useCallback(
    (hsnCode: string) => {
      if (!hsnCode.trim()) {
        return [];
      }
      return normalizedProducts.filter(
        (product: any) =>
          product.hsn_code &&
          product.hsn_code.toLowerCase().includes(hsnCode.toLowerCase()),
      );
    },
    [normalizedProducts],
  );
  const getHsnByProductName = useCallback(
    (productName: string) => {
      if (!productName.trim()) {
        return [];
      }
      const matchingProducts = normalizedProducts.filter((product: any) =>
        product.product_name.toLowerCase().includes(productName.toLowerCase()),
      );
      const hsnCodes = matchingProducts
        .map((product: any) => product.hsn_code)
        .filter((hsn: string) => hsn && hsn.trim())
        .filter(
          (hsn: string, index: number, array: string[]) =>
            array.indexOf(hsn) === index,
        ); // unique
      return hsnCodes;
    },
    [normalizedProducts],
  );
  // Auto-population effects
  React.useEffect(() => {
    // When product name changes, suggest HSN codes
    if (formData.product_name && formData.product_name.length > 2) {
      const suggestedHsns = getHsnByProductName(formData.product_name);
      if (suggestedHsns.length === 1 && !formData.hsn_code) {
        // Auto-populate if there's exactly one matching HSN and HSN field is empty
        setFormData((prev) => ({ ...prev, hsn_code: suggestedHsns[0] }));
      }
    }
  }, [formData.product_name, formData.hsn_code, getHsnByProductName]);
  React.useEffect(() => {
    // When HSN code changes, suggest product info
    if (formData.hsn_code && formData.hsn_code.length > 2) {
      const matchingProducts = getProductsByHsn(formData.hsn_code);
      if (matchingProducts.length > 0 && !formData.product_name) {
        // If there's a strong match and product name is empty, suggest the most common unit/gst_rate
        const commonUnit = matchingProducts[0].unit;
        const commonGstRate = matchingProducts[0].gst_rate;
        if (commonUnit && commonUnit !== formData.unit) {
          setFormData((prev) => ({ ...prev, unit: commonUnit }));
        }
        if (commonGstRate && commonGstRate !== formData.gst_rate) {
          setFormData((prev) => ({ ...prev, gst_rate: String(commonGstRate) }));
        }
      }
    }
  }, [
    formData.hsn_code,
    formData.product_name,
    formData.unit,
    formData.gst_rate,
    getProductsByHsn,
  ]);
  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (error: any) => {
      console.error(msg, err);
      setErrorMessage(
        error.response?.data?.detail || "Failed to delete product",
      );
    },
  });
  const openItemDialog = useCallback((item: any = null) => {
    setSelectedItem(item);
    if (item) {
      setFormData({
        ...item,
        product_name: item.product_name || item.name || "",
      });
    } else {
      setFormData({
        product_name: "",
        hsn_code: "",
        part_number: "",
        unit: "",
        unit_price: "",
        gst_rate: "",
        is_gst_inclusive: false,
        reorder_level: "",
        description: "",
        is_manufactured: false,
        is_active: true,
      });
    }
    setErrorMessage("");
    setItemDialog(true);
  }, []);
  const handleSubmit = () => {
    const data = {
      ...formData,
      name: formData.product_name, // Map back to 'name' for backend compatibility
    };
    // Convert string numbers to actual numbers
    if (data.unit_price) {
      (data as any).unit_price = parseFloat(data.unit_price as string);
    }
    if (data.gst_rate) {
      (data as any).gst_rate = parseFloat(data.gst_rate as string);
    }
    if (data.reorder_level) {
      (data as any).reorder_level = parseInt(data.reorder_level as string);
    }
    if (selectedItem) {
      updateItemMutation.mutate({ ...selectedItem, ...data });
    } else {
      createItemMutation.mutate(data);
    }
  };
  // Auto-open add dialog if action=add in URL
  React.useEffect(() => {
    if (action === "add") {
      openItemDialog(null);
    }
  }, [action, openItemDialog]);
  if (!isOrgContextReady) {
    return <div>Loading...</div>;
  }
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom>
            Product Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => openItemDialog()}
            sx={{ ml: 2 }}
          >
            Add Product
          </Button>
        </Box>
        {/* Products Table */}
        <Paper sx={{ p: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">All Products</Typography>
            <ExcelImportExport
              data={products || []}
              entity="Products"
              onImport={bulkImportProducts}
            />
          </Box>
          {/* Search Bar */}
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              placeholder="Search products by name, HSN code, or part number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ maxWidth: 500 }}
            />
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={true}
                      direction={sortOrder}
                      onClick={handleSortToggle}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>HSN Code</TableCell>
                  <TableCell>Part Number</TableCell>
                  <TableCell>Unit</TableCell>
                  <TableCell>Unit Price</TableCell>
                  <TableCell>GST Rate</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredAndSortedProducts?.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {getProductDisplayName(item)}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {item.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{item.hsn_code || "N/A"}</TableCell>
                    <TableCell>{item.part_number || "N/A"}</TableCell>
                    <TableCell>{item.unit}</TableCell>
                    <TableCell>₹{item.unit_price}</TableCell>
                    <TableCell>{item.gst_rate}%</TableCell>
                    <TableCell>
                      <Chip
                        label={
                          item.is_manufactured ? "Manufactured" : "Purchased"
                        }
                        color={item.is_manufactured ? "primary" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={item.is_active ? "Active" : "Inactive"}
                        color={item.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        onClick={() => openItemDialog(item)}
                        size="small"
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        onClick={() => deleteItemMutation.mutate(item.id)}
                        size="small"
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        {/* Add/Edit Dialog */}
        <Dialog
          open={itemDialog}
          onClose={() => setItemDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {selectedItem ? "Edit Product" : "Add New Product"}
          </DialogTitle>
          <DialogContent>
            {errorMessage && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errorMessage}
              </Alert>
            )}
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Product Name"
                  value={formData.product_name}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      product_name: e.target.value,
                    }))
                  }
                  required
                  helperText={
                    formData.product_name &&
                    formData.product_name.length > 2 &&
                    getHsnByProductName(formData.product_name).length > 0
                      ? `Suggested HSN: ${getHsnByProductName(formData.product_name).slice(0, 3).join(", ")}`
                      : undefined
                  }
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Autocomplete
                  freeSolo
                  options={uniqueHsnCodes}
                  value={formData.hsn_code || ""}
                  onInputChange={(_, newValue) => {
                    setFormData((prev) => ({
                      ...prev,
                      hsn_code: newValue || "",
                    }));
                  }}
                  onChange={(_, newValue) => {
                    setFormData((prev) => ({
                      ...prev,
                      hsn_code: newValue || "",
                    }));
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      fullWidth
                      label="HSN Code"
                      placeholder="Search or enter HSN code..."
                      helperText={
                        formData.hsn_code &&
                        getProductsByHsn(formData.hsn_code).length > 0
                          ? `Found ${getProductsByHsn(formData.hsn_code).length} product(s) with this HSN`
                          : undefined
                      }
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {productsLoading ? (
                              <CircularProgress color="inherit" size={20} />
                            ) : null}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                  renderOption={(props, option) => (
                    <Box component="li" {...props}>
                      <Box sx={{ width: "100%" }}>
                        <Typography
                          variant="body1"
                          sx={{ fontWeight: "medium" }}
                        >
                          {option}
                        </Typography>
                        {getProductsByHsn(option).length > 0 && (
                          <Typography variant="caption" color="text.secondary">
                            {getProductsByHsn(option).length} product(s):{" "}
                            {getProductsByHsn(option)
                              .slice(0, 2)
                              .map((p) => p.product_name)
                              .join(", ")}
                            {getProductsByHsn(option).length > 2 && "..."}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  )}
                  noOptionsText="No HSN codes found"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Part Number"
                  value={formData.part_number}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      part_number: e.target.value,
                    }))
                  }
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit"
                  value={formData.unit}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, unit: e.target.value }))
                  }
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit Price"
                  type="number"
                  value={formData.unit_price}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      unit_price: e.target.value,
                    }))
                  }
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="GST Rate (%)"
                  type="number"
                  value={formData.gst_rate}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      gst_rate: e.target.value,
                    }))
                  }
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Reorder Level"
                  type="number"
                  value={formData.reorder_level}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      reorder_level: e.target.value,
                    }))
                  }
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_gst_inclusive}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          is_gst_inclusive: e.target.checked,
                        }))
                      }
                    />
                  }
                  label="GST Inclusive Pricing"
                />
              </Grid>
              <Grid size={12}>
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
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_manufactured}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          is_manufactured: e.target.checked,
                        }))
                      }
                    />
                  }
                  label="Manufactured Product"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.is_active}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          is_active: e.target.checked,
                        }))
                      }
                    />
                  }
                  label="Active"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setItemDialog(false)}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">
              Save
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};
export default ProductsPage;
