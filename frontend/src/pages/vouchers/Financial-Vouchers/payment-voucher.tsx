// frontend/src/pages/vouchers/Financial-Vouchers/payment-voucher.tsx
import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Container,
  Autocomplete,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import SearchableDropdown from '../../../components/SearchableDropdown';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles, parseRateField } from '../../../utils/voucherUtils';
import { useReferenceOptions } from '../../../utils/nameRefUtils';
import { getEntityBalance, getVoucherBalance } from '../../../services/ledgerService';
import financialVoucherStyles from "../../../styles/financialVoucherStyles";

const PaymentVoucher: React.FC = () => {
  const config = getVoucherConfig('payment-voucher');
  const voucherStyles = getVoucherStyles();
  const {
    mode,
    isLoading,
    showFullModal,
    contextMenu,
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    errors,
    vendorList,
    customerList,
    employeeList,
    sortedVouchers,
    createMutation,
    updateMutation,
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu: handleContextMenuClose,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,
    isViewMode,
  } = useVoucherPage(config);

  const handleVoucherClick = (voucher: any) => {
    reset(voucher);
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
    if (voucher.date) {
      setValue('date', new Date(voucher.date).toISOString().split('T')[0]);
    }
  };

  const totalAmountValue = watch('total_amount');
  const selectedEntity = watch('entity');
  const reference = watch('reference');

  const referenceOptions = useReferenceOptions(
    selectedEntity?.id || null,
    selectedEntity?.type || null
  );

  const paymentMethods = ['Cash','Bank Transfer','Cheque','Credit Card','Debit Card','Online Payment','UPI','Net Banking'];

  const allParties = [
    ...(vendorList || []).map((v: any) => ({ id: v.id, name: v.name, type: 'Vendor', value: v.id, label: `${v.name}` })),
    ...(customerList || []).map((c: any) => ({ id: c.id, name: c.name, type: 'Customer', value: c.id, label: `${c.name}` })),
    ...(employeeList || []).map((e: any) => ({ id: e.id, name: e.name, type: 'Employee', value: e.id, label: `${e.name}` })),
  ];

  const [entityBalance, setEntityBalance] = useState<number | null>(null);
  const [voucherBalance, setVoucherBalance] = useState<number | null>(null);

  useEffect(() => {
    if (selectedEntity) {
      console.log('Fetching entity balance for:', selectedEntity.type, selectedEntity.id);
      getEntityBalance(selectedEntity.type, selectedEntity.id).then((balance) => {
        console.log('Entity balance fetched:', balance);
        setEntityBalance(balance);
      }).catch((err) => {
        console.error('Entity balance fetch error:', err);
        setEntityBalance(null);
      });
    } else {
      setEntityBalance(null);
    }
  }, [selectedEntity]);

  useEffect(() => {
    if (reference && referenceOptions.includes(reference)) {
      console.log('Fetching voucher balance for:', reference);
      getVoucherBalance(reference).then((balance) => {
        console.log('Voucher balance fetched:', balance);
        setVoucherBalance(balance);
      }).catch((err) => {
        console.error('Voucher balance fetch error:', err);
        setVoucherBalance(null);
      });
    } else {
      setVoucherBalance(null);
    }
  }, [reference, referenceOptions]);

  const handleSubmitFormMapped = (data: any) => {
    if (data.entity) {
      data.entity_id = data.entity.id;
      data.entity_type = data.entity.type;
      delete data.entity;
    }
    handleSubmitForm(data);  // Proceed with original submit
  };

  // Grid spacing adjustments
  const firstRowGapPx = 24;   // 3 * 8px
  const secondRowGapPx = 8;   // 1 * 8px

  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Party</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
            <TableCell align="right" sx={{ fontSize: 12, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(sortedVouchers?.length === 0) ? (
            <TableRow>
              <TableCell colSpan={5} align="center">No payment vouchers available</TableCell>
            </TableRow>
          ) : (
            sortedVouchers?.slice(0, 7).map((voucher: any) => (
              <TableRow
                key={voucher.id}
                hover
                onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}
                sx={{ cursor: 'pointer' }}
                onClick={() => handleView(voucher.id)}
              >
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {voucher.voucher_number}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {new Date(voucher.date).toLocaleDateString()}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {voucher.entity?.name || 'N/A'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.total_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Payment Voucher"
                    onView={() => handleView(voucher.id)}
                    onEdit={() => handleEdit(voucher.id)}
                    onDelete={() => handleDelete(voucher)}
                    onPrint={() => handleGeneratePDF()}
                    showKebab={true}
                    onClose={() => {}}
                  />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const formContent = (
    <Box>
      {/* Title + Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" sx={{ fontSize: 18, fontWeight: 'bold', textAlign: 'center', flex: 1 }}>
          Payment Voucher - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Payment Voucher"
          voucherRoute="/vouchers/Financial-Vouchers/payment-voucher"
          currentId={selectedEntity?.id}
        />
      </Box>

      {(createMutation.isPending || updateMutation.isPending) && (
        <Box display="flex" justifyContent="center" my={2}>
          <CircularProgress />
        </Box>
      )}

      <Box component="form" onSubmit={handleSubmit(handleSubmitFormMapped)} sx={{ mt: 1, ...financialVoucherStyles.formContainer, ...voucherStyles.formContainer }}>
        {/* FIRST ROW: 4 fields (25% each) */}
        <Grid container spacing={1} sx={{ mt: 2 }}>
          {[
            { name: 'voucher_number', label: 'Voucher Number', type: 'text', disabled: true },
            { name: 'date', label: 'Date', type: 'date' },
          ].map((field, idx) => (
            <Grid key={idx} item sx={{ flex: `0 0 calc((100% - ${firstRowGapPx}px) / 4)`, maxWidth: `calc((100% - ${firstRowGapPx}px) / 4)` }}>
              <TextField
                {...control.register(field.name)}
                label={field.label}
                type={field.type}
                fullWidth
                disabled={isViewMode || field.disabled}
                InputLabelProps={field.type === 'date' ? { shrink: true } : {}}
                sx={{ ...financialVoucherStyles.field, ...voucherStyles.centerField }}
              />
            </Grid>
          ))}

          <Grid item sx={{ flex: `0 0 calc((100% - ${firstRowGapPx}px) / 4)`, maxWidth: `calc((100% - ${firstRowGapPx}px) / 4)` }}>
            <FormControl fullWidth disabled={isViewMode} sx={{
              ...financialVoucherStyles.field,
              ...voucherStyles.centerField,
              '& .MuiInputBase-root': { height: 27 },
              '& .MuiSelect-select': { padding: '4px 12px', fontSize: 14, textAlign: 'center' },
              '& .MuiInputLabel-root': { fontSize: 12 }
            }}>
              <InputLabel shrink>Payment Mode</InputLabel>
              <Select
                {...control.register('payment_method')}
                value={watch('payment_method') || ''}
                onChange={(e) => setValue('payment_method', e.target.value)}
              >
                <MenuItem value="" disabled>Select Payment Mode</MenuItem>
                {paymentMethods.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>

          <Grid item sx={{ flex: `0 0 calc((100% - ${firstRowGapPx}px) / 4)`, maxWidth: `calc((100% - ${firstRowGapPx}px) / 4)` }}>
            <TextField
              {...control.register('total_amount', { required: 'Amount is required', min: { value: 0.01, message: 'Amount must be > 0' }, setValueAs: parseRateField })}
              label="Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.total_amount}
              helperText={errors.total_amount?.message as string}
              sx={{ ...financialVoucherStyles.field, ...voucherStyles.centerField }}
            />
          </Grid>
        </Grid>

        {/* SECOND ROW: Party Name (50%), Vendor Balance (11%), Reference (26%), Voucher Balance (11%) */}
        <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: 1, mt: 2 }}>
          <Box sx={{ flexBasis: '50%', minWidth: '50%' }}>
            <SearchableDropdown
              label="Party Name"
              options={allParties}
              value={selectedEntity?.id || null}
              onChange={(val) => {
                const party = allParties.find(p => p.id === val);
                if (party) setValue('entity', party);
              }}
              getOptionLabel={(option) => option.label}
              getOptionValue={(option) => option.id}
              placeholder="Select or search party..."
              noOptionsText="No parties found"
              disabled={isViewMode}
              fullWidth
              required
              error={!!errors.entity}
              helperText={errors.entity?.message as string}
            />
          </Box>

          <Box sx={{ flexBasis: '11%', minWidth: '11%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {entityBalance !== null && (
              <Typography
                sx={{ cursor: 'pointer', color: entityBalance < 0 ? 'red' : 'green' }}
                onClick={() => setValue('total_amount', Math.abs(entityBalance))}
              >
                {entityBalance > 0 ? '+' : ''}{entityBalance}
              </Typography>
            )}
          </Box>

          <Box sx={{ flexBasis: '26%', minWidth: '26%' }}>
            <Autocomplete
              size="small"
              freeSolo
              options={referenceOptions}
              value={watch('reference') || ''}
              onChange={(_, val) => setValue('reference', val || '')}
              disabled={isViewMode}
              fullWidth
              renderInput={(params) => (
                <TextField {...params} label="Reference" fullWidth />
              )}
            />
          </Box>

          <Box sx={{ flexBasis: '11%', minWidth: '11%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {voucherBalance !== null && (
              <Typography
                sx={{ cursor: 'pointer', color: voucherBalance < 0 ? 'red' : 'green' }}
                onClick={() => setValue('total_amount', Math.abs(voucherBalance))}
              >
                {voucherBalance > 0 ? '+' : ''}{voucherBalance}
              </Typography>
            )}
          </Box>
        </Box>

        {/* THIRD ROW: Amount in Words (100% width) */}
        <Grid container spacing={1} sx={{ mt: 2 }}>
          <Grid item xs={12} sx={{ width: '100%' }}>
            <TextField
              fullWidth
              label="Amount in Words"
              value={totalAmountValue > 0 ? getAmountInWords(totalAmountValue) : ''}
              disabled
              size="small"
              sx={{ width: '100%' }}
            />
          </Grid>
        </Grid>

        {/* FOURTH ROW: Notes (100% width) */}
        <Grid container spacing={1} sx={{ mt: 2 }}>
          <Grid item xs={12} sx={{ width: '100%' }}>
            <TextField
              {...control.register('notes')}
              label="Notes"
              multiline
              rows={1}
              fullWidth
              disabled={isViewMode}
              sx={{
                ...financialVoucherStyles.notesField,
                width: '100%',
                '& .MuiInputBase-root': { height: '36px', padding: '0 8px' }
              }}
            />
          </Grid>
        </Grid>

        {/* ACTION BUTTONS */}
        <Grid container spacing={1} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Box display="flex" gap={2}>
              {mode !== 'view' && (
                <Button type="submit" variant="contained" color="success" size="small">Save</Button>
              )}
              <Button variant="outlined" onClick={handleCreate} size="small">Clear</Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <>
      <VoucherLayout
        voucherType="Payment Vouchers"
        voucherTitle="Payment Voucher"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Payment Vouchers"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEdit}
            onView={handleView}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            customerList={customerList}
            vendorList={vendorList}
          />
        }
      />
      <VoucherContextMenu
        voucherType="Payment Voucher"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onEdit={(id) => { handleEdit(id); handleContextMenuClose(); }}
        onView={(id) => { handleView(id); handleContextMenuClose(); }}
        onDelete={(id) => { handleDelete(id); handleContextMenuClose(); }}
      />
    </>
  );
};

export default PaymentVoucher;