// frontend/src/components/ServiceAnalytics/AnalyticsFilters.tsx

import React, { useState } from 'react';
import {
  Box,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  TextField,
  Typography,
  Autocomplete
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  ReportPeriod,
  AnalyticsRequest,
  TechnicianOption,
  CustomerOption
} from '../../services/serviceAnalyticsService';

interface AnalyticsFiltersProps {
  filters: AnalyticsRequest;
  onFiltersChange: (filters: AnalyticsRequest) => void;
  technicians: TechnicianOption[];
  customers: CustomerOption[];
}

const AnalyticsFilters: React.FC<AnalyticsFiltersProps> = ({
  filters,
  onFiltersChange,
  technicians,
  customers
}) => {
  const [localFilters, setLocalFilters] = useState<AnalyticsRequest>(filters);

  const handleApplyFilters = () => {
    onFiltersChange(localFilters);
  };

  const handleResetFilters = () => {
    const resetFilters: AnalyticsRequest = {
      period: ReportPeriod.MONTH
    };
    setLocalFilters(resetFilters);
    onFiltersChange(resetFilters);
  };

  const handlePeriodChange = (period: ReportPeriod) => {
    const updatedFilters = {
      ...localFilters,
      period,
      // Clear custom dates when selecting predefined period
      start_date: period === ReportPeriod.CUSTOM ? localFilters.start_date : undefined,
      end_date: period === ReportPeriod.CUSTOM ? localFilters.end_date : undefined
    };
    setLocalFilters(updatedFilters);
  };

  const handleTechnicianChange = (technicianId: number | null) => {
    setLocalFilters({
      ...localFilters,
      technician_id: technicianId || undefined
    });
  };

  const handleCustomerChange = (customerId: number | null) => {
    setLocalFilters({
      ...localFilters,
      customer_id: customerId || undefined
    });
  };

  const selectedTechnician = technicians.find(t => t.id === localFilters.technician_id) || null;
  const selectedCustomer = customers.find(c => c.id === localFilters.customer_id) || null;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h6" gutterBottom>
          Analytics Filters
        </Typography>
        
        <Grid container spacing={3}>
          {/* Period Selection */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Period</InputLabel>
              <Select
                value={localFilters.period || ReportPeriod.MONTH}
                label="Period"
                onChange={(e) => handlePeriodChange(e.target.value as ReportPeriod)}
              >
                <MenuItem value={ReportPeriod.TODAY}>Today</MenuItem>
                <MenuItem value={ReportPeriod.WEEK}>This Week</MenuItem>
                <MenuItem value={ReportPeriod.MONTH}>This Month</MenuItem>
                <MenuItem value={ReportPeriod.QUARTER}>This Quarter</MenuItem>
                <MenuItem value={ReportPeriod.YEAR}>This Year</MenuItem>
                <MenuItem value={ReportPeriod.CUSTOM}>Custom Range</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Custom Date Range - Only show when Custom is selected */}
          {localFilters.period === ReportPeriod.CUSTOM && (
            <>
              <Grid item xs={12} sm={6} md={3}>
                <DatePicker
                  label="Start Date"
                  value={localFilters.start_date ? new Date(localFilters.start_date) : null}
                  onChange={(date) => {
                    setLocalFilters({
                      ...localFilters,
                      start_date: date ? date.toISOString().split('T')[0] : undefined
                    });
                  }}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <DatePicker
                  label="End Date"
                  value={localFilters.end_date ? new Date(localFilters.end_date) : null}
                  onChange={(date) => {
                    setLocalFilters({
                      ...localFilters,
                      end_date: date ? date.toISOString().split('T')[0] : undefined
                    });
                  }}
                  minDate={localFilters.start_date ? new Date(localFilters.start_date) : undefined}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
            </>
          )}

          {/* Technician Filter */}
          <Grid item xs={12} sm={6} md={3}>
            <Autocomplete
              options={technicians}
              getOptionLabel={(option) => option.name}
              value={selectedTechnician}
              onChange={(_, newValue) => handleTechnicianChange(newValue?.id || null)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Technician"
                  placeholder="All Technicians"
                />
              )}
              renderOption={(props, option) => (
                <li {...props}>
                  <Box>
                    <Typography variant="body2">{option.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </li>
              )}
            />
          </Grid>

          {/* Customer Filter */}
          <Grid item xs={12} sm={6} md={3}>
            <Autocomplete
              options={customers}
              getOptionLabel={(option) => option.name}
              value={selectedCustomer}
              onChange={(_, newValue) => handleCustomerChange(newValue?.id || null)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Customer"
                  placeholder="All Customers"
                />
              )}
              renderOption={(props, option) => (
                <li {...props}>
                  <Box>
                    <Typography variant="body2">{option.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.email}
                    </Typography>
                  </Box>
                </li>
              )}
            />
          </Grid>

          {/* Action Buttons */}
          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button 
                variant="outlined" 
                onClick={handleResetFilters}
              >
                Reset
              </Button>
              <Button 
                variant="contained" 
                onClick={handleApplyFilters}
              >
                Apply Filters
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Active Filters Summary */}
        {(localFilters.technician_id || localFilters.customer_id || localFilters.period === ReportPeriod.CUSTOM) && (
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Active Filters:
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {selectedTechnician && (
                <Box component="span" px={1} py={0.5} bgcolor="primary.light" borderRadius={1}>
                  <Typography variant="caption" color="primary.contrastText">
                    Technician: {selectedTechnician.name}
                  </Typography>
                </Box>
              )}
              {selectedCustomer && (
                <Box component="span" px={1} py={0.5} bgcolor="secondary.light" borderRadius={1}>
                  <Typography variant="caption" color="secondary.contrastText">
                    Customer: {selectedCustomer.name}
                  </Typography>
                </Box>
              )}
              {localFilters.period === ReportPeriod.CUSTOM && localFilters.start_date && localFilters.end_date && (
                <Box component="span" px={1} py={0.5} bgcolor="info.light" borderRadius={1}>
                  <Typography variant="caption" color="info.contrastText">
                    Custom Range: {localFilters.start_date} to {localFilters.end_date}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Box>
    </LocalizationProvider>
  );
};

export default AnalyticsFilters;