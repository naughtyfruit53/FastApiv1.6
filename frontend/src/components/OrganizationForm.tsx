'use client';

import React, { useState } from 'react';
import { TextField, Button, CircularProgress, Grid, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import axios from 'axios';

// State to GST state code map (mirrored from backend for autofill)
const STATE_CODE_MAP: { [key: string]: string } = {
  "Andaman & Nicobar Islands": "35",
  "Andhra Pradesh": "37",
  "Arunachal Pradesh": "12",
  "Assam": "18",
  "Bihar": "10",
  "Chandigarh": "04",
  "Chhattisgarh": "22",
  "Dadra & Nagar Haveli & Daman & Diu": "26",
  "Delhi": "07",
  "Goa": "30",
  "Gujarat": "24",
  "Haryana": "06",
  "Himachal Pradesh": "02",
  "Jammu & Kashmir": "01",
  "Jharkhand": "20",
  "Karnataka": "29",
  "Kerala": "32",
  "Ladakh": "38",
  "Lakshadweep": "31",
  "Madhya Pradesh": "23",
  "Maharashtra": "27",
  "Manipur": "14",
  "Meghalaya": "17",
  "Mizoram": "15",
  "Nagaland": "13",
  "Odisha": "21",
  "Puducherry": "34",
  "Punjab": "03",
  "Rajasthan": "08",
  "Sikkim": "11",
  "Tamil Nadu": "33",
  "Telangana": "36",
  "Tripura": "16",
  "Uttar Pradesh": "09",
  "Uttarakhand": "05",
  "West Bengal": "19",
  "Other Territory": "97",
  "Other Country": "99"
};

interface FormData {
  name?: string; // For direct organization creation
  subdomain?: string; // For direct organization creation
  organization_name?: string; // For license creation
  admin_password?: string; // For license creation
  superadmin_email?: string; // For license creation
  primary_email?: string; // For direct organization creation
  primary_phone: string;
  address1?: string; // For license creation
  address?: string; // For direct organization creation
  city: string;
  state: string;
  pin_code: string;
  state_code: string;
  gst_number: string;
  business_type?: string;
  industry?: string;
  website?: string;
  description?: string;
  max_users?: number;
}

interface OrganizationFormProps {
  onSubmit: (data: FormData) => void;
  mode?: 'license' | 'create'; // license = create license, create = direct org creation
  initialData?: Partial<FormData>;
  isEditing?: boolean;
}

const OrganizationForm: React.FC<OrganizationFormProps> = ({ 
  onSubmit, 
  mode = 'license',
  initialData = {},
  isEditing = false 
}) => {
  const [formData, setFormData] = useState<FormData>({
    organization_name: '',
    name: '',
    subdomain: '',
    admin_password: '',
    superadmin_email: '',
    primary_email: '',
    primary_phone: '',
    address1: '',
    address: '',
    city: '',
    state: '',
    pin_code: '',
    state_code: '',
    gst_number: '',
    business_type: '',
    industry: '',
    website: '',
    description: '',
    max_users: 5,
    ...initialData
  });
  const [pincodeLoading, setPincodeLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | { target: { name: string; value: unknown } }) => {
    const name = e.target.name as string;
    const value = e.target.value as string;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
      ...(name === 'state' ? { state_code: STATE_CODE_MAP[value] || '' } : {}),  // Autofill state_code based on state change
    }));
  };

  const handlePincodeChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    handleChange(e);
    if (value.length === 6) {
      setPincodeLoading(true);
      try {
        const response = await axios.get(`/api/pincode/lookup/${value}`);
        const { city, state, state_code } = response.data;
        setFormData((prev) => ({
          ...prev,
          city,
          state,
          state_code
        }));
      } catch (error) {
        console.error('Failed to lookup pincode:', error);
      } finally {
        setPincodeLoading(false);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Transform data based on mode
    let submitData = { ...formData };
    
    if (mode === 'create') {
      // For direct organization creation, map fields appropriately
      submitData = {
        name: formData.name || formData.organization_name,
        subdomain: formData.subdomain,
        primary_email: formData.primary_email || formData.superadmin_email,
        primary_phone: formData.primary_phone,
        address1: formData.address || formData.address1,
        city: formData.city,
        state: formData.state,
        pin_code: formData.pin_code,
        state_code: formData.state_code,
        gst_number: formData.gst_number,
        business_type: formData.business_type,
        industry: formData.industry,
        website: formData.website,
        description: formData.description,
        max_users: formData.max_users
      };
    }
    
    onSubmit(submitData);
  };

  const isLicenseMode = mode === 'license';

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Organization Name"
            name={isLicenseMode ? "organization_name" : "name"}
            value={isLicenseMode ? formData.organization_name : formData.name}
            onChange={handleChange}
            required
          />
        </Grid>
        
        {!isLicenseMode && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Subdomain"
              name="subdomain"
              value={formData.subdomain}
              onChange={handleChange}
              helperText="Used for organization-specific URLs"
              required
            />
          </Grid>
        )}
        
        {isLicenseMode && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Admin Password"
              name="admin_password"
              type="password"
              value={formData.admin_password}
              onChange={handleChange}
              required={!isEditing}
            />
          </Grid>
        )}
        
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Primary Email"
            name={isLicenseMode ? "superadmin_email" : "primary_email"}
            type="email"
            value={isLicenseMode ? formData.superadmin_email : formData.primary_email}
            onChange={handleChange}
            required
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Primary Phone"
            name="primary_phone"
            value={formData.primary_phone}
            onChange={handleChange}
            required
          />
        </Grid>
        
        {!isLicenseMode && (
          <>
            <Grid size={{ xs: 12, sm: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Business Type</InputLabel>
                <Select
                  name="business_type"
                  value={formData.business_type || ''}
                  label="Business Type"
                  onChange={handleChange}
                >
                  <MenuItem value="Manufacturing">Manufacturing</MenuItem>
                  <MenuItem value="Trading">Trading</MenuItem>
                  <MenuItem value="Service">Service</MenuItem>
                  <MenuItem value="Retail">Retail</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Industry"
                name="industry"
                value={formData.industry}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Website"
                name="website"
                type="url"
                value={formData.website}
                onChange={handleChange}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Max Users"
                name="max_users"
                type="number"
                value={formData.max_users}
                onChange={handleChange}
                inputProps={{ min: 1, max: 1000 }}
              />
            </Grid>
          </>
        )}
        
        <Grid size={12}>
          <TextField
            fullWidth
            label="Address"
            name={isLicenseMode ? "address1" : "address"}
            value={isLicenseMode ? formData.address1 : formData.address}
            onChange={handleChange}
            required
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField
            fullWidth
            label="City"
            name="city"
            value={formData.city}
            onChange={handleChange}
            required
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField
            fullWidth
            label="State"
            name="state"
            value={formData.state}
            onChange={handleChange}
            required
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField
            fullWidth
            label="PIN Code"
            name="pin_code"
            value={formData.pin_code}
            onChange={handlePincodeChange}
            required
            InputProps={{
              endAdornment: pincodeLoading ? <CircularProgress size={20} /> : null,
            }}
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="State Code"
            name="state_code"
            value={formData.state_code}
            onChange={handleChange}
            disabled  // Autofilled, so disabled for user input
          />
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="GST No."
            name="gst_number"
            value={formData.gst_number}
            onChange={handleChange}
          />
        </Grid>
        
        {!isLicenseMode && (
          <Grid size={12}>
            <TextField
              fullWidth
              label="Description"
              name="description"
              multiline
              rows={3}
              value={formData.description}
              onChange={handleChange}
            />
          </Grid>
        )}
        
        <Grid size={12}>
          <Button type="submit" variant="contained" color="primary">
            {isEditing ? 'Update Organization' : (isLicenseMode ? 'Create License' : 'Create Organization')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default OrganizationForm;