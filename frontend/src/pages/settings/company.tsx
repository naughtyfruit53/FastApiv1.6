// pages/settings/company.tsx
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
  FormControlLabel,
  Switch,
  FormGroup,
  MenuItem,
  Select,
  InputLabel,
  FormControl
} from '@mui/material';
import { Business, Save, Sync } from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const CompanyProfilePage: React.FC = () => {
  const [tallyEnabled, setTallyEnabled] = React.useState(false);
  const [syncFrequency, setSyncFrequency] = React.useState('manual');

  const handleTallyToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTallyEnabled(event.target.checked);
  };

  const handleSyncFrequencyChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSyncFrequency(event.target.value as string);
  };

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
                    rows=3
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
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Sync sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Tally Sync Integration</Typography>
              </Box>
              
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={tallyEnabled}
                      onChange={handleTallyToggle}
                      name="tallyEnabled"
                    />
                  }
                  label="Enable Tally Sync"
                />
              </FormGroup>
              
              {tallyEnabled && (
                <Grid container spacing={3} sx={{ mt: 2 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Tally Host"
                      placeholder="e.g., localhost or tally.company.com"
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Tally Port"
                      type="number"
                      defaultValue={9000}
                      variant="outlined"
                      inputProps={{ min: 1, max: 65535 }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Tally Company Name"
                      placeholder="Enter the company name in Tally"
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="sync-frequency-label">Sync Frequency</InputLabel>
                      <Select
                        labelId="sync-frequency-label"
                        value={syncFrequency}
                        label="Sync Frequency"
                        onChange={handleSyncFrequencyChange}
                      >
                        <MenuItem value="manual">Manual</MenuItem>
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="hourly">Hourly</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Last Sync"
                      disabled
                      variant="outlined"
                      value="Not synced yet"
                    />
                  </Grid>
                </Grid>
              )}
              
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