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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from "@mui/material";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../lib/api";
import { getProducts } from "../../../services/masterService";
import { ProtectedPage } from '../../../components/ProtectedPage';
interface StockJournalEntry {
  product_id: number;
  debit_quantity: number;
  credit_quantity: number;
  unit: string;
  unit_rate: number;
  debit_value: number;
  credit_value: number;
  from_location?: string;
  to_location?: string;
  from_warehouse?: string;
  to_warehouse?: string;
  from_bin?: string;
  to_bin?: string;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  transformation_type?: string;
}
interface StockJournal {
  id?: number;
  voucher_number: string;
  date: string;
  journal_type: string;
  from_location?: string;
  to_location?: string;
  from_warehouse?: string;
  to_warehouse?: string;
  manufacturing_order_id?: number;
  bom_id?: number;
  transfer_reason?: string;
  assembly_product_id?: number;
  assembly_quantity?: number;
  physical_verification_done: boolean;
  verified_by?: string;
  verification_date?: string;
  notes?: string;
  status: string;
  total_amount: number;
  entries: StockJournalEntry[];
}
const defaultValues: Partial<StockJournal> = {
  voucher_number: "",
  date: new Date().toISOString().split("T")[0],
  journal_type: "transfer",
  physical_verification_done: false,
  status: "draft",
  total_amount: 0,
  entries: [],
};

const journalTypeOptions = [
  { value: "transfer", label: "Stock Transfer" },
  { value: "assembly", label: "Assembly" },
  { value: "disassembly", label: "Disassembly" },
  { value: "adjustment", label: "Stock Adjustment" },
  { value: "manufacturing", label: "Manufacturing" },
];

