import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useForm, useFieldArray } from 'react-hook-form';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Grid, 
  IconButton, 
  Alert, 
  CircularProgress, 
  Container, 
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
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

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
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  journal_type: 'transfer',
  physical_verification_done: false,
  status: 'draft',
  total_amount: 0,
  entries: []
};

const journalTypeOptions = [
  { value: 'transfer', label: 'Stock Transfer' },
  { value: 'assembly', label: 'Assembly' },
  { value: 'disassembly', label: 'Disassembly' },
  { value: 'adjustment', label: 'Stock Adjustment' },
  { value: 'manufacturing', label: 'Manufacturing' }
];

const transformationTypeOptions = [
  { value: 'consume', label: 'Consume' },
  { value: 'produce', label: 'Produce' },
  { value: 'byproduct', label: 'Byproduct' },
  { value: 'scrap', label: 'Scrap' }
];

export default function StockJournal() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<StockJournal>({
    defaultValues
  });

  const {
    fields: entryFields,
    append: appendEntry,
    remove: removeEntry
  } = useFieldArray({
    control,
    name: 'entries'
  });

  // Fetch stock journals list
  const { data: journalList, isLoading } = useQuery({
    queryKey: ['stock-journals'],
    queryFn: () => api.get('/stock-journals').then(res => res.data),
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/boms').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific journal
  const { data: journalData, isFetching } = useQuery({
    queryKey: ['stock-journal', selectedId],
    queryFn: () => api.get(`/stock-journals/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextStockJournalNumber'],
    queryFn: () => api.get('/stock-journals/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedJournals = journalList ? [...journalList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestJournals = sortedJournals.slice(0, 10);
  const productOptions = productList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];
  const bomOptions = bomList || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (journalData) {
      reset(journalData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [journalData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const entries = watch('entries') || [];
    const total = entries.reduce((sum, entry) => 
      sum + (entry.debit_value || 0) - (entry.credit_value || 0), 0);
    setValue('total_amount', total);
  }, [watch('entries'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: StockJournal) => api.post('/stock-journals', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating stock journal:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: StockJournal }) => 
      api.put(`/stock-journals/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating stock journal:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/stock-journals/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-journals'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: StockJournal) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode('edit');
  };

  const handleView = (journal: StockJournal) => {
    setSelectedId(journal.id!);
    setMode('view');
  };

  const handleDelete = (journalId: number) => {
    if (window.confirm('Are you sure you want to delete this journal?')) {
      deleteMutation.mutate(journalId);
    }
  };

  const handleCancel = () => {
    setMode('create');
    setSelectedId(null);
    reset(defaultValues);
  };

  const addEntry = () => {
    appendEntry({
      product_id: 0,
      debit_quantity: 0,
      credit_quantity: 0,
      unit: '',
      unit_rate: 0,
      debit_value: 0,
      credit_value: 0
    });
  };

  const updateEntryValues = (index: number) => {
    const entries = watch('entries');
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
      transfer: 'primary',
      assembly: 'success',
      disassembly: 'warning',
      adjustment: 'info',
      manufacturing: 'secondary'
    };
    return colors[type] || 'default';
  };

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" component="h1" gutterBottom>
        Stock Journals
      </Typography>

      <Grid container spacing={3}>
        {/* Journal List - Left Side */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Journals</Typography>
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}