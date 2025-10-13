// pages/inventory/index.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid as Grid,
  Alert,
  FormControlLabel,
  Checkbox,
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
} from "@mui/material";
import {
  Add,
  Refresh,
  Warning,
  TrendingUp,
  TrendingDown,
  Inventory,
  SwapHoriz,
  GetApp,
  Publish,
  Print,
  MoreVert,
  History as HistoryIcon,
  ShoppingCart as PurchaseIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Edit as EditIcon,
  Tune as AdjustIcon,
  ArrowBack as ArrowBackIcon,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { masterDataService } from "../../services/authService"; // Keep for other calls if needed
import { getStock, getProductMovements, getLastVendorForProduct } from "../../services/stockService"; // CHANGED: Import getStock from stockService
import { useRouter } from "next/router";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import CardActions from "@mui/material/CardActions";
import { toast } from "react-toastify";
import { jsPDF } from "jspdf";
import "jspdf-autotable";
import { organizationService } from "../../services/organizationService";
import SortableTable, { HeadCell } from "../../components/SortableTable";
import AddProductModal from "../../components/AddProductModal";

declare module "jspdf" {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}

const InventoryManagement: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const queryClient = useQueryClient();
  const router = useRouter();
  const [searchText, setSearchText] = useState("");
  const [hideZero, setHideZero] = useState(false);
  const [adjustmentDialog, setAdjustmentDialog] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [adjustment, setAdjustment] = useState({ quantity: "", reason: "" });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [movementsDialogOpen, setMovementsDialogOpen] = useState(false);
  const [selectedMovements, setSelectedMovements] = useState<any[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuItem, setMenuItem] = useState<any>(null);
  const [importExportAnchorEl, setImportExportAnchorEl] = useState<null | HTMLElement>(null);
  const [manualDialogOpen, setManualDialogOpen] = useState(false);
  const [manualFormData, setManualFormData] = useState({
    product_id: 0,
    quantity: 0,
    unit: "",
  });
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<any>(null);
  const [editFormData, setEditFormData] = useState({ quantity: 0 });
  const [productModalOpen, setProductModalOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState<any>(null);
  const [valueDialogOpen, setValueDialogOpen] = useState(false);
  const [filterType, setFilterType] = useState<'none' | 'low_stock' | 'out_of_stock'>('none');
  
  // Fetch data from APIs
  const {
    data: stock,
    isLoading: stockLoading,
    refetch: refetchStock,
  } = useQuery({
    queryKey: ["stock", {search: searchText, show_zero: !hideZero}],
    queryFn: getStock, // CHANGED: Use new getStock from stockService
    refetchInterval: 30000, // Refresh every 30 seconds
  });
  // NEW: Separate query for unfiltered total count
  const {
    data: totalStock,
    isLoading: totalStockLoading,
  } = useQuery({
    queryKey: ["totalStock"],
    queryFn: () => getStock({ queryKey: ["stock", {search: "", show_zero: true}] }), // No filters
  });
  const totalValue = React.useMemo(() => {
    if (!totalStock) return 0;
    return totalStock.reduce(
      (sum: number, item: any) =>
        sum + (item.total_value || item.quantity * (item.unit_price || 0)),
      0,
    );
  }, [totalStock]);
  const { data: lowStock, isLoading: lowStockLoading } = useQuery({
    queryKey: ["lowStock"],
    queryFn: masterDataService.getLowStock,
  });
  const { data: products } = useQuery({
    queryKey: ["products"],
    queryFn: () => masterDataService.getProducts(),
  });
  const { data: organizationData } = useQuery({
    queryKey: ["organization"],
    queryFn: organizationService.getCurrentOrganization,
  });
  // Stock adjustment mutation
  const adjustStockMutation = useMutation({
    mutationFn: ({
      productId,
      quantityChange,
      reason,
    }: {
      productId: number;
      quantityChange: number;
      reason: string;
    }) => masterDataService.adjustStock(productId, quantityChange, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      queryClient.invalidateQueries({ queryKey: ["lowStock"] });
      setAdjustmentDialog(false);
      setAdjustment({ quantity: "", reason: "" });
      setSelectedProduct(null);
    },
  });

  const updateStockMutation = useMutation({
    mutationFn: (data: any) =>
      masterDataService.updateStock(data.product_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      queryClient.invalidateQueries({ queryKey: ["lowStock"] });
      setEditDialogOpen(false);
      setManualDialogOpen(false);
    },
  });

  // Stock import mutation
  const importStockMutation = useMutation({
    mutationFn: ({ file, mode }: { file: File; mode: "add" | "replace" }) =>
      masterDataService.bulkImportStock(file, mode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      queryClient.invalidateQueries({ queryKey: ["lowStock"] });
      alert("Stock import completed successfully.");
    },
    onError: (error: any) => {
      console.error("Bulk import error", error);
      alert(
        `Import failed: ${error.userMessage || "Please check the file format and required columns."}`,
      );
    },
  });
  const handleImportStock = (importedData: any[]) => {
    // Convert imported data back to a format the API expects
    // This is a temporary workaround for the type mismatch
    console.log("Imported stock data:", importedData);
    // For now, just refetch stock data instead of sending to API
    refetchStock();
  };
  const handleAdjustStock = () => {
    if (selectedProduct && adjustment.quantity && adjustment.reason) {
      adjustStockMutation.mutate({
        productId: selectedProduct.product_id,
        quantityChange: parseFloat(adjustment.quantity),
        reason: adjustment.reason,
      });
    }
  };
  const openAdjustmentDialog = (product: any) => {
    setSelectedProduct(product);
    setAdjustmentDialog(true);
  };
  const renderStockTable = (
    stockItems: any[],
    showLowStockOnly = false,
    isLoading = false,
  ) => {
    if (isLoading) {
      return <Typography>Loading stock data...</Typography>;
    }
    if (!stockItems || stockItems.length === 0) {
      return <Typography>No stock data available.</Typography>;
    }
    let filteredItems = stockItems;
    if (filterType === 'low_stock') {
      filteredItems = stockItems.filter(
        (item) => item.quantity > 0 && item.quantity <= (item.reorder_level || 0),
      );
    } else if (filterType === 'out_of_stock') {
      filteredItems = stockItems.filter(
        (item) => item.quantity === 0,
      );
    } else if (showLowStockOnly) {
      filteredItems = stockItems.filter(
        (item) =>
          item.is_low_stock || item.quantity <= (item.reorder_level || 0),
      );
    }

    const headCells: HeadCell<any>[] = [
      { 
        id: 'product_name', 
        label: 'Product Name', 
        numeric: false,
        render: (value, row) => (
          <Typography 
            sx={{ cursor: 'pointer' }}
            onClick={() => handleEditProduct(row)}
          >
            {value}
          </Typography>
        )
      },
      { id: 'quantity', label: 'Current Stock', numeric: true },
      { id: 'unit', label: 'Unit', numeric: false },
      { id: 'unit_price', label: 'Unit Price', numeric: true, render: (value) => `₹${(value || 0).toLocaleString()}` },
      { id: 'total_value', label: 'Total Value', numeric: true, render: (value, row) => `₹${(value || row.quantity * (row.unit_price || 0)).toLocaleString()}` },
      { id: 'reorder_level', label: 'Reorder Level', numeric: true },
      {
        id: 'status' as any, // Dummy id for calculated column
        label: 'Status',
        numeric: false,
        sortable: false,
        render: (value, row) => (
          <Chip
            label={
              row.quantity <= 0
                ? "Out of Stock"
                : row.quantity <= (row.reorder_level || 0)
                  ? "Low Stock"
                  : "Normal"
            }
            color={
              row.quantity <= 0
                ? "error"
                : row.quantity <= (row.reorder_level || 0)
                  ? "warning"
                  : "success"
            }
            size="small"
          />
        ),
      },
    ];

    return (
      <TableContainer component={Paper} sx={{ width: '100%', '& .MuiTableCell-root': { textAlign: 'center' } }}>
        <SortableTable
          data={filteredItems}
          headCells={headCells}
          defaultOrderBy="product_name"
          actions={(item) => (
            <>
              <IconButton
                onClick={(e) =>
                  handleMenuClick(e, item)
                }
              >
                <MoreVert />
              </IconButton>
            </>
          )}
          rowSx={(item) => ({
            backgroundColor:
              item.quantity <= 0
                ? 'error.light'
                : item.quantity <= (item.reorder_level || 0)
                  ? 'warning.light'
                  : 'success.light',
          })}
        />
      </TableContainer>
    );
  };
  const renderSummaryCards = () => {
    if (stockLoading || !stock || totalStockLoading || !totalStock) {
      return <Typography>Loading inventory summary...</Typography>;
    }
    const totalItems = totalStock.length; // Use unfiltered total
    const lowStockItems = totalStock.filter(
      (item: any) => item.quantity <= (item.reorder_level || 0),
    ).length;
    const outOfStockItems = totalStock.filter(
      (item: any) => item.quantity === 0,
    ).length;
    const cards = [
      {
        title: "Total Items",
        value: totalItems,
        color: "#1976D2",
        icon: <Inventory />,
        onClick: () => toast.info(`Total Items: ${totalItems}`),
      },
      {
        title: "Total Value",
        value: `₹${totalValue.toLocaleString()}`,
        color: "#2E7D32",
        icon: <TrendingUp />,
        onClick: () => setValueDialogOpen(true),
      },
      {
        title: "Low Stock Items",
        value: lowStockItems,
        color: "#F57C00",
        icon: <Warning />,
        onClick: () => setFilterType('low_stock'),
      },
      {
        title: "Out of Stock",
        value: outOfStockItems,
        color: "#D32F2F",
        icon: <TrendingDown />,
        onClick: () => setFilterType('out_of_stock'),
      },
    ];
    return (
      <Grid container spacing={3}>
        {cards.map((card, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
            <Card sx={{ cursor: card.onClick ? 'pointer' : 'default' }} onClick={card.onClick}>
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
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>{card.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && filterType !== 'none') {
        setFilterType('none');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [filterType]);

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
      importStockMutation.mutate({ file: selectedFile, mode });
    }
    setImportDialogOpen(false);
    setSelectedFile(null);
  };

  const handleExport = async () => {
    try {
      await masterDataService.exportStock({
        search: searchText,
        show_zero: !hideZero,
      });
    } catch (err) {
      alert("Failed to export stock data. Please try again.");
    }
  };

  const handlePrint = () => {
    generateStockReport("stock_report.pdf", organizationData, stock);
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

  const handleMenuClick = (
    event: React.MouseEvent<HTMLElement>,
    item: any,
  ) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuItem(item);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setMenuItem(null);
  };

  const handleShowMovement = async () => {
    if (menuItem) {
      const movements = await getProductMovements(menuItem.product_id);
      setSelectedMovements(movements);
      setMovementsDialogOpen(true);
    }
    handleMenuClose();
  };

  const handleCreatePurchaseOrder = async () => {
    if (menuItem) {
      const lastVendor = await getLastVendorForProduct(menuItem.product_id);
      router.push(
        `/vouchers/Purchase-Vouchers/purchase-order?productId=${menuItem.product_id}${lastVendor ? `&vendorId=${lastVendor.id}` : ""}`,
      );
    }
    handleMenuClose();
  };

  const handleEditStockQuantity = () => {
    if (menuItem) {
      handleEditStock(menuItem);
    }
    handleMenuClose();
  };

  const handleAdjustStockItem = () => {
    if (menuItem) {
      openAdjustmentDialog(menuItem);
    }
    handleMenuClose();
  };

  const handleEditProduct = (item: any) => {
    // Fix: Use product_id as the id for editing the product (not stock id)
    setSelectedProductForEdit({ ...item, id: item.product_id });
    setProductModalOpen(true);
  };

  const handleProductModalClose = () => {
    setProductModalOpen(false);
    setSelectedProductForEdit(null);
  };

  const handleProductUpdate = async (updatedProduct: any) => {
    try {
      await masterDataService.updateProduct(updatedProduct.id, updatedProduct);
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      toast.success("Product updated successfully");
      handleProductModalClose();
    } catch (err) {
      toast.error("Failed to update product");
    }
  };

  const handleImportExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setImportExportAnchorEl(event.currentTarget);
  };

  const handleImportExportClose = () => {
    setImportExportAnchorEl(null);
  };

  const handleDownloadTemplateMenu = () => {
    handleDownloadTemplate();
    handleImportExportClose();
  };

  const handleImportMenu = () => {
    handleImportClick();
    handleImportExportClose();
  };

  const handleExportMenu = () => {
    handleExport();
    handleImportExportClose();
  };

  const renderDesktopTable = (stockItems: any[], showLowStockOnly = false, isLoading = false) => (
    renderStockTable(stockItems, showLowStockOnly, isLoading)
  );

  const renderMobileCards = (stockItems: any[], showLowStockOnly = false, isLoading = false) => {
    if (isLoading) {
      return <Typography>Loading stock data...</Typography>;
    }
    if (!stockItems || stockItems.length === 0) {
      return <Typography>No stock data available.</Typography>;
    }
    let filteredItems = stockItems;
    if (filterType === 'low_stock') {
      filteredItems = stockItems.filter(
        (item) => item.quantity > 0 && item.quantity <= (item.reorder_level || 0),
      );
    } else if (filterType === 'out_of_stock') {
      filteredItems = stockItems.filter(
        (item) => item.quantity === 0,
      );
    } else if (showLowStockOnly) {
      filteredItems = stockItems.filter(
        (item) =>
          item.is_low_stock || item.quantity <= (item.reorder_level || 0),
      );
    }

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {filteredItems.map((stock: any) => {
          let rowColor = 'inherit';
          if (stock.quantity <= 0) {
            rowColor = 'error.light';
          } else if (stock.quantity <= (stock.reorder_level || 0)) {
            rowColor = 'warning.light';
          } else {
            rowColor = 'success.light';
          }
          return (
            <Card 
              key={stock.id} 
              sx={{ 
                backgroundColor: rowColor,
                boxShadow: 1,
                borderRadius: 2
              }}
            >
              <CardContent sx={{ p: 2, textAlign: 'center' }}>
                <Typography 
                  variant="subtitle1" 
                  fontWeight="bold" 
                  gutterBottom
                  sx={{ cursor: 'pointer' }}
                  onClick={() => handleEditProduct(stock)}
                >
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
                  onClick={(e) =>
                    handleMenuClick(e, stock)
                  }
                  size="small"
                >
                  <MoreVert />
                </IconButton>
              </CardActions>
            </Card>
          );
        })}
      </Box>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ textAlign: 'center' }}>
              Current Stock
            </Typography>
          </Box>
        </Box>
        {/* Summary Cards */}
        <Box sx={{ mb: 4 }}>{renderSummaryCards()}</Box>
        {/* Inventory Content */}
        <Paper sx={{ mb: 4 }}>
          <Box sx={{ p: 3 }}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
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
                            checked={hideZero}
                            onChange={(e) => setHideZero(e.target.checked)}
                          />
                        }
                        label="Hide Zero Stock"
                        labelPlacement="start"
                        sx={{ mr: 0 }}
                      />
                    </InputAdornment>
                  ),
                }}
              />
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Button variant="contained" startIcon={<Add />} onClick={handleManualEntry}>
                  Add Stock Entry
                </Button>
                <Button
                  variant="contained"
                  startIcon={<GetApp />}
                  onClick={handleImportExportClick}
                >
                  Import/Export
                </Button>
                <Menu
                  anchorEl={importExportAnchorEl}
                  open={Boolean(importExportAnchorEl)}
                  onClose={handleImportExportClose}
                >
                  <MenuItem onClick={handleDownloadTemplateMenu}>
                    <ListItemIcon>
                      <GetApp />
                    </ListItemIcon>
                    <ListItemText>Download Template</ListItemText>
                  </MenuItem>
                  <MenuItem onClick={handleImportMenu}>
                    <ListItemIcon>
                      <GetApp />
                    </ListItemIcon>
                    <ListItemText>Import</ListItemText>
                  </MenuItem>
                  <MenuItem onClick={handleExportMenu}>
                    <ListItemIcon>
                      <Publish />
                    </ListItemIcon>
                    <ListItemText>Export</ListItemText>
                  </MenuItem>
                </Menu>
                <Button
                  variant="contained"
                  startIcon={<Print />}
                  onClick={handlePrint}
                >
                  Print Stock
                </Button>
                <IconButton onClick={() => refetchStock()}>
                  <Refresh />
                </IconButton>
              </Box>
            </Box>
            {filterType !== 'none' && (
              <IconButton
                onClick={() => setFilterType('none')}
                sx={{ mb: 2 }}
              >
                <ArrowBackIcon />
              </IconButton>
            )}
            {isMobile ? renderMobileCards(stock || []) : renderDesktopTable(stock || [])}
          </Box>
        </Paper>
      </Container>
      {/* Stock Adjustment Dialog */}
      <Dialog
        open={adjustmentDialog}
        onClose={() => setAdjustmentDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Adjust Stock: {selectedProduct?.product_name}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Current Stock: {selectedProduct?.quantity} {selectedProduct?.unit}
          </Typography>
          <TextField
            fullWidth
            label="Quantity Change"
            placeholder="Enter positive or negative number"
            value={adjustment.quantity}
            onChange={(e) =>
              setAdjustment((prev) => ({ ...prev, quantity: e.target.value }))
            }
            type="number"
            sx={{ mb: 2 }}
            helperText="Use negative numbers to decrease stock, positive to increase"
          />
          <TextField
            fullWidth
            label="Reason"
            placeholder="Reason for adjustment"
            value={adjustment.reason}
            onChange={(e) =>
              setAdjustment((prev) => ({ ...prev, reason: e.target.value }))
            }
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdjustmentDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAdjustStock}
            variant="contained"
            disabled={
              !adjustment.quantity ||
              !adjustment.reason ||
              adjustStockMutation.isPending
            }
          >
            {adjustStockMutation.isPending ? "Adjusting..." : "Adjust Stock"}
          </Button>
        </DialogActions>
      </Dialog>
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
        maxWidth="sm"
        fullScreen={isMobile}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Manual Stock Entry
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => {
                setManualDialogOpen(false);
                setProductModalOpen(true);
              }}
              size="small"
            >
              Add Product
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Autocomplete
            options={products || []}
            getOptionLabel={(option: any) => option.product_name || ''}
            value={products?.find((p: any) => p.id === manualFormData.product_id) || null}
            onChange={(_, newValue) => {
              if (newValue) {
                setManualFormData({
                  ...manualFormData,
                  product_id: newValue.id,
                  unit: newValue.unit,
                });
              }
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Product"
                placeholder="Search products..."
                fullWidth
                sx={{ mb: 2, mt: 2 }}
              />
            )}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
          />
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
      {/* Kebab Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditStockQuantity}>
          <ListItemIcon>
            <EditIcon />
          </ListItemIcon>
          <ListItemText>Edit Stock Quantity</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleAdjustStockItem}>
          <ListItemIcon>
            <AdjustIcon />
          </ListItemIcon>
          <ListItemText>Adjust Stock</ListItemText>
        </MenuItem>
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
      {/* Product Edit Modal */}
      <AddProductModal
        open={productModalOpen}
        onClose={handleProductModalClose}
        onAdd={async (newProduct: any) => {
          try {
            await masterDataService.createProduct(newProduct);
            queryClient.invalidateQueries({ queryKey: ["products"] });
            queryClient.invalidateQueries({ queryKey: ["stock"] });
            toast.success("Product created successfully");
            handleProductModalClose();
            // Reopen manual dialog after product creation
            setManualDialogOpen(true);
          } catch (err: any) {
            const errorMessage = err?.response?.data?.detail || err?.message || "Failed to create product";
            toast.error(`Error creating product: ${errorMessage}`);
            console.error("Product creation error:", err);
          }
        }}
        onUpdate={handleProductUpdate}
        initialData={selectedProductForEdit}
        mode={selectedProductForEdit ? "edit" : "add"}
      />
      {/* Value Dialog */}
      <Dialog open={valueDialogOpen} onClose={() => setValueDialogOpen(false)}>
        <DialogTitle>Total Stock Value</DialogTitle>
        <DialogContent>
          <Typography>Total Stock Value: ₹{(totalValue || 0).toLocaleString()}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setValueDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default InventoryManagement;