// frontend/src/components/ServiceAnalytics/TechnicianPerformanceChart.tsx

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Collapse,
  Rating
} from '@mui/material';
import {
  Person as TechnicianIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Schedule as TimeIcon,
  Assignment as JobIcon,
  Speed as EfficiencyIcon,
  Star as RatingIcon
} from '@mui/icons-material';
import { TechnicianPerformanceMetrics } from '../../services/serviceAnalyticsService';

interface TechnicianPerformanceChartProps {
  data: TechnicianPerformanceMetrics[];
}

const TechnicianPerformanceChart: React.FC<TechnicianPerformanceChartProps> = ({ data }) => {
  const [expandedTechnician, setExpandedTechnician] = useState<number | null>(null);

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getUtilizationColor = (rate: number) => {
    if (rate >= 80) return 'success';
    if (rate >= 60) return 'info';
    if (rate >= 40) return 'warning';
    return 'error';
  };

  const handleTechnicianExpand = (technicianId: number) => {
    setExpandedTechnician(expandedTechnician === technicianId ? null : technicianId);
  };

  // Calculate summary statistics
  const totalJobsAssigned = data.reduce((sum, tech) => sum + tech.total_jobs_assigned, 0);
  const totalJobsCompleted = data.reduce((sum, tech) => sum + tech.jobs_completed, 0);
  const averageUtilization = data.length > 0 
    ? data.reduce((sum, tech) => sum + tech.utilization_rate, 0) / data.length 
    : 0;
  const averageEfficiency = data.length > 0 
    ? data.reduce((sum, tech) => sum + tech.efficiency_score, 0) / data.length 
    : 0;

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader title="Technician Performance" />
        <CardContent>
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary">
              No technician performance data available for the selected period.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Performance metrics will appear here once technicians are assigned to jobs.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader 
        title="Technician Performance" 
        subheader={`${data.length} technicians analyzed`}
      />
      <CardContent>
        {/* Summary Statistics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="primary.main">
                {data.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active Technicians
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="info.main">
                {totalJobsAssigned}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Jobs Assigned
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="success.main">
                {totalJobsCompleted}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Jobs Completed
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="warning.main">
                {averageEfficiency.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Avg Efficiency
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Team Performance Overview */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Team Performance Overview
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="body2" gutterBottom>
                  Average Team Utilization
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <LinearProgress
                    variant="determinate"
                    value={averageUtilization}
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    color={getUtilizationColor(averageUtilization)}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {averageUtilization.toFixed(1)}%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="body2" gutterBottom>
                  Team Completion Rate
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <LinearProgress
                    variant="determinate"
                    value={(totalJobsCompleted / totalJobsAssigned) * 100}
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    color="success"
                  />
                  <Typography variant="body2" color="text.secondary">
                    {totalJobsAssigned > 0 ? ((totalJobsCompleted / totalJobsAssigned) * 100).toFixed(1) : 0}%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* Individual Technician Performance */}
        <Typography variant="h6" gutterBottom>
          Individual Performance
        </Typography>
        <TableContainer component={Paper} elevation={1}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Technician</TableCell>
                <TableCell align="center">Jobs</TableCell>
                <TableCell align="center">Completed</TableCell>
                <TableCell align="center">Utilization</TableCell>
                <TableCell align="center">Efficiency</TableCell>
                <TableCell align="center">Rating</TableCell>
                <TableCell align="center">Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((technician) => (
                <React.Fragment key={technician.technician_id}>
                  <TableRow>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          <TechnicianIcon />
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {technician.technician_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {technician.technician_id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip 
                        label={technician.total_jobs_assigned}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip 
                        label={technician.jobs_completed}
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      <Box>
                        <Typography variant="body2" color={`${getUtilizationColor(technician.utilization_rate)}.main`}>
                          {technician.utilization_rate.toFixed(1)}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={technician.utilization_rate}
                          size="small"
                          sx={{ width: 60, height: 4 }}
                          color={getUtilizationColor(technician.utilization_rate)}
                        />
                      </Box>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip 
                        label={`${technician.efficiency_score.toFixed(1)}%`}
                        size="small"
                        color={getPerformanceColor(technician.efficiency_score)}
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      {technician.customer_rating_average ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Rating 
                            value={technician.customer_rating_average} 
                            readOnly 
                            size="small"
                            precision={0.1}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {technician.customer_rating_average.toFixed(1)}
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          No ratings
                        </Typography>
                      )}
                    </TableCell>
                    
                    <TableCell align="center">
                      <IconButton 
                        size="small"
                        onClick={() => handleTechnicianExpand(technician.technician_id)}
                      >
                        {expandedTechnician === technician.technician_id ? <CollapseIcon /> : <ExpandIcon />}
                      </IconButton>
                    </TableCell>
                  </TableRow>
                  
                  {/* Expanded Details */}
                  <TableRow>
                    <TableCell colSpan={7} sx={{ py: 0 }}>
                      <Collapse in={expandedTechnician === technician.technician_id}>
                        <Box sx={{ p: 2, bgcolor: 'background.default' }}>
                          <Grid container spacing={2}>
                            <Grid item xs={12} sm={4}>
                              <Box display="flex" alignItems="center" gap={1}>
                                <JobIcon color="action" fontSize="small" />
                                <Typography variant="body2">
                                  In Progress: {technician.jobs_in_progress}
                                </Typography>
                              </Box>
                            </Grid>
                            
                            {technician.average_completion_time_hours && (
                              <Grid item xs={12} sm={4}>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <TimeIcon color="action" fontSize="small" />
                                  <Typography variant="body2">
                                    Avg Time: {technician.average_completion_time_hours.toFixed(1)}h
                                  </Typography>
                                </Box>
                              </Grid>
                            )}
                            
                            <Grid item xs={12} sm={4}>
                              <Box display="flex" alignItems="center" gap={1}>
                                <EfficiencyIcon color="action" fontSize="small" />
                                <Typography variant="body2">
                                  Completion Rate: {technician.total_jobs_assigned > 0 
                                    ? ((technician.jobs_completed / technician.total_jobs_assigned) * 100).toFixed(1)
                                    : 0}%
                                </Typography>
                              </Box>
                            </Grid>
                          </Grid>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Performance Insights */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Performance Insights
          </Typography>
          <Grid container spacing={2}>
            {(() => {
              const topPerformer = data.reduce((prev, current) => 
                prev.efficiency_score > current.efficiency_score ? prev : current
              );
              const mostUtilized = data.reduce((prev, current) => 
                prev.utilization_rate > current.utilization_rate ? prev : current
              );
              
              return (
                <>
                  <Grid item xs={12} sm={6}>
                    <Paper elevation={1} sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
                      <Typography variant="body2" gutterBottom>
                        Top Performer
                      </Typography>
                      <Typography variant="h6">
                        {topPerformer.technician_name}
                      </Typography>
                      <Typography variant="body2">
                        Efficiency Score: {topPerformer.efficiency_score.toFixed(1)}%
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper elevation={1} sx={{ p: 2, bgcolor: 'info.light', color: 'info.contrastText' }}>
                      <Typography variant="body2" gutterBottom>
                        Highest Utilization
                      </Typography>
                      <Typography variant="h6">
                        {mostUtilized.technician_name}
                      </Typography>
                      <Typography variant="body2">
                        Utilization Rate: {mostUtilized.utilization_rate.toFixed(1)}%
                      </Typography>
                    </Paper>
                  </Grid>
                </>
              );
            })()}
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

export default TechnicianPerformanceChart;