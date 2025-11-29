// frontend/src/pages/vouchers/Manufacturing-Vouchers/production-order.tsx
import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useForm } from "react-hook-form";
import {
  Box,
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
} from "@mui/material";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../lib/api";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherLayout from "../../../components/VoucherLayout";
import VoucherListModal from "../../../components/VoucherListModal";
import AddBOMModal from "../../../components/AddBOMModal";
import ManufacturingShortageAlert from "../../../components/ManufacturingShortageAlert";
import VoucherDateConflictModal from "../../../components/VoucherDateConflictModal";
import useManufacturingShortages from "../../../hooks/useManufacturingShortages";
import { voucherService } from "../../../services/vouchersService";

import { ProtectedPage } from '../../../components/ProtectedPage';

interface ManufacturingOrder {
  id?: number;
  voucher_number?: string;
  date: string;
  bom_id: number;
  planned_quantity: number;
  produced_quantity?: number;
  scrap_quantity?: number;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  production_status: "planned" | "in_progress" | "completed" | "cancelled";
  priority: "low" | "medium" | "high" | "urgent";
  production_department?: string;
  production_location?: string;
  notes?: string;
  total_amount: number;
  sales_order_id?: number;
  is_deleted?: boolean;
  deletion_remark?: string;
}

const defaultValues: ManufacturingOrder = {
  date: new Date().toISOString().slice(0, 10),
  bom_id: 0,
  planned_quantity: 1,
  produced_quantity: 0,
  scrap_quantity: 0,
  production_status: "planned",
  priority: "medium",
  total_amount: 0,
  sales_order_id: 0,
};

