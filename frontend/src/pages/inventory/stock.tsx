// frontend/src/pages/inventory/stock.tsx
import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { masterDataService } from "../../services/authService"; // Assuming masterDataService is masterService
import {
  getProductMovements,
  getLastVendorForProduct,
} from "../../services/stockService";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/router";
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControl,
  InputLabel,
  Select,
  Stack,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  Card,
  CardContent,
  CardActions,
} from "@mui/material";
import {
  Add,
  Edit,
  Visibility,
  GetApp,
  Publish,
  Print,
  MoreVert,
  History as HistoryIcon,
  ShoppingCart as PurchaseIcon,
} from "@mui/icons-material";
import { jsPDF } from "jspdf";
import "jspdf-autotable";
import { toast } from "react-toastify";
import { organizationService } from "../../services/organizationService";
// Type declaration for jsPDF autoTable extension
declare module "jspdf" {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}
const StockManagement: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const queryClient = useQueryClient();
  const router = useRouter();
  const { user, isOrgContextReady } = useAuth(); // Get organization context readiness
  const [searchText, setSearchText] = useState("");
  const [filteredStockData, setFilteredStockData] = useState<any[]>([]);
  const [showZero, setShowZero] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [manualDialogOpen, setManualDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [movementsDialogOpen, setMovementsDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedStock, setSelectedStock] = useState<any>(null);
  const [selectedMovements, setSelectedMovements] = useState<any[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuProductId, setMenuProductId] = useState<number | null>(null);
  const [manualFormData, setManualFormData] = useState({
    product_id: 0,
    quantity: 0,
    unit: "",
  });
  const [editFormData, setEditFormData] = useState({ quantity: 0 });
  // Params object for stock fetch - service will clean invalid values from queryKey[1]
  const stockParams = {
    search: searchText,
    show_zero: showZero,
    // Add if you have low_stock_only or product_id states
  };
  // Only fetch stock data if organization context is ready
  const { data: stockData, error: stockError, isFetching } = useQuery({
    queryKey: ["stock", stockParams],
    queryFn: () => masterDataService.getStock(stockParams), // Pass stockParams
    enabled: isOrgContextReady, // Wait for organization context before fetching
  });
  const { data: products } = useQuery({
    queryKey: ["products"],
    queryFn: () => masterDataService.getProducts(),
    enabled: isOrgContextReady, // Wait for organization context before fetching
  });
  const { data: organizationData } = useQuery({
    queryKey: ["organization"],
    queryFn: organizationService.getCurrentOrganization,
    enabled: isOrgContextReady, // Wait for organization context before fetching
  });
  const updateStockMutation = useMutation({
    mutationFn: (data: any) =>
      masterDataService.updateStock(data.product_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      setEditDialogOpen(false);
      setManualDialogOpen(false);
    },
  });
  const bulkImportMutation = useMutation({
    mutationFn: ({ file, mode }: { file: File; mode: "add" | "replace" }) =>
      masterDataService.bulkImportStock(file, mode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      alert("Stock import completed successfully.");
    },
    onError: (error: any) => {
      console.error("Bulk import error", error);
      alert(
        `Import failed: ${error.userMessage || "Please check the file format and required columns."}`,
      );
    },
  });
  useEffect(() => {
    if (stockData) {
      let filtered = stockData;
      if (searchText) {
        const lowerSearch = searchText.toLowerCase();
        filtered = stockData.filter((stock: any) =>
          stock.product_name.toLowerCase().includes(lowerSearch)
        );
      }
      if (!showZero) {
        filtered = filtered.filter((stock: any) => stock.quantity > 0);
      }
      setFilteredStockData(filtered);
    }
  }, [stockData, searchText, showZero]);
  const handleEditStock = (stock: any) => {
    setSelectedStock(stock);
    setEditFormData({ quantity: stock.quantity });
    setEditDialogOpen(true);
  };
  const handleSaveEdit = () => {
    if (!selectedStock || !selectedStock.product_id) {
      toast.error("Invalid stock selection. Please try again.");
      return;
    }
    updateStockMutation.mutate({
      product_id: selectedStock.product_id,
      quantity: editFormData.quantity,
    });
  };
  const handleManualEntry = () => {
    setManualDialogOpen(true);
  };
  const handleSaveManual = () => {
    updateStockMutation.mutate(manualFormData);
  };
  const handleDownloadTemplate = () => {
    masterDataService.downloadStockTemplate();
  };
  const handleImportClick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".xlsx, .xls";
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (file) {
        setSelectedFile(file);
        setImportDialogOpen(true); // Show prompt
      }
    };
    input.click();
  };
  const handleImportConfirm = (mode: "add" | "replace") => {
    if (selectedFile) {
      bulkImportMutation.mutate({ file: selectedFile, mode });
    }
    setImportDialogOpen(false);
    setSelectedFile(null);
  };
  const handleExport = async () => {
    try {
      await masterDataService.exportStock({
        search: searchText,
        show_zero: showZero,
      });
    } catch (err) {
      alert("Failed to export stock data. Please try again.");
    }
  };
  const handlePrint = () => {
    generateStockReport("stock_report.pdf", organizationData, stockData);
  };
  const generateStockReport = (
    filePath: string,
    companyData: any,
    items: any[],
  ) => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Stock Report", 14, 20);
    let yPosition = 30;
    companyData.forEach(([key, value]: [string, string]) => {
      doc.text(`${key}: ${value}`, 14, yPosition);
      yPosition += 10;
    });
    yPosition += 20;
    doc.autoTable({
      startY: yPosition,
      head: [
        [
          "S.No",
          "Product Name",
          "Quantity",
          "Unit Price",
          "Total Value",
          "Reorder Level",
          "Last Updated",
        ],
      ],
      body: items.map((item, idx) => [
        idx + 1,
        item.product_name,
        item.quantity,
        item.unit_price,
        item.total_value,
        item.reorder_level,
        item.last_updated,
      ]),
      theme: "striped",
      styles: { cellPadding: 2, fontSize: 10 },
      headStyles: { fillColor: [41, 128, 185], textColor: [255, 255, 255] },
    });
    doc.save(filePath);
  };
  const resetForm = () => {
    setManualFormData({ product_id: 0, quantity: 0, unit: "" });
    setEditFormData({ quantity: 0 });
  };
  // Handle ESC key for canceling import dialog
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setImportDialogOpen(false);
      }
    };
    window.addEventListener("keydown", handleEsc);
    return () => {
      window.removeEventListener("keydown", handleEsc);
    };
  }, []);
  const handleMenuClick = (
    event: React.MouseEvent<HTMLElement>,
    productId: number,
  ) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuProductId(productId);
  };
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setMenuProductId(null);
  };
  const handleShowMovement = async () => {
    if (menuProductId) {
      const movements = await getProductMovements(menuProductId);
      setSelectedMovements(movements);
      setMovementsDialogOpen(true);
    }
    handleMenuClose();
  };
  const handleCreatePurchaseOrder = async () => {
    if (menuProductId) {
      const lastVendor = await getLastVendorForProduct(menuProductId);
      router.push(
        `/vouchers/Purchase-Vouchers/purchase-order?productId=${menuProductId}${lastVendor ? `&vendorId=${lastVendor.id}` : ""}`,
      );
    }
    handleMenuClose();
  };

  const renderDesktopTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Product Name</TableCell>
            <TableCell>Quantity</TableCell>
            <TableCell>Unit Price</TableCell>
            <TableCell>Total Value</TableCell>
            <TableCell>Reorder Level</TableCell>
            <TableCell>Last Updated</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {isFetching ? (
            <TableRow>
              <TableCell colSpan={7} align="center">
                Loading...
              </TableCell>
            </TableRow>
          ) : filteredStockData?.map((stock: any) => (
            <TableRow
              key={stock.id}
              sx={{
                backgroundColor:
                  stock.quantity <= stock.reorder_level
                    ? "yellow.main"
                    : "inherit",
              }}
            >
              <TableCell>{stock.product_name}</TableCell>
              <TableCell>
                {stock.quantity} {stock.unit}
              </TableCell>
              <TableCell>{stock.unit_price}</TableCell>
              <TableCell>{stock.total_value}</TableCell>
              <TableCell>{stock.reorder_level}</TableCell>
              <TableCell>{stock.last_updated}</TableCell>
              <TableCell>
                <IconButton
                  onClick={() =>
                    alert(`Details: {stock.description}`)
                  }
                >
                  <Visibility />
                </IconButton>
                <IconButton onClick={() => handleEditStock(stock)}>
                  <Edit />
                </IconButton>
                <IconButton
                  onClick={(e) =>
                    handleMenuClick(e, stock.product_id)
                  }
                >
                  <MoreVert />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderMobileCards = () => (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {isFetching ? (
        <Typography align="center">Loading...</Typography>
      ) : filteredStockData?.map((stock: any) => (
        <Card 
          key={stock.id} 
          sx={{ 
            backgroundColor: stock.quantity <= stock.reorder_level ? 'warning.light' : 'inherit',
            boxShadow: 1,
            borderRadius: 2
          }}
        >
          <CardContent sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              {stock.product_name}
            </Typography>
            <Typography variant="body2">
              Quantity: {stock.quantity} {stock.unit}
            </Typography>
            <Typography variant="body2">
              Unit Price: {stock.unit_price}
            </Typography>
            <Typography variant="body2">
              Total Value: {stock.total_value}
            </Typography>
            <Typography variant="body2">
              Reorder Level: {stock.reorder_level}
            </Typography>
            <Typography variant="body2">
              Last Updated: {stock.last_updated}
            </Typography>
          </CardContent>
          <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
            <IconButton
              onClick={() =>
                alert(`Details: {stock.description}`)
              }
              size="small"
            >
              <Visibility />
            </IconButton>
            <IconButton onClick={() => handleEditStock(stock)} size="small">
              <Edit />
            </IconButton>
            <IconButton
              onClick={(e) =>
                handleMenuClick(e, stock.product_id)
              }
              size="small"
            >
              <MoreVert />
            </IconButton>
          </CardActions>
        </Card>
      ))}
    </Box>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Stock Management
        </Typography>
        {/* Show loading or error states before organization context is ready */}
        {!isOrgContextReady && (
          <Paper sx={{ p: 3, textAlign: "center" }}>
            <Typography variant="h6" color="text.secondary">
              Loading organization context...
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Please wait while we verify your organization access.
            </Typography>
          </Paper>
        )}
        {/* Show error message if there's a stock loading error */}
        {isOrgContextReady && stockError && (
          <Paper
            sx={{
              p: 3,
              textAlign: "center",
              backgroundColor: "error.light",
              color: "error.contrastText",
            }}
          >
            <Typography variant="h6">Unable to load stock data</Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              {(stockError as any)?.userMessage ||
                stockError?.message ||
                "Please check your organization setup and try again."}
            </Typography>
          </Paper>
        )}
        {/* Only show main interface when organization context is ready */}
        {isOrgContextReady && (
          <>
            <Paper
              sx={{
                p: 2,
                mb: 2,
                position: "sticky",
                top: 0,
                zIndex: 1000,
                backgroundColor: "white",
              }}
            >
              <Grid container spacing={2} alignItems="center">
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    label="Search"
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={showZero}
                                onChange={(e) => setShowZero(e.target.checked)}
                              />
                            }
                            label="Zero Stock"
                            labelPlacement="start"
                            sx={{ mr: 0 }}
                          />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 8 }}>
                  <Stack
                    direction={{ xs: 'column', sm: 'row' }}
                    spacing={1}
                    justifyContent="flex-end"
                    sx={{ flexWrap: 'wrap' }}
                  >
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={handleManualEntry}
                      sx={{ minWidth: "120px" }}
                      disabled={!user?.organization_id}
                    >
                      Manual Entry
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<GetApp />}
                      onClick={handleDownloadTemplate}
                      sx={{ minWidth: "120px" }}
                    >
                      Download Template
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<Publish />}
                      onClick={handleImportClick}
                      sx={{ minWidth: "120px" }}
                      disabled={!user?.organization_id}
                    >
                      Import
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<GetApp />}
                      onClick={handleExport}
                      sx={{ minWidth: "120px" }}
                      disabled={!user?.organization_id}
                    >
                      Export
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<Print />}
                      onClick={handlePrint}
                      sx={{ minWidth: "120px" }}
                      disabled={!user?.organization_id}
                    >
                      Print Stock
                    </Button>
                  </Stack>
                </Grid>
              </Grid>
            </Paper>
            <Box
              sx={{
                overflowY: "auto",
                maxHeight:
                  "calc(100vh - 200px)" /* Adjust based on header heights */,
                position: "relative",
                zIndex: 1,
              }}
            >
              {isMobile ? renderMobileCards() : renderDesktopTable()}
            </Box>
          </>
        )}
      </Container>
      {/* Kebab Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleShowMovement}>
          <ListItemIcon>
            <HistoryIcon />
          </ListItemIcon>
          <ListItemText>Show Movement</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCreatePurchaseOrder}>
          <ListItemIcon>
            <PurchaseIcon />
          </ListItemIcon>
          <ListItemText>Create Purchase Order</ListItemText>
        </MenuItem>
      </Menu>
      {/* Movements Dialog */}
      <Dialog
        open={movementsDialogOpen}
        onClose={() => setMovementsDialogOpen(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>Stock Movements</DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Reference</TableCell>
                  <TableCell>Notes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selectedMovements.map((movement) => (
                  <TableRow key={movement.id}>
                    <TableCell>
                      {new Date(movement.transaction_date).toLocaleString()}
                    </TableCell>
                    <TableCell>{movement.transaction_type}</TableCell>
                    <TableCell>{movement.quantity}</TableCell>
                    <TableCell>{movement.reference_number || "-"}</TableCell>
                    <TableCell>{movement.notes || "-"}</TableCell>
                  </TableRow>
                ))}
                {selectedMovements.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No movements found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMovementsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      {/* Edit Stock Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} fullWidth maxWidth="xs" fullScreen={isMobile}>
        <DialogTitle>Edit Stock</DialogTitle>
        <DialogContent>
          <TextField
            label="Quantity"
            type="number"
            value={editFormData.quantity}
            onChange={(e) =>
              setEditFormData({ quantity: parseFloat(e.target.value) })
            }
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit}>Save</Button>
        </DialogActions>
      </Dialog>
      {/* Manual Entry Dialog */}
      <Dialog
        open={manualDialogOpen}
        onClose={() => setManualDialogOpen(false)}
        fullWidth
        maxWidth="xs"
        fullScreen={isMobile}
      >
        <DialogTitle>Manual Stock Entry</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Product</InputLabel>
            <Select
              value={manualFormData.product_id}
              onChange={(e) => {
                const product = products.find(
                  (p: any) => p.id === e.target.value,
                );
                setManualFormData({
                  ...manualFormData,
                  product_id: product.id,
                  unit: product.unit,
                });
              }}
            >
              {products?.map((p: any) => (
                <MenuItem key={p.id} value={p.id}>
                  {p.product_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Quantity"
            type="number"
            value={manualFormData.quantity}
            onChange={(e) =>
              setManualFormData({
                ...manualFormData,
                quantity: parseFloat(e.target.value),
              })
            }
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Unit"
            value={manualFormData.unit}
            disabled
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManualDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveManual}>Save</Button>
        </DialogActions>
      </Dialog>
      {/* Import Mode Prompt Dialog */}
      <Dialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>Import Stock</DialogTitle>
        <DialogContent>
          <Typography>Existing stock found. Do you want to:</Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid size={{ xs: 6 }}>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => handleImportConfirm("replace")}
              >
                Replace Stock
              </Button>
            </Grid>
            <Grid size={{ xs: 6 }}>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => handleImportConfirm("add")}
              >
                Add to Stock
              </Button>
            </Grid>
          </Grid>
          <Box sx={{ textAlign: "center", mt: 2 }}>
            <Button variant="text" onClick={() => setImportDialogOpen(false)}>
              Cancel
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
};
export default StockManagement;