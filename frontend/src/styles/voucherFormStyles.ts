// frontend/src/styles/voucherFormStyles.ts
// Common styles for voucher forms, using MUI sx objects for easy management.
const voucherFormStyles = {
  field: {
    '& .MuiInputLabel-root': { fontSize: 12 },
    '& .MuiInputBase-input': { fontSize: 14, padding: '4px 12px' },
  },
  notesField: {
    '& .MuiInputLabel-root': { fontSize: 12 },
    '& .MuiInputBase-input': { fontSize: 14 },
  },
  itemsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    mb: 1,
  },
};

export default voucherFormStyles;
