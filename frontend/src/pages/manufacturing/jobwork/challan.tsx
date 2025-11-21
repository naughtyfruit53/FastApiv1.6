import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip } from '@mui/material';
import { ReceiptLong, LocalShipping, Description, Add, Visibility, Edit } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const JobworkChallanPage: React.FC = () => {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const perPage = 10;

  // Fetch jobwork challans
  const { data: challans, isLoading } = useQuery({
    queryKey: ['jobwork-challans', page],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/jobwork-challans?page=${page}&per_page=${perPage}`);
      return response.data;
    },
    enabled: true,
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/jobwork/challan/${id}`);
  };

  const handleEdit = (id: number) => {
    router.push(`/manufacturing/jobwork/challan/edit/${id}`);
  };

  const handleCreate = () => {
    router.push('/manufacturing/jobwork/challan/create');
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Jobwork Challan
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Generate and manage delivery challans for jobwork materials.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreate}
          >
            Create Challan
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Jobwork Challan feature allows you to create delivery documents for materials
          sent out for jobwork or received from customers. This ensures proper tracking
          and compliance.
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <ReceiptLong color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Delivery Challan
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Create delivery challans for materials sent to vendors or customers for jobwork processing.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <LocalShipping color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Material Tracking
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track materials sent out and received back with proper documentation and audit trail.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Description color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Compliance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Generate GST-compliant delivery challans as per statutory requirements.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Challans Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Jobwork Challans
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Challan No.</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Party Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : challans?.items?.length > 0 ? (
                    challans.items.map((challan: any) => (
                      <TableRow key={challan.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            onClick={() => handleView(challan.id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {challan.challan_number}
                          </Button>
                        </TableCell>
                        <TableCell>{new Date(challan.date).toLocaleDateString()}</TableCell>
                        <TableCell>{challan.party_name || '-'}</TableCell>
                        <TableCell>{challan.challan_type || 'Delivery'}</TableCell>
                        <TableCell>
                          <Chip
                            label={challan.status || 'Draft'}
                            color={challan.status === 'approved' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => handleView(challan.id)} title="View">
                            <Visibility fontSize="small" />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleEdit(challan.id)} title="Edit">
                            <Edit fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No challans found. Click "Create Challan" to get started.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Box>
    </Container>
    </ProtectedPage>
  );
};

export default JobworkChallanPage;