const ProductionOrder: React.FC = () => {
  const router = useRouter();
  const { id, mode: queryMode, from_sales_order } = router.query;
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
  const [selectedBOM, setSelectedBOM] = useState<any>(null);
  const [bomCostBreakdown, setBomCostBreakdown] = useState<any>(null);
  const [showAddBOMModal, setShowAddBOMModal] = useState(false);
  const [pendingSubmitData, setPendingSubmitData] = useState<ManufacturingOrder | null>(null);
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [maxProducible, setMaxProducible] = useState<number | null>(null);
  const [ignoreShortage, setIgnoreShortage] = useState(false);
  const [shortageDataOverride, setShortageDataOverride] = useState<any>(null);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  const queryClient = useQueryClient();
  
  // Shortage checking hook
  const {
    shortageData,
    shortageCheck: checkShortages,
    shortageDialog: showShortageDialog,
    setShowShortageDialog,
  } = useManufacturingShortages(selectedId);
  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ManufacturingOrder>({
    defaultValues,
  });
  const watchedBomId = watch("bom_id");
  const watchedQuantity = watch("planned_quantity");
  const watchedDate = watch("date");
  const watchedSalesOrderId = watch("sales_order_id");
  const watchedStatus = watch("production_status");
  // Fetch manufacturing orders
  const { data: orderList, isLoading: isLoadingList } = useQuery({
    queryKey: ["manufacturing-orders"],
    queryFn: () => api.get("/manufacturing/manufacturing-orders?include_deleted=true").then((res) => res.data),
  });
  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ["boms"],
    queryFn: () => api.get("/manufacturing/bom").then((res) => res.data),
  });
  // Enhanced BOM options with "Create New"
  const enhancedBOMOptions = [
    ...(bomList || []),
    { id: null, bom_name: "Create New BOM...", version: "" },
  ];
  // Fetch specific manufacturing order
  const { data: orderData, isLoading } = useQuery({
    queryKey: ["manufacturing-order", selectedId],
    queryFn: () =>
      api.get(`/manufacturing/manufacturing-orders/${selectedId}`).then((res) => res.data),
    enabled: !!selectedId,
  });
  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ["nextManufacturingOrderNumber"],
    queryFn: () =>
      api.get("/manufacturing/manufacturing-orders/next-number").then((res) => res.data),
    enabled: mode === "create",
  });
  // Fetch BOM cost breakdown
  const { data: costBreakdown } = useQuery({
    queryKey: ["bom-cost-breakdown", watchedBomId, watchedQuantity],
    queryFn: () =>
      api
        .get(
          `/manufacturing/bom/${watchedBomId}/cost-breakdown?production_quantity=${watchedQuantity}`,
        )
        .then((res) => res.data),
    enabled: !!watchedBomId && watchedQuantity > 0,
  });
  // NEW: Fetch max producible for BOM
  const { data: maxProducibleData } = useQuery({
    queryKey: ["bom-max-producible", watchedBomId],
    queryFn: () => api.get(`/manufacturing/manufacturing-orders/bom/${watchedBomId}/max-producible`).then((res) => res.data),
    enabled: !!watchedBomId,
  });

  // NEW: Check producible for quantity (enabled false, refetch on need)
  const { data: producibleCheckData, refetch: checkProducible } = useQuery({
    queryKey: ["bom-producible-check", watchedBomId, watchedQuantity],
    queryFn: () => api.get(`/manufacturing/manufacturing-orders/bom/${watchedBomId}/check-producible?quantity=${watchedQuantity}`).then((res) => res.data),
    enabled: false,
  });
  const sortedOrders = orderList
    ? [...orderList].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];
  const latestOrders = sortedOrders.slice(0, 10);
  useEffect(() => {
    if (mode === "create" && nextVoucherNumber) {
      setValue("voucher_number", nextVoucherNumber);
    } else if (orderData) {
      reset(orderData);
    } else if (mode === "create") {
      reset(defaultValues);
    }
  }, [orderData, mode, reset, nextVoucherNumber, setValue]);
  useEffect(() => {
    if (watchedBomId && bomList) {
      const bom = bomList.find((b: any) => b.id === watchedBomId);
      setSelectedBOM(bom);
    }
  }, [watchedBomId, bomList]);
  useEffect(() => {
    if (costBreakdown) {
      setBomCostBreakdown(costBreakdown);
      setValue("total_amount", costBreakdown.cost_breakdown.total_cost);
    }
  }, [costBreakdown, setValue]);

  useEffect(() => {
    if (!selectedId && mode !== "create") {
      setMode("create");
    }
  }, [selectedId, mode]);

  // NEW: Set max producible
  useEffect(() => {
    if (maxProducibleData) {
      setMaxProducible(maxProducibleData.max_producible);
    }
  }, [maxProducibleData]);

  // NEW: Check if quantity > max and show dialog if over
  useEffect(() => {
    const checkOverQuantity = async () => {
      if (watchedBomId && watchedQuantity && maxProducible !== null && watchedQuantity > maxProducible && !ignoreShortage) {
        const { data } = await checkProducible();
        setShortageDataOverride({
          voucher_number: mode === 'create' ? 'New Order Preview' : orderData?.voucher_number,
          is_material_available: false,
          shortages: data.shortages,
          recommendations: [
            { type: 'warning', message: 'Shortage detected for selected quantity', action: 'Reduce quantity or procure materials' },
            { type: 'info', message: `Maximum producible: ${maxProducible} units`, action: 'Adjust planned quantity' }
          ],
          critical_items: data.shortages.filter((s: any) => s.severity === 'no_po').length,
          warning_items: data.shortages.filter((s: any) => s.severity !== 'no_po').length,
        });
        setShowShortageDialog(true);
      } else {
        setShowShortageDialog(false);
        setShortageDataOverride(null);
      }
    };
    checkOverQuantity();
  }, [watchedQuantity, maxProducible, watchedBomId, ignoreShortage, mode, orderData, checkProducible]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      if (watchedDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await api.get(
            `/manufacturing/manufacturing-orders/next-number?voucher_date=${watchedDate}`
          );
          setValue('voucher_number', response.data);
          
          // Check for backdated conflicts
          const conflictResponse = await api.get(
            `/manufacturing/manufacturing-orders/check-backdated-conflict?voucher_date=${watchedDate}`
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

  // Handle pre-filling from sales order
  useEffect(() => {
    const prefillFromSalesOrder = async () => {
      if (from_sales_order && mode === 'create') {
        try {
          const salesOrder = await voucherService.getVoucherById('sales-orders', Number(from_sales_order));
          // Assume single item for simplicity
          const mainItem = salesOrder.items[0];
          setValue('planned_quantity', mainItem.quantity);
          setValue('notes', `Created from sales order ${salesOrder.voucher_number}`);
          
          // Find matching BOM
          const bomsResponse = await api.get("/manufacturing/bom");
          const boms = bomsResponse.data;
          const matchingBom = boms.find((bom: any) => bom.output_item_id === mainItem.product_id);
          if (matchingBom) {
            setValue('bom_id', matchingBom.id);
          }
        } catch (error) {
          console.error('Error pre-filling from sales order:', error);
        }
      }
    };
    
    prefillFromSalesOrder();
  }, [from_sales_order, mode, setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ManufacturingOrder) => {
      if (from_sales_order) {
        data.sales_order_id = Number(from_sales_order);
      }
      return api.post("/manufacturing/manufacturing-orders", data);
    },
    onSuccess: async (newOrder) => {
      queryClient.invalidateQueries({ queryKey: ["manufacturing-orders"] });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue("voucher_number", newNextNumber);
    },
    onError: (error: any) => {
      console.error("Error creating manufacturing order:", error);
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManufacturingOrder }) =>
      api.patch(`/manufacturing/manufacturing-orders/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["manufacturing-orders"] });
      setMode("view");
      reset(orderData);
    },
    onError: (error: any) => {
      console.error("Error updating manufacturing order:", error);
    },
  });
  const deleteMutation = useMutation({
    mutationFn: ({ id, remark }: { id: number; remark: string }) =>
      api.patch(`/manufacturing/manufacturing-orders/${id}`, { is_deleted: true, deletion_remark: remark }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["manufacturing-orders"] });
    },
    onError: (error: any) => {
      console.error("Error soft-deleting manufacturing order:", error);
    },
  });
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.patch(`/manufacturing/manufacturing-orders/${id}/status`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["manufacturing-orders"] });
    },
    onError: (error: any) => {
      console.error("Error updating status:", error);
    },
  });
  const onSubmit = async (data: ManufacturingOrder) => {
    // NEW: For create, check producible if not ignored
    if (mode === "create" && watchedQuantity > (maxProducible || 0) && !ignoreShortage) {
      setShowShortageDialog(true);
      return;
    }

    // For edit mode with an existing order, check shortages before proceeding
    if (mode === "edit" && selectedId) {
      try {
        const shortageInfo = await checkShortages();
        if (shortageInfo && !shortageInfo.is_material_available && !ignoreShortage) {
          // Show shortage dialog and wait for user decision
          setPendingSubmitData({ id: selectedId, data });
          setShowShortageDialog(true);
          return;
        }
      } catch (error) {
        console.error("Error checking shortages:", error);
        // Proceed with submission if shortage check fails
      }
    }
    
    // Proceed with submission
    if (mode === "create") {
      createMutation.mutate(data);
    } else if (mode === "edit" && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    }
    setIgnoreShortage(false); // Reset ignore after submit
  };
  
  const handleProceedWithShortage = () => {
    setShowShortageDialog(false);
    setIgnoreShortage(true);
    if (pendingSubmitData) {
      if (mode === "edit" && selectedId) {
        updateMutation.mutate({ id: selectedId, data: pendingSubmitData.data });
      } else if (mode === "create") {
        createMutation.mutate(pendingSubmitData.data);
      }
      setPendingSubmitData(null);
    }
    // For pre-submit warning, just set ignore and user can submit
  };
  const handleEdit = (order: any) => {
    setSelectedId(order.id);
    setMode("edit");
  };
  const handleView = (order: any) => {
    setSelectedId(order.id);
    setMode("view");
  };
  const handleContextMenuClose = () => {
    setContextMenu(null);
  };
  const handleDeleteOrder = async (id: number) => {
    const remark = prompt("Please provide a remark for deletion (required):");
    if (remark) {
      deleteMutation.mutate({ id, remark });
    }
  };
  const handleChangeStatus = async (id: number) => {
    // Simple prompt for new status; in production, use a dialog with select
    const newStatus = prompt("Enter new status (planned/in_progress/completed/cancelled):");
    if (newStatus && ["planned", "in_progress", "completed", "cancelled"].includes(newStatus)) {
      statusMutation.mutate({ id, status: newStatus });
    } else {
      alert("Invalid status");
    }
  };
  const handlePrintOrder = async (id: number) => {
    // Call PDF generation
    try {
      const response = await api.get(`/manufacturing/manufacturing-orders/${id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `production_order_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error generating PDF:", error);
    }
  };
  const getStatusColor = (status: string) => {
    switch (status) {
      case "planned":
        return "primary";
      case "in_progress":
        return "warning";
      case "completed":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "low":
        return "success";
      case "medium":
        return "default";
      case "high":
        return "warning";
      case "urgent":
        return "error";
      default:
        return "default";
    }
  };
  const handleAddBOM = (newBOM: any) => {
    setValue("bom_id", newBOM.id);
    setShowAddBOMModal(false);
  };
  // Fetch sales orders for select
  const { data: salesOrders } = useQuery({
    queryKey: ["sales-orders"],
    queryFn: () => api.get("/vouchers/sales-orders").then((res) => res.data),
  });
  // Handle sales order selection
  useEffect(() => {
    const fetchSalesOrder = async () => {
      if (watchedSalesOrderId) {
        try {
          const salesOrder = await api.get(`/vouchers/sales-orders/${watchedSalesOrderId}`).then((res) => res.data);
          // Assume single manufactured item
          const manufacturedItem = salesOrder.items.find((item: any) => item.is_manufactured);  // Assume is_manufactured flag
          if (manufacturedItem) {
            setValue('planned_quantity', manufacturedItem.quantity);
            // Find matching BOM
            const boms = await api.get("/manufacturing/bom").then((res) => res.data);
            const matchingBom = boms.find((bom: any) => bom.output_item_id === manufacturedItem.product_id);
            if (matchingBom) {
              setValue('bom_id', matchingBom.id);
            }
          }
        } catch (error) {
          console.error('Error fetching sales order:', error);
        }
      }
    };
    fetchSalesOrder();
  }, [watchedSalesOrderId, setValue]);

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

  const indexContent = (
    <>
      <Typography variant="h6" gutterBottom>
        Recent Orders
      </Typography>
      <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Order #</TableCell>
              <TableCell>BOM</TableCell>
              <TableCell>Qty</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell align="right" sx={{ p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestOrders.map((order) => (
              <TableRow
                key={order.id}
                hover
                sx={{ cursor: "pointer", textDecoration: order.is_deleted ? 'line-through' : 'none' }}
                onContextMenu={(e) => {
                  e.preventDefault();
                  setContextMenu({
                    mouseX: e.clientX - 2,
                    mouseY: e.clientY - 4,
                    voucher: order,
                  });
                }}
              >
                <TableCell>{order.voucher_number}</TableCell>
                <TableCell>{order.bom?.bom_name || "N/A"}</TableCell>
                <TableCell>{order.planned_quantity}</TableCell>
                <TableCell>
                  <Chip
                    label={order.production_status}
                    color={getStatusColor(order.production_status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={order.priority}
                    color={getPriorityColor(order.priority)}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right" sx={{ p: 0 }}>
                  <VoucherContextMenu
                    voucher={order}
                    voucherType="Production Order"
                    onView={handleView}
                    onEdit={handleEdit}
                    onDelete={handleDeleteOrder}
                    onPrint={handlePrintOrder}
                    onChangeStatus={handleChangeStatus}
                    showKebab={true}
                    onClose={() => {}}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );

  const formHeader = (
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <Typography variant="h5" sx={{ fontSize: 20, fontWeight: "bold" }}>
        Production Order - {mode === "create" ? "Create" : mode === "edit" ? "Edit" : "View"}
      </Typography>
      <VoucherHeaderActions
        mode={mode}
        voucherType="Production Order"
        voucherRoute="/vouchers/Manufacturing-Vouchers/production-order"
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
          if (orderData) reset(orderData);
        }}
        showPDFButton={false}
      />
    </Box>
  );

  const formContent = (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Paper sx={{ p: 3 }}>
        <Grid container spacing={2}>
          {/* Basic Information */}
          <Grid size={4}>
            <TextField
              {...control.register("voucher_number")}
              label="Order Number"
              fullWidth
              disabled
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={4}>
            <TextField
              {...control.register("date", { required: true })}
              label="Date"
              type="date"
              fullWidth
              error={!!errors.date}
              disabled={mode === "view"}
              size="small"
              InputLabelProps={{ shrink: true }}
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Priority</InputLabel>
              <Select
                {...control.register("priority")}
                value={watch("priority")}
                onChange={(e) =>
                  setValue(
                    "priority",
                    e.target.value as
                      | "low"
                      | "medium"
                      | "high"
                      | "urgent",
                  )
                }
                disabled={mode === "view"}
                sx={{ height: 27 }}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          {/* NEW: Sales Order Selection */}
          <Grid size={5.25}>
            <Autocomplete
              options={salesOrders || []}
              getOptionLabel={(option: any) => option.voucher_number}
              value={salesOrders?.find((so: any) => so.id === watchedSalesOrderId) || null}
              onChange={(_, newValue) => {
                setValue("sales_order_id", newValue?.id || 0);
              }}
              disabled={mode === "view"}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Sales Order"
                  size="small"
                  sx={{ "& .MuiInputBase-root": { height: 27 } }}
                />
              )}
            />
          </Grid>
          {/* BOM Selection */}
          <Grid size={5.25}>
            <Autocomplete
              options={enhancedBOMOptions}
              getOptionLabel={(option: any) =>
                option.id === null
                  ? option.bom_name
                  : `${option.bom_name} v${option.version}`
              }
              value={
                enhancedBOMOptions.find(
                  (b: any) => b.id === watch("bom_id"),
                ) || null
              }
              onChange={(_, newValue) => {
                if (newValue?.id === null) {
                  setShowAddBOMModal(true);
                } else {
                  setValue("bom_id", newValue?.id || 0);
                }
              }}
              disabled={mode === "view"}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Bill of Materials"
                  error={!!errors.bom_id}
                  size="small"
                  sx={{ "& .MuiInputBase-root": { height: 27 } }}
                />
              )}
            />
          </Grid>
          <Grid size={1.5}>
            <Box sx={{ mt: 1 }}>
              <Typography
                variant="caption"
                color={watchedQuantity > (maxProducible ?? 0) ? 'error' : 'success'}
              >
                Max: {maxProducible ?? 'N/A'}
              </Typography>
            </Box>
          </Grid>
          <Grid size={3}>
            <TextField
              {...control.register("planned_quantity", {
                required: true,
                min: 0.01,
              })}
              label="Planned Quantity"
              type="number"
              fullWidth
              error={!!errors.planned_quantity}
              disabled={mode === "view"}
              size="small"
              InputProps={{ inputProps: { step: 0.01 } }}
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                {...control.register("production_status")}
                value={watchedStatus}
                onChange={(e) =>
                  setValue(
                    "production_status",
                    e.target.value as
                      | "planned"
                      | "in_progress"
                      | "completed"
                      | "cancelled",
                  )
                }
                disabled={mode === "view"}
                sx={{ height: 27 }}
              >
                <MenuItem value="planned">Planned</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          {/* Planning Dates */}
          <Grid size={6}>
            <TextField
              {...control.register("planned_start_date")}
              label="Planned Start Date"
              type="date"
              fullWidth
              disabled={mode === "view"}
              size="small"
              InputLabelProps={{ shrink: true }}
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={6}>
            <TextField
              {...control.register("planned_end_date")}
              label="Planned End Date"
              type="date"
              fullWidth
              disabled={mode === "view"}
              size="small"
              InputLabelProps={{ shrink: true }}
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          {/* Location Information */}
          <Grid size={6}>
            <TextField
              {...control.register("production_department")}
              label="Department"
              fullWidth
              disabled={mode === "view"}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={6}>
            <TextField
              {...control.register("production_location")}
              label="Location"
              fullWidth
              disabled={mode === "view"}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              {...control.register("notes")}
              label="Notes"
              fullWidth
              multiline
              rows={2}
              disabled={mode === "view"}
              size="small"
            />
          </Grid>
          {/* BOM Details */}
          {selectedBOM && (
            <Grid size={12}>
              <Card variant="outlined" sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    BOM Details: {selectedBOM.bom_name} v
                    {selectedBOM.version}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Output Item:{" "}
                    {selectedBOM.output_item?.product_name || "Unknown"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Components: {selectedBOM.components?.length || 0}
                  </Typography>
                  {bomCostBreakdown && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        Estimated Cost:{" "}
                        {bomCostBreakdown.cost_breakdown.total_cost.toFixed(
                          2,
                        )}
                      </Typography>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        Material:{" "}
                        {bomCostBreakdown.cost_breakdown.material_cost.toFixed(
                          2,
                        )}{" "}
                        | Labor:{" "}
                        {bomCostBreakdown.cost_breakdown.labor_cost.toFixed(
                          2,
                        )}{" "}
                        | Overhead:{" "}
                        {bomCostBreakdown.cost_breakdown.overhead_cost.toFixed(
                          2,
                        )}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Paper>
    </form>
  );

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <VoucherLayout
        voucherType="Production Order"
        indexContent={indexContent}
        formHeader={formHeader}
        formContent={formContent}
        onShowAll={() => setShowVoucherListModal(true)}
        centerAligned={false}
      />
      {/* Context Menu */}
      <VoucherContextMenu
        voucherType="Production Order"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
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
            handleDeleteOrder(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
        onPrint={() => {
          if (contextMenu?.voucher) {
            handlePrintOrder(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
        onChangeStatus={() => {
          if (contextMenu?.voucher) {
            handleChangeStatus(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
      />
      <VoucherListModal
        open={showVoucherListModal}
        onClose={() => setShowVoucherListModal(false)}
        voucherType="Production Orders"
        vouchers={sortedOrders || []}
        onVoucherClick={(voucher) => {
          handleView(voucher);
          setShowVoucherListModal(false);
        }}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDeleteOrder}
        onGeneratePDF={handlePrintOrder}
      />
      {/* Add BOM Modal */}
      <AddBOMModal
        open={showAddBOMModal}
        onClose={() => setShowAddBOMModal(false)}
        onAdd={handleAddBOM}
        mode="create"
      />
      {/* Shortage Alert Dialog */}
      <ManufacturingShortageAlert
        open={showShortageDialog}
        onClose={() => {
          setShowShortageDialog(false);
          setPendingSubmitData(null);
          setShortageDataOverride(null);
        }}
        onProceed={handleProceedWithShortage}
        moNumber={shortageData?.voucher_number || shortageDataOverride?.voucher_number}
        isAvailable={shortageData?.is_material_available || shortageDataOverride?.is_material_available || false}
        shortages={shortageData?.shortages || shortageDataOverride?.shortages || []}
        recommendations={shortageData?.recommendations || shortageDataOverride?.recommendations || []}
        title="Material Shortage Detected"
        proceedButtonText="Proceed Anyway"
        showProceedButton={true}
      />
      <VoucherDateConflictModal
        open={showConflictModal}
        onClose={handleCancelConflict}
        conflictInfo={conflictInfo}
        onChangeDateToSuggested={handleChangeDateToSuggested}
        onProceedAnyway={handleProceedAnyway}
        voucherType="Production Order"
      />
    </ProtectedPage>
  );
};
export default ProductionOrder;
