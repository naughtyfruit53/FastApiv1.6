// frontend/src/components/AddContactModal.tsx
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

interface AddContactModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const contactSchema = Yup.object().shape({
  first_name: Yup.string()
    .required("First name is required")
    .min(1, "First name must be at least 1 character")
    .max(100, "First name must be less than 100 characters"),
  last_name: Yup.string()
    .required("Last name is required")
    .min(1, "Last name must be at least 1 character")
    .max(100, "Last name must be less than 100 characters"),
  email: Yup.string()
    .email("Invalid email address")
    .nullable(),
  phone: Yup.string()
    .max(20, "Phone must be less than 20 characters")
    .nullable(),
  mobile: Yup.string()
    .max(20, "Mobile must be less than 20 characters")
    .nullable(),
  job_title: Yup.string()
    .max(100, "Job title must be less than 100 characters")
    .nullable(),
  department: Yup.string()
    .max(100, "Department must be less than 100 characters")
    .nullable(),
  company: Yup.string()
    .max(200, "Company must be less than 200 characters")
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
  source: Yup.string()
    .max(50, "Source must be less than 50 characters")
    .default("manual"),
  status: Yup.string()
    .max(50, "Status must be less than 50 characters")
    .default("active"),
});

export const AddContactModal: React.FC<AddContactModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const formik = useFormik({
    initialValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      mobile: "",
      job_title: "",
      department: "",
      company: "",
      address1: "",
      address2: "",
      city: "",
      state: "",
      pin_code: "",
      country: "",
      source: "manual",
      status: "active",
      notes: "",
    },
    validationSchema: contactSchema,
    onSubmit: async (values) => {
      setSubmitting(true);
      setError(null);
      
      try {
        const token = localStorage.getItem("access_token");
        await api.post("/contacts", values, {
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
        console.error("Error creating contact:", err);
        setError(
          err.response?.data?.detail || "Failed to create contact. Please try again."
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
      <DialogTitle>Add New Contact</DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                name="first_name"
                required
                value={formik.values.first_name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.first_name && Boolean(formik.errors.first_name)}
                helperText={formik.touched.first_name && formik.errors.first_name}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                name="last_name"
                required
                value={formik.values.last_name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.last_name && Boolean(formik.errors.last_name)}
                helperText={formik.touched.last_name && formik.errors.last_name}
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
                label="Mobile"
                name="mobile"
                value={formik.values.mobile}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.mobile && Boolean(formik.errors.mobile)}
                helperText={formik.touched.mobile && formik.errors.mobile}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Job Title"
                name="job_title"
                value={formik.values.job_title}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.job_title && Boolean(formik.errors.job_title)}
                helperText={formik.touched.job_title && formik.errors.job_title}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                name="department"
                value={formik.values.department}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.department && Boolean(formik.errors.department)}
                helperText={formik.touched.department && formik.errors.department}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Company"
                name="company"
                value={formik.values.company}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.company && Boolean(formik.errors.company)}
                helperText={formik.touched.company && formik.errors.company}
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
                label="Status"
                name="status"
                value={formik.values.status}
                onChange={formik.handleChange}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="lead">Lead</MenuItem>
              </TextField>
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
                <MenuItem value="manual">Manual Entry</MenuItem>
                <MenuItem value="website">Website</MenuItem>
                <MenuItem value="referral">Referral</MenuItem>
                <MenuItem value="social_media">Social Media</MenuItem>
                <MenuItem value="exhibition">Exhibition</MenuItem>
                <MenuItem value="cold_call">Cold Call</MenuItem>
                <MenuItem value="email_campaign">Email Campaign</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes"
                name="notes"
                value={formik.values.notes}
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
            {submitting ? <CircularProgress size={24} /> : "Add Contact"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddContactModal;
