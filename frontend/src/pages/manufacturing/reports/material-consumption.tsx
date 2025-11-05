import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, TextField, MenuItem } from '@mui/material';
import { BarChart, Inventory, TrendingDown, Download, Visibility } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const MaterialConsumptionPage: React.FC = () => {
  const router = useRouter();
  const [dateRange, setDateRange] = useState('this-month');
  const [materialFilter, setMaterialFilter] = useState('all');

  // Fetch material consumption data
  const { data: consumptionData, isLoading } = useQuery({
    queryKey: ['material-consumption', dateRange, materialFilter],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/material-consumption?range=${dateRange}&material=${materialFilter}`);
      return response.data;
    },
    enabled: true,
  });

  const handleViewMaterial = (id: number) => {
    router.push(`/products/${id}`);
  };

  const handleViewOrder = (id: number) => {
    router.push(`/manufacturing/production-order/${id}`);
  };

  const handleExport = () => {
    console.log('Exporting material consumption report');
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Material Consumption Report
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track and analyze material usage in manufacturing processes.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Export Report
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Material Consumption Report helps you monitor material usage patterns,
          identify waste, and optimize inventory planning for production.
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <BarChart color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Total Consumption
                  </Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {consumptionData?.total_consumed || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Units consumed {dateRange.replace('-', ' ')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Inventory color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    BOM Variance
                  </Typography>
                </Box>
                <Typography variant="h4" color={consumptionData?.variance >= 0 ? 'error.main' : 'success.main'}>
                  {consumptionData?.variance >= 0 ? '+' : ''}{consumptionData?.variance || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Vs. BOM standard consumption
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingDown color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Waste Percentage
                  </Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  {consumptionData?.waste_percentage || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Material waste this period
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
                  label="Material Type"
                  value={materialFilter}
                  onChange={(e) => setMaterialFilter(e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Materials</MenuItem>
                  <MenuItem value="raw-materials">Raw Materials</MenuItem>
                  <MenuItem value="components">Components</MenuItem>
                  <MenuItem value="consumables">Consumables</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Consumption Details Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Material Consumption Details
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Material</TableCell>
                    <TableCell>Production Order</TableCell>
                    <TableCell>Standard Qty</TableCell>
                    <TableCell>Actual Qty</TableCell>
                    <TableCell>Variance</TableCell>
                    <TableCell>Unit Cost</TableCell>
                    <TableCell>Total Cost</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : consumptionData?.items?.length > 0 ? (
                    consumptionData.items.map((item: any) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            onClick={() => handleViewMaterial(item.material_id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {item.material_name}
                          </Button>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            onClick={() => handleViewOrder(item.order_id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {item.order_number}
                          </Button>
                        </TableCell>
                        <TableCell>{item.standard_quantity || 0}</TableCell>
                        <TableCell>{item.actual_quantity || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${item.variance >= 0 ? '+' : ''}${item.variance || 0}%`}
                            color={Math.abs(item.variance) > 5 ? 'error' : 'success'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.unit_cost ? `₹${item.unit_cost.toFixed(2)}` : '-'}</TableCell>
                        <TableCell>{item.total_cost ? `₹${item.total_cost.toFixed(2)}` : '-'}</TableCell>
                        <TableCell align="right">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewMaterial(item.material_id)}
                            title="View Material"
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No consumption data available for the selected period.
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

export default MaterialConsumptionPage;
