// Standalone Vendors Page - Extract from masters/index.tsx
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
  Business,
  Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { masterDataService } from '../../services/authService';
import ExcelImportExport from '../../components/ExcelImportExport';
import { bulkImportVendors } from '../../services/masterService';
import Grid from '@mui/material/Grid';
import { useAuth } from '../../context/AuthContext';
import AddVendorModal from '../../components/AddVendorModal';

const VendorsPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isOrgContextReady } = useAuth();
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: vendors, isLoading: vendorsLoading } = useQuery({
    queryKey: ['vendors'],
    queryFn: () => masterDataService.getVendors(),
    enabled: isOrgContextReady,
  });

  const handleVendorAdd = async (vendorData: any) => {
    setAddVendorLoading(true);
    try {
      const response = await masterDataService.createVendor(vendorData);
      const newVendor = response;
      
      // Update query data immediately
      queryClient.setQueryData(['vendors'], (old: any) => old ? [...old, newVendor] : [newVendor]);
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      
      setShowAddVendorModal(false);
      alert('Vendor added successfully!');
    } catch (error: any) {
      console.error('Error adding vendor:', error);
      let errorMsg = 'Error adding vendor';
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
      setAddVendorLoading(false);
    }
  };

  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteVendor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
    },
    onError: (error: any) => {
      console.error('Error deleting vendor:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to delete vendor');
    }
  });

  const openAddVendorModal = useCallback(() => {
    setErrorMessage('');
    setShowAddVendorModal(true);
  }, []);

  // Auto-open add modal if action=add in URL
  React.useEffect(() => {
    if (action === 'add') {
      openAddVendorModal();
    }
  }, [action, openAddVendorModal]);

  if (!isOrgContextReady) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Vendor Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openAddVendorModal}
            sx={{ ml: 2 }}
          >
            Add Vendor
          </Button>
        </Box>

        {/* Vendors Table */}
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">All Vendors</Typography>
            <ExcelImportExport
              data={vendors || []}
              entity="Vendors"
              onImport={bulkImportVendors}
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
                {vendors?.map((item: any) => (
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

        {/* Add Vendor Modal */}
        <AddVendorModal
          open={showAddVendorModal}
          onClose={() => setShowAddVendorModal(false)}
          onAdd={handleVendorAdd}
          loading={addVendorLoading}
        />
      </Box>
    </Container>
  );
};

export default VendorsPage;