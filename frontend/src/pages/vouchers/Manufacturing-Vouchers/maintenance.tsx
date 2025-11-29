// frontend/src/pages/vouchers/Manufacturing-Vouchers/maintenance.tsx
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
  Tooltip,
  Card,
  CardContent,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Visibility,
  FileDownload,
  Refresh,
  Build,
  Warning,
  CheckCircle,
  Timeline,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, Controller } from "react-hook-form";
import { toast } from "react-toastify";
import { ProtectedPage } from "../../../components/ProtectedPage";
import api from "../../../lib/api";

// Types
interface Machine {
  id: number;
  name: string;
  code: string;
  location: string;
  model: string;
  make?: string;
  serial_no?: string;
  status: string;
  criticality: string;
  created_at: string;
}

interface PreventiveSchedule {
  id: number;
  machine_id: number;
  frequency: string;
  tasks: string;
  assigned_technician?: string;
  next_due_date: string;
  overdue: boolean;
  created_at: string;
}

interface Breakdown {
  id: number;
  machine_id: number;
  breakdown_type: string;
  date: string;
  reported_by: string;
  description: string;
  root_cause?: string;
  status: string;
  downtime_hours: number;
  created_at: string;
}

interface PerformanceLog {
  id: number;
  machine_id: number;
  date: string;
  runtime_hours: number;
  idle_hours: number;
  efficiency_percentage: number;
  created_at: string;
}

interface SparePart {
  id: number;
  machine_id: number;
  name: string;
  code: string;
  quantity: number;
  min_level: number;
  reorder_level: number;
  unit_cost: number;
  created_at: string;
}

