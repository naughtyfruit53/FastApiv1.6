// frontend/src/pages/vouchers/Manufacturing-Vouchers/production-entry.tsx
import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useForm, Controller } from "react-hook-form";
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Autocomplete,
  Divider,
} from "@mui/material";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../lib/api";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherLayout from "../../../components/VoucherLayout";
import VoucherListModal from "../../../components/VoucherListModal";
import VoucherDateConflictModal from "../../../components/VoucherDateConflictModal";
import { voucherService } from "../../../services/vouchersService";
import BOMConsumptionModal from "../../../components/BOMConsumptionModal";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";

import { ProtectedPage } from '../../../components/ProtectedPage';
import { useAuth } from "../../../context/AuthContext";
// Assume this exists or create similar to purchase-order

const schema = yup.object().shape({
  production_order_id: yup.number().required(),
  date: yup.date().required(),
  shift: yup.string(),
  machine: yup.string(),
  operator: yup.string(),
  batch_number: yup.string().required(),
  actual_quantity: yup.number().positive().required(),
  rejected_quantity: yup.number().min(0).required(),
  time_taken: yup.number().positive().required(),
  labor_hours: yup.number().positive().required(),
  machine_hours: yup.number().positive().required(),
  power_consumption: yup.number(),
  downtime_events: yup.array().of(yup.string()),
  notes: yup.string(),
  bom_consumption: yup.array().min(1, "BOM consumption is required").required(),
});

interface ProductionEntry {
  id?: number;
  voucher_number?: string;
  production_order_id: number;
  date: string;
  shift?: string;
  machine?: string;
  operator?: string;
  batch_number: string;
  actual_quantity: number;
  rejected_quantity: number;
  time_taken: number;
  labor_hours: number;
  machine_hours: number;
  power_consumption?: number;
  downtime_events?: string[];
  notes?: string;
  attachments?: File[];
  bom_consumption?: Array<{
    component_id: number;
    actual_qty: number;
    wastage_qty: number;
  }>;
  is_deleted?: boolean;
  deletion_remark?: string;
}

const defaultValues: ProductionEntry = {
  production_order_id: 0,
  date: new Date().toISOString().slice(0, 10),
  shift: '',
  machine: '',
  operator: '',
  batch_number: '',
  actual_quantity: 0,
  rejected_quantity: 0,
  time_taken: 0,
  labor_hours: 0,
  machine_hours: 0,
  power_consumption: 0,
  downtime_events: [],
  notes: '',
  bom_consumption: [],
};

