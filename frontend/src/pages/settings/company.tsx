// frontend/src/pages/settings/company.tsx

import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Divider,
  Alert,
} from '@mui/material';
import { Business, Save } from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const CompanyProfilePage: React.FC = () => {
  // Debug logging
  console.log("CompanyProfilePage.tsx - Rendering company profile page");

  return (
    <DashboardLayout
      title="Company Profile"
      subtitle="Manage your organization's information and settings"
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Update your company details to ensure accurate business information across all modules.
          </Alert>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Business sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Company Information</Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    defaultValue="TritIQ Business Solutions"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Registration Number"
                    placeholder="Enter registration number"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Tax ID / VAT Number"
                    placeholder="Enter tax identification"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Industry"
                    placeholder="e.g., Technology, Manufacturing"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Address"
                    multiline
                    rows="3"
                    placeholder="Enter complete address"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    placeholder="+1 (555) 123-4567"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    placeholder="contact@company.com"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Website"
                    placeholder="https://www.company.com"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Currency"
                    defaultValue="USD"
                    variant="outlined"
                  />
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 3 }} />
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  variant="contained" 
                  startIcon={<Save />}
                  sx={{ minWidth: 120 }}
                >
                  Save Changes
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Company Logo
              </Typography>
              <Box sx={{ 
                border: '2px dashed', 
                borderColor: 'grey.300',
                borderRadius: 1,
                p: 3,
                textAlign: 'center',
                minHeight: 200,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}>
                <Typography variant="body2" color="textSecondary">
                  Drag & drop your logo here
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  or
                </Typography>
                <Button variant="outlined" sx={{ mt: 1 }}>
                  Browse Files
                </Button>
              </Box>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                Recommended size: 200x200px, Max: 2MB
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default CompanyProfilePage;