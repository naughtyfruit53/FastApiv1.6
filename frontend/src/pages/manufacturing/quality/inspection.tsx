import React, { useState } from 'react';
import { Container, Box, Typography, Alert, Card, CardContent, CardActionArea, Grid, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip } from '@mui/material';
import { Assessment, CheckCircle, Warning, Add, Visibility, Edit } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';

const QualityInspectionPage: React.FC = () => {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const perPage = 10;

  // Fetch quality inspections
  const { data: inspections, isLoading } = useQuery({
    queryKey: ['quality-inspections', page],
    queryFn: async () => {
      const response = await api.get(`/manufacturing/quality-inspections?page=${page}&per_page=${perPage}`);
      return response.data;
    },
    enabled: true,
  });

  const handleView = (id: number) => {
    router.push(`/manufacturing/quality/inspection/${id}`);
  };

  const handleEdit = (id: number) => {
    router.push(`/manufacturing/quality/inspection/edit/${id}`);
  };

  const handleCreate = () => {
    router.push('/manufacturing/quality/inspection/create');
  };

  // Tile click handlers
  const handleInspectionPlansClick = () => {
    router.push('/manufacturing/quality/inspection-plans');
  };

  const handleAcceptanceClick = () => {
    router.push('/manufacturing/quality/acceptance');
  };

  const handleNonConformanceClick = () => {
    router.push('/manufacturing/quality/non-conformance');
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Quality Inspection
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Conduct quality inspections for manufactured goods and jobwork items.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreate}
          >
            Create Inspection
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Quality Inspection module helps maintain quality standards by enabling
          systematic inspection of raw materials, work-in-progress, and finished goods.
        </Alert>

        {/* Clickable Tiles */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                }
              }}
            >
              <CardActionArea onClick={handleInspectionPlansClick}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Assessment color="primary" sx={{ fontSize: 40 }} />
                    <Typography variant="h6">
                      Inspection Plans
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Define inspection criteria and quality parameters for different product types.
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                }
              }}
            >
              <CardActionArea onClick={handleAcceptanceClick}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <CheckCircle color="success" sx={{ fontSize: 40 }} />
                    <Typography variant="h6">
                      Acceptance
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Record inspection results and approve or reject batches based on quality standards.
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                }
              }}
            >
              <CardActionArea onClick={handleNonConformanceClick}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Warning color="error" sx={{ fontSize: 40 }} />
                    <Typography variant="h6">
                      Non-Conformance
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Track and manage non-conformance issues and corrective actions.
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Inspections Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Quality Inspections
            </Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Inspection No.</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Product/Batch</TableCell>
                    <TableCell>Inspector</TableCell>
                    <TableCell>Result</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : inspections?.items?.length > 0 ? (
                    inspections.items.map((inspection: any) => (
                      <TableRow key={inspection.id} hover>
                        <TableCell>
                          <Button
                            variant="text"
                            onClick={() => handleView(inspection.id)}
                            sx={{ textTransform: 'none' }}
                          >
                            {inspection.inspection_number}
                          </Button>
                        </TableCell>
                        <TableCell>{new Date(inspection.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {inspection.product_name ? (
                            <Button
                              variant="text"
                              size="small"
                              onClick={() => router.push(`/products/${inspection.product_id}`)}
                              sx={{ textTransform: 'none' }}
                            >
                              {inspection.product_name}
                            </Button>
                          ) : inspection.batch_number || '-'}
                        </TableCell>
                        <TableCell>{inspection.inspector_name || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={inspection.result || 'Pending'}
                            color={
                              inspection.result === 'passed' ? 'success' : 
                              inspection.result === 'failed' ? 'error' : 
                              'default'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={inspection.status || 'Draft'}
                            color={inspection.status === 'completed' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => handleView(inspection.id)} title="View">
                            <Visibility fontSize="small" />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleEdit(inspection.id)} title="Edit">
                            <Edit fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No inspections found. Click "Create Inspection" to get started.
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

export default QualityInspectionPage;