const ProductionEntryPage: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const [mode, setMode] = useState<"create" | "edit" | "view">(
    (queryMode as "create" | "edit" | "view") || "create",
  );
  const [selectedId, setSelectedId] = useState<number | null>(
    id ? Number(id) : null,
  );
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    voucher: any;
  } | null>(null);
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [machines, setMachines] = useState<any[]>([]);
  const [operators, setOperators] = useState<any[]>([]);
  const [productionOrders, setProductionOrders] = useState<any[]>([]);
  const [selectedProductionOrder, setSelectedProductionOrder] = useState<any>(null);
  const [bomData, setBomData] = useState<any>(null);
  const [bomConsumptionData, setBomConsumptionData] = useState<Array<{
    componentId: number;
    plannedQty: number;
    actualQty: number;
    wastageQty: number;
    name: string;
  }>>([]);
  const [showBOMModal, setShowBOMModal] = useState(false);
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  const [maxProducible, setMaxProducible] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ProductionEntry>({
    resolver: yupResolver(schema),
    defaultValues,
  });
  const watchedProductionOrderId = watch("production_order_id");
  const watchedDate = watch("date");
  const watchedActualQuantity = watch("actual_quantity");

  // Fetch production entries list
  const { data: entryList, isLoading: isLoadingList } = useQuery({
    queryKey: ["production-entries"],
    queryFn: () => voucherService.getVouchers("manufacturing/production-entries", { include_deleted: true }),
  });

  // Fetch specific production entry
  const { data: entryData, isLoading } = useQuery({
    queryKey: ["production-entry", selectedId],
    queryFn: () =>
      voucherService.getVoucherById("manufacturing/production-entries", selectedId!),
    enabled: !!selectedId,
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ["nextProductionEntryNumber"],
    queryFn: () =>
      voucherService.getNextVoucherNumber("/manufacturing/production-entries/next-number"),
    enabled: mode === "create",
  });

  // NEW: Fetch max producible for BOM
  const { data: maxProducibleData } = useQuery({
    queryKey: ["bom-max-producible", selectedProductionOrder?.bom_id],
    queryFn: () => api.get(`/manufacturing/bom/${selectedProductionOrder?.bom_id}/max-producible`).then((res) => res.data),
    enabled: !!selectedProductionOrder?.bom_id,
  });

  useEffect(() => {
    if (maxProducibleData) {
      setMaxProducible(maxProducibleData.max_producible);
    }
  }, [maxProducibleData]);

  // Fetch dropdown data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [machinesRes, operatorsRes, ordersRes] = await Promise.all([
          api.get("/manufacturing/manufacturing-orders/machines"),
          api.get("/hr/employees"),
          voucherService.getVouchers("manufacturing/manufacturing-orders"),
        ]);
        setMachines(machinesRes.data);
        setOperators(operatorsRes.data);
        setProductionOrders(ordersRes);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (mode === "create" && nextVoucherNumber) {
      setValue("voucher_number", nextVoucherNumber);
    } else if (entryData) {
      reset(entryData);
      if (entryData.bom_consumption && entryData.production_order?.bom_id) {
        const fetchBOM = async () => {
          const res = await api.get(`/manufacturing/bom/${entryData.production_order.bom_id}`);
          const consumption = res.data.components.map((comp: any) => {
            const saved = entryData.bom_consumption.find((c: any) => c.component_id === comp.id) || {};
            return {
              componentId: comp.id,
              name: comp.name,
              plannedQty: comp.quantity * (entryData.production_order.planned_quantity || 0),
              actualQty: saved.actual_qty || 0,
              wastageQty: saved.wastage_qty || 0,
            };
          });
          setBomConsumptionData(consumption);
        };
        fetchBOM();
      }
    } else if (mode === "create") {
      reset(defaultValues);
    }
  }, [entryData, mode, reset, nextVoucherNumber, setValue]);

  useEffect(() => {
    if (watchedProductionOrderId) {
      const order = productionOrders.find((o: any) => o.id === watchedProductionOrderId);
      setSelectedProductionOrder(order);
      if (order && order.bom_id) {
        const fetchBOM = async () => {
          try {
            const res = await api.get(`/manufacturing/bom/${order.bom_id}`);
            setBomData(res.data);
            if (res.data && res.data.components) {
              const consumption = res.data.components.map((comp: any) => ({
                componentId: comp.id,
                name: comp.name,
                plannedQty: comp.quantity * (order.planned_quantity || 0),
                actualQty: 0,
                wastageQty: 0,
              }));
              setBomConsumptionData(consumption);
            }
          } catch (error) {
            console.error("Error fetching BOM:", error);
            setBomData(null);
            setBomConsumptionData([]);
          }
        };
        fetchBOM();
      }
    }
  }, [watchedProductionOrderId, productionOrders]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      if (watchedDate && mode === 'create') {
        try {
          const response = await api.get(
            `/manufacturing/production-entries/next-number?voucher_date=${watchedDate}`
          );
          setValue('voucher_number', response.data);
          
          const conflictResponse = await api.get(
            `/manufacturing/production-entries/check-backdated-conflict?voucher_date=${watchedDate}`
          );
          
          if (conflictResponse.data.has_conflict) {
            setConflictInfo(conflictResponse.data);
            setShowConflictModal(true);
            setPendingDate(watchedDate);
          }
        } catch (error) {
          console.error('Error fetching voucher number:', error);
        }
      }
    };
    
    fetchVoucherNumber();
  }, [watchedDate, mode, setValue]);

  useEffect(() => {
    if (!selectedId && mode !== "create") {
      setMode("create");
    }
  }, [selectedId, mode]);

  const sortedEntries = entryList
    ? [...entryList].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];
  const latestEntries = sortedEntries.slice(0, 10);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ProductionEntry) => {
      return voucherService.createVoucher("manufacturing/production-entries", data);
    },
    onSuccess: async (newEntry) => {
      // Update production order status
      if (newEntry.production_order_id) {
        await voucherService.updateVoucher("manufacturing/manufacturing-orders", newEntry.production_order_id, { production_status: "in_progress" });
      }
      queryClient.invalidateQueries({ queryKey: ["production-entries"] });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue("voucher_number", newNextNumber);
    },
    onError: (error: any) => {
      console.error("Error creating production entry:", error);
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductionEntry }) =>
      voucherService.updateVoucher("manufacturing/production-entries", id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["production-entries"] });
      setMode("view");
      reset(entryData);
    },
    onError: (error: any) => {
      console.error("Error updating production entry:", error);
    },
  });
  const deleteMutation = useMutation({
    mutationFn: ({ id, remark }: { id: number; remark: string }) =>
      api.patch(`/manufacturing/production-entries/${id}`, { is_deleted: true, deletion_remark: remark }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["production-entries"] });
    },
    onError: (error: any) => {
      console.error("Error soft-deleting production entry:", error);
    },
  });
  const onSubmit = async (data: ProductionEntry) => {
    // Proceed with submission
    if (mode === "create") {
      createMutation.mutate(data);
    } else if (mode === "edit" && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    }
  };

  const handleEdit = (entry: any) => {
    setSelectedId(entry.id);
    setMode("edit");
  };
  const handleView = (entry: any) => {
    setSelectedId(entry.id);
    setMode("view");
  };
  const handleDeleteEntry = async (id: number) => {
    const remark = prompt("Please provide a remark for deletion (required):");
    if (remark) {
      deleteMutation.mutate({ id, remark });
    }
  };
  const handlePrintEntry = async (id: number) => {
    try {
      const response = await api.get(`/manufacturing/production-entries/${id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `production_entry_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error generating PDF:", error);
    }
  };
  const handleAddMachine = () => {
    alert("Coming soon");
  };
  const handleAddOperator = () => {
    alert("Coming soon");
  };
  const handleBOMSubmit = (data: Array<{ componentId: number; actualQty: number; wastageQty: number }>) => {
    setValue("bom_consumption", data.map(({ componentId, actualQty, wastageQty }) => ({
      component_id: componentId,
      actual_qty: actualQty,
      wastage_qty: wastageQty,
    })));
    setShowBOMModal(false);
  };

  // Conflict modal handlers
  const handleChangeDateToSuggested = () => {
    if (conflictInfo?.suggested_date) {
      setValue('date', conflictInfo.suggested_date.split('T')[0]);
      setShowConflictModal(false);
      setPendingDate(null);
    }
  };

  const handleProceedAnyway = () => {
    setShowConflictModal(false);
  };

  const handleCancelConflict = () => {
    setShowConflictModal(false);
    if (pendingDate) {
      setValue('date', '');
    }
    setPendingDate(null);
  };

  // Enhanced options for machines and operators
  const enhancedMachines = [
    { id: null, name: "Add New Machine..." },
    ...machines
  ];

  const enhancedOperators = [
    { id: null, name: "Add New Operator..." },
    ...operators
  ];

  const indexContent = (
    <>
      <Typography variant="h6" gutterBottom sx={{ fontSize: 16, fontWeight: "bold" }}>
        Recent Entries
      </Typography>
      <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Entry #</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Order</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Qty</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Date</TableCell>
              <TableCell align="right" sx={{ p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestEntries.map((entry: any) => {
              const dateStr = entry.date ? entry.date.split('T')[0] : '';
              const displayDate = dateStr ? new Date(dateStr).toLocaleDateString('en-GB') : 'N/A';
              return (
                <TableRow
                  key={entry.id}
                  hover
                  sx={{ cursor: "pointer", textDecoration: entry.is_deleted ? 'line-through' : 'none' }}
                  onContextMenu={(e) => {
                    e.preventDefault();
                    setContextMenu({
                      mouseX: e.clientX - 2,
                      mouseY: e.clientY - 4,
                      voucher: entry,
                    });
                  }}
                >
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{entry.voucher_number}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{entry.production_order?.voucher_number || "N/A"}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{entry.actual_quantity}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{displayDate}</TableCell>
                  <TableCell align="right" sx={{ p: 0 }}>
                    <VoucherContextMenu
                      voucher={entry}
                      voucherType="Production Entry"
                      onView={handleView}
                      onEdit={handleEdit}
                      onDelete={handleDeleteEntry}
                      onPrint={handlePrintEntry}
                      showKebab={true}
                      onClose={() => {}}
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );

  const formHeader = (
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <Typography variant="h5" sx={{ fontSize: 20, fontWeight: "bold" }}>
        Production Entry - {mode === "create" ? "Create" : mode === "edit" ? "Edit" : "View"}
      </Typography>
      <VoucherHeaderActions
        mode={mode}
        voucherType="Production Entry"
        voucherRoute="/vouchers/Manufacturing-Vouchers/production-entry"
        currentId={selectedId || undefined}
        onEdit={() => setMode("edit")}
        onCreate={() => {
          setMode("create");
          setSelectedId(null);
          reset(defaultValues);
          refetchNextNumber();
        }}
        onCancel={() => {
          setMode("view");
          if (entryData) reset(entryData);
        }}
        onSave={handleSubmit(onSubmit)}
        showPDFButton={false}
      />
    </Box>
  );

  const formContent = (
    <Paper sx={{ p: 3, width: '100%' }}>
      <Grid container spacing={2}>
        {/* First row: 3 fields */}
        <Grid size={4}>
          <TextField
            {...control.register("voucher_number")}
            label="Entry Number"
            fullWidth
            disabled
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={{ "& .MuiInputBase-root": { height: 27 } }}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="date"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Date"
                type="date"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.date}
                helperText={errors.date?.message}
                size="small"
                InputLabelProps={{ shrink: true }}
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="production_order_id"
            control={control}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={productionOrders}
                getOptionLabel={(option: any) => option.voucher_number}
                value={productionOrders.find((o: any) => o.id === field.value) || null}
                onChange={(_, value) => field.onChange(value?.id || 0)}
                disabled={mode === "view"}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Production Order No."
                    error={!!errors.production_order_id}
                    helperText={errors.production_order_id?.message}
                    size="small"
                    sx={{ "& .MuiInputBase-root": { height: 27 } }}
                  />
                )}
              />
            )}
          />
        </Grid>
        {/* Divider */}
        <Grid size={12}>
          <Divider sx={{ my: 2 }} />
        </Grid>
        {/* Centered BOM button with width 4 */}
        <Grid size={12} container justifyContent="center">
          <Grid size={4}>
            <Button 
              variant="contained" 
              onClick={() => setShowBOMModal(true)}
              disabled={mode === "view" || !selectedProductionOrder || !bomData}
              fullWidth
              sx={{ height: 27 }}
            >
              Manage BOM Consumption
            </Button>
          </Grid>
        </Grid>
        {/* Next row: Shift, Machine, Operator */}
        <Grid size={4}>
          <Controller
            name="shift"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Shift"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.shift}
                helperText={errors.shift?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="machine"
            control={control}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={enhancedMachines}
                getOptionLabel={(option) => option.name}
                value={enhancedMachines.find((m: any) => m.id === field.value) || null}
                onChange={(_, value) => {
                  if (value?.id === null) {
                    handleAddMachine();
                  } else {
                    field.onChange(value?.id || '');
                  }
                }}
                disabled={mode === "view"}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Machine"
                    error={!!errors.machine}
                    helperText={errors.machine?.message}
                    size="small"
                    sx={{ "& .MuiInputBase-root": { height: 27 } }}
                  />
                )}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="operator"
            control={control}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={enhancedOperators}
                getOptionLabel={(option) => option.id === null ? option.name : option.user?.full_name || option.employee_code}
                value={enhancedOperators.find((o: any) => o.id === field.value) || null}
                onChange={(_, value) => {
                  if (value?.id === null) {
                    handleAddOperator();
                  } else {
                    field.onChange(value?.id || '');
                  }
                }}
                disabled={mode === "view"}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Operator"
                    error={!!errors.operator}
                    helperText={errors.operator?.message}
                    size="small"
                    sx={{ "& .MuiInputBase-root": { height: 27 } }}
                  />
                )}
              />
            )}
          />
        </Grid>
        {/* Remaining fields */}
        <Grid size={4}>
          <Controller
            name="actual_quantity"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Actual Output"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.actual_quantity}
                helperText={errors.actual_quantity?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
          {maxProducible !== null && (
            <Typography 
              variant="caption" 
              color={watchedActualQuantity > maxProducible ? 'error' : 'success'}
              sx={{ mt: 0.5, display: 'block' }}
            >
              Max producible: {maxProducible}
            </Typography>
          )}
        </Grid>
        <Grid size={4}>
          <Controller
            name="batch_number"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Batch Number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.batch_number}
                helperText={errors.batch_number?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="rejected_quantity"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Rejected Quantity"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.rejected_quantity}
                helperText={errors.rejected_quantity?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="time_taken"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Time Taken (hours)"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.time_taken}
                helperText={errors.time_taken?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="labor_hours"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Labor Hours"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.labor_hours}
                helperText={errors.labor_hours?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="machine_hours"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Machine Hours"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.machine_hours}
                helperText={errors.machine_hours?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="power_consumption"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Power Consumption"
                type="number"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.power_consumption}
                helperText={errors.power_consumption?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={4}>
          <Controller
            name="downtime_events"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Downtime Events (comma-separated)"
                fullWidth
                disabled={mode === "view"}
                error={!!errors.downtime_events}
                helperText={errors.downtime_events?.message}
                size="small"
                sx={{ "& .MuiInputBase-root": { height: 27 } }}
              />
            )}
          />
        </Grid>
        <Grid size={12}>
          <Controller
            name="notes"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Notes"
                multiline
                rows={2}
                fullWidth
                disabled={mode === "view"}
                error={!!errors.notes}
                helperText={errors.notes?.message}
                size="small"
              />
            )}
          />
        </Grid>
        <Grid size={12}>
          <input
            type="file"
            multiple
            disabled={mode === "view"}
            onChange={(e) => setValue("attachments", Array.from(e.target.files || []))}
          />
        </Grid>
      </Grid>
    </Paper>
  );

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <VoucherLayout
        voucherType="Production Entry"
        indexContent={indexContent}
        formHeader={formHeader}
        formContent={formContent}
        onShowAll={() => setShowVoucherListModal(true)}
        centerAligned={false}
      />
      {/* Context Menu */}
      <VoucherContextMenu
        voucherType="Production Entry"
        contextMenu={contextMenu}
        onClose={() => setContextMenu(null)}
        onEdit={() => {
          if (contextMenu?.voucher) {
            handleEdit(contextMenu.voucher);
          }
          setContextMenu(null);
        }}
        onView={() => {
          if (contextMenu?.voucher) {
            handleView(contextMenu.voucher);
          }
          setContextMenu(null);
        }}
        onDelete={() => {
          if (contextMenu?.voucher) {
            handleDeleteEntry(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
        onPrint={() => {
          if (contextMenu?.voucher) {
            handlePrintEntry(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
        showKebab={true}
      />
      <VoucherListModal
        open={showVoucherListModal}
        onClose={() => setShowVoucherListModal(false)}
        voucherType="Production Entries"
        vouchers={sortedEntries || []}
        onVoucherClick={(voucher) => {
          handleView(voucher);
          setShowVoucherListModal(false);
        }}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDeleteEntry}
        onGeneratePDF={handlePrintEntry}
      />
      <BOMConsumptionModal
        open={showBOMModal}
        onClose={() => setShowBOMModal(false)}
        onSubmit={handleBOMSubmit}
        plannedQuantity={selectedProductionOrder?.planned_quantity || 0}
        components={bomConsumptionData}
      />
      <VoucherDateConflictModal
        open={showConflictModal}
        onClose={handleCancelConflict}
        conflictInfo={conflictInfo}
        onChangeDateToSuggested={handleChangeDateToSuggested}
        onProceedAnyway={handleProceedAnyway}
        voucherType="Production Entry"
      />
    </ProtectedPage>
  );
};

export default ProductionEntryPage;
