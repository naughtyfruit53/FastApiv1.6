// frontend/src/components/AddAccountModal.tsx
import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useFormik } from "formik";
import * as Yup from "yup";
import api from "@/lib/api";

interface AddAccountModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const accountSchema = Yup.object().shape({
  name: Yup.string()
    .required("Account name is required")
    .min(1, "Name must be at least 1 character")
    .max(200, "Name must be less than 200 characters"),
  type: Yup.string()
    .max(50, "Type must be less than 50 characters")
    .default("customer"),
  industry: Yup.string()
    .max(100, "Industry must be less than 100 characters")
    .nullable(),
  size: Yup.string()
    .max(50, "Size must be less than 50 characters")
    .nullable(),
  revenue: Yup.number()
    .min(0, "Revenue must be positive")
    .nullable(),
  employees: Yup.number()
    .integer("Employees must be a whole number")
    .min(0, "Employees must be positive")
    .nullable(),
  website: Yup.string()
    .url("Invalid website URL")
    .max(200, "Website must be less than 200 characters")
    .nullable(),
  phone: Yup.string()
    .max(20, "Phone must be less than 20 characters")
    .nullable(),
  email: Yup.string()
    .email("Invalid email address")
    .nullable(),
  city: Yup.string()
    .max(100, "City must be less than 100 characters")
    .nullable(),
  state: Yup.string()
    .max(100, "State must be less than 100 characters")
    .nullable(),
  pin_code: Yup.string()
    .max(20, "PIN code must be less than 20 characters")
    .nullable(),
  country: Yup.string()
    .max(100, "Country must be less than 100 characters")
    .nullable(),
  status: Yup.string()
    .max(50, "Status must be less than 50 characters")
    .default("active"),
  source: Yup.string()
    .max(50, "Source must be less than 50 characters")
    .nullable(),
  contact_person: Yup.string()
    .max(100, "Contact person must be less than 100 characters")
    .nullable(),
  contact_number: Yup.string()
    .max(20, "Contact number must be less than 20 characters")
    .nullable(),
});

export const AddAccountModal: React.FC<AddAccountModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const formik = useFormik({
    initialValues: {
      name: "",
      type: "customer",
      industry: "",
      size: "",
      revenue: "",
      employees: "",
      website: "",
      phone: "",
      email: "",
      address1: "",
      address2: "",
      city: "",
      state: "",
      pin_code: "",
      country: "",
      status: "active",
      source: "",
      description: "",
      contact_person: "",
      contact_number: "",
    },
    validationSchema: accountSchema,
    onSubmit: async (values) => {
      setSubmitting(true);
      setError(null);
      
      try {
        const token = localStorage.getItem("access_token");
        
        // Convert string numbers to actual numbers
        const submitData = {
          ...values,
          revenue: values.revenue ? parseFloat(values.revenue as string) : null,
          employees: values.employees ? parseInt(values.employees as string, 10) : null,
        };
        
        await api.post("/accounts", submitData, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        
        if (onSuccess) {
          onSuccess();
        }
        
        formik.resetForm();
        onClose();
      } catch (err: any) {
        console.error("Error creating account:", err);
        setError(
          err.response?.data?.detail || "Failed to create account. Please try again."
        );
      } finally {
        setSubmitting(false);
      }
    },
  });

  const handleClose = () => {
    formik.resetForm();
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Add New Account</DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Account Name"
                name="name"
                required
                value={formik.values.name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Account Type"
                name="type"
                value={formik.values.type}
                onChange={formik.handleChange}
              >
                <MenuItem value="customer">Customer</MenuItem>
                <MenuItem value="prospect">Prospect</MenuItem>
                <MenuItem value="partner">Partner</MenuItem>
                <MenuItem value="vendor">Vendor</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Status"
                name="status"
                value={formik.values.status}
                onChange={formik.handleChange}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="prospect">Prospect</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Industry"
                name="industry"
                value={formik.values.industry}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.industry && Boolean(formik.errors.industry)}
                helperText={formik.touched.industry && formik.errors.industry}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Company Size"
                name="size"
                value={formik.values.size}
                onChange={formik.handleChange}
              >
                <MenuItem value="">Not Specified</MenuItem>
                <MenuItem value="small">Small (1-50 employees)</MenuItem>
                <MenuItem value="medium">Medium (51-500 employees)</MenuItem>
                <MenuItem value="large">Large (501-5000 employees)</MenuItem>
                <MenuItem value="enterprise">Enterprise (5000+ employees)</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Annual Revenue"
                name="revenue"
                type="number"
                value={formik.values.revenue}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.revenue && Boolean(formik.errors.revenue)}
                helperText={formik.touched.revenue && formik.errors.revenue}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Number of Employees"
                name="employees"
                type="number"
                value={formik.values.employees}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.employees && Boolean(formik.errors.employees)}
                helperText={formik.touched.employees && formik.errors.employees}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Website"
                name="website"
                type="url"
                placeholder="https://example.com"
                value={formik.values.website}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.website && Boolean(formik.errors.website)}
                helperText={formik.touched.website && formik.errors.website}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                name="phone"
                value={formik.values.phone}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={formik.touched.phone && formik.errors.phone}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Person"
                name="contact_person"
                value={formik.values.contact_person}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.contact_person && Boolean(formik.errors.contact_person)}
                helperText={formik.touched.contact_person && formik.errors.contact_person}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Number"
                name="contact_number"
                value={formik.values.contact_number}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.contact_number && Boolean(formik.errors.contact_number)}
                helperText={formik.touched.contact_number && formik.errors.contact_number}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address Line 1"
                name="address1"
                value={formik.values.address1}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address Line 2"
                name="address2"
                value={formik.values.address2}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="City"
                name="city"
                value={formik.values.city}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.city && Boolean(formik.errors.city)}
                helperText={formik.touched.city && formik.errors.city}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="State"
                name="state"
                value={formik.values.state}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.state && Boolean(formik.errors.state)}
                helperText={formik.touched.state && formik.errors.state}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="PIN Code"
                name="pin_code"
                value={formik.values.pin_code}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.pin_code && Boolean(formik.errors.pin_code)}
                helperText={formik.touched.pin_code && formik.errors.pin_code}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Country"
                name="country"
                value={formik.values.country}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.country && Boolean(formik.errors.country)}
                helperText={formik.touched.country && formik.errors.country}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Source"
                name="source"
                value={formik.values.source}
                onChange={formik.handleChange}
              >
                <MenuItem value="">Not Specified</MenuItem>
                <MenuItem value="referral">Referral</MenuItem>
                <MenuItem value="website">Website</MenuItem>
                <MenuItem value="social_media">Social Media</MenuItem>
                <MenuItem value="exhibition">Exhibition</MenuItem>
                <MenuItem value="cold_call">Cold Call</MenuItem>
                <MenuItem value="email_campaign">Email Campaign</MenuItem>
                <MenuItem value="partner">Partner</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                name="description"
                value={formik.values.description}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose} disabled={submitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={submitting || !formik.isValid}
          >
            {submitting ? <CircularProgress size={24} /> : "Add Account"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddAccountModal;