// ==================== MACHINE MASTER TAB ====================
const MachineMasterTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);

  const { data: machines, isLoading, refetch } = useQuery({
    queryKey: ["machines"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/machines");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      name: "",
      code: "",
      location: "",
      model: "",
      make: "",
      serial_no: "",
      status: "active",
      criticality: "medium",
      amc_details: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/maintenance/machines", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["machines"] });
      setDialogOpen(false);
      reset();
      toast.success("Machine created successfully");
    },
    onError: () => toast.error("Failed to create machine"),
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.put(`/manufacturing/maintenance/machines/${selectedMachine?.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["machines"] });
      setDialogOpen(false);
      setSelectedMachine(null);
      reset();
      toast.success("Machine updated successfully");
    },
    onError: () => toast.error("Failed to update machine"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/manufacturing/maintenance/machines/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["machines"] });
      toast.success("Machine deactivated");
    },
    onError: () => toast.error("Failed to deactivate machine"),
  });

  const handleEdit = (machine: Machine) => {
    setSelectedMachine(machine);
    reset({
      name: machine.name,
      code: machine.code,
      location: machine.location,
      model: machine.model,
      make: machine.make || "",
      serial_no: machine.serial_no || "",
      status: machine.status,
      criticality: machine.criticality,
    });
    setDialogOpen(true);
  };

  const handleCreate = () => {
    setSelectedMachine(null);
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    if (selectedMachine) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Machine Master</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Machine
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
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Model</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Criticality</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {machines?.length > 0 ? (
                machines.map((machine: Machine) => (
                  <TableRow key={machine.id}>
                    <TableCell>{machine.code}</TableCell>
                    <TableCell>{machine.name}</TableCell>
                    <TableCell>{machine.location}</TableCell>
                    <TableCell>{machine.model}</TableCell>
                    <TableCell>
                      <Chip
                        label={machine.status}
                        color={machine.status === "active" ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={machine.criticality}
                        color={
                          machine.criticality === "critical"
                            ? "error"
                            : machine.criticality === "high"
                            ? "warning"
                            : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleEdit(machine)}>
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton size="small" onClick={() => deleteMutation.mutate(machine.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No machines found. Click "Add Machine" to create one.
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
          <DialogTitle>{selectedMachine ? "Edit Machine" : "Add Machine"}</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="code"
                  control={control}
                  rules={{ required: "Code is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Machine Code" error={!!errors.code} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: "Name is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Machine Name" error={!!errors.name} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="location"
                  control={control}
                  rules={{ required: "Location is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Location" error={!!errors.location} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="model"
                  control={control}
                  rules={{ required: "Model is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Model" error={!!errors.model} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="make"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Make" />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="serial_no"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Serial Number" />}
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
                        <MenuItem value="active">Active</MenuItem>
                        <MenuItem value="inactive">Inactive</MenuItem>
                        <MenuItem value="under_maintenance">Under Maintenance</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="criticality"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Criticality</InputLabel>
                      <Select {...field} label="Criticality">
                        <MenuItem value="low">Low</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="high">High</MenuItem>
                        <MenuItem value="critical">Critical</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="amc_details"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="AMC Details" multiline rows={2} />
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

// ==================== PREVENTIVE SCHEDULE TAB ====================
const PreventiveScheduleTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: schedules, isLoading, refetch } = useQuery({
    queryKey: ["preventive-schedules"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/preventive-schedules");
      return response.data;
    },
  });

  const { data: machines } = useQuery({
    queryKey: ["machines"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/machines");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      machine_id: 0,
      frequency: "weekly",
      tasks: "",
      assigned_technician: "",
      next_due_date: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/maintenance/preventive-schedules", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["preventive-schedules"] });
      setDialogOpen(false);
      reset();
      toast.success("Schedule created successfully");
    },
    onError: () => toast.error("Failed to create schedule"),
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => api.post(`/manufacturing/maintenance/preventive-schedules/${id}/complete`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["preventive-schedules"] });
      toast.success("Maintenance completed");
    },
    onError: () => toast.error("Failed to complete maintenance"),
  });

  const handleCreate = () => {
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    createMutation.mutate(data);
  };

  const overdueCount = schedules?.filter((s: PreventiveSchedule) => s.overdue).length || 0;

  return (
    <Box sx={{ mt: 2 }}>
      {overdueCount > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {overdueCount} preventive maintenance task(s) are overdue!
        </Alert>
      )}

      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Preventive Maintenance Schedule</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Schedule
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
                <TableCell>Machine</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Technician</TableCell>
                <TableCell>Next Due</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {schedules?.length > 0 ? (
                schedules.map((schedule: PreventiveSchedule) => (
                  <TableRow key={schedule.id} sx={{ backgroundColor: schedule.overdue ? "error.light" : "inherit" }}>
                    <TableCell>
                      {machines?.find((m: Machine) => m.id === schedule.machine_id)?.name || schedule.machine_id}
                    </TableCell>
                    <TableCell>{schedule.frequency}</TableCell>
                    <TableCell>{schedule.assigned_technician || "-"}</TableCell>
                    <TableCell>{new Date(schedule.next_due_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={schedule.overdue ? "Overdue" : "Scheduled"}
                        color={schedule.overdue ? "error" : "success"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Complete Maintenance">
                        <IconButton size="small" onClick={() => completeMutation.mutate(schedule.id)}>
                          <CheckCircle fontSize="small" color="success" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No schedules found. Click "Add Schedule" to create one.
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
          <DialogTitle>Add Preventive Maintenance Schedule</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="machine_id"
                  control={control}
                  rules={{ required: "Machine is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.machine_id}>
                      <InputLabel>Machine</InputLabel>
                      <Select {...field} label="Machine">
                        {machines?.map((machine: Machine) => (
                          <MenuItem key={machine.id} value={machine.id}>
                            {machine.name} ({machine.code})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="frequency"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Frequency</InputLabel>
                      <Select {...field} label="Frequency">
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="weekly">Weekly</MenuItem>
                        <MenuItem value="monthly">Monthly</MenuItem>
                        <MenuItem value="quarterly">Quarterly</MenuItem>
                        <MenuItem value="annually">Annually</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="assigned_technician"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Assigned Technician" />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="next_due_date"
                  control={control}
                  rules={{ required: "Next due date is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Next Due Date"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      error={!!errors.next_due_date}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="tasks"
                  control={control}
                  rules={{ required: "Tasks are required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Tasks (Checklist)"
                      multiline
                      rows={4}
                      helperText="Enter tasks as JSON or comma-separated list"
                      error={!!errors.tasks}
                    />
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

// ==================== BREAKDOWN TAB ====================
const BreakdownTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: breakdowns, isLoading, refetch } = useQuery({
    queryKey: ["breakdowns"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/breakdowns");
      return response.data;
    },
  });

  const { data: machines } = useQuery({
    queryKey: ["machines"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/machines");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      machine_id: 0,
      breakdown_type: "",
      date: "",
      reported_by: "",
      description: "",
      root_cause: "",
      downtime_hours: 0,
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/maintenance/breakdowns", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["breakdowns"] });
      setDialogOpen(false);
      reset();
      toast.success("Breakdown recorded successfully");
    },
    onError: () => toast.error("Failed to record breakdown"),
  });

  const closeMutation = useMutation({
    mutationFn: (id: number) => api.post(`/manufacturing/maintenance/breakdowns/${id}/close`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["breakdowns"] });
      toast.success("Breakdown closed");
    },
    onError: () => toast.error("Failed to close breakdown"),
  });

  const handleCreate = () => {
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    createMutation.mutate(data);
  };

  const openBreakdowns = breakdowns?.filter((b: Breakdown) => b.status === "open").length || 0;

  return (
    <Box sx={{ mt: 2 }}>
      {openBreakdowns > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {openBreakdowns} open breakdown(s) require attention!
        </Alert>
      )}

      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Breakdown Maintenance</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate} color="error">
            Report Breakdown
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
                <TableCell>Machine</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Reported By</TableCell>
                <TableCell>Downtime (hrs)</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {breakdowns?.length > 0 ? (
                breakdowns.map((breakdown: Breakdown) => (
                  <TableRow key={breakdown.id}>
                    <TableCell>
                      {machines?.find((m: Machine) => m.id === breakdown.machine_id)?.name || breakdown.machine_id}
                    </TableCell>
                    <TableCell>{breakdown.breakdown_type}</TableCell>
                    <TableCell>{new Date(breakdown.date).toLocaleDateString()}</TableCell>
                    <TableCell>{breakdown.reported_by}</TableCell>
                    <TableCell>{breakdown.downtime_hours}</TableCell>
                    <TableCell>
                      <Chip
                        label={breakdown.status}
                        color={breakdown.status === "open" ? "error" : "success"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {breakdown.status === "open" && (
                        <Tooltip title="Close Breakdown">
                          <IconButton size="small" onClick={() => closeMutation.mutate(breakdown.id)}>
                            <CheckCircle fontSize="small" color="success" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No breakdowns recorded.
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
          <DialogTitle>Report Breakdown</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="machine_id"
                  control={control}
                  rules={{ required: "Machine is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.machine_id}>
                      <InputLabel>Machine</InputLabel>
                      <Select {...field} label="Machine">
                        {machines?.map((machine: Machine) => (
                          <MenuItem key={machine.id} value={machine.id}>
                            {machine.name} ({machine.code})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="breakdown_type"
                  control={control}
                  rules={{ required: "Type is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.breakdown_type}>
                      <InputLabel>Breakdown Type</InputLabel>
                      <Select {...field} label="Breakdown Type">
                        <MenuItem value="mechanical">Mechanical</MenuItem>
                        <MenuItem value="electrical">Electrical</MenuItem>
                        <MenuItem value="software">Software</MenuItem>
                        <MenuItem value="other">Other</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="date"
                  control={control}
                  rules={{ required: "Date is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Date"
                      type="datetime-local"
                      InputLabelProps={{ shrink: true }}
                      error={!!errors.date}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="reported_by"
                  control={control}
                  rules={{ required: "Reporter is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Reported By" error={!!errors.reported_by} />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  rules={{ required: "Description is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Description"
                      multiline
                      rows={3}
                      error={!!errors.description}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="root_cause"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Root Cause (if known)" />}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="downtime_hours"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Estimated Downtime (hours)" type="number" />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="error" disabled={createMutation.isPending}>
              {createMutation.isPending ? <CircularProgress size={24} /> : "Report"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== PERFORMANCE LOGS TAB ====================
const PerformanceLogsTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: logs, isLoading, refetch } = useQuery({
    queryKey: ["performance-logs"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/performance-logs");
      return response.data;
    },
  });

  const { data: machines } = useQuery({
    queryKey: ["machines"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/machines");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      machine_id: 0,
      date: "",
      runtime_hours: 0,
      idle_hours: 0,
      efficiency_percentage: 0,
      error_codes: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/maintenance/performance-logs", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["performance-logs"] });
      setDialogOpen(false);
      reset();
      toast.success("Performance log added");
    },
    onError: () => toast.error("Failed to add performance log"),
  });

  const handleExportCSV = async () => {
    try {
      const response = await api.get("/manufacturing/maintenance/performance-logs/export/csv", {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "performance_logs_export.csv");
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
        <Typography variant="h6">Performance Logs</Typography>
        <Box>
          <Button variant="outlined" startIcon={<FileDownload />} onClick={handleExportCSV} sx={{ mr: 1 }}>
            Export CSV
          </Button>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Log
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
                <TableCell>Machine</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Runtime (hrs)</TableCell>
                <TableCell>Idle (hrs)</TableCell>
                <TableCell>Efficiency %</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs?.length > 0 ? (
                logs.map((log: PerformanceLog) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      {machines?.find((m: Machine) => m.id === log.machine_id)?.name || log.machine_id}
                    </TableCell>
                    <TableCell>{new Date(log.date).toLocaleDateString()}</TableCell>
                    <TableCell>{log.runtime_hours}</TableCell>
                    <TableCell>{log.idle_hours}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${log.efficiency_percentage}%`}
                        color={
                          log.efficiency_percentage >= 80
                            ? "success"
                            : log.efficiency_percentage >= 60
                            ? "warning"
                            : "error"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(log.created_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No performance logs found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Add Performance Log</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Controller
                  name="machine_id"
                  control={control}
                  rules={{ required: "Machine is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.machine_id}>
                      <InputLabel>Machine</InputLabel>
                      <Select {...field} label="Machine">
                        {machines?.map((machine: Machine) => (
                          <MenuItem key={machine.id} value={machine.id}>
                            {machine.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="date"
                  control={control}
                  rules={{ required: "Date is required" }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Date"
                      type="datetime-local"
                      InputLabelProps={{ shrink: true }}
                      error={!!errors.date}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={6}>
                <Controller
                  name="runtime_hours"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Runtime Hours" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={6}>
                <Controller
                  name="idle_hours"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Idle Hours" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="efficiency_percentage"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Efficiency %" type="number" />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              {createMutation.isPending ? <CircularProgress size={24} /> : "Add"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== SPARE PARTS TAB ====================
const SparePartsTab: React.FC = () => {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: spareParts, isLoading, refetch } = useQuery({
    queryKey: ["spare-parts"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/spare-parts");
      return response.data;
    },
  });

  const { data: machines } = useQuery({
    queryKey: ["machines"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/machines");
      return response.data;
    },
  });

  const { data: reorderAlerts } = useQuery({
    queryKey: ["reorder-alerts"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/maintenance/spare-parts/alerts/reorder");
      return response.data;
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      machine_id: 0,
      name: "",
      code: "",
      quantity: 0,
      min_level: 0,
      reorder_level: 0,
      unit_cost: 0,
      location_bin: "",
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post("/manufacturing/maintenance/spare-parts", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["spare-parts"] });
      queryClient.invalidateQueries({ queryKey: ["reorder-alerts"] });
      setDialogOpen(false);
      reset();
      toast.success("Spare part added");
    },
    onError: () => toast.error("Failed to add spare part"),
  });

  const handleCreate = () => {
    reset();
    setDialogOpen(true);
  };

  const onSubmit = (data: any) => {
    createMutation.mutate(data);
  };

  return (
    <Box sx={{ mt: 2 }}>
      {reorderAlerts?.count > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {reorderAlerts.count} spare part(s) need reordering!
        </Alert>
      )}

      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Spare Parts Inventory</Typography>
        <Box>
          <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Spare Part
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
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Machine</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Reorder Level</TableCell>
                <TableCell>Unit Cost</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {spareParts?.length > 0 ? (
                spareParts.map((part: SparePart) => (
                  <TableRow
                    key={part.id}
                    sx={{ backgroundColor: part.quantity <= part.reorder_level ? "warning.light" : "inherit" }}
                  >
                    <TableCell>{part.code}</TableCell>
                    <TableCell>{part.name}</TableCell>
                    <TableCell>
                      {machines?.find((m: Machine) => m.id === part.machine_id)?.name || part.machine_id}
                    </TableCell>
                    <TableCell>{part.quantity}</TableCell>
                    <TableCell>{part.reorder_level}</TableCell>
                    <TableCell>₹{part.unit_cost.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={part.quantity <= part.reorder_level ? "Reorder" : "OK"}
                        color={part.quantity <= part.reorder_level ? "warning" : "success"}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No spare parts found.
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
          <DialogTitle>Add Spare Part</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="code"
                  control={control}
                  rules={{ required: "Code is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Part Code" error={!!errors.code} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="name"
                  control={control}
                  rules={{ required: "Name is required" }}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Part Name" error={!!errors.name} />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="machine_id"
                  control={control}
                  rules={{ required: "Machine is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.machine_id}>
                      <InputLabel>Applicable Machine</InputLabel>
                      <Select {...field} label="Applicable Machine">
                        {machines?.map((machine: Machine) => (
                          <MenuItem key={machine.id} value={machine.id}>
                            {machine.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Controller
                  name="location_bin"
                  control={control}
                  render={({ field }) => <TextField {...field} fullWidth label="Location/Bin" />}
                />
              </Grid>
              <Grid item xs={6} md={3}>
                <Controller
                  name="quantity"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Current Stock" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={6} md={3}>
                <Controller
                  name="min_level"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Min Level" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={6} md={3}>
                <Controller
                  name="reorder_level"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Reorder Level" type="number" />
                  )}
                />
              </Grid>
              <Grid item xs={6} md={3}>
                <Controller
                  name="unit_cost"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} fullWidth label="Unit Cost" type="number" />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              {createMutation.isPending ? <CircularProgress size={24} /> : "Add"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

// ==================== MAIN COMPONENT ====================
const MachineMaintenance: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
      <Container maxWidth="xl">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Machine Maintenance
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Manage machines, preventive maintenance, breakdowns, and spare parts.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            Track machine health, schedule preventive maintenance, log breakdowns, 
            and manage spare parts inventory.
          </Alert>

          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
              <Tab icon={<Build />} label="Machine Master" />
              <Tab icon={<Timeline />} label="Preventive Schedule" />
              <Tab icon={<Warning />} label="Breakdown" />
              <Tab label="Performance Logs" />
              <Tab label="Spare Parts" />
            </Tabs>
          </Paper>

          {tabValue === 0 && <MachineMasterTab />}
          {tabValue === 1 && <PreventiveScheduleTab />}
          {tabValue === 2 && <BreakdownTab />}
          {tabValue === 3 && <PerformanceLogsTab />}
          {tabValue === 4 && <SparePartsTab />}
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default MachineMaintenance;