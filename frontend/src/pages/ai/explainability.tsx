// AI Explainability Page
import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Help as HelpIcon,
} from '@mui/icons-material';

const AIExplainabilityPage: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState('sales-prediction');
  const [loading, setLoading] = useState(false);

  const models = [
    { id: 'sales-prediction', name: 'Sales Prediction Model', type: 'Regression' },
    { id: 'churn-prediction', name: 'Customer Churn Prediction', type: 'Classification' },
    { id: 'inventory-forecast', name: 'Inventory Forecasting', type: 'Regression' },
  ];

  const mockFeatureImportance = [
    { feature: 'Previous Month Sales', importance: 0.45, impact: 'positive' },
    { feature: 'Marketing Spend', importance: 0.28, impact: 'positive' },
    { feature: 'Season', importance: 0.15, impact: 'positive' },
    { feature: 'Competitor Price', importance: 0.08, impact: 'negative' },
    { feature: 'Economic Index', importance: 0.04, impact: 'positive' },
  ];

  const mockShapValues = [
    { feature: 'Previous Month Sales', value: 150000, shapValue: 12500, contribution: '+₹12,500' },
    { feature: 'Marketing Spend', value: 25000, shapValue: 8200, contribution: '+₹8,200' },
    { feature: 'Season', value: 'Summer', shapValue: 5100, contribution: '+₹5,100' },
    { feature: 'Competitor Price', value: 450, shapValue: -2300, contribution: '-₹2,300' },
    { feature: 'Economic Index', value: 1.05, shapValue: 1500, contribution: '+₹1,500' },
  ];

  const handleExplain = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          AI Model Explainability
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Understand how AI models make predictions and decisions
        </Typography>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 4 }}>
        <AlertTitle>What is AI Explainability?</AlertTitle>
        AI Explainability helps you understand how machine learning models arrive at their
        predictions. It shows which features (inputs) have the most impact on the model's
        decisions, making AI transparent and trustworthy.
      </Alert>

      {/* Model Selection */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Select Model to Explain
        </Typography>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Model</InputLabel>
              <Select
                value={selectedModel}
                label="Model"
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {models.map((model) => (
                  <MenuItem key={model.id} value={model.id}>
                    {model.name} ({model.type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleExplain}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Explain Model'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Model Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Accuracy
              </Typography>
              <Typography variant="h3" color="primary" fontWeight="bold">
                92.5%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                R² Score: 0.89
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Training Samples
              </Typography>
              <Typography variant="h3" color="secondary" fontWeight="bold">
                12,453
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 24 months
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Features Used
              </Typography>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                18
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Top 5 shown below
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Feature Importance */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Global Feature Importance
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Shows which features have the most impact on predictions across all samples
        </Typography>
        <Divider sx={{ my: 2 }} />
        <Grid container spacing={2}>
          {mockFeatureImportance.map((item, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 1,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2" fontWeight="medium">
                      {item.feature}
                    </Typography>
                    {item.impact === 'positive' ? (
                      <TrendingUpIcon
                        sx={{ ml: 1, fontSize: 16 }}
                        color="success"
                      />
                    ) : (
                      <TrendingDownIcon
                        sx={{ ml: 1, fontSize: 16 }}
                        color="error"
                      />
                    )}
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {(item.importance * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={item.importance * 100}
                  sx={{ height: 8, borderRadius: 1 }}
                  color={item.impact === 'positive' ? 'success' : 'error'}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* SHAP Values Explanation */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          SHAP Values Explanation
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          SHAP (SHapley Additive exPlanations) values show how each feature contributes
          to a specific prediction
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Example Prediction:</strong> Sales forecast for next month is{' '}
            <strong>₹1,75,000</strong> (Base value: ₹1,50,000)
          </Typography>
        </Alert>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Feature</TableCell>
                <TableCell>Value</TableCell>
                <TableCell align="right">SHAP Value</TableCell>
                <TableCell align="right">Contribution</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockShapValues.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.feature}</TableCell>
                  <TableCell>{item.value}</TableCell>
                  <TableCell align="right">
                    {item.shapValue > 0 ? '+' : ''}
                    {item.shapValue.toFixed(0)}
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={item.contribution}
                      color={item.shapValue > 0 ? 'success' : 'error'}
                      size="small"
                      icon={
                        item.shapValue > 0 ? (
                          <TrendingUpIcon />
                        ) : (
                          <TrendingDownIcon />
                        )
                      }
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* How to Interpret */}
      <Paper sx={{ p: 3, backgroundColor: '#f5f5f5' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <BrainIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" fontWeight="bold">
            How to Interpret Results
          </Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Feature Importance
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Shows the average impact of each feature across all predictions. Higher
              values indicate more influence on the model's decisions.
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              SHAP Values
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Show how each feature pushes the prediction higher (positive) or lower
              (negative) from the base value for a specific instance.
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Positive Impact
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Features with positive SHAP values increase the predicted value. Focus on
              optimizing these features for better outcomes.
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Negative Impact
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Features with negative SHAP values decrease the predicted value. Consider
              strategies to mitigate their negative effects.
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default AIExplainabilityPage;
