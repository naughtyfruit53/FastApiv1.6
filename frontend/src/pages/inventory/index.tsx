// pages/inventory/index.tsx
import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
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
  Edit,
  Refresh,
  Warning,
  TrendingUp,
  TrendingDown,
  Inventory,
  SwapHoriz,
  Visibility,
  GetApp,
  Publish,
  Print,
  MoreVert,
  History as HistoryIcon,
  ShoppingCart as PurchaseIcon,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { masterDataService } from "../../services/authService";
import { getProductMovements, getLastVendorForProduct } from "../../services/stockService";
import { useRouter } from "next/router";
import ExcelImportExport from "../../components/ExcelImportExport";
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

declare module "jspdf" {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`inventory-tabpanel-${index}`}
      aria-labelledby={`inventory-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}
const InventoryManagement: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const queryClient = useQueryClient();
  const router = useRouter();
  const [tabValue, setTabValue] = useState(0);
  const [searchText, setSearchText] = useState("");
  const [showZero, setShowZero] = useState(false);
  const [adjustmentDialog, setAdjustmentDialog] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [adjustment, setAdjustment] = useState({ quantity: "", reason: "" });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [movementsDialogOpen, setMovementsDialogOpen] = useState(false);
  const [selectedMovements, setSelectedMovements] = useState<any[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuProductId, setMenuProductId] = useState<number | null>(null);
  const [importExportAnchorEl, setImportExportAnchorEl] = useState<null | HTMLElement>(null);
  const [manualDialogOpen, setManualDialogOpen] = useState(false);
  const [manualFormData, setManualFormData] = useState({
    product_id: 0,
    quantity: 0,
    unit: "",
  });
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({ quantity: 0 });
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  // Fetch data from APIs
  const {
    data: stock,
    isLoading: stockLoading,
    refetch: refetchStock,
  } = useQuery({
    queryKey: ["stock"],
    queryFn: () => masterDataService.getStock(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
  const { data: lowStock, isLoading: lowStockLoading } = useQuery({
    queryKey: ["lowStock"],
    queryFn: masterDataService.getLowStock,
    enabled: tabValue === 1,
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
    let filteredItems = showLowStockOnly
      ? stockItems.filter(
          (item) =>
            item.is_low_stock || item.quantity <= (item.reorder_level || 0),
        )
      : stockItems;
    if (searchText) {
      const lowerSearch = searchText.toLowerCase();
      filteredItems = filteredItems.filter((stock: any) =>
        stock.product_name.toLowerCase().includes(lowerSearch)
      );
    }
    if (!showZero) {
      filteredItems = filteredItems.filter((stock: any) => stock.quantity > 0);
    }
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product Name</TableCell>
              <TableCell>Current Stock</TableCell>
              <TableCell>Unit</TableCell>
              <TableCell>Unit Price</TableCell>
              <TableCell>Total Value</TableCell>
              <TableCell>Reorder Level</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredItems.map((item) => (
              <TableRow key={item.product_id || item.id}>
                <TableCell>{item.product_name}</TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    {item.quantity}
                    {item.quantity <= (item.reorder_level || 0) && (
                      <Warning sx={{ color: "orange", ml: 1 }} />
                    )}
                  </Box>
                </TableCell>
                <TableCell>{item.unit}</TableCell>
                <TableCell>
                  ₹{(item.unit_price || 0).toLocaleString()}
                </TableCell>
                <TableCell>
                  ₹
                  {(
                    item.total_value || item.quantity * (item.unit_price || 0)
                  ).toLocaleString()}
                </TableCell>
                <TableCell>{item.reorder_level || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={
                      item.quantity <= (item.reorder_level || 0)
                        ? "Low Stock"
                        : item.quantity === 0
                          ? "Out of Stock"
                          : "Normal"
                    }
                    color={
                      item.quantity === 0
                        ? "error"
                        : item.quantity <= (item.reorder_level || 0)
                          ? "warning"
                          : "success"
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => openAdjustmentDialog(item)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton size="small" color="info">
                    <Visibility />
                  </IconButton>
                  <IconButton size="small" color="secondary">
                    <SwapHoriz />
                  </IconButton>
                  <IconButton
                    onClick={(e) =>
                      handleMenuClick(e, item.product_id)
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
  };
  const renderSummaryCards = () => {
    if (stockLoading || !stock) {
      return <Typography>Loading inventory summary...</Typography>;
    }
    const totalItems = stock.length;
    const totalValue = stock.reduce(
      (sum: number, item: any) =>
        sum + (item.total_value || item.quantity * (item.unit_price || 0)),
      0,
    );
    const lowStockItems = stock.filter(
      (item: any) => item.quantity <= (item.reorder_level || 0),
    ).length;
    const outOfStockItems = stock.filter(
      (item: any) => item.quantity === 0,
    ).length;
    const cards = [
      {
        title: "Total Items",
        value: totalItems,
        color: "#1976D2",
        icon: <Inventory />,
      },
      {
        title: "Total Value",
        value: `₹${totalValue.toLocaleString()}`,
        color: "#2E7D32",
        icon: <TrendingUp />,
      },
      {
        title: "Low Stock Items",
        value: lowStockItems,
        color: "#F57C00",
        icon: <Warning />,
      },
      {
        title: "Out of Stock",
        value: outOfStockItems,
        color: "#D32F2F",
        icon: <TrendingDown />,
      },
    ];
    return (
      <Grid container spacing={3}>
        {cards.map((card, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
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
        show_zero: showZero,
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
    let filteredItems = showLowStockOnly
      ? stockItems.filter(
          (item) =>
            item.is_low_stock || item.quantity <= (item.reorder_level || 0),
        )
      : stockItems;
    if (searchText) {
      const lowerSearch = searchText.toLowerCase();
      filteredItems = filteredItems.filter((stock: any) =>
        stock.product_name.toLowerCase().includes(lowerSearch)
      );
    }
    if (!showZero) {
      filteredItems = filteredItems.filter((stock: any) => stock.quantity > 0);
    }
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {filteredItems.map((stock: any) => (
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
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 4,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Inventory Management
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Real-time stock monitoring and inventory control
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={() => refetchStock()}
          >
            Refresh Stock
          </Button>
        </Box>
        {/* Summary Cards */}
        <Box sx={{ mb: 4 }}>{renderSummaryCards()}</Box>
        {/* Inventory Tabs */}
        <Paper sx={{ mb: 4 }}>
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="inventory tabs"
            >
              <Tab label="Current Stock" />
              <Tab label="Low Stock Alert" />
              <Tab label="Stock Movements" />
              <Tab label="Stock Valuation" />
            </Tabs>
          </Box>
          <TabPanel value={tabValue} index={0}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
              <Typography variant="h6">Current Stock Levels</Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
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
              </Box>
            </Box>
            <ExcelImportExport
              data={stock || []}
              entity="Stock"
              onImport={handleImportStock}
            />
            {isMobile ? renderMobileCards(stock || []) : renderDesktopTable(stock || [])}
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ mb: 3 }}>
              <Alert severity="warning" sx={{ mb: 2 }}>
                Items below reorder level require immediate attention
              </Alert>
              <Typography variant="h6">Low Stock Alert</Typography>
            </Box>
            {renderStockTable(
              lowStock || stock || [],
              true,
              lowStockLoading || stockLoading,
            )}
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
              <Typography variant="h6">Stock Movements</Typography>
              <Button variant="contained" startIcon={<SwapHoriz />}>
                View All Movements
              </Button>
            </Box>
            <Typography>Stock movement tracking coming soon...</Typography>
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
              <Typography variant="h6">Stock Valuation Report</Typography>
              <Button variant="contained" startIcon={<TrendingUp />}>
                Generate Report
              </Button>
            </Box>
            <Typography>Stock valuation reporting coming soon...</Typography>
          </TabPanel>
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
    </Box>
  );
};
export default InventoryManagement;