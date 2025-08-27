'use client';

import React, { useState, useEffect } from 'react';
import {
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Alert,
  CircularProgress,
  SelectChangeEvent
} from '@mui/material';
import { organizationService } from '../services/organizationService';

interface Organization {
  id: number;
  name: string;
  subdomain: string;
  role: string;
  is_current: boolean;
}

const OrganizationSwitcher: React.FC = () => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrganization, setCurrentOrganization] = useState<number | ''>('');
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUserOrganizations();
  }, []);

  const fetchUserOrganizations = async () => {
    try {
      setLoading(true);
      const orgs = await organizationService.getUserOrganizations();
      setOrganizations(orgs);
      
      // Find current organization
      const current = orgs.find((org: Organization) => org.is_current);
      if (current) {
        setCurrentOrganization(current.id);
      }
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOrganizationSwitch = async (event: SelectChangeEvent<number | ''>) => {
    const organizationId = event.target.value as number;
    
    if (!organizationId || organizationId === currentOrganization) {
      return;
    }

    try {
      setSwitching(true);
      setError(null);
      
      await organizationService.switchOrganization(organizationId);
      
      // Update current organization state
      setCurrentOrganization(organizationId);
      setOrganizations(prev => 
        prev.map(org => ({
          ...org,
          is_current: org.id === organizationId
        }))
      );
      
      // Refresh the page to update all components with new organization context
      window.location.reload();
      
    } catch (error: any) {
      setError(error.message);
    } finally {
      setSwitching(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <CircularProgress size={20} />
        <Typography variant="caption">Loading organizations...</Typography>
      </Box>
    );
  }

  if (organizations.length === 0) {
    return (
      <Typography variant="caption" color="text.secondary">
        No organizations available
      </Typography>
    );
  }

  if (organizations.length === 1) {
    const org = organizations[0];
    return (
      <Box>
        <Typography variant="body2" fontWeight="medium">
          {org.name}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Role: {org.role}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minWidth: 200 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 1, fontSize: '0.8rem' }}>
          {error}
        </Alert>
      )}
      
      <FormControl fullWidth size="small">
        <InputLabel id="organization-select-label">Organization</InputLabel>
        <Select
          labelId="organization-select-label"
          value={currentOrganization}
          label="Organization"
          onChange={handleOrganizationSwitch}
          disabled={switching}
        >
          {organizations.map((org) => (
            <MenuItem key={org.id} value={org.id}>
              <Box>
                <Typography variant="body2" fontWeight="medium">
                  {org.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Role: {org.role} | {org.subdomain}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      {switching && (
        <Box display="flex" alignItems="center" gap={1} mt={1}>
          <CircularProgress size={16} />
          <Typography variant="caption">Switching organization...</Typography>
        </Box>
      )}
    </Box>
  );
};

export default OrganizationSwitcher;