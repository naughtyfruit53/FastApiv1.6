// frontend/src/pages/inventory/low-stock.tsx

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getLowStockReport, getProductMovements, getLastVendorForProduct } from '../../services/stockService';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import { MoreVert, History as HistoryIcon, ShoppingCart as PurchaseIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useAuth } from '../../context/AuthContext';

const LowStockReport: React.FC = () => {
  const router = useRouter();
  const { isOrgContextReady } = useAuth();
  const [movementsDialogOpen, setMovementsDialogOpen] = useState(false);
  const [selectedMovements, setSelectedMovements] = useState<any[]>([]);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuProductId, setMenuProductId] = useState<number | null>(null);

  const { data: lowStockItems, isLoading } = useQuery({
    queryKey: ['lowStock'],
    queryFn: getLowStockReport,
    enabled: isOrgContextReady,
  });

  if (isLoading) {return <Typography>Loading low stock report...</Typography>;}

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, productId: number) => {
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
      router.push(`/vouchers/Purchase-Vouchers/purchase-order?productId=${menuProductId}${lastVendor ? `&vendorId=${lastVendor.id}` : ''}`);
    }
    handleMenuClose();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Low Stock Report
      </Typography>
      {lowStockItems?.length === 0 ? (
        <Alert severity="success">No low stock items found. All items are above reorder levels.</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>Current Stock</TableCell>
                <TableCell>Reorder Level</TableCell>
                <TableCell>Deficit</TableCell>
                <TableCell>Suggested Order</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {lowStockItems?.map((item) => (
                <TableRow key={item.product_id} sx={{ backgroundColor: 'warning.light' }}>
                  <TableCell>{item.product_name}</TableCell>
                  <TableCell>{item.quantity} {item.unit}</TableCell>
                  <TableCell>{item.reorder_level}</TableCell>
                  <TableCell>{item.quantity - item.reorder_level}</TableCell>
                  <TableCell>{item.suggested_order_quantity || item.reorder_level * 2}</TableCell>
                  <TableCell>{item.location || '-'}</TableCell>
                  <TableCell>
                    <IconButton onClick={(e) => handleMenuClick(e, item.product_id)}>
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Kebab Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleShowMovement}>
          <ListItemIcon><HistoryIcon /></ListItemIcon>
          <ListItemText>Show Movement</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCreatePurchaseOrder}>
          <ListItemIcon><PurchaseIcon /></ListItemIcon>
          <ListItemText>Create Purchase Order</ListItemText>
        </MenuItem>
      </Menu>

      {/* Movements Dialog */}
      <Dialog open={movementsDialogOpen} onClose={() => setMovementsDialogOpen(false)} maxWidth="md" fullWidth>
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
                    <TableCell>{new Date(movement.transaction_date).toLocaleString()}</TableCell>
                    <TableCell>{movement.transaction_type}</TableCell>
                    <TableCell>{movement.quantity}</TableCell>
                    <TableCell>{movement.reference_number || '-'}</TableCell>
                    <TableCell>{movement.notes || '-'}</TableCell>
                  </TableRow>
                ))}
                {selectedMovements.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">No movements found</TableCell>
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
    </Container>
  );
};

export default LowStockReport;