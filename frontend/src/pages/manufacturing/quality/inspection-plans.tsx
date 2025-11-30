import React from 'react';
import { Container, Box, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Breadcrumbs, Link, Card, CardContent } from '@mui/material';
import { Add, Visibility, Edit, ArrowBack } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import NextLink from 'next/link';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const InspectionPlansPage: React.FC = () => {
  const router = useRouter();

  // Fetch QC templates (inspection plans)
  const { data: templates, isLoading } = useQuery({
    queryKey: ['qc-templates'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/templates');
      return response.data;
    },
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/quality/inspection-plans/${id}`);
  };

  const handleCreate = () => {
    router.push('/manufacturing/quality/inspection-plans/create');
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
            <Typography color="text.primary">Inspection Plans</Typography>
          </Breadcrumbs>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton onClick={() => router.push('/manufacturing/quality/inspection')}>
                <ArrowBack />
              </IconButton>
              <Box>
                <Typography variant="h4" component="h1" gutterBottom>
                  Inspection Plans
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Define inspection criteria and quality parameters for different product types.
                </Typography>
              </Box>
            </Box>
            <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
              Create Plan
            </Button>
          </Box>

          <Card>
            <CardContent>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Plan Name</TableCell>
                      <TableCell>Product</TableCell>
                      <TableCell>Parameters</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">Loading...</TableCell>
                      </TableRow>
                    ) : templates?.length > 0 ? (
                      templates.map((template: any) => (
                        <TableRow key={template.id} hover>
                          <TableCell>{template.name}</TableCell>
                          <TableCell>{template.product_name || 'All Products'}</TableCell>
                          <TableCell>{template.parameters?.length || 0} parameters</TableCell>
                          <TableCell>
                            <Chip
                              label={template.is_active ? 'Active' : 'Inactive'}
                              color={template.is_active ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {template.created_at ? new Date(template.created_at).toLocaleDateString() : '-'}
                          </TableCell>
                          <TableCell align="right">
                            <IconButton size="small" onClick={() => handleView(template.id)}>
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
                          No inspection plans found. Click "Create Plan" to get started.
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

export default InspectionPlansPage;
