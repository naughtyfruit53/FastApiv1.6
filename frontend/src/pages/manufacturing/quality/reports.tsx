import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, TextField, MenuItem } from '@mui/material';
import { BarChart, TrendingUp, Assessment, Download, Visibility } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const QualityReportsPage: React.FC = () => {
  const router = useRouter();
  const [reportType, setReportType] = useState('quality-trends');
  const [dateRange, setDateRange] = useState('last-30-days');

  // Fetch quality reports
  const { data: reportData, isLoading } = useQuery({
    queryKey: ['quality-reports', reportType, dateRange],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/quality-reports?type=${reportType}&range=${dateRange}`);
      return response.data;
    },
    enabled: true,
  });

  const handleViewInspection = (id: number) => {
    router.push(`/manufacturing/quality/inspection/${id}`);
  };

  const handleExportReport = () => {
    // Export logic to be implemented
    console.log('Exporting report:', reportType);
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Quality Reports
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Analyze quality metrics and inspection data.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExportReport}
          >
            Export Report
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Quality Reports provide insights into quality trends, rejection rates,
          and inspection performance across your manufacturing operations.
        </Alert>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => setReportType('quality-trends')}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <BarChart color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Quality Trends
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track quality metrics over time and identify improvement areas.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => setReportType('rejection-analysis')}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Rejection Analysis
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Analyze rejection patterns and root causes for quality issues.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ cursor: 'pointer' }} onClick={() => setReportType('compliance')}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Assessment color="primary" sx={{ fontSize: 40 }} />
                  <Typography variant="h6">
                    Compliance Reports
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Generate compliance reports for audits and certifications.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  select
                  fullWidth
                  label="Report Type"
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  size="small"
                >
                  <MenuItem value="quality-trends">Quality Trends</MenuItem>
                  <MenuItem value="rejection-analysis">Rejection Analysis</MenuItem>
                  <MenuItem value="compliance">Compliance Reports</MenuItem>
                  <MenuItem value="inspector-performance">Inspector Performance</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  select
                  fullWidth
                  label="Date Range"
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  size="small"
                >
                  <MenuItem value="last-7-days">Last 7 Days</MenuItem>
                  <MenuItem value="last-30-days">Last 30 Days</MenuItem>
                  <MenuItem value="last-90-days">Last 90 Days</MenuItem>
                  <MenuItem value="this-year">This Year</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Report Data Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {reportType === 'quality-trends' ? 'Quality Trends' : 
               reportType === 'rejection-analysis' ? 'Rejection Analysis' : 
               reportType === 'compliance' ? 'Compliance Status' : 'Inspector Performance'}
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date/Period</TableCell>
                    <TableCell>Inspections</TableCell>
                    <TableCell>Pass Rate</TableCell>
                    <TableCell>Reject Rate</TableCell>
                    <TableCell>Defect Type</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : reportData?.items?.length > 0 ? (
                    reportData.items.map((item: any, index: number) => (
                      <TableRow key={index} hover>
                        <TableCell>{item.period || new Date(item.date).toLocaleDateString()}</TableCell>
                        <TableCell>{item.total_inspections || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${item.pass_rate || 0}%`}
                            color="success"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${item.reject_rate || 0}%`}
                            color={item.reject_rate > 10 ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.defect_type || '-'}</TableCell>
                        <TableCell align="right">
                          <IconButton 
                            size="small" 
                            onClick={() => item.inspection_id && handleViewInspection(item.inspection_id)}
                            title="View Details"
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No data available for the selected filters.
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

export default QualityReportsPage;
