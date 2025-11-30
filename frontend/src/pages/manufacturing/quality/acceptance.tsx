import React from 'react';
import { Container, Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Breadcrumbs, Link, Card, CardContent, Alert } from '@mui/material';
import { CheckCircle, Visibility, Edit, ArrowBack } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const AcceptancePage: React.FC = () => {
  const router = useRouter();

  // Fetch accepted inspections
  const { data: inspections, isLoading } = useQuery({
    queryKey: ['qc-inspections-accepted'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/inspections?overall_status=pass');
      return response.data;
    },
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/quality/inspection/${id}`);
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
            <Typography color="text.primary">Acceptance</Typography>
          </Breadcrumbs>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton onClick={() => router.push('/manufacturing/quality/inspection')}>
                <ArrowBack />
              </IconButton>
              <Box>
                <Typography variant="h4" component="h1" gutterBottom>
                  Acceptance
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Inspections with status "Passed" - approved batches based on quality standards.
                </Typography>
              </Box>
            </Box>
          </Box>

          <Alert 
            severity="success" 
            icon={<CheckCircle />} 
            sx={{ mb: 3 }}
          >
            This page shows all inspections that have passed quality checks.
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
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">Loading...</TableCell>
                      </TableRow>
                    ) : inspections?.length > 0 ? (
                      inspections.map((inspection: any) => (
                        <TableRow key={inspection.id} hover sx={{ backgroundColor: 'success.50' }}>
                          <TableCell>
                            <Button
                              variant="text"
                              onClick={() => handleView(inspection.id)}
                              sx={{ textTransform: 'none' }}
                            >
                              {inspection.inspection_number}
                            </Button>
                          </TableCell>
                          <TableCell>{inspection.date ? new Date(inspection.date).toLocaleDateString() : '-'}</TableCell>
                          <TableCell>{inspection.product_name || inspection.batch_number || '-'}</TableCell>
                          <TableCell>{inspection.inspector_name || '-'}</TableCell>
                          <TableCell>
                            <Chip label="Passed" color="success" size="small" />
                          </TableCell>
                          <TableCell align="right">
                            <IconButton size="small" onClick={() => handleView(inspection.id)}>
                              <Visibility fontSize="small" />
                            </IconButton>
                            <IconButton size="small">
                              <Edit fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          No accepted inspections found.
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

export default AcceptancePage;
