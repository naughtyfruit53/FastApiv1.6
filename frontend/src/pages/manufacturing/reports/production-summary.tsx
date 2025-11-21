import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, TextField, MenuItem } from '@mui/material';
import { Assessment, TrendingUp, Build, Download, Visibility } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const ProductionSummaryPage: React.FC = () => {
  const router = useRouter();
  const [dateRange, setDateRange] = useState('this-month');
  const [productFilter, setProductFilter] = useState('all');

  // Fetch production summary
  const { data: summaryData, isLoading } = useQuery({
    queryKey: ['production-summary', dateRange, productFilter],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/production-summary?range=${dateRange}&product=${productFilter}`);
      return response.data;
    },
    enabled: true,
  });

  const handleViewOrder = (id: number) => {
    router.push(`/manufacturing/production-order/${id}`);
  };

  const handleViewProduct = (id: number) => {
    router.push(`/products/${id}`);
  };

  const handleExport = () => {
    // Export logic to be implemented
    console.log('Exporting production summary');
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Production Summary
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Overview of production activities and performance metrics.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Export Summary
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Production Summary provides a comprehensive view of your manufacturing
          operations, including production volumes, efficiency, and capacity utilization.
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Assessment color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Production Volume
                  </Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {summaryData?.total_production || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Units produced {dateRange.replace('-', ' ')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Efficiency Rate
                  </Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {summaryData?.efficiency_rate || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overall production efficiency
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Build color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Capacity Utilization
                  </Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  {summaryData?.capacity_utilization || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Equipment & labor utilization
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Date Range"
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  size="small"
                >
                  <MenuItem value="today">Today</MenuItem>
                  <MenuItem value="this-week">This Week</MenuItem>
                  <MenuItem value="this-month">This Month</MenuItem>
                  <MenuItem value="this-quarter">This Quarter</MenuItem>
                  <MenuItem value="this-year">This Year</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Product Filter"
                  value={productFilter}
                  onChange={(e) => setProductFilter(e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Products</MenuItem>
                  <MenuItem value="finished-goods">Finished Goods</MenuItem>
                  <MenuItem value="semi-finished">Semi-Finished</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Production Details Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Production Details
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order No.</TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell>Planned Qty</TableCell>
                    <TableCell>Produced Qty</TableCell>
                    <TableCell>Completion %</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : summaryData?.items?.length > 0 ? (
                    summaryData.items.map((item: any) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            onClick={() => handleViewOrder(item.order_id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {item.order_number}
                          </Button>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            onClick={() => handleViewProduct(item.product_id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {item.product_name}
                          </Button>
                        </TableCell>
                        <TableCell>{item.planned_quantity || 0}</TableCell>
                        <TableCell>{item.produced_quantity || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${item.completion_percentage || 0}%`}
                            color={item.completion_percentage >= 100 ? 'success' : 'primary'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={item.status || 'In Progress'}
                            color={item.status === 'completed' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewOrder(item.order_id)}
                            title="View Order"
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No production data available for the selected period.
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

export default ProductionSummaryPage;
