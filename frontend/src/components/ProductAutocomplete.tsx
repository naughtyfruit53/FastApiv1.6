// src/components/ProductAutocomplete.tsx
import React, { useState, useCallback } from 'react';
import {
  Autocomplete,
  TextField,
  CircularProgress,
  Box,
  Typography,
  Chip
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { getProducts, createProduct } from '../services/masterService';
import AddProductModal from './AddProductModal';

interface Product {
  id: number;
  product_name: string; // Updated to match API response format
  hsn_code?: string;
  part_number?: string;
  unit: string;
  unit_price: number;
  gst_rate?: number;
  is_gst_inclusive?: boolean;
  reorder_level?: number;
  description?: string;
  is_manufactured?: boolean;
}

interface ProductAutocompleteProps {
  value: Product | null;
  onChange: (product: Product | null) => void;
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  label?: string;
  placeholder?: string;
  size?: 'small' | 'medium';
}

const ProductAutocomplete: React.FC<ProductAutocompleteProps> = ({
  value,
  onChange,
  error = false,
  helperText = '',
  disabled = false,
  label = 'Product',
  placeholder = 'Search or add product...',
  size = 'medium'
}) => {
  const [inputValue, setInputValue] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch all products
  const { data: allProducts = [], isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
    enabled: true,
    staleTime: Infinity, // Cache indefinitely since it's all data
  });

  // Create product mutation
  const createProductMutation = useMutation({
    mutationFn: createProduct,
    onSuccess: (newProduct) => {
      // Invalidate queries
      queryClient.invalidateQueries({queryKey: ['products']});
      
      // Auto-select the newly created product
      onChange(newProduct);
      setAddModalOpen(false);
    },
    onError: (error: any) => {
      console.error('Failed to create product:', error);
    }
  });

  // Filtered options based on input
  const filteredOptions = React.useMemo(() => {
    const lowerInput = inputValue.toLowerCase();
    return allProducts.filter((product: any) => 
      product.product_name.toLowerCase().includes(lowerInput) ||
      (product.hsn_code || '').toLowerCase().includes(lowerInput) ||
      (product.part_number || '').toLowerCase().includes(lowerInput)
    );
  }, [allProducts, inputValue]);

  // Create options array with "Add Product" option
  const options = React.useMemo(() => {
    const addOption = {
      id: -1,
      product_name: '➕ Add Product',
      isAddOption: true,
    };
    
    return [addOption, ...filteredOptions];
  }, [filteredOptions]);

  const handleSelectionChange = (_: any, newValue: any) => {
    if (newValue?.isAddOption) {
      setAddModalOpen(true);
      return;
    }
    
    onChange(newValue);
  };

  const handleAddProduct = async (productData: any) => {
    await createProductMutation.mutateAsync(productData);
  };

  return (
    <>
      <Autocomplete
        value={value}
        onChange={handleSelectionChange}
        inputValue={inputValue}
        onInputChange={(_, newInputValue) => setInputValue(newInputValue)}
        options={options}
        getOptionLabel={(option) => {
          if (option.isAddOption) return option.product_name;
          return option.product_name;
        }}
        isOptionEqualToValue={(option, value) => option.id === value?.id}
        loading={isLoading}
        disabled={disabled}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            placeholder={placeholder}
            error={error}
            helperText={helperText}
            size={size}
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={(props, option) => {
          if (option.isAddOption) {
            return (
              <Box component="li" {...props} sx={{ 
                color: 'primary.main', 
                fontWeight: 'bold',
                borderBottom: '1px solid #eee'
              }}>
                <AddIcon sx={{ mr: 1 }} />
                {option.product_name}
              </Box>
            );
          }

          return (
            <Box component="li" {...props}>
              <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                {option.product_name}
              </Typography>
            </Box>
          );
        }}
        noOptionsText={
          inputValue.length < 1 
            ? "Type to search or select from list..." 
            : "No products found"
        }
      />

      <AddProductModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onAdd={handleAddProduct}
        loading={createProductMutation.isPending}
        initialName={inputValue}
      />
    </>
  );
};

export default ProductAutocomplete;