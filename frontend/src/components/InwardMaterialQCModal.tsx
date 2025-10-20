// frontend/src/components/InwardMaterialQCModal.tsx
import React, { useState, useRef } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Grid,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Divider,
  Chip,
} from "@mui/material";
import {
  CloudUpload,
  Delete,
  CheckCircle,
  Cancel,
  Info,
} from "@mui/icons-material";
import { useForm, Controller } from "react-hook-form";
import { toast } from "react-toastify";

interface QCFormData {
  inspection_date: string;
  inspector_name: string;
  accepted_quantity: number;
  rejected_quantity: number;
  qc_result: "pass" | "fail" | "partial";
  rejection_reason?: string;
  measurements?: string;
  remarks?: string;
}

interface QCFile {
  file: File;
  preview: string;
}

interface InwardMaterialQCModalProps {
  open: boolean;
  onClose: () => void;
  itemData: {
    product_id: number;
    product_name: string;
    ordered_quantity: number;
    received_quantity: number;
    accepted_quantity?: number;
    rejected_quantity?: number;
    unit: string;
    grn_item_id?: number;
  };
  onSave: (qcData: QCFormData, files: File[]) => Promise<void>;
}

const InwardMaterialQCModal: React.FC<InwardMaterialQCModalProps> = ({
  open,
  onClose,
  itemData,
  onSave,
}) => {
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<QCFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<QCFormData>({
    defaultValues: {
      inspection_date: new Date().toISOString().split("T")[0],
      inspector_name: "",
      accepted_quantity: itemData.accepted_quantity || itemData.received_quantity,
      rejected_quantity: itemData.rejected_quantity || 0,
      qc_result: "pass",
      rejection_reason: "",
      measurements: "",
      remarks: "",
    },
  });

  const acceptedQty = watch("accepted_quantity");
  const rejectedQty = watch("rejected_quantity");
  const qcResult = watch("qc_result");

  // Auto-calculate QC result based on quantities
  React.useEffect(() => {
    const accepted = acceptedQty || 0;
    const rejected = rejectedQty || 0;
    const total = accepted + rejected;

    if (total > itemData.received_quantity) {
      // Invalid state
      return;
    }

    if (rejected === 0) {
      setValue("qc_result", "pass");
    } else if (accepted === 0) {
      setValue("qc_result", "fail");
    } else {
      setValue("qc_result", "partial");
    }
  }, [acceptedQty, rejectedQty, itemData.received_quantity, setValue]);

  // Reset form when modal opens
  React.useEffect(() => {
    if (open) {
      reset({
        inspection_date: new Date().toISOString().split("T")[0],
        inspector_name: "",
        accepted_quantity: itemData.accepted_quantity || itemData.received_quantity,
        rejected_quantity: itemData.rejected_quantity || 0,
        qc_result: "pass",
        rejection_reason: "",
        measurements: "",
        remarks: "",
      });
      setUploadedFiles([]);
    }
  }, [open, itemData, reset]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const newFiles: QCFile[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error(`File ${file.name} is too large. Maximum size is 5MB.`);
        continue;
      }

      // Check total files (max 5)
      if (uploadedFiles.length + newFiles.length >= 5) {
        toast.warning("Maximum 5 files allowed");
        break;
      }

      newFiles.push({
        file,
        preview: URL.createObjectURL(file),
      });
    }

    setUploadedFiles([...uploadedFiles, ...newFiles]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleFileRemove = (index: number) => {
    const newFiles = [...uploadedFiles];
    URL.revokeObjectURL(newFiles[index].preview);
    newFiles.splice(index, 1);
    setUploadedFiles(newFiles);
  };

  const onSubmit = async (data: QCFormData) => {
    // Validate quantities
    const total = (data.accepted_quantity || 0) + (data.rejected_quantity || 0);
    if (total > itemData.received_quantity) {
      toast.error(
        `Total of accepted (${data.accepted_quantity}) and rejected (${data.rejected_quantity}) quantities cannot exceed received quantity (${itemData.received_quantity})`
      );
      return;
    }

    if (total < itemData.received_quantity) {
      toast.warning(
        `Total QC quantity (${total}) is less than received quantity (${itemData.received_quantity}). Continue?`
      );
    }

    // Require rejection reason if there are rejected items
    if ((data.rejected_quantity || 0) > 0 && !data.rejection_reason?.trim()) {
      toast.error("Please provide a rejection reason for rejected items");
      return;
    }

    try {
      setLoading(true);
      const files = uploadedFiles.map((f) => f.file);
      await onSave(data, files);
      
      // Clean up file previews
      uploadedFiles.forEach((f) => URL.revokeObjectURL(f.preview));
      
      toast.success("Quality check completed successfully");
      onClose();
    } catch (error: any) {
      toast.error(error.message || "Failed to save quality check");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    // Clean up file previews
    uploadedFiles.forEach((f) => URL.revokeObjectURL(f.preview));
    onClose();
  };

  const getQCResultColor = (result: string) => {
    switch (result) {
      case "pass":
        return "success";
      case "fail":
        return "error";
      case "partial":
        return "warning";
      default:
        return "default";
    }
  };

  const getQCResultIcon = (result: string) => {
    switch (result) {
      case "pass":
        return <CheckCircle />;
      case "fail":
        return <Cancel />;
      case "partial":
        return <Info />;
      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: "600px" },
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Inward Material Quality Check</Typography>
          <Chip
            label={qcResult.toUpperCase()}
            color={getQCResultColor(qcResult) as any}
            icon={getQCResultIcon(qcResult)}
            sx={{ ml: 2 }}
          />
        </Box>
      </DialogTitle>

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {/* Item Information */}
          <Paper sx={{ p: 2, mb: 3, bgcolor: "grey.50" }}>
            <Typography variant="subtitle2" gutterBottom>
              Item Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Product: <strong>{itemData.product_name}</strong>
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Unit: <strong>{itemData.unit}</strong>
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="textSecondary">
                  Ordered: <strong>{itemData.ordered_quantity}</strong>
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="textSecondary">
                  Received: <strong>{itemData.received_quantity}</strong>
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="textSecondary">
                  Pending QC:{" "}
                  <strong>
                    {itemData.received_quantity - (acceptedQty || 0) - (rejectedQty || 0)}
                  </strong>
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          <Grid container spacing={2}>
            {/* Inspection Details */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="inspection_date"
                control={control}
                rules={{ required: "Inspection date is required" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Inspection Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.inspection_date}
                    helperText={errors.inspection_date?.message}
                    disabled={loading}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="inspector_name"
                control={control}
                rules={{ required: "Inspector name is required" }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Inspector Name"
                    error={!!errors.inspector_name}
                    helperText={errors.inspector_name?.message}
                    disabled={loading}
                  />
                )}
              />
            </Grid>

            {/* Quantities */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="accepted_quantity"
                control={control}
                rules={{
                  required: "Accepted quantity is required",
                  min: { value: 0, message: "Cannot be negative" },
                  max: {
                    value: itemData.received_quantity,
                    message: "Cannot exceed received quantity",
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Accepted Quantity"
                    type="number"
                    inputProps={{ step: 0.01, min: 0 }}
                    error={!!errors.accepted_quantity}
                    helperText={errors.accepted_quantity?.message}
                    disabled={loading}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="rejected_quantity"
                control={control}
                rules={{
                  min: { value: 0, message: "Cannot be negative" },
                  max: {
                    value: itemData.received_quantity,
                    message: "Cannot exceed received quantity",
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Rejected Quantity"
                    type="number"
                    inputProps={{ step: 0.01, min: 0 }}
                    error={!!errors.rejected_quantity}
                    helperText={errors.rejected_quantity?.message}
                    disabled={loading}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                  />
                )}
              />
            </Grid>

            {/* Validation Alert */}
            {(acceptedQty || 0) + (rejectedQty || 0) > itemData.received_quantity && (
              <Grid item xs={12}>
                <Alert severity="error">
                  Total of accepted and rejected quantities cannot exceed received
                  quantity ({itemData.received_quantity})
                </Alert>
              </Grid>
            )}

            {/* QC Result */}
            <Grid item xs={12}>
              <Controller
                name="qc_result"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth disabled>
                    <InputLabel>QC Result (Auto-calculated)</InputLabel>
                    <Select {...field} label="QC Result (Auto-calculated)">
                      <MenuItem value="pass">Pass (All Accepted)</MenuItem>
                      <MenuItem value="partial">Partial (Some Rejected)</MenuItem>
                      <MenuItem value="fail">Fail (All Rejected)</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            {/* Rejection Reason (shown if rejected > 0) */}
            {(rejectedQty || 0) > 0 && (
              <Grid item xs={12}>
                <Controller
                  name="rejection_reason"
                  control={control}
                  rules={{
                    required:
                      rejectedQty > 0 ? "Rejection reason is required" : false,
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Rejection Reason *"
                      multiline
                      rows={2}
                      error={!!errors.rejection_reason}
                      helperText={errors.rejection_reason?.message}
                      disabled={loading}
                      placeholder="Describe the reason for rejection..."
                    />
                  )}
                />
              </Grid>
            )}

            {/* Measurements */}
            <Grid item xs={12}>
              <Controller
                name="measurements"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Measurements (Optional)"
                    multiline
                    rows={2}
                    disabled={loading}
                    placeholder="Enter any measurements or specifications checked..."
                  />
                )}
              />
            </Grid>

            {/* Remarks */}
            <Grid item xs={12}>
              <Controller
                name="remarks"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Additional Remarks"
                    multiline
                    rows={2}
                    disabled={loading}
                    placeholder="Any additional comments or observations..."
                  />
                )}
              />
            </Grid>

            {/* File Upload */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Attach Photos/Documents (Optional, max 5 files, 5MB each)
              </Typography>
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
                onClick={() => fileInputRef.current?.click()}
                disabled={loading || uploadedFiles.length >= 5}
                sx={{ mt: 1 }}
              >
                Upload Files
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                hidden
                multiple
                accept="image/*,.pdf,.doc,.docx"
                onChange={handleFileSelect}
              />
              {uploadedFiles.length > 0 && (
                <List sx={{ mt: 2 }}>
                  {uploadedFiles.map((file, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={file.file.name}
                        secondary={`${(file.file.size / 1024).toFixed(2)} KB`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => handleFileRemove(index)}
                          disabled={loading}
                        >
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleClose} disabled={loading} color="inherit">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={
              loading ||
              (acceptedQty || 0) + (rejectedQty || 0) > itemData.received_quantity
            }
          >
            {loading ? "Saving..." : "Save Quality Check"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default InwardMaterialQCModal;
