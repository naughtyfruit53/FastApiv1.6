# SearchableDropdown Enhancement Guide

## Overview
The `SearchableDropdown` component has been enhanced with "Add New" functionality to streamline the user experience when creating new entities directly from dropdown selections.

## New Features

### 1. Add New Option as First Item
Display "Add New [Entity]" as the first selectable option in the dropdown.

### 2. No Results Add Option
When search returns no results, show a clickable "Add New" option with the search term.

### 3. Custom Entity Naming
Specify the entity name for better UX (e.g., "Add New Customer", "Add New Product").

## New Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `entityName` | `string` | `'Item'` | Name of the entity for "Add New [Entity]" text |
| `showAddAsFirstOption` | `boolean` | `false` | Show "Add New" as first option in dropdown |

## Usage Examples

### Example 1: Basic Usage with Add New
```tsx
import SearchableDropdown from '@/components/SearchableDropdown';

function VoucherForm() {
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [vendors, setVendors] = useState([...]);
  const [addVendorModalOpen, setAddVendorModalOpen] = useState(false);

  return (
    <>
      <SearchableDropdown
        label="Vendor"
        options={vendors}
        value={selectedVendor}
        onChange={setSelectedVendor}
        onAddNew={() => setAddVendorModalOpen(true)}
        entityName="Vendor"
        showAddAsFirstOption={true}
        getOptionLabel={(option) => option.name}
        getOptionValue={(option) => option.id}
        placeholder="Select or add vendor..."
      />
      
      <AddVendorModal
        open={addVendorModalOpen}
        onClose={() => setAddVendorModalOpen(false)}
        onAdd={async (newVendor) => {
          // Add to list and select
          setVendors([...vendors, newVendor]);
          setSelectedVendor(newVendor.id);
          setAddVendorModalOpen(false);
        }}
      />
    </>
  );
}
```

### Example 2: Customer Selection
```tsx
<SearchableDropdown
  label="Customer"
  options={customers}
  value={selectedCustomer}
  onChange={setSelectedCustomer}
  onAddNew={() => setAddCustomerModalOpen(true)}
  entityName="Customer"
  showAddAsFirstOption={true}
  getOptionLabel={(option) => option.name}
  getOptionValue={(option) => option.id}
  placeholder="Select or add customer..."
  required
  error={!!errors.customer}
  helperText={errors.customer?.message}
/>
```

### Example 3: Product Selection
```tsx
<SearchableDropdown
  label="Product"
  options={products}
  value={selectedProduct}
  onChange={setSelectedProduct}
  onAddNew={() => setAddProductModalOpen(true)}
  entityName="Product"
  showAddAsFirstOption={true}
  getOptionLabel={(option) => `${option.name} (${option.sku})`}
  getOptionValue={(option) => option.id}
  placeholder="Select or add product..."
/>
```

### Example 4: With Async Search
```tsx
const fetchVendors = async (searchTerm: string) => {
  const response = await api.get('/vendors', {
    params: { search: searchTerm }
  });
  return response.data.map(v => ({
    label: v.name,
    value: v.id,
    ...v
  }));
};

<SearchableDropdown
  label="Vendor"
  options={[]} // Initial empty, will be populated by fetchOptions
  value={selectedVendor}
  onChange={setSelectedVendor}
  fetchOptions={fetchVendors}
  onAddNew={() => setAddVendorModalOpen(true)}
  entityName="Vendor"
  showAddAsFirstOption={true}
  placeholder="Search vendors..."
/>
```

## Behavior

### Add New as First Option
When `showAddAsFirstOption={true}`:
- "Add New [Entity]" appears as the first option
- Clicking it triggers the `onAddNew` callback
- Styled with primary color and add icon for visibility

### No Results Add Option
When user searches and no results are found:
- If `onAddNew` is provided and there's a search term
- Shows clickable: "Add New [Entity]: '[search term]'"
- Clicking triggers `onAddNew` callback
- You can use the search term to pre-populate the add modal

### Visual Styling
- Add New options are styled with:
  - Primary color (blue)
  - Bold font weight
  - Add icon (+)
  - Hover effect for better UX

## Migration Guide

