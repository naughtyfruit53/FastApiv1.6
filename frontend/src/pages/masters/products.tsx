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
  Alert,
  FormControlLabel,
  Checkbox,
  TableSortLabel,
  InputAdornment,
} from "@mui/material";
import { Add, Edit, Delete, Search as SearchIcon } from "@mui/icons-material"; // Renamed import to SearchIcon
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { masterDataService } from "../../services/authService";
import ExcelImportExport from "../../components/ExcelImportExport";
import { bulkImportProducts } from "../../services/masterService";
import Grid from "@mui/material/Grid";
import { useAuth } from "../../context/AuthContext";
import { toast } from "react-toastify";
import AddProductModal from "../../components/AddProductModal"; // Added import for unified modal

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
      id: product.id,
      name: product.product_name,
      unit_price: product.unit_price,
      reorder_level: product.reorder_level,
      unit: product.unit,
      hsn_code: product.hsn_code,
      part_number: product.part_number,
      gst_rate: product.gst_rate,
      is_active: product.is_active
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
      queryClient.refetchQueries({ queryKey: ["products"] });
      setItemDialog(false);
      setSelectedItem(null);
    },
    onError: (error: any) => {
      console.error(error);
      setErrorMessage(
        error.response?.data?.detail || "Failed to create product",
      );
    },
  });

  const updateItemMutation = useMutation({
    mutationFn: (data: any) => masterDataService.updateProduct(data.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.refetchQueries({ queryKey: ["products"] });
      setItemDialog(false);
      setSelectedItem(null);
    },
    onError: (error: any) => {
      console.error(error);
      setErrorMessage(
        error.response?.data?.detail || "Failed to update product",
      );
    },
  });

  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (error: any) => {
      console.error(error);
      setErrorMessage(
        error.response?.data?.detail || "Failed to delete product",
      );
    },
  });

  const openItemDialog = useCallback((item: any = null) => {
    setSelectedItem(item);
    setErrorMessage("");
    setItemDialog(true);
  }, []);

  const handleAddProduct = async (data: any) => {
    if (selectedItem) {
      updateItemMutation.mutate({ id: selectedItem.id, ...data });
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
                    <SearchIcon />
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
                      Product Name
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
        {/* Unified Add/Edit Modal */}
        <AddProductModal
          open={itemDialog}
          onClose={() => setItemDialog(false)}
          onAdd={handleAddProduct}
          loading={createItemMutation.isPending || updateItemMutation.isPending}
          initialName={selectedItem ? selectedItem.product_name : ""}
        />
      </Box>
    </Container>
  );
};
export default ProductsPage;