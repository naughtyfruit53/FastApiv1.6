// Standalone Customers Page - Extract from masters/index.tsx
import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Email,
  Phone,
  Person,
  Visibility,
  Analytics
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { masterDataService } from '../../services/authService';
import ExcelImportExport from '../../components/ExcelImportExport';
import { bulkImportCustomers } from '../../services/masterService';
import Grid from '@mui/material/Grid';
import { useAuth } from '../../context/AuthContext';
import AddCustomerModal from '../../components/AddCustomerModal';
import CustomerAnalyticsModal from '../../components/CustomerAnalyticsModal';

const CustomersPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isOrgContextReady } = useAuth();
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [addCustomerLoading, setAddCustomerLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [analyticsModal, setAnalyticsModal] = useState<{
    open: boolean;
    customerId?: number;
    customerName?: string;
  }>({ open: false });
  const queryClient = useQueryClient();

  const { data: customers, isLoading: customersLoading } = useQuery({
    queryKey: ['customers'],
    queryFn: () => masterDataService.getCustomers(),
    enabled: isOrgContextReady,
  });

  const handleCustomerAdd = async (customerData: any) => {
    setAddCustomerLoading(true);
    try {
      const response = await masterDataService.createCustomer(customerData);
      const newCustomer = response;
      
      // Update query data immediately
      queryClient.setQueryData(['customers'], (old: any) => old ? [...old, newCustomer] : [newCustomer]);
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      
      setShowAddCustomerModal(false);
      alert('Customer added successfully!');
    } catch (error: any) {
      console.error('Error adding customer:', error);
      let errorMsg = 'Error adding customer';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((err: any) => err.msg || err).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        }
      }
      setErrorMessage(errorMsg);
    } finally {
      setAddCustomerLoading(false);
    }
  };

  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteCustomer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
    onError: (error: any) => {
      console.error('Error deleting customer:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to delete customer');
    }
  });

  const openAddCustomerModal = useCallback(() => {
    setErrorMessage('');
    setShowAddCustomerModal(true);
  }, []);

  // Auto-open add modal if action=add in URL
  React.useEffect(() => {
    if (action === 'add') {
      openAddCustomerModal();
    }
  }, [action, openAddCustomerModal]);

  if (!isOrgContextReady) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Customer Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openAddCustomerModal}
            sx={{ ml: 2 }}
          >
            Add Customer
          </Button>
        </Box>

        {/* Customers Table */}
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">All Customers</Typography>
            <ExcelImportExport
              data={customers || []}
              entity="Customers"
              onImport={bulkImportCustomers}
            />
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>GST Number</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customers?.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {item.address1}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Phone sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                        {item.contact_number}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Email sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                        {item.email || 'N/A'}
                      </Box>
                    </TableCell>
                    <TableCell>{item.city}, {item.state}</TableCell>
                    <TableCell>{item.gst_number || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.is_active ? 'Active' : 'Inactive'}
                        color={item.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        size="small" 
                        title="View Analytics"
                        onClick={() => setAnalyticsModal({
                          open: true,
                          customerId: item.id,
                          customerName: item.name
                        })}
                        color="info"
                      >
                        <Analytics />
                      </IconButton>
                      <IconButton disabled size="small" title="Edit functionality temporarily disabled">
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => deleteItemMutation.mutate(item.id)} size="small" color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Add Customer Modal */}
        <AddCustomerModal
          open={showAddCustomerModal}
          onClose={() => setShowAddCustomerModal(false)}
          onAdd={handleCustomerAdd}
          loading={addCustomerLoading}
        />

        {/* Customer Analytics Modal */}
        {analyticsModal.customerId && (
          <CustomerAnalyticsModal
            open={analyticsModal.open}
            onClose={() => setAnalyticsModal({ open: false })}
            customerId={analyticsModal.customerId}
            customerName={analyticsModal.customerName}
          />
        )}
      </Box>
    </Container>
  );
};

export default CustomersPage;