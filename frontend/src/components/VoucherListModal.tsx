// frontend/src/components/VoucherListModal.tsx
// Reusable modal component for displaying voucher lists with clickable functionality

import React, { useState } from 'react';
import {
  Modal,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Button,
  Grid,
  Chip,
  IconButton,
} from '@mui/material';
import { Close, Search } from '@mui/icons-material';
import VoucherContextMenu from './VoucherContextMenu';

interface VoucherListModalProps {
  open: boolean;
  onClose: () => void;
  voucherType: string;
  vouchers: any[];
  onVoucherClick: (voucher: any) => void;
  onEdit?: (id: number) => void;
  onView?: (id: number) => void;
  onDelete?: (id: number) => void;
  onGeneratePDF?: (voucher: any) => void;
  customerList?: any[];
  vendorList?: any[];
}

const VoucherListModal: React.FC<VoucherListModalProps> = ({
  open,
  onClose,
  voucherType,
  vouchers,
  onVoucherClick,
  onEdit,
  onView,
  onDelete,
  onGeneratePDF,
  customerList = [],
  vendorList = [],
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; voucher: any } | null>(null);

  // Filter vouchers based on search criteria
  const filteredVouchers = vouchers.filter((voucher) => {
    const matchesSearch = searchTerm === '' || 
      voucher.voucher_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      voucher.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      voucher.notes?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFromDate = fromDate === '' || new Date(voucher.date) >= new Date(fromDate);
    const matchesToDate = toDate === '' || new Date(voucher.date) <= new Date(toDate);
    
    return matchesSearch && matchesFromDate && matchesToDate;
  });

  const handleContextMenu = (event: React.MouseEvent, voucher: any) => {
    event.preventDefault();
    setContextMenu(
      contextMenu === null
        ? { mouseX: event.clientX, mouseY: event.clientY, voucher }
        : null,
    );
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  const handleVoucherClick = (voucher: any, event: React.MouseEvent) => {
    // Don't trigger if right-click (context menu)
    if (event.button === 2) return;
    
    onVoucherClick(voucher);
    onClose(); // Close modal after selection
  };

  const getEntityName = (voucher: any) => {
    if (voucher.customer_id && customerList.length > 0) {
      return customerList.find((c: any) => c.id === voucher.customer_id)?.name || 'N/A';
    }
    if (voucher.vendor_id && vendorList.length > 0) {
      return vendorList.find((v: any) => v.id === voucher.vendor_id)?.name || 'N/A';
    }
    return 'N/A';
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const modalStyle = {
    position: 'absolute' as const,
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '90%',
    maxWidth: 1000,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: 2,
    maxHeight: '90vh',
    overflow: 'auto',
  };

  return (
    <>
      <Modal open={open} onClose={onClose}>
        <Box sx={modalStyle}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              All {voucherType}
            </Typography>
            <IconButton onClick={onClose}>
              <Close />
            </IconButton>
          </Box>

          {/* Search Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="Voucher number, reference, notes..."
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <TextField
                label="From Date"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <TextField
                label="To Date"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 2 }}>
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setFromDate('');
                  setToDate('');
                }}
                fullWidth
                sx={{ height: '56px' }}
              >
                Clear
              </Button>
            </Grid>
          </Grid>

          {/* Results Summary */}
          <Box sx={{ mb: 2 }}>
            <Chip
              label={`${filteredVouchers.length} of ${vouchers.length} vouchers`}
              color="primary"
              variant="outlined"
            />
          </Box>

          {/* Voucher Table */}
          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold' }}>Voucher No.</TableCell>
                  <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold' }}>Customer</TableCell>
                  <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold' }}>Amount</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVouchers.map((voucher) => (
                  <TableRow
                    key={voucher.id}
                    hover
                    onClick={(e) => handleVoucherClick(voucher, e)}
                    onContextMenu={(e) => handleContextMenu(e, voucher)}
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <TableCell align="center">
                      <Typography variant="body2" fontWeight="medium">
                        {voucher.voucher_number}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">{formatDate(voucher.date)}</TableCell>
                    <TableCell align="center">{getEntityName(voucher)}</TableCell>
                    <TableCell align="center">
                      ₹{voucher.total_amount?.toLocaleString() || '0'}
                    </TableCell>
                  </TableRow>
                ))}
                {filteredVouchers.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography color="text.secondary">
                        No vouchers found matching your criteria
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Modal>

      {/* Context Menu */}
      {contextMenu && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType={voucherType}
          onView={onView || (() => {})}
          onEdit={onEdit || (() => {})}
          onDelete={onDelete || (() => {})}
          onPrint={onGeneratePDF ? () => onGeneratePDF(contextMenu.voucher) : undefined}
          open={true}
          onClose={handleCloseContextMenu}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}
    </>
  );
};

export default VoucherListModal;