import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Grid,
  TextField,
  Alert,
  CircularProgress,
  Avatar,
  Divider,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import {
  Edit,
  Save,
  Cancel,
  Business,
  Email,
  Phone,
  Language,
  LocationOn
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { companyService } from '../services/authService';

const CompanyDetailsPage: React.FC = () => {
  const router = useRouter();
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    business_type: '',
    industry: '',
    website: '',
    primary_email: '',
    primary_phone: '',
    address1: '',
    address2: '',
    city: '',
    state: '',
    pin_code: '',
    gst_number: '',
    pan_number: '',
    description: ''
  });

  const queryClient = useQueryClient();

  // Fetch company details
  const { data: company, isLoading, error } = useQuery({
    queryKey: ['company'],
    queryFn: () => companyService.getCurrentCompany()
  });

  // Update company mutation
  const updateMutation = useMutation({
    mutationFn: (data: any) => companyService.updateCompany(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company'] });
      setEditMode(false);
    },
    onError: (error: any) => {
      console.error('Error updating company:', error);
    }
  });

  React.useEffect(() => {
    if (company) {
      setFormData({
        name: company.name || '',
        business_type: company.business_type || '',
        industry: company.industry || '',
        website: company.website || '',
        primary_email: company.primary_email || '',
        primary_phone: company.primary_phone || '',
        address1: company.address1 || '',
        address2: company.address2 || '',
        city: company.city || '',
        state: company.state || '',
        pin_code: company.pin_code || '',
        gst_number: company.gst_number || '',
        pan_number: company.pan_number || '',
        description: company.description || ''
      });
    }
  }, [company]);

  const handleEdit = () => {
    setEditMode(true);
  };

  const handleCancel = () => {
    setEditMode(false);
    // Reset form data to original values
    if (company) {
      setFormData({
        name: company.name || '',
        business_type: company.business_type || '',
        industry: company.industry || '',
        website: company.website || '',
        primary_email: company.primary_email || '',
        primary_phone: company.primary_phone || '',
        address1: company.address1 || '',
        address2: company.address2 || '',
        city: company.city || '',
        state: company.state || '',
        pin_code: company.pin_code || '',
        gst_number: company.gst_number || '',
        pan_number: company.pan_number || '',
        description: company.description || ''
      });
    }
  };

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Alert severity="error">
            Failed to load company details. Please try again.
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Company Details
          </Typography>
          {!editMode ? (
            <Button
              variant="contained"
              startIcon={<Edit />}
              onClick={handleEdit}
            >
              Edit Details
            </Button>
          ) : (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Cancel />}
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSave}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </Box>
          )}
        </Box>

        <Grid container spacing={3}>
          {/* Company Overview Card */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: 'fit-content' }}>
              <CardHeader
                avatar={
                  <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                    <Business sx={{ fontSize: 32 }} />
                  </Avatar>
                }
                title={company?.name || 'Company Name'}
                subheader={company?.business_type || 'Business Type'}
              />
              <CardContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Email color="action" />
                    <Typography variant="body2" color="textSecondary">
                      {company?.primary_email || 'No email set'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Phone color="action" />
                    <Typography variant="body2" color="textSecondary">
                      {company?.primary_phone || 'No phone set'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Language color="action" />
                    <Typography variant="body2" color="textSecondary">
                      {company?.website || 'No website set'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LocationOn color="action" />
                    <Typography variant="body2" color="textSecondary">
                      {company?.city && company?.state ? `${company.city}, ${company.state}` : 'No location set'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Company Details Form */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Business Type"
                    value={formData.business_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, business_type: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Industry"
                    value={formData.industry}
                    onChange={(e) => setFormData(prev => ({ ...prev, industry: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Website"
                    value={formData.website}
                    onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Contact Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Primary Email"
                    type="email"
                    value={formData.primary_email}
                    onChange={(e) => setFormData(prev => ({ ...prev, primary_email: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Primary Phone"
                    value={formData.primary_phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, primary_phone: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Address Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address Line 1"
                    value={formData.address1}
                    onChange={(e) => setFormData(prev => ({ ...prev, address1: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address Line 2"
                    value={formData.address2}
                    onChange={(e) => setFormData(prev => ({ ...prev, address2: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="City"
                    value={formData.city}
                    onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="State"
                    value={formData.state}
                    onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="PIN Code"
                    value={formData.pin_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, pin_code: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Legal Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="GST Number"
                    value={formData.gst_number}
                    onChange={(e) => setFormData(prev => ({ ...prev, gst_number: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="PAN Number"
                    value={formData.pan_number}
                    onChange={(e) => setFormData(prev => ({ ...prev, pan_number: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Description"
                    multiline
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    disabled={!editMode}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>

        {updateMutation.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Failed to update company details. Please try again.
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default CompanyDetailsPage;