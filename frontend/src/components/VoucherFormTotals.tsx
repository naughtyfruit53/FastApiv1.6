// src/components/VoucherFormTotals.tsx
// Reusable component for voucher totals section.
import React from 'react';
import { Box, Typography, TextField, InputAdornment, IconButton } from '@mui/material';
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
  totalAdditionalCharges?: number;
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
  totalAdditionalCharges = 0,
}) => {
  const safeNumber = (value: number) => isNaN(value) ? 0 : value;
  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
      <Box sx={{ minWidth: 300 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px' }}>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>Subtotal:</Typography>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>
              ₹{safeNumber(totalSubtotal).toLocaleString()}
            </Typography>
          </Box>

          {totalDiscountEnabled && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
              <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>
                Disc {totalDiscountType === 'percentage' ? '%' : '₹'}:
              </Typography>
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
            </Box>
          )}

          {safeNumber(totalAdditionalCharges) > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
              <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>Additional Charges:</Typography>
              <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{safeNumber(totalAdditionalCharges).toLocaleString()}</Typography>
            </Box>
          )}

          {isIntrastate ? (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
                <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>CGST:</Typography>
                <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{safeNumber(totalCgst).toLocaleString()}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
                <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>SGST:</Typography>
                <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{safeNumber(totalSgst).toLocaleString()}</Typography>
              </Box>
            </>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
              <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>IGST:</Typography>
              <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{safeNumber(totalIgst).toLocaleString()}</Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>Round Off:</Typography>
            <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>₹{safeNumber(totalRoundOff) > 0 ? '+' : ''}{safeNumber(totalRoundOff).toLocaleString()}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '200px', mt: 1 }}>
            <Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>Total:</Typography>
            <Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>₹{safeNumber(Math.round(totalAmount)).toLocaleString()}</Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default VoucherFormTotals;