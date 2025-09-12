// src/components/VoucherFormTotals.tsx
// Reusable component for voucher totals section.
import React from 'react';
import { Box, Grid, Typography, TextField, InputAdornment, IconButton } from '@mui/material';
import { Clear } from '@mui/icons-material';

interface VoucherFormTotalsProps {
  totalSubtotal: number;
  totalCgst: number;
  totalSgst: number;
  totalIgst: number;
  totalAmount: number;
  totalRoundOff: number;
  isIntrastate: boolean;
  totalDiscountEnabled: boolean;
  totalDiscountType: string;
  mode: string;
  watch: any;
  control: any;
  setValue: any;
  handleToggleTotalDiscount: (checked: boolean) => void;
  getAmountInWords: (amount: number) => string;
}

const VoucherFormTotals: React.FC<VoucherFormTotalsProps> = ({
  totalSubtotal,
  totalCgst,
  totalSgst,
  totalIgst,
  totalAmount,
  totalRoundOff,
  isIntrastate,
  totalDiscountEnabled,
  totalDiscountType,
  mode,
  watch,
  control,
  setValue,
  handleToggleTotalDiscount,
  getAmountInWords,
}) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
      <Box sx={{ minWidth: 300 }}>
        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>Subtotal:</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>
              ₹{totalSubtotal.toLocaleString()}
            </Typography>
          </Grid>

          {totalDiscountEnabled && (
            <>
              <Grid item xs={6}>
                <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>
                  Disc {totalDiscountType === 'percentage' ? '%' : '₹'}:
                </Typography>
              </Grid>
              <Grid item xs={6} sx={{ textAlign: 'right' }}>
                {mode === "view" ? (
                  <Typography variant="body2" sx={{ fontSize: 14, fontWeight: 'bold' }}>
                    {totalDiscountType === 'percentage' ? `${watch("total_discount") || 0}%` : `₹${(watch("total_discount") || 0).toLocaleString()}`}
                  </Typography>
                ) : (
                  <TextField
                    type="number"
                    {...control.register("total_discount", { valueAsNumber: true })}
                    size="small"
                    sx={{ width: 120 }}
                    InputProps={{
                      inputProps: { min: 0, step: totalDiscountType === 'percentage' ? 0.01 : 0.01 },
                      endAdornment: (
                        <InputAdornment position="end" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Typography sx={{ mr: 0.5 }}>{totalDiscountType === 'percentage' ? '%' : '₹'}</Typography>
                          <IconButton size="small" onClick={() => { setValue("total_discount", 0); handleToggleTotalDiscount(false); }} aria-label="clear discount">
                            <Clear fontSize="small" />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              </Grid>
            </>
          )}

          {isIntrastate ? (
            <>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>CGST:</Typography></Grid>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{totalCgst.toLocaleString()}</Typography></Grid>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>SGST:</Typography></Grid>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{totalSgst.toLocaleString()}</Typography></Grid>
            </>
          ) : (
            <>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>IGST:</Typography></Grid>
              <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{totalIgst.toLocaleString()}</Typography></Grid>
            </>
          )}
          <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>Round Off:</Typography></Grid>
          <Grid item xs={6}><Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{totalRoundOff > 0 ? '+' : ''}{totalRoundOff.toLocaleString()}</Typography></Grid>
          <Grid item xs={6}><Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>Total:</Typography></Grid>
          <Grid item xs={6}><Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>₹{Math.round(totalAmount).toLocaleString()}</Typography></Grid>
        </Grid>
        <TextField
          fullWidth
          label="Amount in Words"
          value={getAmountInWords(totalAmount)}
          disabled
          InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
          inputProps={{ style: { fontSize: 14 } }}
          size="small"
          sx={{ mt: 2 }}
        />
      </Box>
    </Box>
  );
};

export default VoucherFormTotals;