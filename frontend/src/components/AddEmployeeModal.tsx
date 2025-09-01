import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Paper,
  LinearProgress,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { CloudUpload, Description, Delete as DeleteIcon } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { usePincodeLookup } from '../hooks/usePincodeLookup';
import api from '../lib/api';
interface AddEmployeeModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (_data: any) => Promise<void>;
  loading?: boolean;
  initialData?: any;
  mode: 'create' | 'edit';
}
interface EmployeeFormData {
  full_name: string;
  email: string;
  phone: string;
  date_of_birth?: string;
  gender?: string;
  employee_code: string;
  employee_type: string;
  hire_date?: string;
  job_title?: string;
  department?: string;
  work_location?: string;
  reporting_manager_id?: number;
  pan_number?: string;
  aadhaar_number?: string;
  passport_number?: string;
  driving_license?: string;
  bank_account_number?: string;
  bank_name?: string;
  ifsc_code?: string;
  bank_branch?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pin_code?: string;
  country?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
}
const AddEmployeeModal: React.FC<AddEmployeeModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false,
  initialData,
  mode,
}) => {
  const fileInputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ];
  const [documents, setDocuments] = useState<
    Array<{ file: File | null; type: string; extractedData?: any; loading: boolean; error?: string }>
  >(
    Array.from({ length: 5 }, () => ({
      file: null,
      type: '',
      extractedData: null,
      loading: false,
      error: undefined,
    }))
  );
  const [tabValue, setTabValue] = useState(0);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
    control,
  } = useForm<EmployeeFormData>({
    defaultValues: initialData || {
      full_name: '',
      email: '',
      phone: '',
      employee_code: '',
      employee_type: 'permanent',
      gender: '',
      country: 'India',
    },
  });
  const { lookupPincode, pincodeData, loading: pincodeLoading, error: pincodeError, clearData } = usePincodeLookup();
  const watchedPincode = watch('pin_code');
  useEffect(() => {
    if (pincodeData) {
      setValue('city', pincodeData.city);
      setValue('state', pincodeData.state);
    }
  }, [pincodeData, setValue]);
  useEffect(() => {
    if (watchedPincode && /^\d{6}$/.test(watchedPincode)) {
      const timeoutId = setTimeout(() => {
        lookupPincode(watchedPincode);
      }, 500);
      return () => clearTimeout(timeoutId);
    } else {
      clearData();
    }
  }, [watchedPincode, lookupPincode, clearData]);
  const handleDocumentUpload = async (index: number, file: File) => {
    const updatedDocs = [...documents];
    updatedDocs[index] = { ...updatedDocs[index], loading: true, error: undefined };
    setDocuments(updatedDocs);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', updatedDocs[index].type || 'general');
      const response: { data: { success: boolean; extracted_data?: any; detail?: string } } = await api.post(
        '/pdf-extraction/extract/employee',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );
      if (response.data.success) {
        const extractedData = response.data.extracted_data;
        Object.entries(extractedData).forEach(([key, value]) => {
          if (value) {setValue(key as keyof EmployeeFormData, value as string);}
        });
        updatedDocs[index] = { ...updatedDocs[index], file, extractedData, loading: false };
      } else {
        throw new globalThis.Error(response.data.detail || 'Extraction failed');
      }
    } catch (error: any) {
      updatedDocs[index] = {
        ...updatedDocs[index],
        loading: false,
        error: error.message || 'Failed to process document',
      };
    }
    setDocuments(updatedDocs);
  };
  const handleFileChange = (index: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {return alert('Please upload a PDF file');}
      if (file.size > 10 * 1024 * 1024) {return alert('File size should be less than 10MB');}
      handleDocumentUpload(index, file);
    }
  };
  const triggerUpload = (index: number) => {
    fileInputRefs[index].current?.click();
  };
  const removeDocument = (index: number) => {
    const updatedDocs = [...documents];
    updatedDocs[index] = { file: null, type: '', extractedData: null, loading: false, error: undefined };
    setDocuments(updatedDocs);
  };
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  const onSubmit = async (employeeData: EmployeeFormData) => {
    try {
      const formData = new FormData();
      Object.entries(employeeData).forEach(([key, value]) => {
        formData.append(key, value as string);
      });
      documents.forEach((doc, index) => {
        if (doc.file) {
          formData.append(`documents_${index}`, doc.file);
          formData.append(`document_types_${index}`, doc.type);
        }
      });
      const endpoint = mode === 'create' ? '/hr/employees' : `/hr/employees/${initialData?.id}`;
      const method = mode === 'create' ? 'post' : 'put';
      const response = await api[method](endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await onAdd(response.data);
      reset();
      onClose();
    } catch (error: any) {
      console.error('Error saving employee:', error);
      alert(error.response?.data?.detail || 'Failed to save employee');
    }
  };
  const handleClose = () => {
    reset();
    clearData();
    setDocuments(
      Array.from({ length: 5 }, () => ({
        file: null,
        type: '',
        extractedData: null,
        loading: false,
        error: undefined,
      }))
    );
    onClose();
  };
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">{mode === 'create' ? 'Add New Employee' : 'Edit Employee'}</Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Personal Details" />
            <Tab label="Employment Details" />
            <Tab label="KYC & Bank" />
            <Tab label="Address & Emergency" />
          </Tabs>
          {tabValue === 0 && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Full Name *"
                  {...register('full_name', { required: 'Full name is required' })}
                  error={!!errors.full_name}
                  helperText={errors.full_name?.message}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Email *"
                  type="email"
                  {...register('email', { required: 'Email is required' })}
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Phone Number"
                  {...register('phone')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  {...register('date_of_birth')}
                  InputLabelProps={{ shrink: true }}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Gender</InputLabel>
                  <Controller
                    name="gender"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Gender">
                        <MenuItem value="male">Male</MenuItem>
                        <MenuItem value="female">Female</MenuItem>
                        <MenuItem value="other">Other</MenuItem>
                        <MenuItem value="prefer_not_to_say">Prefer not to say</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
            </Grid>
          )}
          {tabValue === 1 && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Employee Code *"
                  {...register('employee_code', { required: 'Employee code is required' })}
                  error={!!errors.employee_code}
                  helperText={errors.employee_code?.message}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Employee Type</InputLabel>
                  <Controller
                    name="employee_type"
                    control={control}
                    render={({ field }) => (
                      <Select {...field} label="Employee Type">
                        <MenuItem value="permanent">Permanent</MenuItem>
                        <MenuItem value="contract">Contract</MenuItem>
                        <MenuItem value="intern">Intern</MenuItem>
                        <MenuItem value="consultant">Consultant</MenuItem>
                      </Select>
                    )}
                  />
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Hire Date"
                  type="date"
                  {...register('hire_date')}
                  InputLabelProps={{ shrink: true }}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Job Title"
                  {...register('job_title')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Department"
                  {...register('department')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Work Location"
                  {...register('work_location')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Reporting Manager ID"
                  type="number"
                  {...register('reporting_manager_id')}
                  margin="normal"
                />
              </Grid>
            </Grid>
          )}
          {tabValue === 2 && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="PAN Number"
                  {...register('pan_number')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Aadhaar Number"
                  {...register('aadhaar_number')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Passport Number"
                  {...register('passport_number')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Driving License"
                  {...register('driving_license')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Bank Account Number"
                  {...register('bank_account_number')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Bank Name"
                  {...register('bank_name')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="IFSC Code"
                  {...register('ifsc_code')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Bank Branch"
                  {...register('bank_branch')}
                  margin="normal"
                />
              </Grid>
              <Grid size={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Upload Documents (up to 5 PDFs)
                </Typography>
                {documents.map((doc, index) => (
                  <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <FormControl fullWidth>
                        <InputLabel>Document Type</InputLabel>
                        <Select
                          value={doc.type}
                          label="Document Type"
                          onChange={(e) => {
                            const updated = [...documents];
                            updated[index].type = e.target.value as string;
                            setDocuments(updated);
                          }}
                        >
                          <MenuItem value="aadhaar">Aadhaar</MenuItem>
                          <MenuItem value="pan">PAN</MenuItem>
                          <MenuItem value="passport">Passport</MenuItem>
                          <MenuItem value="driving_license">Driving License</MenuItem>
                          <MenuItem value="bank_passbook">Bank Passbook</MenuItem>
                          <MenuItem value="other">Other</MenuItem>
                        </Select>
                      </FormControl>
                      <Button variant="outlined" startIcon={<CloudUpload />} onClick={() => triggerUpload(index)}>
                        Upload PDF
                      </Button>
                      <input
                        ref={fileInputRefs[index]}
                        type="file"
                        accept=".pdf"
                        style={{ display: 'none' }}
                        onChange={(e) => handleFileChange(index, e)}
                      />
                    </Box>
                    {doc.loading && <LinearProgress sx={{ mt: 1 }} />}
                    {doc.file && (
                      <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Description />
                        <Typography>{doc.file.name}</Typography>
                        <IconButton color="error" onClick={() => removeDocument(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    )}
                    {doc.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {doc.error}
                      </Alert>
                    )}
                    {doc.extractedData && (
                      <Alert severity="success" sx={{ mt: 1 }}>
                        Extracted: {Object.keys(doc.extractedData).join(', ')}
                      </Alert>
                    )}
                  </Paper>
                ))}
              </Grid>
            </Grid>
          )}
          {tabValue === 3 && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Address Line 1"
                  {...register('address_line1')}
                  margin="normal"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Address Line 2"
                  {...register('address_line2')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  fullWidth
                  label="PIN Code"
                  {...register('pin_code')}
                  error={!!pincodeError}
                  helperText={pincodeError}
                  margin="normal"
                  InputProps={{
                    endAdornment: pincodeLoading ? <CircularProgress size={16} /> : null,
                  }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  fullWidth
                  label="City"
                  {...register('city')}
                  margin="normal"
                  InputProps={{ readOnly: !!pincodeData }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  fullWidth
                  label="State"
                  {...register('state')}
                  margin="normal"
                  InputProps={{ readOnly: !!pincodeData }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Country"
                  {...register('country')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Name"
                  {...register('emergency_contact_name')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Phone"
                  {...register('emergency_contact_phone')}
                  margin="normal"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  fullWidth
                  label="Emergency Contact Relation"
                  {...register('emergency_contact_relation')}
                  margin="normal"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : mode === 'create' ? 'Add Employee' : 'Update Employee'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
export default AddEmployeeModal;