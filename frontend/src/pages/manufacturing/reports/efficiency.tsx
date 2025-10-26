import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, TextField, MenuItem, LinearProgress } from '@mui/material';
import { TrendingUp, Speed, Timer, Download, Visibility } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';

const ManufacturingEfficiencyPage: React.FC = () => {
  const router = useRouter();
  const [dateRange, setDateRange] = useState('this-month');
  const [machineFilter, setMachineFilter] = useState('all');

  // Fetch efficiency data
  const { data: efficiencyData, isLoading } = useQuery({
    queryKey: ['manufacturing-efficiency', dateRange, machineFilter],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/efficiency-report?range=${dateRange}&machine=${machineFilter}`);
      return response.data;
    },
    enabled: true,
  });

  const handleViewMachine = (id: number) => {
    router.push(`/manufacturing/machines/${id}`);
  };

  const handleViewOrder = (id: number) => {
    router.push(`/manufacturing/production-order/${id}`);
  };

  const handleExport = () => {
    console.log('Exporting efficiency report');
  };

  const getOEEColor = (oee: number) => {
    if (oee >= 85) return 'success';
    if (oee >= 60) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Manufacturing Efficiency Report
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Monitor and analyze manufacturing efficiency metrics.
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
          Manufacturing Efficiency Report provides insights into productivity,
          cycle times, and overall equipment effectiveness (OEE).
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Average OEE
                  </Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {efficiencyData?.average_oee || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overall equipment effectiveness
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={efficiencyData?.average_oee || 0} 
                  sx={{ mt: 2 }}
                  color={getOEEColor(efficiencyData?.average_oee || 0) as any}
                />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Speed color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Throughput Rate
                  </Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {efficiencyData?.throughput_rate || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Units per hour average
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Timer color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Average Cycle Time
                  </Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  {efficiencyData?.average_cycle_time || 0} min
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Per unit production time
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
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Machine/Line"
                  value={machineFilter}
                  onChange={(e) => setMachineFilter(e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Machines</MenuItem>
                  <MenuItem value="line-1">Production Line 1</MenuItem>
                  <MenuItem value="line-2">Production Line 2</MenuItem>
                  <MenuItem value="assembly">Assembly</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Efficiency Details Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detailed Efficiency Metrics
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Machine/Line</TableCell>
                    <TableCell>Production Order</TableCell>
                    <TableCell>OEE %</TableCell>
                    <TableCell>Availability %</TableCell>
                    <TableCell>Performance %</TableCell>
                    <TableCell>Quality %</TableCell>
                    <TableCell>Downtime (hrs)</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : efficiencyData?.items?.length > 0 ? (
                    efficiencyData.items.map((item: any) => (
                      <TableRow key={item.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            size="small"
                            onClick={() => item.machine_id && handleViewMachine(item.machine_id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {item.machine_name}
                          </Button>
                        </TableCell>
                        <TableCell>
                          {item.order_number ? (
                            <Button
                              variant="text"
                              size="small"
                              onClick={() => handleViewOrder(item.order_id)}
                              sx={{ textTransform: 'none' }}
                            >
                              {item.order_number}
                            </Button>
                          ) : '-'}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${item.oee || 0}%`}
                            color={getOEEColor(item.oee || 0) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.availability || 0}%</TableCell>
                        <TableCell>{item.performance || 0}%</TableCell>
                        <TableCell>{item.quality || 0}%</TableCell>
                        <TableCell>{item.downtime_hours || 0}</TableCell>
                        <TableCell align="right">
                          <IconButton 
                            size="small" 
                            onClick={() => item.machine_id && handleViewMachine(item.machine_id)}
                            title="View Details"
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No efficiency data available for the selected period.
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
};

export default ManufacturingEfficiencyPage;
