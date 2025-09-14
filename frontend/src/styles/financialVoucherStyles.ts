// frontend/src/styles/financialVoucherStyles.ts
// Customized styles for financial voucher forms (e.g., payment, receipt vouchers).
// Based on voucherFormStyles but with adjustments for better full-width utilization:
// - Increased field heights slightly for better visibility and to reduce vertical blank space.
// - Added explicit full-width and padding tweaks to ensure fields stretch horizontally.
// - Smaller fonts for labels/inputs to fit more compactly without looking cramped.
// - Added formContainer to control overall form padding/margins, reducing right-side blank space.
// Use this in financial voucher pages for consistency.

const financialVoucherStyles = {
  formContainer: {
    padding: '4px', // Reduced padding to minimize blank spaces on sides
    width: '100%', // Ensure full container width
    maxWidth: '100%', // Prevent any max-width restrictions
    boxSizing: 'border-box', // Include padding in width calculation
  },
  field: {
    width: '100%', // Ensure full width within grid items
    '& .MuiInputBase-root': { height: 35 }, // Slightly taller than standard (27) to fill vertical space better
    '& .MuiInputLabel-root': { fontSize: 11 }, // Smaller label for compactness
    '& .MuiInputBase-input': { fontSize: 13, padding: '6px 10px' }, // Adjusted padding for better horizontal fill
  },
  notesField: {
    width: '100%',
    '& .MuiInputBase-root': { minHeight: 60 }, // Taller for notes to reduce blank space below
    '& .MuiInputLabel-root': { fontSize: 11 },
    '& .MuiInputBase-input': { fontSize: 13, padding: '6px 10px' },
  },
  itemsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 35, // Match field height
    mb: 0.5, // Reduced margin for tighter layout
  },
};

export default financialVoucherStyles;