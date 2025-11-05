import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip } from '@mui/material';
import { Inventory, CheckCircle, LocalShipping, Add, Visibility, Edit } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const JobworkReceiptPage: React.FC = () => {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const perPage = 10;

  // Fetch jobwork receipts
  const { data: receipts, isLoading } = useQuery({
    queryKey: ['jobwork-receipts', page],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/jobwork-receipts?page=${page}&per_page=${perPage}`);
      return response.data;
    },
    enabled: true,
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/jobwork/receipt/${id}`);
  };

  const handleEdit = (id: number) => {
    router.push(`/manufacturing/jobwork/receipt/edit/${id}`);
  };

  const handleCreate = () => {
    router.push('/manufacturing/jobwork/receipt/create');
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Jobwork Receipt
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Record receipt of finished goods from jobwork processing.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreate}
          >
            Create Receipt
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Jobwork Receipt allows you to record the receipt of processed materials back
          into your inventory. Update stock levels and track quality inspection results.
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Inventory color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Receive Goods
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Record the receipt of finished goods from vendors or delivery of processed goods to customers.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <CheckCircle color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Quality Check
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Perform quality inspection and record acceptance or rejection of received goods.
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
                    Stock Update
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Automatically update inventory levels upon receipt confirmation.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Receipts Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Jobwork Receipts
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Receipt No.</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Challan Ref</TableCell>
                    <TableCell>Party Name</TableCell>
                    <TableCell>Quality Status</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : receipts?.items?.length > 0 ? (
                    receipts.items.map((receipt: any) => (
                      <TableRow key={receipt.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            onClick={() => handleView(receipt.id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {receipt.receipt_number}
                          </Button>
                        </TableCell>
                        <TableCell>{new Date(receipt.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {receipt.challan_ref ? (
                            <Button
                              variant="text"
                              size="small"
                              onClick={() => router.push(`/manufacturing/jobwork/challan/${receipt.challan_id}`)}
                              sx={{ textTransform: 'none' }}
                            >
                              {receipt.challan_ref}
                            </Button>
                          ) : '-'}
                        </TableCell>
                        <TableCell>{receipt.party_name || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={receipt.quality_status || 'Pending'}
                            color={receipt.quality_status === 'passed' ? 'success' : receipt.quality_status === 'failed' ? 'error' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={receipt.status || 'Draft'}
                            color={receipt.status === 'completed' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => handleView(receipt.id)} title="View">
                            <Visibility fontSize="small" />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleEdit(receipt.id)} title="Edit">
                            <Edit fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No receipts found. Click "Create Receipt" to get started.
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
  );
    </ProtectedPage>
  );
};

export default JobworkReceiptPage;
