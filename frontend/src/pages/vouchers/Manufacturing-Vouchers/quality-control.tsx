// frontend/src/pages/vouchers/Manufacturing-Vouchers/quality-control.tsx
import React, { useState } from "react";
import {
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  FormControlLabel,
  Switch,
  Tooltip,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Visibility,
  FileDownload,
  CheckCircle,
  Cancel,
  Refresh,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, Controller } from "react-hook-form";
import { toast } from "react-toastify";
import { ProtectedPage } from "../../../components/ProtectedPage";
import api from "../../../lib/api";

// Types
interface QCTemplate {
  id: number;
  product_id: number;
  test_name: string;
  description?: string;
  parameters?: string;
  tolerance_min?: number;
  tolerance_max?: number;
  unit?: string;
  method?: string;
  sampling_size?: number;
  version: string;
  is_active: boolean;
  created_at: string;
}

interface QCInspection {
  id: number;
  batch_id: number;
  work_order_id?: number;
  item_id?: number;
  template_id?: number;
  inspector: string;
  scheduled_date?: string;
  test_results: string;
  measurements?: string;
  photos?: string;
  overall_status: string;
  status: string;
  notes?: string;
  signed_off_by?: number;
  signed_off_at?: string;
  created_at: string;
}

interface Rejection {
  id: number;
  qc_inspection_id: number;
  work_order_id?: number;
  lot_number?: string;
  reason: string;
  reason_code?: string;
  quantity: number;
  ncr_reference?: string;
  mrb_reference?: string;
  disposition?: string;
  rework_required: boolean;
  notes?: string;
  approval_status: string;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
}

