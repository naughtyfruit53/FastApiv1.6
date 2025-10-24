// frontend/src/components/AddVendorModal.tsx
import React, { useEffect, useState, useRef, useCallback, useMemo } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Grid,
  Alert,
  InputAdornment,
  Box,
  Paper,
  Chip,
  Tooltip,
  LinearProgress,
  IconButton,
} from "@mui/material";
import {
  CloudUpload,
  Description,
  Check,
  Search,
} from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { usePincodeLookup } from "../hooks/usePincodeLookup";
import api from "../lib/api";
import { debounce } from "lodash";
import isEqual from "lodash/isEqual";
import { toast } from "react-toastify"; // Added for toast notifications

interface AddVendorModalProps {
  open: boolean;
  onClose: () => void;
  onSave?: (data: any) => Promise<any>;
  loading?: boolean;
  initialData?: any;
  context?: "voucher" | "vendor";
  organization_id?: number;
}

interface VendorFormData {
  name: string;
  contact_number: string;
  email: string;
  address1: string;
  address2: string;
  city: string;
  state: string;
  pin_code: string;
  gst_number: string;
  pan_number: string;
  state_code: string;
  organization_id?: number;
}

const AddVendorModal: React.FC<AddVendorModalProps> = ({
  open,
  onClose,
  onSave,
  loading = false,
  initialData = {},
  context = "vendor",
  organization_id,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [gstFile, setGstFile] = useState<File | null>(null);
  const [gstUploadLoading, setGstUploadLoading] = useState(false);
  const [gstExtractedData, setGstExtractedData] = useState<any>(null);
  const [gstUploadError, setGstUploadError] = useState<string | null>(null);
  const [gstSearchLoading, setGstSearchLoading] = useState(false);
  const [localGstNumber, setLocalGstNumber] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
  } = useForm<VendorFormData>({
    defaultValues: {
      name: "",
      contact_number: "",
      email: "",
      address1: "",
      address2: "",
      city: "",
      state: "",
      pin_code: "",
      gst_number: "",
      pan_number: "",
      state_code: "",
      organization_id: organization_id,
    },
  });
  const {
    lookupPincode,
    pincodeData,
    loading: pincodeLoading,
    error: pincodeError,
    clearData,
  } = usePincodeLookup();
  const watchedPincode = watch("pin_code");
  const watchedGstNumber = watch("gst_number");
  const isMounted = useRef(true);
  const hasSetPincode = useRef(false);
  const previousInitialData = useRef<any>(null);

  const memoizedInitialData = useMemo(() => initialData, [initialData]);

  useEffect(() => {
    if (open && !isEqual(previousInitialData.current, memoizedInitialData)) {
      console.log("Resetting form with initialData:", memoizedInitialData);
      const initialGstNumber = memoizedInitialData.gst_number || "";
      reset({
        name: memoizedInitialData.name || "",
        contact_number: memoizedInitialData.contact_number || "",
        email: memoizedInitialData.email || "",
        address1: memoizedInitialData.address1 || "",
        address2: memoizedInitialData.address2 || "",
        city: memoizedInitialData.city || "",
        state: memoizedInitialData.state || "",
        pin_code: memoizedInitialData.pin_code || "",
        gst_number: initialGstNumber,
        pan_number: memoizedInitialData.pan_number || "",
        state_code: memoizedInitialData.state_code || "",
        organization_id: organization_id || memoizedInitialData.organization_id,
      });
      setLocalGstNumber(initialGstNumber.toUpperCase());
      setGstFile(null);
      setGstExtractedData(null);
      setGstUploadError(null);
      setGstSearchLoading(false);
      setFormError(null);
      clearData();
      hasSetPincode.current = false;
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      previousInitialData.current = memoizedInitialData;
    }
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, [open, memoizedInitialData, reset, clearData, organization_id]);

  const debouncedSetGstNumber = useCallback(
    debounce((value: string) => {
      if (isMounted.current) {
        setValue("gst_number", value.toUpperCase(), { shouldValidate: true });
      }
    }, 300),
    [setValue],
  );

  useEffect(() => {
    if (pincodeData && isMounted.current && !hasSetPincode.current) {
      hasSetPincode.current = true;
      const currentValues = watch();
      const updates: Partial<VendorFormData> = {};
      if (currentValues.city !== pincodeData.city) {
        updates.city = pincodeData.city;
      }
      if (currentValues.state !== pincodeData.state) {
        updates.state = pincodeData.state;
      }
      if (currentValues.state_code !== pincodeData.state_code) {
        updates.state_code = pincodeData.state_code;
      }
      if (Object.keys(updates).length > 0) {
        console.log("Updating form with pincode data:", updates);
        reset({ ...currentValues, ...updates, gst_number: watchedGstNumber });
      }
    }
  }, [pincodeData, reset, watch, watchedGstNumber]);

  const handleClearData = useCallback(() => {
    clearData();
    hasSetPincode.current = false;
  }, [clearData]);

  useEffect(() => {
    if (!isMounted.current) return;

    if (watchedPincode && /^\d{6}$/.test(watchedPincode)) {
      const timeoutId = setTimeout(() => {
        lookupPincode(watchedPincode);
      }, 500);
      return () => clearTimeout(timeoutId);
    } else {
      handleClearData();
    }
  }, [watchedPincode, lookupPincode, handleClearData]);

  const handleGstFileUpload = useCallback(
    async (file: File) => {
      setGstUploadLoading(true);
      setGstUploadError(null);
      try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await api.post(
          "/pdf-extraction/extract/vendor",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          },
        );
        console.log("GST file upload response:", response.data);
        if (response.data.success && isMounted.current) {
          const extractedData = response.data.extracted_data;
          const currentValues = watch();
          const updates: Partial<VendorFormData> = {};
          Object.entries(extractedData).forEach(([key, value]) => {
            if (value && currentValues[key as keyof VendorFormData] !== value) {
              updates[key as keyof VendorFormData] = value as string;
            }
          });
          if (Object.keys(updates).length > 0) {
            console.log("Updating form with GST extracted data:", updates);
            reset({ ...currentValues, ...updates, gst_number: watchedGstNumber });
          }
          setGstExtractedData(extractedData);
          setLocalGstNumber((extractedData.gst_number || watchedGstNumber).toUpperCase());
          setGstFile(file);
        } else {
          const errorMessage =
            (response.data as any)?.detail || "Extraction failed";
          throw new Error(errorMessage);
        }
      } catch (error: any) {
        console.error("Error processing GST certificate:", {
          message: error.message,
          status: error.response?.status,
          details: error.response?.data?.detail,
        });
        if (isMounted.current) {
          setGstUploadError(
            error.response?.data?.detail ||
              "Failed to process GST certificate. Please try again.",
          );
          toast.error(
            error.response?.data?.detail ||
              "Failed to process GST certificate. Please try again.",
          );
        }
      } finally {
        if (isMounted.current) {
          setGstUploadLoading(false);
        }
      }
    },
    [reset, watch, watchedGstNumber],
  );

  const handleFileInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file) {
        if (file.type !== "application/pdf") {
          setGstUploadError("Please upload a PDF file");
          toast.error("Please upload a PDF file");
          return;
        }
        if (file.size > 10 * 1024 * 1024) {
          setGstUploadError("File size should be less than 10MB");
          toast.error("File size should be less than 10MB");
          return;
        }
        handleGstFileUpload(file);
      }
    },
    [handleGstFileUpload],
  );

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const removeGstFile = () => {
    setGstFile(null);
    setGstExtractedData(null);
    setGstUploadError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleGstSearch = useCallback(async () => {
    if (
      !watchedGstNumber ||
      !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(
        watchedGstNumber,
      )
    ) {
      setGstUploadError("Please enter a valid GSTIN");
      toast.error("Please enter a valid GSTIN");
      return;
    }
    setGstSearchLoading(true);
    setGstUploadError(null);
    try {
      const response = await api.get(`/gst/search/${watchedGstNumber}`);
      console.log("GST search response:", response.data);
      const data = response.data;
      const currentValues = watch();
      const updates: Partial<VendorFormData> = {};
      Object.entries(data).forEach(([key, value]) => {
        if (value && currentValues[key as keyof VendorFormData] !== value) {
          updates[key as keyof VendorFormData] = value as string;
        }
      });
      if (Object.keys(updates).length > 0 && isMounted.current) {
        console.log("Updating form with GST search data:", updates);
        reset({ ...currentValues, ...updates, gst_number: watchedGstNumber });
      }
    } catch (error: any) {
      console.error("GST search error:", {
        message: error.message,
        status: error.response?.status,
        details: error.response?.data?.detail,
      });
      let errorMessage = "Failed to fetch GST details. Please check GSTIN.";
      if (error.response?.status === 400) {
        errorMessage =
          error.response.data.detail || "Invalid GSTIN - please verify the number.";
      } else if (error.response?.status === 500) {
        errorMessage =
          error.response.data.detail || "Server error during GST search - try again later.";
      }
      if (isMounted.current) {
        setGstUploadError(errorMessage);
        toast.error(errorMessage);
      }
    } finally {
      if (isMounted.current) {
        setGstSearchLoading(false);
      }
    }
  }, [watchedGstNumber, reset, watch]);

  const onSubmit = async (vendorData: VendorFormData) => {
    setFormError(null);
    try {
      const requiredFields = [
        "name",
        "contact_number",
        "address1",
        "city",
        "state",
        "pin_code",
      ];
      for (const field of requiredFields) {
        if (!vendorData[field] || String(vendorData[field]).trim() === "") {
          setFormError(`${field.replace("_", " ")} is required`);
          toast.error(`${field.replace("_", " ")} is required`);
          return;
        }
      }
      const cleanData = {
        name: vendorData.name,
        contact_number: vendorData.contact_number,
        email: vendorData.email || undefined,
        address1: vendorData.address1,
        address2: vendorData.address2 || undefined,
        city: vendorData.city,
        state: vendorData.state,
        pin_code: vendorData.pin_code,
        gst_number: vendorData.gst_number || undefined,
        pan_number: vendorData.pan_number || undefined,
        state_code: vendorData.state_code || undefined, // Allow undefined state_code
        organization_id: organization_id || vendorData.organization_id,
      };
      console.log("Submitting vendor data:", cleanData);
      let createdVendor = null;
      if (typeof onSave === "function") {
        createdVendor = await onSave(cleanData);
        console.log("Vendor saved successfully:", createdVendor);
      } else {
        console.error("onSave is not provided or not a function");
        setFormError("Internal error: Save function not available");
        toast.error("Internal error: Save function not available");
        return;
      }
      reset();
      setLocalGstNumber("");
      onClose();
      return createdVendor;
    } catch (error: any) {
      console.error("Error saving vendor:", {
        message: error.message,
        status: error.response?.status,
        details: error.response?.data?.detail,
      });
      let errorMessage = "Failed to save vendor. Please try again.";
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail
            .map(
              (err: any) =>
                `${err.loc ? err.loc.join(" -> ") + ": " : ""}${err.msg || err.type}`,
            )
            .join(", ");
        } else if (typeof detail === "string") {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      setFormError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const handleClose = () => {
    reset();
    setLocalGstNumber("");
    setFormError(null);
    clearData();
    removeGstFile();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">
          {initialData.id ? "Edit Vendor" : "Add New Vendor"}
        </Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {formError && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
              onClose={() => setFormError(null)}
            >
              {formError}
            </Alert>
          )}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Vendor Name *"
                {...register("name", { required: "Vendor name is required" })}
                error={!!errors.name}
                helperText={errors.name?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("name") || !!gstExtractedData?.name,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Contact Number *"
                {...register("contact_number", {
                  required: "Contact number is required",
                })}
                error={!!errors.contact_number}
                helperText={errors.contact_number?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("contact_number") || !!gstExtractedData?.phone,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                {...register("email", {
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address",
                  },
                })}
                error={!!errors.email}
                helperText={errors.email?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("email") || !!gstExtractedData?.email,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="GST Number"
                value={localGstNumber}
                onChange={(e) => {
                  const upperValue = e.target.value.toUpperCase();
                  setLocalGstNumber(upperValue);
                  debouncedSetGstNumber(upperValue);
                }}
                margin="normal"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {gstSearchLoading ? (
                        <CircularProgress size={16} />
                      ) : (
                        <IconButton
                          onClick={handleGstSearch}
                          disabled={gstSearchLoading || !watchedGstNumber}
                          aria-label="Search GST"
                          color="primary"
                        >
                          <Search />
                        </IconButton>
                      )}
                    </InputAdornment>
                  ),
                }}
                InputLabelProps={{
                  shrink: !!localGstNumber || !!gstExtractedData?.gst_number,
                }}
              />
            </Grid>
            <Grid size={12}>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: "grey.50",
                  border: "1px dashed",
                  borderColor: "grey.300",
                }}
              >
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="space-between"
                  mb={1}
                >
                  <Typography variant="subtitle2" color="textSecondary">
                    GST Certificate Upload (Optional)
                  </Typography>
                  <Tooltip title="Upload GST certificate PDF to auto-fill vendor details">
                    <Typography variant="caption" color="textSecondary">
                      PDF Auto-Extract
                    </Typography>
                  </Tooltip>
                </Box>
                {!gstFile && !gstUploadLoading && (
                  <Box
                    sx={{
                      border: "2px dashed",
                      borderColor: "grey.300",
                      borderRadius: 1,
                      p: 3,
                      textAlign: "center",
                      cursor: "pointer",
                      "&:hover": {
                        borderColor: "primary.main",
                        bgcolor: "action.hover",
                      },
                    }}
                    onClick={triggerFileUpload}
                  >
                    <CloudUpload
                      sx={{ fontSize: 48, color: "grey.400", mb: 1 }}
                    />
                    <Typography
                      variant="body2"
                      color="textSecondary"
                      gutterBottom
                    >
                      Click to upload GST certificate (PDF only)
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Maximum file size: 10MB
                    </Typography>
                  </Box>
                )}
                {gstUploadLoading && (
                  <Box sx={{ p: 3, textAlign: "center" }}>
                    <CircularProgress size={40} sx={{ mb: 2 }} />
                    <Typography
                      variant="body2"
                      color="textSecondary"
                      gutterBottom
                    >
                      Processing GST certificate...
                    </Typography>
                    <LinearProgress sx={{ mt: 1 }} />
                  </Box>
                )}
                {gstFile && !gstUploadLoading && (
                  <Box sx={{ p: 2, bgcolor: "success.light", borderRadius: 1 }}>
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="space-between"
                    >
                      <Box display="flex" alignItems="center" gap={1}>
                        <Description color="primary" />
                        <Typography variant="body2" fontWeight="medium">
                          {gstFile.name}
                        </Typography>
                        <Chip
                          icon={<Check />}
                          label="Processed"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Box>
                      <Button
                        size="small"
                        onClick={removeGstFile}
                        color="error"
                        variant="outlined"
                      >
                        Remove
                      </Button>
                    </Box>
                    {gstExtractedData && (
                      <Alert severity="success" sx={{ mt: 1 }}>
                        <Typography variant="caption">
                          Auto-populated: {Object.keys(gstExtractedData).join(", ")}
                        </Typography>
                      </Alert>
                    )}
                  </Box>
                )}
                {gstUploadError && (
                  <Alert
                    severity="error"
                    sx={{ mt: 1 }}
                    onClose={() => setGstUploadError(null)}
                  >
                    {gstUploadError}
                  </Alert>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  style={{ display: "none" }}
                  onChange={handleFileInputChange}
                />
              </Paper>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="PAN Number"
                {...register("pan_number")}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("pan_number") || !!gstExtractedData?.pan_number,
                }}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 1 *"
                {...register("address1", {
                  required: "Address line 1 is required",
                })}
                error={!!errors.address1}
                helperText={errors.address1?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("address1") || !!gstExtractedData?.address1,
                }}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 2"
                {...register("address2")}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch("address2") || !!gstExtractedData?.address2,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="PIN Code *"
                {...register("pin_code", {
                  required: "PIN code is required",
                  pattern: {
                    value: /^\d{6}$/,
                    message: "Please enter a valid 6-digit PIN code",
                  },
                })}
                error={!!errors.pin_code}
                helperText={
                  errors.pin_code?.message || (pincodeError && pincodeError)
                }
                margin="normal"
                InputProps={{
                  endAdornment: pincodeLoading ? (
                    <InputAdornment position="end">
                      <CircularProgress size={16} />
                    </InputAdornment>
                  ) : null,
                }}
                InputLabelProps={{
                  shrink: !!watch("pin_code") || !!gstExtractedData?.pin_code,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="City *"
                {...register("city", { required: "City is required" })}
                error={!!errors.city}
                helperText={errors.city?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink:
                    !!watch("city") ||
                    !!pincodeData ||
                    !!gstExtractedData?.city,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="State *"
                {...register("state", { required: "State is required" })}
                error={!!errors.state}
                helperText={errors.state?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink:
                    !!watch("state") ||
                    !!pincodeData ||
                    !!gstExtractedData?.state,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="State Code *"
                {...register("state_code", {
                  required: "State code is required",
                })}
                error={!!errors.state_code}
                helperText={errors.state_code?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink:
                    !!watch("state_code") ||
                    !!pincodeData ||
                    !!gstExtractedData?.state_code,
                }}
              />
            </Grid>
            {pincodeError && (
              <Grid size={12}>
                <Alert severity="warning" sx={{ mt: 1 }}>
                  {pincodeError}
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading
              ? "Saving..."
              : initialData.id
              ? "Update Vendor"
              : "Add Vendor"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddVendorModal;