import React from 'react';
import { Container, Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Breadcrumbs, Link, Card, CardContent, Alert } from '@mui/material';
import { Warning, Visibility, Edit, ArrowBack, Add } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const NonConformancePage: React.FC = () => {
  const router = useRouter();

  // Fetch failed/rejected inspections
  const { data: inspections, isLoading } = useQuery({
    queryKey: ['qc-inspections-non-conforming'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/inspections?overall_status=fail');
      return response.data;
    },
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/quality/inspection/${id}`);
  };

  const handleCreateCorrectiveAction = (inspectionId: number) => {
    router.push(`/manufacturing/quality/non-conformance/${inspectionId}/corrective-action`);
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
      <Container maxWidth="xl">
        <Box sx={{ mt: 3 }}>
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link component={NextLink} href="/manufacturing/quality/inspection" color="inherit">
              Quality Inspection
            </Link>
            <Typography color="text.primary">Non-Conformance</Typography>
          </Breadcrumbs>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton onClick={() => router.push('/manufacturing/quality/inspection')}>
                <ArrowBack />
              </IconButton>
              <Box>
                <Typography variant="h4" component="h1" gutterBottom>
                  Non-Conformance
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Track and manage non-conformance issues and corrective actions.
                </Typography>
              </Box>
            </Box>
          </Box>

          <Alert 
            severity="error" 
            icon={<Warning />} 
            sx={{ mb: 3 }}
          >
            This page shows all inspections that have failed quality checks and require corrective action.
          </Alert>

          <Card>
            <CardContent>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Inspection No.</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Product/Batch</TableCell>
                      <TableCell>Inspector</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Defects</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">Loading...</TableCell>
                      </TableRow>
                    ) : inspections?.length > 0 ? (
                      inspections.map((inspection: any) => (
                        <TableRow 
                          key={inspection.id} 
                          hover 
                          sx={{ 
                            backgroundColor: 'error.50',
                            '&:hover': { backgroundColor: 'error.100' }
                          }}
                        >
                          <TableCell>
                            <Button
                              variant="text"
                              onClick={() => handleView(inspection.id)}
                              sx={{ textTransform: 'none', color: 'error.main' }}
                            >
                              {inspection.inspection_number}
                            </Button>
                          </TableCell>
                          <TableCell>{inspection.date ? new Date(inspection.date).toLocaleDateString() : '-'}</TableCell>
                          <TableCell>{inspection.product_name || inspection.batch_number || '-'}</TableCell>
                          <TableCell>{inspection.inspector_name || '-'}</TableCell>
                          <TableCell>
                            <Chip label="Failed" color="error" size="small" />
                          </TableCell>
                          <TableCell>
                            {inspection.defect_count || 0} defects found
                          </TableCell>
                          <TableCell align="right">
                            <IconButton size="small" onClick={() => handleView(inspection.id)} title="View Details">
                              <Visibility fontSize="small" />
                            </IconButton>
                            <IconButton size="small" title="Edit">
                              <Edit fontSize="small" />
                            </IconButton>
                            <Button
                              size="small"
                              variant="outlined"
                              color="warning"
                              startIcon={<Add />}
                              onClick={() => handleCreateCorrectiveAction(inspection.id)}
                              sx={{ ml: 1 }}
                            >
                              Action
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          No non-conforming inspections found. All inspections passed quality checks.
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

export default NonConformancePage;
