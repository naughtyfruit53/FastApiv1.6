// frontend/src/pages/vouchers/Manufacturing-Vouchers/production-entry.tsx
import React, { useState, useEffect } from "react";
import { Typography, Container, Box, Button, Grid, TextField, Select, MenuItem, FormControl, InputLabel, CircularProgress, Autocomplete } from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { ProtectedPage } from "../../../components/ProtectedPage";
import { useAuth } from "../../../context/AuthContext";
import api from "../../../services/api/client"; // Assuming this is your API client

// Define form schema with all required fields
const schema = yup.object().shape({
  productionOrderNo: yup.string().required("Production Order No. is required"),
  date: yup.date().required("Date is required"),
  shift: yup.string(),
  machine: yup.string().required("Machine is required"),
  operator: yup.string().required("Operator is required"),
  status: yup.string().oneOf(["Planned", "In-progress", "Completed", "Rework"]).required("Status is required"),
  productId: yup.number().required("Product is required"),
  plannedQuantity: yup.number().positive().required("Planned Quantity is required"),
  actualQuantity: yup.number().positive().required("Actual Quantity is required"),
  wastagePercentage: yup.number().min(0).max(100),
  batchNumber: yup.string().required("Batch Number is required"),
  rejectedQuantity: yup.number().min(0).required("Rejected Quantity is required"),
  timeTaken: yup.number().positive().required("Time Taken is required"),
  laborHours: yup.number().positive().required("Labor Hours is required"),
  machineHours: yup.number().positive().required("Machine Hours is required"),
  powerConsumption: yup.number(),
  downtimeEvents: yup.array().of(yup.string()),
  notes: yup.string(),
  attachments: yup.array().of(yup.mixed()),
});

interface ProductionEntryFormData {
  productionOrderNo: string;
  date: Date;
  shift?: string;
  machine: string;
  operator: string;
  status: "Planned" | "In-progress" | "Completed" | "Rework";
  productId: number;
  plannedQuantity: number;
  actualQuantity: number;
  wastagePercentage?: number;
  batchNumber: string;
  rejectedQuantity: number;
  timeTaken: number;
  laborHours: number;
  machineHours: number;
  powerConsumption?: number;
  downtimeEvents?: string[];
  notes?: string;
  attachments?: File[];
}

