// frontend/src/pages/settings/company.tsx

import React, { useState } from "react";
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
  CircularProgress,
} from "@mui/material";
import { Business, Save, Upload } from "@mui/icons-material";
import { useForm, Controller } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companyService } from "../../services/authService";
import { toast } from "react-toastify";
import DashboardLayout from "../../components/DashboardLayout";

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const CompanyProfilePage: React.FC = () => {
  const queryClient = useQueryClient();
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  const { data: company, isLoading: isFetching } = useQuery({
    queryKey: ["currentCompany"],
    queryFn: companyService.getCurrentCompany,
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => companyService.updateCompany(company?.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentCompany"] });
      toast.success("Company details updated successfully!");
    },
    onError: (error: any) => {
      toast.error(`Failed to update company: ${error.message}`);
    },
  });

  const uploadLogoMutation = useMutation({
    mutationFn: (formData: FormData) => companyService.uploadCompanyLogo(company?.id, formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentCompany"] });
      toast.success("Logo uploaded successfully!");
      setLogoFile(null);
      setLogoPreview(null);
    },
    onError: (error: any) => {
      toast.error(`Failed to upload logo: ${error.message}`);
    },
  });

  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      name: "",
      address1: "",
      address2: "",
      city: "",
      state: "",
      pin_code: "",
      state_code: "",
      contact_number: "",
      email: "",
      gst_number: "",
      pan_number: "",
      registration_number: "",
      business_type: "",
      industry: "",
      website: "",
    },
  });

  React.useEffect(() => {
    if (company) {
      reset({
        name: company.name || "",
        address1: company.address1 || "",
        address2: company.address2 || "",
        city: company.city || "",
        state: company.state || "",
        pin_code: company.pin_code || "",
        state_code: company.state_code || "",
        contact_number: company.contact_number || "",
        email: company.email || "",
        gst_number: company.gst_number || "",
        pan_number: company.pan_number || "",
        registration_number: company.registration_number || "",
        business_type: company.business_type || "",
        industry: company.industry || "",
        website: company.website || "",
      });
      if (company.logo_path) {
        setLogoPreview(`${API_URL}${company.logo_path}`);
      }
    }
  }, [company, reset]);

  const onSubmit = (data: any) => {
    updateMutation.mutate(data);
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Logo file size must be less than 5MB");
        return;
      }
      if (!file.type.startsWith('image/')) {
        toast.error("Only image files are allowed");
        return;
      }
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadLogo = () => {
    if (logoFile && company?.id) {
      const formData = new FormData();
      formData.append('file', logoFile);
      uploadLogoMutation.mutate(formData);
    }
  };

  if (isFetching) {
    return (
      <DashboardLayout title="Company Profile">
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      </DashboardLayout>
    );
  }

  if (!company) {
    return (
      <DashboardLayout title="Company Profile">
        <Alert severity="error">Failed to load company details. Please try refreshing.</Alert>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Company Profile"
      subtitle="Manage your organization's information and settings"
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Update your company details to ensure accurate business information across all modules. Fields marked with * are required.
          </Alert>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Business sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Company Information</Typography>
              </Box>
              
              <form onSubmit={handleSubmit(onSubmit)}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="name"
                      control={control}
                      rules={{ required: "Company Name is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Company Name *"
                          variant="outlined"
                          error={!!errors.name}
                          helperText={errors.name?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="registration_number"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Registration Number"
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="gst_number"
                      control={control}
                      rules={{ required: "GST Number is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="GST Number *"
                          variant="outlined"
                          error={!!errors.gst_number}
                          helperText={errors.gst_number?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="pan_number"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="PAN Number"
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="business_type"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Business Type"
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="industry"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Industry"
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Controller
                      name="address1"
                      control={control}
                      rules={{ required: "Address Line 1 is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Address Line 1 *"
                          multiline
                          rows={2}
                          variant="outlined"
                          error={!!errors.address1}
                          helperText={errors.address1?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Controller
                      name="address2"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Address Line 2"
                          multiline
                          rows={2}
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="city"
                      control={control}
                      rules={{ required: "City is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="City *"
                          variant="outlined"
                          error={!!errors.city}
                          helperText={errors.city?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="state"
                      control={control}
                      rules={{ required: "State is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="State *"
                          variant="outlined"
                          error={!!errors.state}
                          helperText={errors.state?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="pin_code"
                      control={control}
                      rules={{ required: "Pin Code is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Pin Code *"
                          variant="outlined"
                          error={!!errors.pin_code}
                          helperText={errors.pin_code?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="state_code"
                      control={control}
                      rules={{ required: "State Code is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="State Code *"
                          variant="outlined"
                          error={!!errors.state_code}
                          helperText={errors.state_code?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="contact_number"
                      control={control}
                      rules={{ required: "Contact Number is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Contact Number *"
                          variant="outlined"
                          error={!!errors.contact_number}
                          helperText={errors.contact_number?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="email"
                      control={control}
                      rules={{ required: "Email is required" }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Email *"
                          type="email"
                          variant="outlined"
                          error={!!errors.email}
                          helperText={errors.email?.message as string}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Controller
                      name="website"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Website"
                          variant="outlined"
                        />
                      )}
                    />
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 3 }} />
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    type="submit"
                    variant="contained" 
                    startIcon={<Save />}
                    sx={{ minWidth: 120 }}
                    disabled={updateMutation.isPending}
                  >
                    {updateMutation.isPending ? <CircularProgress size={20} /> : "Save Changes"}
                  </Button>
                </Box>
              </form>
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
                justifyContent: 'center',
                alignItems: 'center'
              }}>
                {logoPreview ? (
                  <img 
                    src={logoPreview} 
                    alt="Logo Preview" 
                    style={{ maxWidth: '100%', maxHeight: 150, marginBottom: 16 }} 
                  />
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    No logo uploaded yet
                  </Typography>
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoChange}
                  style={{ display: 'none' }}
                  id="logo-upload"
                />
                <label htmlFor="logo-upload">
                  <Button variant="outlined" component="span" startIcon={<Upload />}>
                    Select Logo
                  </Button>
                </label>
              </Box>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                Recommended size: 200x200px, Max: 5MB, Formats: PNG/JPG
              </Typography>
              {logoFile && (
                <Button 
                  variant="contained" 
                  onClick={handleUploadLogo}
                  sx={{ mt: 2 }}
                  disabled={uploadLogoMutation.isPending}
                >
                  {uploadLogoMutation.isPending ? <CircularProgress size={20} /> : "Upload Logo"}
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default CompanyProfilePage;