// ==================== QC TEMPLATES TAB ====================
const QCTemplatesTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<QCTemplate | null>(null);

  const { data: templates, isLoading, refetch } = useQuery({
    queryKey: ["qc-templates"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/quality-control/templates");
      return response.data;
    },
  });

  const { data: products } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const response = await api.get("/products");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      product_id: 0,
      test_name: "",
      description: "",
      parameters: "",
      tolerance_min: 0,
      tolerance_max: 0,
      unit: "",
      method: "",
      sampling_size: 1,
      version: "1.0",
      is_active: true,
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/quality-control/templates", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["qc-templates"] });
      setDialogOpen(false);
      reset();
      toast.success("QC Template created successfully");
    },
    onError: () => toast.error("Failed to create QC Template"),
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.put(`/manufacturing/quality-control/templates/${selectedTemplate?.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["qc-templates"] });
      setDialogOpen(false);
      setSelectedTemplate(null);
      reset();
      toast.success("QC Template updated successfully");
    },
    onError: () => toast.error("Failed to update QC Template"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/manufacturing/quality-control/templates/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["qc-templates"] });
      toast.success("QC Template deactivated");
    },
    onError: () => toast.error("Failed to deactivate QC Template"),
  });

  const handleEdit = (template: QCTemplate) => {
    setSelectedTemplate(template);
    reset({
      product_id: template.product_id,
      test_name: template.test_name,
      description: template.description || "",
      parameters: template.parameters || "",
      tolerance_min: template.tolerance_min || 0,
      tolerance_max: template.tolerance_max || 0,
      unit: template.unit || "",
      method: template.method || "",
      sampling_size: template.sampling_size || 1,
      version: template.version,
      is_active: template.is_active,
    });
    setDialogOpen(true);
  };

  const handleCreate = () => {
    setSelectedTemplate(null);
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    if (selectedTemplate) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">QC Templates</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Template
          </Button>
        </Box>
      </Box>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Test Name</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Method</TableCell>
                <TableCell>Tolerance</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {templates?.length > 0 ? (
                templates.map((template: QCTemplate) => (
                  <TableRow key={template.id}>
                    <TableCell>{template.test_name}</TableCell>
                    <TableCell>
                      {products?.find((p: any) => p.id === template.product_id)?.product_name || template.product_id}
                    </TableCell>
                    <TableCell>{template.method || "-"}</TableCell>
                    <TableCell>
                      {template.tolerance_min !== null && template.tolerance_max !== null
                        ? `${template.tolerance_min} - ${template.tolerance_max} ${template.unit || ""}`
                        : "-"}
                    </TableCell>
                    <TableCell>{template.version}</TableCell>
                    <TableCell>
                      <Chip
                        label={template.is_active ? "Active" : "Inactive"}
                        color={template.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleEdit(template)}>
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton size="small" onClick={() => deleteMutation.mutate(template.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No templates found. Click "Add Template" to create one.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>{selectedTemplate ? "Edit QC Template" : "Create QC Template"}</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="product_id"
                  control={control}
                  rules={{ required: "Product is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.product_id}>
                      <InputLabel>Product</InputLabel>
                      <Select {...field} label="Product">
                        {products?.map((product: any) => (
                          <MenuItem key={product.id} value={product.id}>
                            {product.product_name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="test_name"
                  control={control}
                  rules={{ required: "Test name is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Test Name" error={!!errors.test_name} />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Description" multiline rows={2} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="tolerance_min"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Min Tolerance" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="tolerance_max"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Max Tolerance" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="unit"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Unit" />}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="method"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Test Method" />}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="sampling_size"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Sampling Size" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Controller
                  name="version"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Version" />}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="parameters"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Parameters (JSON)"
                      multiline
                      rows={3}
                      helperText="JSON format: target values, tolerances, specs"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="is_active"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch checked={field.value} onChange={field.onChange} />}
                      label="Active"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending || updateMutation.isPending}>
              {createMutation.isPending || updateMutation.isPending ? <CircularProgress size={24} /> : "Save"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== INSPECTIONS TAB ====================
const InspectionsTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState<QCInspection | null>(null);
  const [filters, setFilters] = useState({ status: "", overall_status: "" });

  const { data: inspections, isLoading, refetch } = useQuery({
    queryKey: ["qc-inspections", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.status) params.append("status", filters.status);
      if (filters.overall_status) params.append("overall_status", filters.overall_status);
      const response = await api.get(`/manufacturing/quality-control/inspections?${params.toString()}`);
      return response.data;
    },
  });

  const { data: templates } = useQuery({
    queryKey: ["qc-templates"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/quality-control/templates");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      batch_id: 0,
      work_order_id: 0,
      template_id: 0,
      inspector: "",
      test_results: "{}",
      overall_status: "pending",
      status: "draft",
      notes: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/quality-control/inspections", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["qc-inspections"] });
      setDialogOpen(false);
      reset();
      toast.success("Inspection created successfully");
    },
    onError: () => toast.error("Failed to create inspection"),
  });

  const signOffMutation = useMutation({
    mutationFn: (id: number) => api.post(`/manufacturing/quality-control/inspections/${id}/sign-off`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["qc-inspections"] });
      toast.success("Inspection signed off successfully");
    },
    onError: () => toast.error("Failed to sign off inspection"),
  });

  const handleCreate = () => {
    setSelectedInspection(null);
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    createMutation.mutate(data);
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Inspections</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Create Inspection
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filters.status}
            label="Status"
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="draft">Draft</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Result</InputLabel>
          <Select
            value={filters.overall_status}
            label="Result"
            onChange={(e) => setFilters({ ...filters, overall_status: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="pass">Pass</MenuItem>
            <MenuItem value="fail">Fail</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Batch ID</TableCell>
                <TableCell>Inspector</TableCell>
                <TableCell>Template</TableCell>
                <TableCell>Result</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {inspections?.length > 0 ? (
                inspections.map((inspection: QCInspection) => (
                  <TableRow key={inspection.id}>
                    <TableCell>{inspection.id}</TableCell>
                    <TableCell>{inspection.batch_id}</TableCell>
                    <TableCell>{inspection.inspector}</TableCell>
                    <TableCell>
                      {templates?.find((t: any) => t.id === inspection.template_id)?.test_name || "-"}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={inspection.overall_status}
                        color={
                          inspection.overall_status === "pass"
                            ? "success"
                            : inspection.overall_status === "fail"
                            ? "error"
                            : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={inspection.status}
                        color={inspection.status === "completed" ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(inspection.created_at).toLocaleDateString()}</TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {inspection.status !== "completed" && (
                        <Tooltip title="Sign Off">
                          <IconButton size="small" onClick={() => signOffMutation.mutate(inspection.id)}>
                            <CheckCircle fontSize="small" color="success" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No inspections found. Click "Create Inspection" to start.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Create Inspection</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="batch_id"
                  control={control}
                  rules={{ required: "Batch ID is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Batch ID"
                      type="number"
                      error={!!errors.batch_id}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="work_order_id"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Work Order ID (Optional)" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="template_id"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>QC Template</InputLabel>
                      <Select {...field} label="QC Template">
                        <MenuItem value={0}>None</MenuItem>
                        {templates?.map((template: any) => (
                          <MenuItem key={template.id} value={template.id}>
                            {template.test_name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="inspector"
                  control={control}
                  rules={{ required: "Inspector is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Inspector Name" error={!!errors.inspector} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="overall_status"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Result</InputLabel>
                      <Select {...field} label="Result">
                        <MenuItem value="pending">Pending</MenuItem>
                        <MenuItem value="pass">Pass</MenuItem>
                        <MenuItem value="fail">Fail</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Status</InputLabel>
                      <Select {...field} label="Status">
                        <MenuItem value="draft">Draft</MenuItem>
                        <MenuItem value="in_progress">In Progress</MenuItem>
                        <MenuItem value="completed">Completed</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="test_results"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Test Results (JSON)"
                      multiline
                      rows={3}
                      helperText="Enter test results in JSON format"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="notes"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Notes" multiline rows={2} />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              {createMutation.isPending ? <CircularProgress size={24} /> : "Create"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== REJECTIONS TAB ====================
const RejectionsTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: rejections, isLoading, refetch } = useQuery({
    queryKey: ["rejections"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/quality-control/rejections");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      qc_inspection_id: 0,
      reason: "",
      reason_code: "",
      quantity: 0,
      ncr_reference: "",
      disposition: "",
      rework_required: false,
      notes: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/quality-control/rejections", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rejections"] });
      setDialogOpen(false);
      reset();
      toast.success("Rejection logged successfully");
    },
    onError: () => toast.error("Failed to log rejection"),
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => api.post(`/manufacturing/quality-control/rejections/${id}/approve`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rejections"] });
      toast.success("Rejection approved");
    },
    onError: () => toast.error("Failed to approve rejection"),
  });

  const handleExportCSV = async () => {
    try {
      const response = await api.get("/manufacturing/quality-control/rejections/export/csv", {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "rejections_export.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Export completed");
    } catch {
      toast.error("Export failed");
    }
  };

  const handleCreate = () => {
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    createMutation.mutate(data);
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Rejections</Typography>
        <Box>
          <Button variant="outlined" startIcon={<FileDownload />} onClick={handleExportCSV} sx={{ mr: 1 }}>
            Export CSV
          </Button>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Log Rejection
          </Button>
        </Box>
      </Box>

      {isLoading ? (
        <CircularProgress />
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Inspection ID</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Disposition</TableCell>
                <TableCell>NCR Ref</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rejections?.length > 0 ? (
                rejections.map((rejection: Rejection) => (
                  <TableRow key={rejection.id}>
                    <TableCell>{rejection.id}</TableCell>
                    <TableCell>{rejection.qc_inspection_id}</TableCell>
                    <TableCell>{rejection.reason}</TableCell>
                    <TableCell>{rejection.quantity}</TableCell>
                    <TableCell>
                      <Chip
                        label={rejection.disposition || "Pending"}
                        color={
                          rejection.disposition === "scrap"
                            ? "error"
                            : rejection.disposition === "rework"
                            ? "warning"
                            : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{rejection.ncr_reference || "-"}</TableCell>
                    <TableCell>
                      <Chip
                        label={rejection.approval_status}
                        color={rejection.approval_status === "approved" ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(rejection.created_at).toLocaleDateString()}</TableCell>
                    <TableCell align="right">
                      {rejection.approval_status === "pending" && (
                        <Tooltip title="Approve">
                          <IconButton size="small" onClick={() => approveMutation.mutate(rejection.id)}>
                            <CheckCircle fontSize="small" color="success" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    No rejections found. Click "Log Rejection" to add one.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Log Rejection</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="qc_inspection_id"
                  control={control}
                  rules={{ required: "Inspection ID is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="QC Inspection ID"
                      type="number"
                      error={!!errors.qc_inspection_id}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="quantity"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Rejected Quantity" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="reason"
                  control={control}
                  rules={{ required: "Reason is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Reason" multiline rows={2} error={!!errors.reason} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="reason_code"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Reason Code" />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="disposition"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Disposition</InputLabel>
                      <Select {...field} label="Disposition">
                        <MenuItem value="">Select...</MenuItem>
                        <MenuItem value="rework">Rework</MenuItem>
                        <MenuItem value="scrap">Scrap</MenuItem>
                        <MenuItem value="return">Return to Vendor</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="ncr_reference"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="NCR Reference" />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="rework_required"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch checked={field.value} onChange={field.onChange} />}
                      label="Rework Required"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="notes"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Notes" multiline rows={2} />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              {createMutation.isPending ? <CircularProgress size={24} /> : "Log Rejection"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== MAIN COMPONENT ====================
const QualityControl: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
      <Container maxWidth="xl">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Quality Control
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Manage QC templates, inspections, and rejections for quality assurance.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            Use QC Templates to define inspection criteria, create Inspections to record test results, 
            and log Rejections for non-conforming items.
          </Alert>

          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
              <Tab label="QC Templates" />
              <Tab label="Inspections" />
              <Tab label="Rejections" />
            </Tabs>
          </Paper>

          {tabValue === 0 && <QCTemplatesTab />}
          {tabValue === 1 && <InspectionsTab />}
          {tabValue === 2 && <RejectionsTab />}
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default QualityControl;