const ProductionEntry: React.FC = () => {
  const { user } = useAuth();
  const [machines, setMachines] = useState<any[]>([]);
  const [operators, setOperators] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [bomData, setBomData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);

  const { control, handleSubmit, formState: { errors }, reset, watch, setValue } = useForm<ProductionEntryFormData>({
    resolver: yupResolver(schema),
  });

  const productId = watch("productId");
  const plannedQuantity = watch("plannedQuantity");
  const actualQuantity = watch("actualQuantity");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [machinesRes, operatorsRes, productsRes] = await Promise.all([
          api.get("/manufacturing/manufacturing-orders/machines").catch((e) => {
            console.error("Failed to fetch machines:", e);
            return { data: [] };
          }),
          api.get("/hr/employees").catch((e) => {
            console.error("Failed to fetch operators:", e);
            return { data: [] };
          }),
          api.get("/products").catch((e) => {
            console.error("Failed to fetch products:", e);
            return { data: [] };
          }),
        ]);
        setMachines(machinesRes.data);
        setOperators(operatorsRes.data);
        setProducts(productsRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (productId) {
      const fetchBOM = async () => {
        try {
          const res = await api.get(`/manufacturing/bom?product_id=${productId}`).catch((e) => {
            console.error("Failed to fetch BOM:", e);
            return { data: null };
          });
          setBomData(res.data);
          // Pre-fill based on BOM
          if (plannedQuantity && res.data && res.data.components) {
            res.data.components.forEach((comp: any, index: number) => {
              setValue(`bomComponents.${index}.requiredQty`, comp.quantity * plannedQuantity);
            });
          }
        } catch (error) {
          console.error("Error fetching BOM:", error);
          setBomData(null);
        }
      };
      fetchBOM();
    }
  }, [productId, plannedQuantity, setValue]);

  useEffect(() => {
    if (plannedQuantity && actualQuantity) {
      const wastage = ((plannedQuantity - actualQuantity) / plannedQuantity) * 100;
      setValue("wastagePercentage", wastage);
    }
  }, [plannedQuantity, actualQuantity, setValue]);

  const onSubmit = async (data: ProductionEntryFormData) => {
    setSubmitLoading(true);
    try {
      // Handle file uploads if attachments
      const formData = new FormData();
      if (data.attachments) {
        data.attachments.forEach((file) => formData.append("attachments", file));
      }
      await api.post("/manufacturing/production-entries", { ...data, createdBy: user?.id }); // Adjusted endpoint
      // Trigger inventory updates and QC notification via backend
      reset();
      alert("Production entry recorded successfully!");
    } catch (error) {
      console.error("Error submitting production entry:", error);
      alert("Failed to record production entry.");
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <ProtectedPage moduleKey="manufacturing" action="create">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Production Entry
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Record production activity, consumption, output, and resources.
          </Typography>

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={2}>
              {/* A. Production Order Details */}
              <Grid item xs={12}>
                <Typography variant="h6">Order Details</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Production Order No."
                  disabled // Auto-generated
                  {...control.register("productionOrderNo")}
                  error={!!errors.productionOrderNo}
                  helperText={errors.productionOrderNo?.message}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="date"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Date"
                      type="date"
                      fullWidth
                      error={!!errors.date}
                      helperText={errors.date?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="shift"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Shift"
                      fullWidth
                      error={!!errors.shift}
                      helperText={errors.shift?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="machine"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      options={machines}
                      getOptionLabel={(option) => option.name}
                      onChange={(_, value) => field.onChange(value?.id)}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Machine"
                          error={!!errors.machine}
                          helperText={errors.machine?.message}
                        />
                      )}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="operator"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      options={operators}
                      getOptionLabel={(option) => option.user.full_name || option.employee_code} // UPDATED: Adjusted to match EmployeeProfileResponse structure
                      onChange={(_, value) => field.onChange(value?.id)}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Operator"
                          error={!!errors.operator}
                          helperText={errors.operator?.message}
                        />
                      )}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!errors.status}>
                  <InputLabel>Status</InputLabel>
                  <Controller
                    name="status"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Status">
                        <MenuItem value="Planned">Planned</MenuItem>
                        <MenuItem value="In-progress">In-progress</MenuItem>
                        <MenuItem value="Completed">Completed</MenuItem>
                        <MenuItem value="Rework">Rework</MenuItem>
                      </Select>
                    )}
                  />
                  {errors.status && <Typography color="error">{errors.status.message}</Typography>}
                </FormControl>
              </Grid>

              {/* B. BOM Consumption */}
              <Grid item xs={12}>
                <Typography variant="h6">BOM Consumption</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="productId"
                  control={control}
                  render={({ field }) => (
                    <Autocomplete
                      {...field}
                      options={products}
                      getOptionLabel={(option) => option.product_name} // UPDATED: Adjusted to match ProductResponse
                      onChange={(_, value) => field.onChange(value?.id)}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Product"
                          error={!!errors.productId}
                          helperText={errors.productId?.message}
                        />
                      )}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="plannedQuantity"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Planned Quantity"
                      type="number"
                      fullWidth
                      error={!!errors.plannedQuantity}
                      helperText={errors.plannedQuantity?.message}
                    />
                  )}
                />
              </Grid>
              {/* Add dynamic fields for BOM components if bomData */}
              {bomData && bomData.components.map((comp: any, index: number) => (
                <Grid key={index} item xs={12} md={4}>
                  <TextField
                    label={`${comp.name} Actual Qty`}
                    type="number"
                    {...control.register(`bomComponents.${index}.actualQty`)}
                  />
                  <TextField
                    label="Over/Under"
                    disabled
                    value={(watch(`bomComponents.${index}.actualQty`) || 0) - (comp.quantity * plannedQuantity)}
                  />
                </Grid>
              ))}
              <Grid item xs={12} md={6}>
                <Controller
                  name="wastagePercentage"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Wastage %"
                      type="number"
                      fullWidth
                      disabled // Auto-calc
                      error={!!errors.wastagePercentage}
                      helperText={errors.wastagePercentage?.message}
                    />
                  )}
                />
              </Grid>

              {/* C. Finished Goods Output */}
              <Grid item xs={12}>
                <Typography variant="h6">Finished Goods Output</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="actualQuantity"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Actual Output"
                      type="number"
                      fullWidth
                      error={!!errors.actualQuantity}
                      helperText={errors.actualQuantity?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Batch Number"
                  disabled // Auto-generate
                  {...control.register("batchNumber")}
                  error={!!errors.batchNumber}
                  helperText={errors.batchNumber?.message}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="rejectedQuantity"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Rejected Quantity"
                      type="number"
                      fullWidth
                      error={!!errors.rejectedQuantity}
                      helperText={errors.rejectedQuantity?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="timeTaken"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Time Taken (hours)"
                      type="number"
                      fullWidth
                      error={!!errors.timeTaken}
                      helperText={errors.timeTaken?.message}
                    />
                  )}
                />
              </Grid>

              {/* D. Resource Utilization */}
              <Grid item xs={12}>
                <Typography variant="h6">Resource Utilization</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="laborHours"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Labor Hours"
                      type="number"
                      fullWidth
                      error={!!errors.laborHours}
                      helperText={errors.laborHours?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="machineHours"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Machine Hours"
                      type="number"
                      fullWidth
                      error={!!errors.machineHours}
                      helperText={errors.machineHours?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="powerConsumption"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Power Consumption"
                      type="number"
                      fullWidth
                      error={!!errors.powerConsumption}
                      helperText={errors.powerConsumption?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="downtimeEvents"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Downtime Events (comma-separated)"
                      fullWidth
                      error={!!errors.downtimeEvents}
                      helperText={errors.downtimeEvents?.message}
                    />
                  )}
                />
              </Grid>

              {/* E. Stock Movements - Handled backend */}

              {/* F. Attachments & Notes */}
              <Grid item xs={12}>
                <Typography variant="h6">Attachments & Notes</Typography>
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="notes"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Notes"
                      multiline
                      rows={4}
                      fullWidth
                      error={!!errors.notes}
                      helperText={errors.notes?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <input
                  type="file"
                  multiple
                  onChange={(e) => setValue("attachments", Array.from(e.target.files || []))}
                />
              </Grid>
              <Grid item xs={12}>
                <Button type="submit" variant="contained" disabled={submitLoading}>
                  {submitLoading ? <CircularProgress size={24} /> : "Submit Production Entry"}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default ProductionEntry;