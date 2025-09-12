// frontend/src/styles/voucherFormStyles.ts
// Common styles for voucher forms, using MUI sx objects for easy management.
const voucherFormStyles = {
  field: {
    '& .MuiInputBase-root': { height: 40 },
    '& .MuiInputLabel-root': { fontSize: 14, top: -4 },
    '& .MuiInputBase-input': { fontSize: 14, padding: '8px 12px' },
  },
  notesField: {
    '& .MuiInputBase-root': { minHeight: 60 },
    '& .MuiInputLabel-root': { fontSize: 14 },
    '& .MuiInputBase-input': { fontSize: 14 },
  },
  itemsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 32,
    mb: 1,
  },
};

export default voucherFormStyles;