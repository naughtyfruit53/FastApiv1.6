import React, { useState, useEffect } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import {
  Box,
  Button,
  Typography,
  Grid,
  CircularProgress,
  Container,
  Card,
  CardContent,
  TextField,
  Chip,
} from "@mui/material";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../lib/api";
import { getProducts } from "../../../services/masterService";
interface ManufacturingJournalFinishedProduct {
  product_id: number;
  quantity: number;
  unit: string;
  unit_cost: number;
  quality_grade?: string;
  batch_number?: string;
  lot_number?: string;
}
interface ManufacturingJournalMaterial {
  product_id: number;
  quantity_consumed: number;
  unit: string;
  unit_cost: number;
  batch_number?: string;
  lot_number?: string;
}
interface ManufacturingJournalByproduct {
  product_id: number;
  quantity: number;
  unit: string;
  unit_value: number;
  batch_number?: string;
  condition?: string;
}
interface ManufacturingJournalVoucher {
  id?: number;
  voucher_number: string;
  date: string;
  manufacturing_order_id: number;
  bom_id: number;
  date_of_manufacture: string;
  shift?: string;
  operator?: string;
  supervisor?: string;
  machine_used?: string;
  finished_quantity: number;
  scrap_quantity: number;
  rework_quantity: number;
  byproduct_quantity: number;
  material_cost: number;
  labor_cost: number;
  overhead_cost: number;
  quality_grade?: string;
  quality_remarks?: string;
  narration?: string;
  notes?: string;
  status: string;
  finished_products: ManufacturingJournalFinishedProduct[];
  consumed_materials: ManufacturingJournalMaterial[];
  byproducts: ManufacturingJournalByproduct[];
}
const defaultValues: Partial<ManufacturingJournalVoucher> = {
  voucher_number: "",
  date: new Date().toISOString().split("T")[0],
  date_of_manufacture: new Date().toISOString().split("T")[0],
  finished_quantity: 0,
  scrap_quantity: 0,
  rework_quantity: 0,
  byproduct_quantity: 0,
  material_cost: 0,
  labor_cost: 0,
  overhead_cost: 0,
  status: "draft",
  finished_products: [],
  consumed_materials: [],
  byproducts: [],
};
export default function ManufacturingJournalVoucher() {
  const [mode, setMode] = useState<"create" | "edit" | "view">("create");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { control, handleSubmit, watch, setValue, reset, formState } =
    useForm<ManufacturingJournalVoucher>({
      defaultValues,
    });
  const {
    fields: finishedProductFields,
    append: appendFinishedProduct,
    remove: removeFinishedProduct,
  } = useFieldArray({
    control,
    name: "finished_products",
  });
  const {
    fields: materialFields,
    append: appendMaterial,
    remove: removeMaterial,
  } = useFieldArray({
    control,
    name: "consumed_materials",
  });
  const {
    fields: byproductFields,
    append: appendByproduct,
    remove: removeByproduct,
  } = useFieldArray({
    control,
    name: "byproducts",
  });
  const watchedDate = watch('date');
  // Fetch vouchers list
  const { data: voucherList, isLoading } = useQuery({
    queryKey: ["manufacturing-journal-vouchers"],
    queryFn: () =>
      api.get("/manufacturing/manufacturing-journal-vouchers").then((res) => res.data),
  });
  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ["manufacturing-orders"],
    queryFn: () => api.get("/manufacturing/manufacturing-orders").then((res) => res.data),
  });
  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ["boms"],
    queryFn: () => api.get("/manufacturing/bom").then((res) => res.data),
  });
  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });
  // Fetch specific voucher
  const { data: voucherData } = useQuery({
    queryKey: ["manufacturing-journal-voucher", selectedId],
    queryFn: () =>
      api
        .get(`/manufacturing/manufacturing-journal-vouchers/${selectedId}`)
        .then((res) => res.data),
    enabled: !!selectedId,
  });
  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ["nextManufacturingJournalNumber"],
    queryFn: () =>
      api
        .get("/manufacturing/manufacturing-journal-vouchers/next-number")
        .then((res) => res.data),
    enabled: mode === "create",
  });
  
  const sortedVouchers = voucherList
    ? [...voucherList].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];
  
  useEffect(() => {
    if (mode === "create" && nextVoucherNumber) {
      setValue("voucher_number", nextVoucherNumber);
    } else if (voucherData) {
      reset(voucherData);
    } else if (mode === "create") {
      reset(defaultValues);
    }
  }, [voucherData, mode, reset, nextVoucherNumber, setValue]);
  // Calculate totals
  useEffect(() => {
    const materialCost = watch("material_cost") || 0;
    const laborCost = watch("labor_cost") || 0;
    const overheadCost = watch("overhead_cost") || 0;
    // setValue('total_amount', totalCost); // Commented out due to type mismatch
  }, [
    watch("material_cost"),
    watch("labor_cost"),
    watch("overhead_cost"),
    setValue,
  ]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      if (watchedDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await api.get(
            `/manufacturing/manufacturing-journal-vouchers/next-number?voucher_date=${watchedDate}`
          );
          setValue('voucher_number', response.data);
          
          // Check for backdated conflicts
          const conflictResponse = await api.get(
            `/manufacturing/manufacturing-journal-vouchers/check-backdated-conflict?voucher_date=${watchedDate}`
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
  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ManufacturingJournalVoucher) =>
      api.post("/manufacturing/manufacturing-journal-vouchers", data),
    onSuccess: async () => {
      queryClient.invalidateQueries({
        queryKey: ["manufacturing-journal-vouchers"],
      });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue("voucher_number", newNextNumber);
    },
    onError: (error: any) => {
      console.error("Error creating manufacturing journal:", error);
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: ManufacturingJournalVoucher;
    }) => api.put(`/manufacturing/manufacturing-journal-vouchers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["manufacturing-journal-vouchers"],
      });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error("Error updating manufacturing journal:", error);
    },
  });
  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      api.delete(`/manufacturing/manufacturing-journal-vouchers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["manufacturing-journal-vouchers"],
      });
      if (selectedId) {
        setSelectedId(null);
        setMode("create");
        reset(defaultValues);
      }
    },
  });
  const onSubmit = (data: ManufacturingJournalVoucher) => {
    if (mode === "edit" && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };
  const handleEdit = (voucher: ManufacturingJournalVoucher) => {
    setSelectedId(voucher.id!);
    setMode("edit");
  };
  const handleView = (voucher: ManufacturingJournalVoucher) => {
    setSelectedId(voucher.id!);
    setMode("view");
  };
  const handleDelete = (voucherId: number) => {
    if (window.confirm("Are you sure you want to delete this voucher?")) {
      deleteMutation.mutate(voucherId);
    }
  };
  const handleCancel = () => {
    setMode("create");
    setSelectedId(null);
    reset(defaultValues);
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
    // Keep the current date
  };

  const handleCancelConflict = () => {
    setShowConflictModal(false);
    if (pendingDate) {
      // Revert to previous date or clear
      setValue('date', '');
    }
    setPendingDate(null);
  };

    if (isLoading) {
    return (
      <Container>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="200px"
        >
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Manufacturing Journal Vouchers
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Record manufacturing activities, material consumption, and finished goods production
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {/* Voucher List - Left Side */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                mb={2}
              >
                <Typography variant="h6">Recent Vouchers</Typography>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => {
                    setMode("create");
                    reset(defaultValues);
                  }}
                  disabled={mode === "create"}
                >
                  New Voucher
                </Button>
              </Box>
              <Box sx={{ maxHeight: "600px", overflowY: "auto" }}>
                {sortedVouchers.slice(0, 10).map((voucher: any) => (
                  <Card
                    key={voucher.id}
                    variant="outlined"
                    sx={{
                      mb: 1,
                      cursor: "pointer",
                      "&:hover": { bgcolor: "action.hover" },
                    }}
                    onClick={() => handleView(voucher)}
                  >
                    <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle2">
                            {voucher.voucher_number}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(voucher.date).toLocaleDateString()} • Qty: {voucher.finished_quantity}
                          </Typography>
                        </Box>
                        <Chip
                          label={voucher.status}
                          size="small"
                          color={voucher.status === "approved" ? "success" : "default"}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Voucher Form - Right Side */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                mb={2}
              >
                <Typography variant="h6">
                  {mode === "create" && "Create Manufacturing Journal"}
                  {mode === "edit" && "Edit Manufacturing Journal"}
                  {mode === "view" && "View Manufacturing Journal"}
                </Typography>
                {mode !== "create" && (
                  <Button variant="outlined" onClick={handleCancel}>
                    Cancel
                  </Button>
                )}
              </Box>
              <form onSubmit={handleSubmit(onSubmit)}>
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Voucher Number"
                      {...control.register("voucher_number")}
                      fullWidth
                      disabled
                      value={watch("voucher_number")}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date"
                      type="date"
                      {...control.register("date")}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date of Manufacture"
                      type="date"
                      {...control.register("date_of_manufacture")}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Finished Quantity"
                      type="number"
                      {...control.register("finished_quantity")}
                      fullWidth
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Scrap Quantity"
                      type="number"
                      {...control.register("scrap_quantity")}
                      fullWidth
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Material Cost"
                      type="number"
                      {...control.register("material_cost")}
                      fullWidth
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <TextField
                      label="Labor Cost"
                      type="number"
                      {...control.register("labor_cost")}
                      fullWidth
                      disabled={mode === "view"}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="Narration"
                      {...control.register("narration")}
                      fullWidth
                      multiline
                      rows={2}
                      disabled={mode === "view"}
                    />
                  </Grid>
                </Grid>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Manufacturing journal records production activities and costs
                </Typography>

                {mode !== "view" && (
                  <Box display="flex" gap={2} mt={3}>
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={createMutation.isPending || updateMutation.isPending}
                    >
                      {mode === "edit" ? "Update" : "Create"} Voucher
                    </Button>
                    {mode !== "create" && (
                      <Button variant="outlined" onClick={handleCancel}>
                        Cancel
                      </Button>
                    )}
                  </Box>
                )}
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};