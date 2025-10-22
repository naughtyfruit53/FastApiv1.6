import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Description as DescriptionIcon,
  Insights as InsightsIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`explainability-tabpanel-${index}`}
      aria-labelledby={`explainability-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface ModelExplainability {
  id: number;
  model_id: number;
  model_name: string;
  model_type: string;
  method: string;
  scope: string;
  top_features: Array<{ feature: string; importance: number }>;
  created_at: string;
}

interface ExplainabilityReport {
  id: number;
  report_name: string;
  report_type: string;
  model_count: number;
  generated_at: string;
}

const ExplainabilityDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [models, setModels] = useState<ModelExplainability[]>([]);
  const [reports, setReports] = useState<ExplainabilityReport[]>([]);
  const [selectedModel, setSelectedModel] = useState<number | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newExplainability, setNewExplainability] = useState({
    model_id: 0,
    model_type: 'predictive_model',
    method: 'shap',
    scope: 'global',
  });

  const dashboardData = {
    total_models_with_explainability: 8,
    total_prediction_explanations: 150,
    total_reports: 5,
  };

  // Mock feature importance data
  const featureImportanceData = [
    { feature: 'age', importance: 0.35 },
    { feature: 'income', importance: 0.28 },
    { feature: 'credit_score', importance: 0.22 },
    { feature: 'employment_length', importance: 0.10 },
    { feature: 'debt_ratio', importance: 0.05 },
  ];

  useEffect(() => {
    fetchModels();
    fetchReports();
  }, []);

  const fetchModels = async () => {
    // Mock data
    setModels([
      {
        id: 1,
        model_id: 1,
        model_name: 'Sales Forecast Model',
        model_type: 'predictive_model',
        method: 'shap',
        scope: 'global',
        top_features: featureImportanceData,
        created_at: new Date().toISOString(),
      },
      {
        id: 2,
        model_id: 2,
        model_name: 'Customer Churn Model',
        model_type: 'automl_run',
        method: 'lime',
        scope: 'local',
        top_features: featureImportanceData,
        created_at: new Date().toISOString(),
      },
    ]);
  };

  const fetchReports = async () => {
    // Mock data
    setReports([
      {
        id: 1,
        report_name: 'Q4 Model Performance Analysis',
        report_type: 'global_summary',
        model_count: 5,
        generated_at: new Date().toISOString(),
      },
    ]);
  };

  const handleCreateExplainability = async () => {
    console.log('Creating explainability:', newExplainability);
    setOpenDialog(false);
    fetchModels();
  };

  return (
    <Box>
      {/* Dashboard Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Models with Explainability</Typography>
              </Box>
              <Typography variant="h3">
                {dashboardData.total_models_with_explainability}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <InsightsIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Prediction Explanations</Typography>
              </Box>
              <Typography variant="h3">
                {dashboardData.total_prediction_explanations}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DescriptionIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Reports Generated</Typography>
              </Box>
              <Typography variant="h3">{dashboardData.total_reports}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
            <Tab label="Model Explainability" />
            <Tab label="Feature Importance" />
            <Tab label="Reports" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Models with Explainability</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Add Explainability
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Model Name</TableCell>
                  <TableCell>Model Type</TableCell>
                  <TableCell>Method</TableCell>
                  <TableCell>Scope</TableCell>
                  <TableCell>Top Features</TableCell>
                  <TableCell>Created</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.model_name}</TableCell>
                    <TableCell>
                      <Chip label={model.model_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip label={model.method.toUpperCase()} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      <Chip label={model.scope} size="small" />
                    </TableCell>
                    <TableCell>
                      {model.top_features.slice(0, 3).map((f, i) => (
                        <Chip
                          key={i}
                          label={f.feature}
                          size="small"
                          sx={{ mr: 0.5 }}
                        />
                      ))}
                    </TableCell>
                    <TableCell>
                      {new Date(model.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Feature Importance Analysis
          </Typography>
          <FormControl sx={{ mb: 3, minWidth: 300 }}>
            <InputLabel>Select Model</InputLabel>
            <Select
              value={selectedModel || ''}
              label="Select Model"
              onChange={(e) => setSelectedModel(Number(e.target.value))}
            >
              {models.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.model_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {selectedModel && (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={featureImportanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="feature" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="importance" fill="#1976d2" name="Feature Importance" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Explainability Reports</Typography>
            <Button variant="contained" startIcon={<AddIcon />}>
              Generate Report
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Report Name</TableCell>
                  <TableCell>Report Type</TableCell>
                  <TableCell>Models Analyzed</TableCell>
                  <TableCell>Generated At</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell>{report.report_name}</TableCell>
                    <TableCell>
                      <Chip label={report.report_type} size="small" />
                    </TableCell>
                    <TableCell>{report.model_count}</TableCell>
                    <TableCell>
                      {new Date(report.generated_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Button size="small" variant="outlined">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Create Explainability Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Model Explainability</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Model ID"
                value={newExplainability.model_id}
                onChange={(e) =>
                  setNewExplainability({
                    ...newExplainability,
                    model_id: parseInt(e.target.value),
                  })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={newExplainability.model_type}
                  label="Model Type"
                  onChange={(e) =>
                    setNewExplainability({
                      ...newExplainability,
                      model_type: e.target.value,
                    })
                  }
                >
                  <MenuItem value="predictive_model">Predictive Model</MenuItem>
                  <MenuItem value="automl_run">AutoML Run</MenuItem>
                  <MenuItem value="ml_training">ML Training</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Method</InputLabel>
                <Select
                  value={newExplainability.method}
                  label="Method"
                  onChange={(e) =>
                    setNewExplainability({
                      ...newExplainability,
                      method: e.target.value,
                    })
                  }
                >
                  <MenuItem value="shap">SHAP</MenuItem>
                  <MenuItem value="lime">LIME</MenuItem>
                  <MenuItem value="feature_importance">Feature Importance</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Scope</InputLabel>
                <Select
                  value={newExplainability.scope}
                  label="Scope"
                  onChange={(e) =>
                    setNewExplainability({
                      ...newExplainability,
                      scope: e.target.value,
                    })
                  }
                >
                  <MenuItem value="global">Global</MenuItem>
                  <MenuItem value="local">Local</MenuItem>
                  <MenuItem value="cohort">Cohort</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateExplainability} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExplainabilityDashboard;
