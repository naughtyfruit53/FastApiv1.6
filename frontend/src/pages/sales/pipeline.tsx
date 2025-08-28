'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Button,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  CircularProgress,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  DragIndicator as DragIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MoneyIcon
} from '@mui/icons-material';

interface PipelineStage {
  id: string;
  name: string;
  probability: number;
  color: string;
  order: number;
}

interface Opportunity {
  id: number;
  name: string;
  account: string;
  amount: number;
  stage: string;
  owner: string;
  closeDate: string;
  probability: number;
}

interface Pipeline {
  id: number;
  name: string;
  description: string;
  stages: PipelineStage[];
  isDefault: boolean;
  isActive: boolean;
}

const SalesPipeline: React.FC = () => {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [opportunities, setOpportunities] = useState<{[stageId: string]: Opportunity[]}>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchPipelineData = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockStages: PipelineStage[] = [
          { id: 'qualification', name: 'Qualification', probability: 10, color: '#f44336', order: 1 },
          { id: 'needs-analysis', name: 'Needs Analysis', probability: 25, color: '#ff9800', order: 2 },
          { id: 'proposal', name: 'Proposal', probability: 50, color: '#2196f3', order: 3 },
          { id: 'negotiation', name: 'Negotiation', probability: 75, color: '#4caf50', order: 4 },
          { id: 'closed-won', name: 'Closed Won', probability: 100, color: '#8bc34a', order: 5 }
        ];

        const mockPipeline: Pipeline = {
          id: 1,
          name: 'Standard Sales Pipeline',
          description: 'Default sales pipeline for all opportunities',
          stages: mockStages,
          isDefault: true,
          isActive: true
        };

        const mockOpportunities: {[stageId: string]: Opportunity[]} = {
          'qualification': [
            {
              id: 1,
              name: 'ERP Implementation',
              account: 'Manufacturing Co',
              amount: 75000,
              stage: 'qualification',
              owner: 'Sarah Johnson',
              closeDate: '2024-03-30',
              probability: 10
            },
            {
              id: 4,
              name: 'CRM Software',
              account: 'Retail Corp',
              amount: 25000,
              stage: 'qualification',
              owner: 'Mike Wilson',
              closeDate: '2024-04-15',
              probability: 10
            }
          ],
          'needs-analysis': [
            {
              id: 5,
              name: 'Analytics Platform',
              account: 'Data Co',
              amount: 50000,
              stage: 'needs-analysis',
              owner: 'Lisa Davis',
              closeDate: '2024-03-15',
              probability: 25
            }
          ],
          'proposal': [
            {
              id: 2,
              name: 'Enterprise Software License',
              account: 'TechCorp Ltd',
              amount: 150000,
              stage: 'proposal',
              owner: 'Sarah Johnson',
              closeDate: '2024-02-15',
              probability: 50
            }
          ],
          'negotiation': [
            {
              id: 3,
              name: 'Cloud Migration Project',
              account: 'Global Systems Inc',
              amount: 300000,
              stage: 'negotiation',
              owner: 'David Brown',
              closeDate: '2024-02-28',
              probability: 75
            }
          ],
          'closed-won': [
            {
              id: 6,
              name: 'Small Business Package',
              account: 'Local Startup',
              amount: 15000,
              stage: 'closed-won',
              owner: 'Mike Wilson',
              closeDate: '2024-01-30',
              probability: 100
            }
          ]
        };
        
        setPipelines([mockPipeline]);
        setSelectedPipeline(mockPipeline);
        setOpportunities(mockOpportunities);
      } catch (err) {
        setError('Failed to load pipeline data');
        console.error('Error fetching pipeline data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPipelineData();
  }, []);

  const calculateStageMetrics = (stageId: string) => {
    const stageOpps = opportunities[stageId] || [];
    const count = stageOpps.length;
    const value = stageOpps.reduce((sum, opp) => sum + opp.amount, 0);
    const weightedValue = stageOpps.reduce((sum, opp) => sum + (opp.amount * opp.probability / 100), 0);
    
    return { count, value, weightedValue };
  };

  const getTotalPipelineValue = () => {
    return Object.values(opportunities).flat().reduce((sum, opp) => sum + opp.amount, 0);
  };

  const getWeightedPipelineValue = () => {
    return Object.values(opportunities).flat().reduce((sum, opp) => sum + (opp.amount * opp.probability / 100), 0);
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Sales Pipeline
      </Typography>

      {/* Pipeline Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Opportunities
              </Typography>
              <Typography variant="h4">
                {Object.values(opportunities).flat().length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pipeline Value
              </Typography>
              <Typography variant="h4">
                ${getTotalPipelineValue().toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Weighted Value
              </Typography>
              <Typography variant="h4">
                ${Math.round(getWeightedPipelineValue()).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Conversion Rate
              </Typography>
              <Typography variant="h4">
                {Object.values(opportunities).flat().length > 0 
                  ? Math.round((opportunities['closed-won']?.length || 0) / Object.values(opportunities).flat().length * 100)
                  : 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {selectedPipeline && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">{selectedPipeline.name}</Typography>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => setDialogOpen(true)}
            >
              Configure Pipeline
            </Button>
          </Box>

          {/* Pipeline Stages */}
          <Grid container spacing={2}>
            {selectedPipeline.stages.map((stage) => {
              const metrics = calculateStageMetrics(stage.id);
              const stageOpps = opportunities[stage.id] || [];
              
              return (
                <Grid item xs={12} md={2.4} key={stage.id}>
                  <Paper 
                    sx={{ 
                      p: 2, 
                      height: '500px',
                      borderTop: `4px solid ${stage.color}`,
                      display: 'flex',
                      flexDirection: 'column'
                    }}
                  >
                    {/* Stage Header */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h6" sx={{ fontSize: '14px', fontWeight: 'bold' }}>
                        {stage.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {stage.probability}% probability
                      </Typography>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="body2">
                        {metrics.count} opp{metrics.count !== 1 ? 's' : ''} • ${metrics.value.toLocaleString()}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(metrics.weightedValue / metrics.value) * 100 || 0}
                        sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      />
                    </Box>

                    {/* Opportunities List */}
                    <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                      {stageOpps.map((opportunity) => (
                        <Card 
                          key={opportunity.id} 
                          sx={{ 
                            mb: 1, 
                            cursor: 'pointer',
                            '&:hover': { backgroundColor: 'action.hover' }
                          }}
                          onClick={() => {
                            // Handle opportunity click - navigate to detail view
                            console.log('Opportunity clicked:', opportunity.id);
                          }}
                        >
                          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Typography variant="subtitle2" sx={{ fontSize: '12px', fontWeight: 'bold' }}>
                              {opportunity.name}
                            </Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ fontSize: '11px' }}>
                              {opportunity.account}
                            </Typography>
                            <Typography variant="body2" sx={{ fontSize: '12px', fontWeight: 'bold', mt: 1 }}>
                              ${opportunity.amount.toLocaleString()}
                            </Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ fontSize: '11px' }}>
                              {opportunity.owner}
                            </Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ fontSize: '11px' }}>
                              Close: {new Date(opportunity.closeDate).toLocaleDateString()}
                            </Typography>
                          </CardContent>
                        </Card>
                      ))}
                      
                      {/* Add Opportunity Button */}
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<AddIcon />}
                        fullWidth
                        sx={{ mt: 1, fontSize: '11px' }}
                        onClick={() => {
                          // Handle add opportunity to this stage
                          console.log('Add opportunity to stage:', stage.id);
                        }}
                      >
                        Add Opportunity
                      </Button>
                    </Box>
                  </Paper>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      )}

      {/* Pipeline Configuration Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Configure Sales Pipeline</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>Pipeline Stages</Typography>
            {selectedPipeline?.stages.map((stage, index) => (
              <Card key={stage.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <IconButton size="small">
                      <DragIcon />
                    </IconButton>
                    <TextField
                      label="Stage Name"
                      value={stage.name}
                      sx={{ flexGrow: 1 }}
                      disabled
                    />
                    <TextField
                      label="Probability %"
                      type="number"
                      value={stage.probability}
                      sx={{ width: 120 }}
                      disabled
                    />
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        backgroundColor: stage.color,
                        borderRadius: 1,
                        border: '1px solid #ccc'
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            ))}
            <Alert severity="info" sx={{ mt: 2 }}>
              Pipeline customization will be available with backend integration. 
              Contact your administrator to modify pipeline stages.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button variant="contained" disabled>Save Changes</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SalesPipeline;