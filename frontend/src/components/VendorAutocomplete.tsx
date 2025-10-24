// frontend/src/components/VendorAutocomplete.tsx
import React, { useState, useCallback, useMemo } from "react";
import { Autocomplete, TextField, CircularProgress, Box } from "@mui/material";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as masterDataService from "../services/masterService";
import AddVendorModal from "./AddVendorModal";
import { useCompany } from "../context/CompanyContext";
import voucherFormStyles from "../styles/voucherFormStyles";

interface VendorAutocompleteProps {
  value: any;
  onChange: (value: any) => void;
  label?: string;
  vendorList?: any[];
}

const VendorAutocomplete: React.FC<VendorAutocompleteProps> = ({
  value,
  onChange,
  label = "Select Vendor",
  vendorList = [],
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [openModal, setOpenModal] = useState(false);
  const { company } = useCompany();
  const queryClient = useQueryClient();

  const { data: vendors, isLoading, error } = useQuery({
    queryKey: ["vendors", searchTerm, company?.organization_id],
    queryFn: () =>
      masterDataService.searchVendors({
        queryKey: ["vendors", searchTerm, 10, company?.organization_id],
      }),
    enabled: !!company?.organization_id,
    onError: (err: any) => {
      console.error("Vendor fetch error:", {
        message: err.message,
        status: err.response?.status,
        details: err.response?.data?.detail,
      });
    },
  });

  const options = useMemo(() => {
    const sourceVendors = vendors && vendors.length > 0 ? vendors : vendorList;
    console.log("Source vendors:", sourceVendors);
    const vendorOptions = (sourceVendors || [])
      .map((vendor: any) => ({
        label: vendor.name,
        id: vendor.id,
        value: vendor,
      }))
      .sort((a, b) => a.label.localeCompare(b.label)); // Sort alphabetically A-Z
    
    // Always show "Add New Vendor" at the top
    return [
      { label: "Add New Vendor", id: "add-vendor", value: null },
      ...vendorOptions,
    ];
  }, [vendors, vendorList]);

  const handleVendorSave = useCallback(
    async (vendorData: any) => {
      try {
        const newVendor = await masterDataService.createVendor({
          ...vendorData,
          organization_id: company?.organization_id,
        });
        console.log("New vendor created:", newVendor);
        queryClient.invalidateQueries(["vendors"]); // Refresh vendor list
        onChange(newVendor); // Set new vendor as selected
        setOpenModal(false);
        return newVendor;
      } catch (error) {
        console.error("Failed to save vendor:", error);
        throw error;
      }
    },
    [onChange, company, queryClient],
  );

  return (
    <Box>
      <Autocomplete
        options={options}
        getOptionLabel={(option) => option.label || ""}
        value={value ? options.find((opt) => opt.id === value.id) || value : null}
        onChange={(event, newValue) => {
          if (newValue?.id === "add-vendor") {
            setOpenModal(true);
          } else {
            onChange(newValue?.value || null);
          }
        }}
        inputValue={searchTerm}
        onInputChange={(event, newInputValue) => setSearchTerm(newInputValue)}
        loading={isLoading}
        disabled={isLoading && !options.length}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            variant="outlined"
            error={!!error}
            helperText={error ? `Failed to load vendors: ${error.message || "Unknown error"}` : ""}
            sx={{ ...params.sx, ...voucherFormStyles.field }}
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoading ? <CircularProgress size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
      />
      <AddVendorModal
        open={openModal}
        onClose={() => setOpenModal(false)}
        onSave={handleVendorSave}
        context="voucher"
        organization_id={company?.organization_id}
      />
    </Box>
  );
};

export default VendorAutocomplete;