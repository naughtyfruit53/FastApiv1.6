/**
 * A/B Testing Dashboard Page
 * Page for managing and viewing A/B test experiments
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  CheckCircle as CompleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import abTestingService, {
  Experiment,
  ExperimentStatus,
  Variant,
  VariantType,
  ExperimentResults,
} from '../../services/abTestingService';

const ABTestingDashboard: React.FC = () => {
  const router = useRouter();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [results, setResults] = useState<ExperimentResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [variantDialogOpen, setVariantDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<ExperimentStatus | 'all'>('all');
  const [tabValue, setTabValue] = useState(0);

  // Form states
  const [newExperiment, setNewExperiment] = useState({
    experiment_name: '',
    description: '',
    traffic_split: { control: 50, treatment: 50 },
  });

  const [newVariant, setNewVariant] = useState({
    variant_name: '',
    variant_type: VariantType.CONTROL,
    traffic_percentage: 50,
    model_version: '',
  });

  useEffect(() => {
    loadExperiments();
  }, [statusFilter]);

  useEffect(() => {
    if (selectedExperiment) {
      loadVariants(selectedExperiment.id);
      loadResults(selectedExperiment.id);
    }
  }, [selectedExperiment]);

  const loadExperiments = async () => {
    try {
      setLoading(true);
      const filter = statusFilter === 'all' ? undefined : statusFilter;
      const data = await abTestingService.listExperiments(filter);
      setExperiments(data);
    } catch (error) {
      console.error('Error loading experiments:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadVariants = async (experimentId: number) => {
    try {
      const data = await abTestingService.getVariants(experimentId);
      setVariants(data);
    } catch (error) {
      console.error('Error loading variants:', error);
    }
  };

  const loadResults = async (experimentId: number) => {
    try {
      const data = await abTestingService.getExperimentResults(experimentId);
      setResults(data);
    } catch (error) {
      console.error('Error loading results:', error);
    }
  };

  const handleCreateExperiment = async () => {
    try {
      await abTestingService.createExperiment(newExperiment);
      setCreateDialogOpen(false);
      setNewExperiment({
        experiment_name: '',
        description: '',
        traffic_split: { control: 50, treatment: 50 },
      });
      loadExperiments();
    } catch (error) {
      console.error('Error creating experiment:', error);
    }
  };

  const handleCreateVariant = async () => {
    if (!selectedExperiment) return;

    try {
      await abTestingService.createVariant(selectedExperiment.id, newVariant);
      setVariantDialogOpen(false);
      setNewVariant({
        variant_name: '',
        variant_type: VariantType.CONTROL,
        traffic_percentage: 50,
        model_version: '',
      });
      loadVariants(selectedExperiment.id);
    } catch (error) {
      console.error('Error creating variant:', error);
    }
  };

  const handleStartExperiment = async (experimentId: number) => {
    try {
      await abTestingService.startExperiment(experimentId);
      loadExperiments();
    } catch (error) {
      console.error('Error starting experiment:', error);
    }
  };

  const handlePauseExperiment = async (experimentId: number) => {
    try {
      await abTestingService.pauseExperiment(experimentId);
      loadExperiments();
    } catch (error) {
      console.error('Error pausing experiment:', error);
    }
  };

  const handleCompleteExperiment = async (experimentId: number) => {
    try {
      await abTestingService.completeExperiment(experimentId);
      loadExperiments();
    } catch (error) {
      console.error('Error completing experiment:', error);
    }
  };

  const getStatusColor = (status: ExperimentStatus) => {
    switch (status) {
      case ExperimentStatus.RUNNING:
        return 'success';
      case ExperimentStatus.PAUSED:
        return 'warning';
      case ExperimentStatus.COMPLETED:
        return 'info';
      case ExperimentStatus.DRAFT:
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          A/B Testing Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadExperiments}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Experiment
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Experiments List */}
        <Grid item xs={12} md={selectedExperiment ? 6 : 12}>
          <Card>
            <CardHeader
              title="Experiments"
              action={
                <Tabs value={statusFilter} onChange={(_, v) => setStatusFilter(v)}>
                  <Tab label="All" value="all" />
                  <Tab label="Running" value={ExperimentStatus.RUNNING} />
                  <Tab label="Draft" value={ExperimentStatus.DRAFT} />
                  <Tab label="Completed" value={ExperimentStatus.COMPLETED} />
                </Tabs>
              }
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Start Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {experiments.map((exp) => (
                      <TableRow
                        key={exp.id}
                        hover
                        onClick={() => setSelectedExperiment(exp)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <TableCell>{exp.experiment_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={exp.status}
                            color={getStatusColor(exp.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {exp.start_date
                            ? new Date(exp.start_date).toLocaleDateString()
                            : '-'}
                        </TableCell>
                        <TableCell>
                          {exp.status === ExperimentStatus.DRAFT && (
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStartExperiment(exp.id);
                              }}
                            >
                              <PlayIcon />
                            </IconButton>
                          )}
                          {exp.status === ExperimentStatus.RUNNING && (
                            <>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handlePauseExperiment(exp.id);
                                }}
                              >
                                <PauseIcon />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCompleteExperiment(exp.id);
                                }}
                              >
                                <CompleteIcon />
                              </IconButton>
                            </>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Experiment Details */}
        {selectedExperiment && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader
                title={selectedExperiment.experiment_name}
                subheader={selectedExperiment.description}
                action={
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => setVariantDialogOpen(true)}
                  >
                    Add Variant
                  </Button>
                }
              />
              <CardContent>
                <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
                  <Tab label="Variants" />
                  <Tab label="Results" />
                </Tabs>

                {/* Variants Tab */}
                {tabValue === 0 && (
                  <Box sx={{ mt: 2 }}>
                    {variants.map((variant) => (
                      <Paper key={variant.id} sx={{ p: 2, mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="h6">{variant.variant_name}</Typography>
                          <Chip
                            label={variant.variant_type}
                            color={
                              variant.variant_type === VariantType.CONTROL
                                ? 'primary'
                                : 'secondary'
                            }
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Traffic: {variant.traffic_percentage}%
                        </Typography>
                        {variant.model_version && (
                          <Typography variant="body2" color="text.secondary">
                            Model Version: {variant.model_version}
                          </Typography>
                        )}
                      </Paper>
                    ))}
                  </Box>
                )}

                {/* Results Tab */}
                {tabValue === 1 && results && (
                  <Box sx={{ mt: 2 }}>
                    {Object.entries(results.variants).map(([variantName, variantData]) => (
                      <Paper key={variantName} sx={{ p: 2, mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          {variantName}
                        </Typography>
                        <Typography variant="body2">
                          Sample Size: {variantData.sample_size}
                        </Typography>
                        {Object.entries(variantData.metrics).map(([metricName, metricStats]) => (
                          <Box key={metricName} sx={{ mt: 1 }}>
                            <Typography variant="subtitle2">{metricName}</Typography>
                            <Grid container spacing={1}>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  Mean: {metricStats.mean.toFixed(2)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  Count: {metricStats.count}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  Min: {metricStats.min.toFixed(2)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="body2" color="text.secondary">
                                  Max: {metricStats.max.toFixed(2)}
                                </Typography>
                              </Grid>
                            </Grid>
                          </Box>
                        ))}
                      </Paper>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Create Experiment Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Experiment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Experiment Name"
            value={newExperiment.experiment_name}
            onChange={(e) =>
              setNewExperiment({ ...newExperiment, experiment_name: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={newExperiment.description}
            onChange={(e) =>
              setNewExperiment({ ...newExperiment, description: e.target.value })
            }
            margin="normal"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateExperiment} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Variant Dialog */}
      <Dialog
        open={variantDialogOpen}
        onClose={() => setVariantDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Variant</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Variant Name"
            value={newVariant.variant_name}
            onChange={(e) =>
              setNewVariant({ ...newVariant, variant_name: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            select
            label="Variant Type"
            value={newVariant.variant_type}
            onChange={(e) =>
              setNewVariant({
                ...newVariant,
                variant_type: e.target.value as VariantType,
              })
            }
            margin="normal"
            SelectProps={{ native: true }}
          >
            <option value={VariantType.CONTROL}>Control</option>
            <option value={VariantType.TREATMENT}>Treatment</option>
          </TextField>
          <TextField
            fullWidth
            type="number"
            label="Traffic Percentage"
            value={newVariant.traffic_percentage}
            onChange={(e) =>
              setNewVariant({
                ...newVariant,
                traffic_percentage: parseFloat(e.target.value),
              })
            }
            margin="normal"
            inputProps={{ min: 0, max: 100 }}
          />
          <TextField
            fullWidth
            label="Model Version"
            value={newVariant.model_version}
            onChange={(e) =>
              setNewVariant({ ...newVariant, model_version: e.target.value })
            }
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVariantDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateVariant} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ABTestingDashboard;
