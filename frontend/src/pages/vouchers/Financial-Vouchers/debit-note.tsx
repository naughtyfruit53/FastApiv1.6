// Debit Note Page - Refactored using shared DRY logic with 40:60 split layout
import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Container,
  Autocomplete,
  InputAdornment,
  Tooltip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@mui/material";
import { Add } from "@mui/icons-material";
import AddCustomerModal from "../../../components/AddCustomerModal";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherListModal from "../../../components/VoucherListModal";
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';
import axios from 'axios';
import { useVoucherPage } from "../../../hooks/useVoucherPage";
import { formatCurrency } from "../../../utils/currencyUtils";
import {
  getVoucherConfig,
  getVoucherStyles,
} from "../../../utils/voucherUtils";
const DebitNotePage: React.FC = () => {
  const config = getVoucherConfig("debit-note");
  const voucherStyles = getVoucherStyles();
  const {
    // State
    mode,
    setMode,
    isLoading,
    showAddCustomerModal,
    setShowAddCustomerModal,
    addCustomerLoading,
    setAddCustomerLoading,
    showFullModal,
    contextMenu,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,
    // Form
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    errors,
    // Data
    voucherList,
    customerList,
    sortedVouchers,
    // Mutations
    createMutation,
    updateMutation,
    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu: handleContextMenuClose,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,
    // Utilities
    isViewMode,
  } = useVoucherPage(config);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  
  // Watch form values
  const watchedValues = watch();
  const totalAmount = watchedValues?.total_amount || 0;
  // Combined customer options for autocomplete
  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach((key) => {
      setValue(key, voucher[key]);
    });
  };
  // Handle customer creation success
  const handleCustomerCreated = async (newCustomer: any): Promise<void> => {
    setValue("customer_id", newCustomer.id);
    refreshMasterData();
  };

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      const currentDate = watch('date');
      if (currentDate && mode === 'create') {
        try {
          const response = await axios.get(
            `/api/v1/debit-notes/next-number?voucher_date=${currentDate}`
          );
          setValue('voucher_number', response.data);
          
          const conflictResponse = await axios.get(
            `/api/v1/debit-notes/check-backdated-conflict?voucher_date=${currentDate}`
          );
          
          if (conflictResponse.data.has_conflict) {
            setConflictInfo(conflictResponse.data);
            setShowConflictModal(true);
            setPendingDate(currentDate);
          }
        } catch (error) {
          console.error('Error fetching voucher number:', error);
        }
      }
    };
    
    fetchVoucherNumber();
  }, [watch('date'), mode, setValue]);

  // Conflict modal handlers
  const handleChangeDateToSuggested = () => {
    if (conflictInfo?.suggested_date) {
      setValue('date', conflictInfo.suggested_date.split('T')[0]);
      setShowConflictModal(false);
      setPendingDate(null);
    }
  };

  const handleProceedAnyway = () => {
    setShowConflictModal(false);
  };

  const handleCancelConflict = () => {
    setShowConflictModal(false);
    if (pendingDate) {
      setValue('date', '');
    }
    setPendingDate(null);
  };
  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List (40%) */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Paper
            sx={{
              p: 2,
              height: "calc(100vh - 120px)",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h6">Debit Notes</Typography>
              <VoucherHeaderActions
                mode={mode}
                voucherType="Debit Note"
                voucherRoute="/vouchers/Financial-Vouchers/debit-note"
                onModeChange={(newMode) => setMode(newMode)}
                onModalOpen={handleModalOpen}
              />
            </Box>
            {isLoading ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ flexGrow: 1, overflow: "auto" }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sr.</TableCell>
                      <TableCell>Voucher #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sortedVouchers
                      .slice(0, 7)
                      .map((voucher: any, index: number) => (
                        <TableRow
                          key={voucher.id}
                          onClick={() => handleVoucherClick(voucher)}
                          onContextMenu={(e) => handleContextMenu(e, voucher)}
                          sx={{
                            cursor: "pointer",
                            "&:hover": { bgcolor: "action.hover" },
                          }}
                        >
                          <TableCell>{index + 1}</TableCell>
                          <TableCell>{voucher.voucher_number}</TableCell>
                          <TableCell>
                            {new Date(voucher.date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            {customerList?.find(
                              (c: any) => c.id === voucher.customer_id,
                            )?.name || "N/A"}
                          </TableCell>
                          <TableCell>
                            {formatCurrency(voucher.total_amount || 0)}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Paper>
        </Grid>
        {/* Right side - Voucher Form (60%) */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper sx={{ p: 3, height: "calc(100vh - 120px)", overflow: "auto" }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h6">
                {mode === "create"
                  ? "Create"
                  : mode === "edit"
                    ? "Edit"
                    : "View"}{" "}
                Debit Note
              </Typography>
              {mode !== "create" && (
                <Box>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleGeneratePDF()}
                    sx={{ mr: 1 }}
                  >
                    Generate PDF
                  </Button>
                </Box>
              )}
            </Box>
            {(createMutation.isPending || updateMutation.isPending) && (
              <Box display="flex" justifyContent="center" my={2}>
                <CircularProgress />
              </Box>
            )}
            <Box
              component="form"
              onSubmit={handleSubmit(handleSubmitForm)}
              sx={{
                mt: 3,
                ...voucherStyles.formContainer,
              }}
            >
              <Grid container spacing={3}>
                <Grid size={6}>
                  <TextField
                    {...control.register("voucher_number")}
                    label="Debit Note Number"
                    fullWidth
                    disabled={true}
                    sx={voucherStyles.centerField}
                    InputProps={{
                      readOnly: true,
                      style: { textAlign: "center", fontWeight: "bold" },
                    }}
                  />
                </Grid>
                <Grid size={6}>
                  <TextField
                    {...control.register("date")}
                    label="Date"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    sx={voucherStyles.centerField}
                    disabled={isViewMode}
                  />
                </Grid>
                <Grid size={12}>
                  <Autocomplete
                    options={customerList || []}
                    getOptionLabel={(option) => option.name || ""}
                    value={
                      customerList?.find(
                        (c: any) => c.id === watch("customer_id"),
                      ) || null
                    }
                    onChange={(_, newValue) => {
                      setValue("customer_id", newValue?.id || null);
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Customer"
                        required
                        disabled={isViewMode}
                        error={!!errors.customer_id}
                        helperText={errors.customer_id?.message as string}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {!isViewMode && (
                                <Tooltip title="Add New Customer">
                                  <Button
                                    size="small"
                                    onClick={() =>
                                      setShowAddCustomerModal(true)
                                    }
                                    sx={{ minWidth: "auto", p: 0.5 }}
                                  >
                                    <Add fontSize="small" />
                                  </Button>
                                </Tooltip>
                              )}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
                    disabled={isViewMode}
                  />
                </Grid>
                <Grid size={6}>
                  <TextField
                    {...control.register("total_amount")}
                    label="Total Amount"
                    type="number"
                    fullWidth
                    required
                    disabled={isViewMode}
                    sx={voucherStyles.centerField}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">₹</InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid size={6}>
                  <TextField
                    {...control.register("reference")}
                    label="Reference"
                    fullWidth
                    disabled={isViewMode}
                    sx={voucherStyles.centerField}
                  />
                </Grid>
                <Grid size={12}>
                  <TextField
                    {...control.register("notes")}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={3}
                    disabled={isViewMode}
                  />
                </Grid>
                {totalAmount > 0 && (
                  <Grid size={12}>
                    <Alert severity="info">
                      <Typography variant="body2">
                        Amount in words: {getAmountInWords(totalAmount)}
                      </Typography>
                    </Alert>
                  </Grid>
                )}
                {!isViewMode && (
                  <Grid size={12}>
                    <Box
                      sx={{
                        display: "flex",
                        gap: 2,
                        justifyContent: "flex-end",
                      }}
                    >
                      <Button
                        type="submit"
                        variant="contained"
                        disabled={
                          createMutation.isPending || updateMutation.isPending
                        }
                      >
                        {mode === "create" ? "Create" : "Update"} Debit Note
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      {/* Add Customer Modal */}
      <AddCustomerModal
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onAdd={handleCustomerCreated}
        loading={addCustomerLoading}
      />
      {/* Context Menu */}
      <VoucherContextMenu
        voucherType="debit-note"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onPrint={() => handleGeneratePDF()}
      />
      {/* Voucher List Modal */}
      <VoucherListModal
        open={showFullModal}
        onClose={handleModalClose}
        vouchers={filteredVouchers}
        voucherType="Debit Note"
        onVoucherClick={handleView}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onGeneratePDF={handleGeneratePDF}
      />
      <VoucherDateConflictModal
        open={showConflictModal}
        onClose={handleCancelConflict}
        conflictInfo={conflictInfo}
        onChangeDateToSuggested={handleChangeDateToSuggested}
        onProceedAnyway={handleProceedAnyway}
        voucherType="Debit Note"
      />
    </Container>
  );
};
export default DebitNotePage;
