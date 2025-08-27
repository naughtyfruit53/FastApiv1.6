'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TableContainer,
  Grid as Grid,
  TextField,
} from '@mui/material';
import {
  Add,
  Visibility,
  Business,
  Security,
  Restore,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { organizationService } from '../../services/authService';
import adminService from '../../services/adminService';
import CreateOrganizationLicenseModal from '../../components/CreateOrganizationLicenseModal';

interface Organization {
  id: number;
  name: string;
  subdomain: string;
  status: string;
  primary_email: string;
  primary_phone: string;
  plan_type: string;
  max_users: number;
  created_at: string;
  company_details_completed: boolean;
}

const LicenseManagement: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // API calls using real service
  const { data: organizations, isLoading } = useQuery({
    queryKey: ['organizations'],
    queryFn: organizationService.getAllOrganizations
  });

  const createLicenseMutation = useMutation({
    mutationFn: organizationService.createLicense,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setCreateDialogOpen(false);
    }
  });

  const handleCreateLicense = (result: any) => {
    // License creation is handled by the modal
    queryClient.invalidateQueries({ queryKey: ['organizations'] });
  };

  const handleResetPassword = async (primary_email: string, orgName: string) => {
    try {
      // Add confirmation dialog for reset action
      const confirmed = window.confirm(
        `Are you sure you want to reset the password for the organization admin of "${orgName}"?\n\n` +
        `This will generate a new temporary password for: ${primary_email}`
      );
      
      if (!confirmed) {
        return;
      }

      const response = await adminService.resetUserPassword(primary_email);
      
      // Better user feedback with success dialog
      alert(
        `✅ Password Reset Successful\n\n` +
        `Organization: ${orgName}\n` +
        `Admin Email: ${primary_email}\n` +
        `New Temporary Password: ${response.new_password}\n\n` +
        `⚠️ Please save this password immediately and share it securely with the admin.\n` +
        `The admin must change this password on their next login.`
      );
    } catch (error: any) {
      alert(
        `❌ Password Reset Failed\n\n` +
        `Organization: ${orgName}\n` +
        `Admin Email: ${primary_email}\n` +
        `Error: ${error.message || 'Failed to reset password'}\n\n` +
        `Please try again or contact support if the issue persists.`
      );
    }
  };

  const getStatusChip = (status: string) => {
    const statusConfig = {
      active: { label: 'Active', color: 'success' as const },
      trial: { label: 'Trial', color: 'info' as const },
      suspended: { label: 'Suspended', color: 'error' as const },
      hold: { label: 'On Hold', color: 'warning' as const }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || 
                   { label: status, color: 'default' as const };
    
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const filteredOrganizations = organizations?.filter((org: Organization) =>
    org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    org.primary_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    org.subdomain.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          License Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create New License
        </Button>
      </Box>
      <Paper sx={{ mb: 3, p: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Security sx={{ mr: 1 }} />
          License Creation Overview
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary">
                {organizations?.length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Licenses
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                {organizations?.filter((org: Organization) => org.status === 'active').length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Active Licenses
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="info.main">
                {organizations?.filter((org: Organization) => org.status === 'trial').length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Trial Licenses
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main">
                {organizations?.filter((org: Organization) => org.status === 'suspended').length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Suspended Licenses
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Search Bar */}
      <Box sx={{ mb: 3 }}>
        <Grid container justifyContent="flex-start">
          <Grid size={5}>
            <TextField
              fullWidth
              label="Search by Name, Email, or Subdomain"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
        </Grid>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Organization</TableCell>
              <TableCell>Subdomain</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : filteredOrganizations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No organizations found.
                </TableCell>
              </TableRow>
            ) : (
              filteredOrganizations.map((org: Organization) => (
                <TableRow key={org.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Business sx={{ mr: 1, color: 'primary.main' }} />
                      <Box>
                        <Typography 
                          variant="body2" 
                          fontWeight="medium"
                          component="button"
                          onClick={() => router.push(`/admin/organizations/${org.id}`)}
                          sx={{
                            color: 'primary.main',
                            textDecoration: 'underline',
                            cursor: 'pointer',
                            border: 'none',
                            background: 'transparent',
                            padding: 0,
                            font: 'inherit',
                            '&:hover': {
                              color: 'primary.dark',
                            }
                          }}
                          title="Click to view organization details"
                        >
                          {org.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          ID: {org.id}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="primary">
                      {org.subdomain}.tritiq.com
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {org.primary_email}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {org.primary_phone}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                      {org.plan_type} (Max {org.max_users} users)
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getStatusChip(org.status)}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(org.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="info"
                      onClick={() => router.push(`/admin/organizations/${org.id}`)}
                      title="View Details"
                    >
                      <Visibility />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="secondary"
                      onClick={() => handleResetPassword(org.primary_email, org.name)}
                      title="Reset Organization Admin Password"
                    >
                      <Restore />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {/* Enhanced Create License Modal */}
      <CreateOrganizationLicenseModal
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={handleCreateLicense}
      />
    </Container>
  );
};

export default LicenseManagement;