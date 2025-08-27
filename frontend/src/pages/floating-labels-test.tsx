'use client';

import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Grid,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';

interface TestFormData {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  role: string;
  organization_name: string;
  address: string;
  city: string;
  state: string;
  pin_code: string;
  gst_number: string;
}

const FloatingLabelsTest: React.FC = () => {
  const [formData, setFormData] = useState<TestFormData>({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    role: 'standard_user',
    organization_name: '',
    address: '',
    city: '',
    state: '',
    pin_code: '',
    gst_number: ''
  });

  const { control, handleSubmit, formState: { errors } } = useForm<TestFormData>({
    defaultValues: formData
  });

  const handleInputChange = (field: keyof TestFormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  const onSubmit = (data: TestFormData) => {
    console.log('Form data:', data);
    alert('Form submitted successfully! Check console for data.');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom align="center">
        Floating Labels Test Page
      </Typography>
      
      <Typography variant="body1" gutterBottom align="center" sx={{ mb: 4 }}>
        This page demonstrates the floating label behavior across all form components.
        Watch how labels animate and float above fields when you focus or enter data.
      </Typography>

      <Grid container spacing={4}>
        {/* Login Form Demo */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Login Form Style
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Uses react-hook-form with Controller for proper floating label behavior
            </Typography>
            
            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
              <Controller
                name="email"
                control={control}
                rules={{
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address'
                  }
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Email Address"
                    type="email"
                    variant="outlined"
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    margin="normal"
                  />
                )}
              />

              <Controller
                name="password"
                control={control}
                rules={{ required: 'Password is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Password"
                    type="password"
                    variant="outlined"
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    margin="normal"
                  />
                )}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Standard Form Demo */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Standard Form Style
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Uses standard TextField components with controlled values
            </Typography>

            <TextField
              fullWidth
              label="Full Name"
              value={formData.full_name}
              onChange={handleInputChange('full_name')}
              margin="normal"
            />

            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone}
              onChange={handleInputChange('phone')}
              margin="normal"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Role</InputLabel>
              <Select
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                label="Role"
              >
                <MenuItem value="standard_user">Standard User</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="org_admin">Organization Admin</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Organization Form Demo */}
        <Grid size={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Organization Form Style
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Multi-field form layout demonstrating consistent floating label behavior
            </Typography>

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Organization Name"
                  value={formData.organization_name}
                  onChange={handleInputChange('organization_name')}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="GST Number"
                  value={formData.gst_number}
                  onChange={handleInputChange('gst_number')}
                  placeholder="22AAAAA0000A1Z5"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Address"
                  value={formData.address}
                  onChange={handleInputChange('address')}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="City"
                  value={formData.city}
                  onChange={handleInputChange('city')}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="State"
                  value={formData.state}
                  onChange={handleInputChange('state')}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  fullWidth
                  label="PIN Code"
                  value={formData.pin_code}
                  onChange={handleInputChange('pin_code')}
                  required
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 3 }}>
              <Button variant="contained" onClick={handleSubmit(onSubmit)}>
                Test Submit
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, p: 3, backgroundColor: 'background.paper', borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          ✅ Floating Label Implementation Summary
        </Typography>
        <Typography variant="body2" component="div">
          <ul>
            <li><strong>LoginForm.tsx</strong> - ✓ Uses proper floating labels with Controller</li>
            <li><strong>AdminUserForm.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>OTPLogin.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>OrganizationForm.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>CompanyDetailsModal.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>AddUserDialog.tsx</strong> - ✓ Uses TextField with label prop (removed redundant "Optional" placeholders)</li>
            <li><strong>AddProductModal.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>AddCustomerModal.tsx</strong> - ✓ Uses TextField with label prop</li>
            <li><strong>All Autocomplete components</strong> - ✓ Use TextField with label prop in renderInput</li>
          </ul>
        </Typography>
      </Box>
    </Container>
  );
};

export default FloatingLabelsTest;