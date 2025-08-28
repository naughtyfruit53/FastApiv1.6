'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import AddCustomerModal from '../../components/AddCustomerModal';

interface Customer {
  id: number;
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  status: 'active' | 'inactive' | 'prospect';
  created_at: string;
}

const SalesCustomerDatabase: React.FC = () => {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [addCustomerModalOpen, setAddCustomerModalOpen] = useState(false);

  // Mock data - in production this would link to master customers
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData: Customer[] = [
          {
            id: 1,
            name: 'TechCorp Ltd',
            contact_person: 'John Smith',
            email: 'john.smith@techcorp.com',
            phone: '+1-555-0123',
            address: '123 Tech Street',
            city: 'San Francisco',
            state: 'CA',
            status: 'active',
            created_at: '2022-03-10'
          },
          {
            id: 2,
            name: 'Global Systems Inc',
            contact_person: 'Mike Wilson',
            email: 'mike.wilson@globalsystems.com',
            phone: '+1-555-0124',
            address: '456 Business Ave',
            city: 'New York',
            state: 'NY',
            status: 'active',
            created_at: '2021-07-15'
          },
          {
            id: 3,
            name: 'Manufacturing Co',
            contact_person: 'Lisa Davis',
            email: 'lisa.davis@manufacturing.com',
            phone: '+1-555-0125',
            address: '789 Industrial Blvd',
            city: 'Detroit',
            state: 'MI',
            status: 'prospect',
            created_at: '2024-01-10'
          }
        ];
        
        setCustomers(mockData);
      } catch (err) {
        setError('Failed to load customers');
        console.error('Error fetching customers:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.contact_person.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'prospect': return 'primary';
      case 'inactive': return 'default';
      default: return 'default';
    }
  };

  const handleGoToMasterCustomers = () => {
    router.push('/customers');
  };

  const handleAddCustomer = async (customerData: any) => {
    try {
      // Here you would call the customer creation API
      console.log('Adding customer:', customerData);
      // Refresh the customers list after adding
      setAddCustomerModalOpen(false);
    } catch (error) {
      console.error('Error adding customer:', error);
      throw error; // Let the modal handle the error
    }
  };

  const handleViewCustomerAnalytics = (customerId: number) => {
    router.push(`/analytics/customer?id=${customerId}`);
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Customer Database
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Customers
              </Typography>
              <Typography variant="h4">
                {customers.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Customers
              </Typography>
              <Typography variant="h4" color="success.main">
                {customers.filter(c => c.status === 'active').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Prospects
              </Typography>
              <Typography variant="h4" color="primary.main">
                {customers.filter(c => c.status === 'prospect').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                This Month
              </Typography>
              <Typography variant="h4">
                {customers.filter(c => new Date(c.created_at).getMonth() === new Date().getMonth()).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                New customers
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <TextField
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => router.push('/sales/customer-analytics')}
          >
            View Analytics
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleGoToMasterCustomers}
          >
            Add Customer
          </Button>
        </Box>
      </Box>

      {/* Customers Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Customer Name</TableCell>
              <TableCell>Contact Person</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Customer Since</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredCustomers.map((customer) => (
              <TableRow key={customer.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle2">
                      {customer.name}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{customer.contact_person}</TableCell>
                <TableCell>{customer.email}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>
                  {customer.city}, {customer.state}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={customer.status}
                    color={getStatusColor(customer.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(customer.created_at).toLocaleDateString()}</TableCell>
                <TableCell align="center">
                  <Tooltip title="View Details">
                    <IconButton 
                      size="small" 
                      onClick={() => router.push(`/customers?action=view&id=${customer.id}`)}
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit Customer">
                    <IconButton 
                      size="small" 
                      onClick={() => router.push(`/customers?action=edit&id=${customer.id}`)}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Customer Analytics">
                    <IconButton 
                      size="small" 
                      onClick={() => handleViewCustomerAnalytics(customer.id)}
                    >
                      <AnalyticsIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Integration Footer */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="body2" color="textSecondary">
          <strong>Note:</strong> This customer database is integrated with the Master Data management system. 
          All customer records are synchronized and any changes made here will be reflected in master data and vice versa.
        </Typography>
      </Box>
    </Container>
  );
};

export default SalesCustomerDatabase;