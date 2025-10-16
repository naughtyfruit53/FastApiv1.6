// frontend/src/components/ProductAutocomplete.tsx
import React, { useState } from "react";
import {
  Autocomplete,
  TextField,
  CircularProgress,
  Box,
  Typography,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProducts, createProduct } from "../services/masterService";
import AddProductModal from "./AddProductModal";

interface Product {
  id: number;
  product_name: string;
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
  size?: "small" | "medium";
}

const ProductAutocomplete: React.FC<ProductAutocompleteProps> = ({
  value,
  onChange,
  error = false,
  helperText = "",
  disabled = false,
  label = "Product",
  placeholder = "Search or add product...",
  size = "medium",
}) => {
  const [inputValue, setInputValue] = useState("");
  const [addModalOpen, setAddModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: allProducts = [], isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
    enabled: true,
    staleTime: Infinity,
  });

  const createProductMutation = useMutation({
    mutationFn: createProduct,
    onSuccess: (newProduct) => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onChange(newProduct);
      setAddModalOpen(false);
    },
    onError: (err: any) => {
      console.error("[ProductAutocomplete] Failed to create product:", err);
    },
  });

  const filteredOptions = React.useMemo(() => {
    const lowerInput = inputValue.toLowerCase();
    return allProducts.filter(
      (product: any) =>
        (product.product_name || "").toLowerCase().includes(lowerInput) ||
        (product.hsn_code || "").toLowerCase().includes(lowerInput) ||
        (product.part_number || "").toLowerCase().includes(lowerInput),
    );
  }, [allProducts, inputValue]);

  const options = React.useMemo(() => {
    let opts = [...filteredOptions];
    if (value && value.id && !opts.find((opt) => opt.id === value.id)) {
      opts = [{ ...value, product_name: value.product_name || "" }, ...opts];
    }
    const addOption = {
      id: -1,
      product_name: "➕ Add Product",
      isAddOption: true,
    };
    return [addOption, ...opts];
  }, [filteredOptions, value]);

  const handleSelectionChange = (_: any, newValue: any) => {
    if (newValue?.isAddOption) {
      setAddModalOpen(true);
      return;
    }
    onChange(newValue ? { ...newValue, product_name: newValue.product_name || "" } : null);
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
        getOptionLabel={(option) => option.product_name || ""}
        isOptionEqualToValue={(option, selectedValue) =>
          option.id === selectedValue?.id
        }
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
                  {isLoading ? (
                    <CircularProgress color="inherit" size={20} />
                  ) : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={(props, option) => {
          if (option.isAddOption) {
            return (
              <Box
                component="li"
                {...props}
                sx={{
                  color: "primary.main",
                  fontWeight: "bold",
                  borderBottom: "1px solid #eee",
                }}
              >
                <AddIcon sx={{ mr: 1 }} />
                {option.product_name}
              </Box>
            );
          }
          return (
            <Box component="li" {...props}>
              <Typography variant="body1" sx={{ fontWeight: "medium" }}>
                {option.product_name || ""}
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