### Before (without Add New)
```tsx
<SearchableDropdown
  label="Party Name"
  options={allParties}
  value={selectedEntity?.id}
  onChange={(val) => {
    const party = allParties.find(p => p.id === val);
    if (party) setValue('entity', party);
  }}
  getOptionLabel={(option) => option.label}
  getOptionValue={(option) => option.id}
  placeholder="Select party..."
/>

{/* Separate Add button */}
<Button onClick={() => setAddModalOpen(true)}>
  Add New Party
</Button>
```

### After (with Add New integrated)
```tsx
<SearchableDropdown
  label="Party Name"
  options={allParties}
  value={selectedEntity?.id}
  onChange={(val) => {
    const party = allParties.find(p => p.id === val);
    if (party) setValue('entity', party);
  }}
  onAddNew={() => setAddModalOpen(true)}
  entityName="Party"
  showAddAsFirstOption={true}
  getOptionLabel={(option) => option.label}
  getOptionValue={(option) => option.id}
  placeholder="Select or add party..."
/>

{/* No need for separate button - integrated in dropdown */}
```

## Best Practices

1. **Always provide `entityName`**: Use meaningful entity names for better UX
   ```tsx
   entityName="Customer" // Good
   entityName="Item"     // Generic, less helpful
   ```

2. **Handle modal state properly**: Close modal after successful add
   ```tsx
   onAddNew={() => setAddModalOpen(true)}
   
   onAdd={async (newItem) => {
     await createItem(newItem);
     setAddModalOpen(false); // Don't forget to close
     refreshList(); // Refresh the dropdown list
   }}
   ```

3. **Update list after adding**: Ensure new item appears in dropdown
   ```tsx
   onAdd={async (newVendor) => {
     const created = await api.post('/vendors', newVendor);
     setVendors([...vendors, created]); // Add to list
     setSelectedVendor(created.id);    // Auto-select
     setAddModalOpen(false);
   }}
   ```

4. **Use with existing icon button**: You can keep both options
   ```tsx
   <Box sx={{ display: 'flex', gap: 1 }}>
     <SearchableDropdown
       {...props}
       showAddAsFirstOption={true}
       flex: 1
     />
     <IconButton onClick={() => setAddModalOpen(true)}>
       <AddIcon />
     </IconButton>
   </Box>
   ```

## Recommended Form Updates

The following forms/modals should be updated to use the enhanced dropdown:

### High Priority (User-facing forms)
- ✅ Payment Voucher - Party selection
- ✅ Receipt Voucher - Party selection
- ✅ Sales Voucher - Customer selection
- ✅ Purchase Voucher - Vendor selection
- ✅ Quotation - Customer selection
- ✅ Sales Order - Customer selection

### Medium Priority
- Product selection in vouchers
- Chart of Accounts selection
- Employee selection
- Cost center selection

### Low Priority
- Admin forms
- Settings forms

## Testing Checklist

When implementing the enhanced dropdown:

- [ ] Add New option appears as first item
- [ ] Clicking Add New opens the correct modal
- [ ] Search with no results shows Add New option
- [ ] Clicking no-results Add New opens modal
- [ ] Modal closes after successful add
- [ ] New item appears in dropdown list
- [ ] New item is auto-selected
- [ ] Visual styling is consistent (primary color, icon)
- [ ] Accessibility: Keyboard navigation works
- [ ] Mobile: Touch targets are adequate

## Troubleshooting

### Add New option not appearing
- Check `showAddAsFirstOption={true}` is set
- Verify `onAddNew` prop is provided
- Check `entityName` is set

### Modal not opening
- Verify `onAddNew` callback is correct
- Check state management for modal open/close

### New item not in list after adding
- Ensure list is refreshed after add
- Check API response includes new item
- Verify state update logic

### Duplicate entries
- Use unique keys in options
- Check for duplicate API calls
- Verify debouncing if using fetchOptions

## API Reference

See [SearchableDropdown.tsx](../frontend/src/components/SearchableDropdown.tsx) for complete API documentation.

## Support

For issues or questions:
- Check existing component tests
- Review similar implementations in the codebase
- Consult the team lead for complex scenarios