const entryTypeOptions = [
  { value: "consume", label: "Consume" },
  { value: "produce", label: "Produce" },
  { value: "byproduct", label: "Byproduct" },
  { value: "scrap", label: "Scrap" },
];
export default function StockJournal() {
  const [mode, setMode] = useState<"create" | "edit" | "view">("create");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { control, handleSubmit, watch, setValue, reset, formState } =
    useForm<StockJournal>({
      defaultValues,
    });
  const {
    fields: entryFields,
    append: appendEntry,
    remove: removeEntry,
  } = useFieldArray({
    control,
    name: "entries",
  });
  const watchedDate = watch("date");
  // Fetch stock journals list
  const { data: journalList, isLoading } = useQuery({
    queryKey: ["stock-journals"],
    queryFn: () => api.get("/manufacturing/stock-journals").then((res) => res.data),
  });
  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ["manufacturing-orders"],
    queryFn: () => api.get("/manufacturing/manufacturing-orders").then((res) => res.data),
  });
  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ["boms"],
    queryFn: () => api.get("/manufacturing/boms").then((res) => res.data),
  });
  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });
  // Fetch specific journal
  const { data: journalData } = useQuery({
    queryKey: ["stock-journal", selectedId],
    queryFn: () =>
      api.get(`/manufacturing/stock-journals/${selectedId}`).then((res) => res.data),
    enabled: !!selectedId,
  });
  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ["nextStockJournalNumber"],
    queryFn: () =>
      api.get("/manufacturing/stock-journals/next-number").then((res) => res.data),
    enabled: mode === "create",
  });
  const sortedJournals = journalList
    ? [...journalList].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
    : [];
  useEffect(() => {
    if (mode === "create" && nextVoucherNumber) {
      setValue("voucher_number", nextVoucherNumber);
    } else if (journalData) {
      reset(journalData);
    } else if (mode === "create") {
      reset(defaultValues);
    }
  }, [journalData, mode, reset, nextVoucherNumber, setValue]);
  // Calculate totals
  useEffect(() => {
    const entries = watch("entries") || [];
    const total = entries.reduce(
      (sum, entry) =>
        sum + (entry.debit_value || 0) - (entry.credit_value || 0),
      0,
    );
    setValue("total_amount", total);
  }, [watch("entries"), setValue]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      if (watchedDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await api.get(
            `/manufacturing/stock-journals/next-number?voucher_date=${watchedDate}`
          );
          setValue('voucher_number', response.data);
          
          // Check for backdated conflicts
          const conflictResponse = await api.get(
            `/manufacturing/stock-journals/check-backdated-conflict?voucher_date=${watchedDate}`
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
    mutationFn: (data: StockJournal) => api.post("/manufacturing/stock-journals", data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ["stock-journals"] });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue("voucher_number", newNextNumber);
    },
    onError: (error: any) => {
      console.error("Error creating journal:", error);
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: StockJournal }) =>
      api.put(`/manufacturing/stock-journals/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock-journals"] });
      setMode("create");
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error("Error updating journal:", error);
    },
  });
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/manufacturing/stock-journals/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stock-journals"] });
      if (selectedId) {
        setSelectedId(null);
        setMode("create");
        reset(defaultValues);
      }
    },
  });
  const onSubmit = (data: StockJournal) => {
    if (mode === "edit" && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };
  const handleEdit = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode("edit");
  };
  const handleView = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode("view");
  };
  const handleDelete = (journalId: number) => {
    if (window.confirm("Are you sure you want to delete this journal?")) {
      deleteMutation.mutate(journalId);
    }
  };
  const handleCancel = () => {
    setMode("create");
    setSelectedId(null);
    reset(defaultValues);
  };
  const addEntry = () => {
    appendEntry({
      product_id: 0,
      debit_quantity: 0,
      credit_quantity: 0,
      unit: "",
      unit_rate: 0,
      debit_value: 0,
      credit_value: 0,
    });
  };
  const updateEntryValues = (index: number) => {
    const entries = watch("entries");
    const entry = entries[index];
    if (entry) {
      const debitValue = entry.debit_quantity * entry.unit_rate;
      const creditValue = entry.credit_quantity * entry.unit_rate;
      setValue(`entries.${index}.debit_value`, debitValue);
      setValue(`entries.${index}.credit_value`, creditValue);
    }
  };
  const getJournalTypeIcon = (type: string) => {
    const colors = {
      transfer: "primary",
      assembly: "success",
      disassembly: "warning",
      adjustment: "info",
      manufacturing: "secondary",
    };
    return colors[type] || "default";
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
      <ProtectedPage moduleKey="manufacturing" action="write">
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
      </ProtectedPage>
    );
  }
  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="xl">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Stock Journals
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage stock movements, transfers, and adjustments
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {/* Journal List - Left Side */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                mb={2}
              >
                <Typography variant="h6">Recent Journals</Typography>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => {
                    setMode("create");
                    reset(defaultValues);
                  }}
                  disabled={mode === "create"}
                >
                  New Journal
                </Button>
              </Box>
              <Box sx={{ maxHeight: "600px", overflowY: "auto" }}>
                {sortedJournals.slice(0, 10).map((journal: any) => (
                  <Card
                    key={journal.id}
                    variant="outlined"
                    sx={{
                      mb: 1,
                      cursor: "pointer",
                      "&:hover": { bgcolor: "action.hover" },
                    }}
                    onClick={() => handleView(journal)}
                  >
                    <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle2">
                            {journal.voucher_number}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(journal.date).toLocaleDateString()} • {journal.journal_type}
                          </Typography>
                        </Box>
                        <Chip
                          label={journal.status}
                          size="small"
                          color={getJournalTypeIcon(journal.journal_type) as any}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Journal Form - Right Side */}
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
                  {mode === "create" && "Create Stock Journal"}
                  {mode === "edit" && "Edit Stock Journal"}
                  {mode === "view" && "View Stock Journal"}
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
                    <FormControl fullWidth>
                      <InputLabel>Journal Type</InputLabel>
                      <Select
                        value={watch("journal_type")}
                        onChange={(e) => setValue("journal_type", e.target.value)}
                        disabled={mode === "view"}
                      >
                        {journalTypeOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField
                      label="Notes"
                      {...control.register("notes")}
                      fullWidth
                      multiline
                      rows={2}
                      disabled={mode === "view"}
                    />
                  </Grid>
                </Grid>

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Journal Entries</Typography>
                  {mode !== "view" && (
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={addEntry}
                    >
                      Add Entry
                    </Button>
                  )}
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Add stock entries with debits (stock in) and credits (stock out)
                </Typography>

                {mode !== "view" && (
                  <Box display="flex" gap={2} mt={3}>
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={createMutation.isPending || updateMutation.isPending}
                    >
                      {mode === "edit" ? "Update" : "Create"} Journal
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
    </ProtectedPage>
  );
}