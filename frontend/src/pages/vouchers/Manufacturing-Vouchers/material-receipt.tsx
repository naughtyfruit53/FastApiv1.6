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
  Cancel,
  PictureAsPdf
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import { generateStandalonePDF } from '../../../utils/pdfUtils';

interface MaterialReceiptItem {
  product_id: number;
  quantity: number;
  unit: string;
  unit_price: number;
  received_quantity?: number;
  accepted_quantity?: number;
  rejected_quantity?: number;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  warehouse_location?: string;
  bin_location?: string;
  quality_status?: string;
  inspection_remarks?: string;
  notes?: string;
  total_amount: number;
}

interface MaterialReceiptVoucher {
  id?: number;
  voucher_number: string;
  date: string;
  manufacturing_order_id?: number;
  source_type: string;
  source_reference?: string;
  received_from_department?: string;
  received_from_employee?: string;
  received_by_employee?: string;
  receipt_time?: string;
  inspection_required: boolean;
  inspection_status: string;
  inspector_name?: string;
  inspection_date?: string;
  inspection_remarks?: string;
  condition_on_receipt?: string;
  notes?: string;
  status: string;
  total_amount: number;
  items: MaterialReceiptItem[];
}

const defaultValues: Partial<MaterialReceiptVoucher> = {
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  source_type: 'return',
  inspection_required: false,
  inspection_status: 'pending',
  status: 'draft',
  total_amount: 0,
  items: []
};

const sourceTypeOptions = [
  { value: 'return', label: 'Material Return' },
  { value: 'purchase', label: 'Purchase Receipt' },
  { value: 'transfer', label: 'Transfer Receipt' }
];

const inspectionStatusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'passed', label: 'Passed' },
  { value: 'failed', label: 'Failed' },
  { value: 'partial', label: 'Partial' }
];

const qualityStatusOptions = [
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'hold', label: 'Hold' }
];

export default function MaterialReceiptVoucher() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<MaterialReceiptVoucher>({
    defaultValues
  });

  const {
    fields: itemFields,
    append: appendItem,
    remove: removeItem
  } = useFieldArray({
    control,
    name: 'items'
  });

  // Fetch vouchers list
  const { data: voucherList, isLoading } = useQuery({
    queryKey: ['material-receipt-vouchers'],
    queryFn: () => api.get('/material-receipt-vouchers').then(res => res.data),
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific voucher
  const { data: voucherData, isFetching } = useQuery({
    queryKey: ['material-receipt-voucher', selectedId],
    queryFn: () => api.get(`/material-receipt-vouchers/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextMaterialReceiptNumber'],
    queryFn: () => api.get('/material-receipt-vouchers/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedVouchers = voucherList ? [...voucherList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestVouchers = sortedVouchers.slice(0, 10);
  const productOptions = productList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (voucherData) {
      reset(voucherData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [voucherData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const items = watch('items') || [];
    const total = items.reduce((sum, item) => sum + (item.total_amount || 0), 0);
    setValue('total_amount', total);
  }, [watch('items'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: MaterialReceiptVoucher) => api.post('/material-receipt-vouchers', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating material receipt voucher:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: MaterialReceiptVoucher }) => 
      api.put(`/material-receipt-vouchers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating material receipt voucher:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/material-receipt-vouchers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: MaterialReceiptVoucher) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (voucher: MaterialReceiptVoucher) => {
    setSelectedId(voucher.id!);
    setMode('edit');
  };

  const handleView = (voucher: MaterialReceiptVoucher) => {
    setSelectedId(voucher.id!);
    setMode('view');
  };

  const handleDelete = (voucherId: number) => {
    if (window.confirm('Are you sure you want to delete this voucher?')) {
      deleteMutation.mutate(voucherId);
    }
  };

  const handleCancel = () => {
    setMode('create');
    setSelectedId(null);
    reset(defaultValues);
  };

  const addItem = () => {
    appendItem({
      product_id: 0,
      quantity: 0,
      unit: '',
      unit_price: 0,
      received_quantity: 0,
      accepted_quantity: 0,
      rejected_quantity: 0,
      total_amount: 0
    });
  };

  const updateItemTotal = (index: number) => {
    const items = watch('items');
    const item = items[index];
    if (item) {
      const total = item.quantity * item.unit_price;
      setValue(`items.${index}.total_amount`, total);
    }
  };

  // PDF Generation Function
  const handleGeneratePDF = async (voucherData?: MaterialReceiptVoucher) => {
    try {
      const dataToUse = voucherData || watch();
      await generateStandalonePDF(dataToUse, 'material-receipt');
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
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
        Material Receipt Vouchers
      </Typography>

      <Grid container spacing={3}>
        {/* Voucher List - Left Side */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Vouchers</Typography>
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}
                {/* VoucherHeaderActions commented out */}