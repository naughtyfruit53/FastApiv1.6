// frontend/src/styles/voucherFormStyles.ts
// Common styles for voucher forms, using MUI sx objects for easy management.
const voucherFormStyles = {
  field: {
    '& .MuiInputBase-root': { height: 27 },
    '& .MuiInputLabel-root': { fontSize: 12 },
    '& .MuiInputBase-input': { fontSize: 14, padding: '4px 12px' },
  },
  notesField: {
    '& .MuiInputBase-root': { height: 27 },
    '& .MuiInputLabel-root': { fontSize: 12 },
    '& .MuiInputBase-input': { fontSize: 14 },
  },
  itemsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 27,
    mb: 1,
  },
};

export default voucherFormStyles;