// pages/hr/employees.tsx
// Employee Management Page with CRUD operations

import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Tooltip,
  InputAdornment,
  Pagination,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  ContactPhone as ContactIcon,
  AccountBalance as BankIcon,
  PhotoCamera as PhotoCameraIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useAuth } from '../../hooks/useAuth';
import { hrService, Employee } from '../../services';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`employee-tabpanel-${index}`}
      aria-labelledby={`employee-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `employee-tab-${index}`,
    'aria-controls': `employee-tabpanel-${index}`,
  };
}

const EmployeesManagement: NextPage = () => {
  const router = useRouter();
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [dialogTabValue, setDialogTabValue] = useState(0);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [page, setPage] = useState(1);
  const [rowsPerPage] = useState(10);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError(null);
      const employeesData = await hrService.getEmployees();
      setEmployees(employeesData);
    } catch (err: any) {
      console.error('Error fetching employees:', err);
      setError(err.userMessage || 'Failed to load employees');
      setEmployees([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1);
  };

  const handleFilterDepartment = (event: any) => {
    setFilterDepartment(event.target.value);
    setPage(1);
  };

  const handleFilterStatus = (event: any) => {
    setFilterStatus(event.target.value);
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleViewEmployee = (employee: any) => {
    setSelectedEmployee(employee);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleEditEmployee = (employee: any) => {
    setSelectedEmployee(employee);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleCreateEmployee = () => {
    setSelectedEmployee(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedEmployee(null);
    setDialogTabValue(0); // Reset dialog tab to first tab
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'resigned':
        return 'warning';
      case 'terminated':
        return 'error';
      case 'on_leave':
        return 'info';
      default:
        return 'default';
    }
  };

  const getEmployeeTypeColor = (type: string) => {
    switch (type) {
      case 'permanent':
        return 'primary';
      case 'contract':
        return 'secondary';
      case 'intern':
        return 'info';
      case 'consultant':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Filter employees based on search and filters
  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = (employee.user?.full_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.employee_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (employee.user?.email || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const employeeDept = employee.department || employee.user?.department;
    const matchesDepartment = !filterDepartment || employeeDept === filterDepartment;
    const matchesStatus = !filterStatus || employee.employment_status === filterStatus;
    
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  // Paginate results
  const paginatedEmployees = filteredEmployees.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const totalPages = Math.ceil(filteredEmployees.length / rowsPerPage);

  // Get unique departments for filter
  const departments = [...new Set(employees.map(emp => emp.department || emp.user?.department).filter(Boolean))];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Employee Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
          >
            Import
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
          >
            Export
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateEmployee}
          >
            Add Employee
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button size="small" onClick={fetchEmployees} sx={{ ml: 1 }}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Employees
                  </Typography>
                  <Typography variant="h4">
                    {employees.length}
                  </Typography>
                </Box>
                <PersonIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {employees.filter(emp => emp.employment_status === 'active').length}
                  </Typography>
                </Box>
                <WorkIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Permanent
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {employees.filter(emp => emp.employee_type === 'permanent').length}
                  </Typography>
                </Box>
                <BankIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Contract
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {employees.filter(emp => emp.employee_type === 'contract').length}
                  </Typography>
                </Box>
                <ContactIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Search */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search employees..."
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Department</InputLabel>
              <Select
                value={filterDepartment}
                label="Department"
                onChange={handleFilterDepartment}
              >
                <MenuItem value="">All Departments</MenuItem>
                {departments.map((dept) => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={handleFilterStatus}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="resigned">Resigned</MenuItem>
                <MenuItem value="terminated">Terminated</MenuItem>
                <MenuItem value="on_leave">On Leave</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterIcon />}
              sx={{ height: '56px' }}
            >
              More Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Employees Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Employee Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Job Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Hire Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                paginatedEmployees.map((employee) => (
                  <TableRow key={employee.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {employee.employee_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {employee.user?.full_name || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {employee.user?.email || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {employee.department || employee.user?.department || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {employee.position || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={employee.employee_type}
                        color={getEmployeeTypeColor(employee.employee_type) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={employee.employment_status}
                        color={getStatusColor(employee.employment_status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {employee.hire_date}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View">
                          <IconButton
                            size="small"
                            onClick={() => handleViewEmployee(employee)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => handleEditEmployee(employee)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
          <Typography variant="body2" color="textSecondary">
            Showing {((page - 1) * rowsPerPage) + 1} to {Math.min(page * rowsPerPage, filteredEmployees.length)} of {filteredEmployees.length} entries
          </Typography>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      </Paper>

      {/* Employee Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Add New Employee' : 
           dialogMode === 'edit' ? 'Edit Employee' : 'Employee Details'}
        </DialogTitle>
        <DialogContent>
          {selectedEmployee && (
            <Box sx={{ mt: 2 }}>
              <Tabs value={dialogTabValue} onChange={(e, newValue) => setDialogTabValue(newValue)}>
                <Tab label="Basic Information" />
                <Tab label="Employment Details" />
                <Tab label="KYC Documents" />
                <Tab label="Contact & Address" />
              </Tabs>
              
              {/* Basic Information Tab */}
              {dialogTabValue === 0 && (
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Employee Code"
                        value={selectedEmployee.employee_code}
                        disabled={dialogMode === 'view'}
                        helperText="Auto-generated if empty"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Full Name"
                        value={selectedEmployee.user.full_name}
                        disabled={dialogMode === 'view'}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        value={selectedEmployee.user.email}
                        disabled={dialogMode === 'view'}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Phone Number"
                        value={selectedEmployee.phone || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Date of Birth"
                        type="date"
                        value={selectedEmployee.date_of_birth || ''}
                        disabled={dialogMode === 'view'}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth disabled={dialogMode === 'view'}>
                        <InputLabel>Gender</InputLabel>
                        <Select value={selectedEmployee.gender || ''} label="Gender">
                          <MenuItem value="male">Male</MenuItem>
                          <MenuItem value="female">Female</MenuItem>
                          <MenuItem value="other">Other</MenuItem>
                          <MenuItem value="prefer_not_to_say">Prefer not to say</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {/* Employment Details Tab */}
              {dialogTabValue === 1 && (
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Department"
                        value={selectedEmployee.user.department}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Job Title"
                        value={selectedEmployee.job_title}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth disabled={dialogMode === 'view'}>
                        <InputLabel>Employee Type</InputLabel>
                        <Select
                          value={selectedEmployee.employee_type}
                          label="Employee Type"
                        >
                          <MenuItem value="permanent">Permanent</MenuItem>
                          <MenuItem value="contract">Contract</MenuItem>
                          <MenuItem value="intern">Intern</MenuItem>
                          <MenuItem value="consultant">Consultant</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Work Location"
                        value={selectedEmployee.work_location}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Hire Date"
                        type="date"
                        value={selectedEmployee.hire_date}
                        disabled={dialogMode === 'view'}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Reporting Manager"
                        value={selectedEmployee.reporting_manager || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Salary"
                        type="number"
                        value={selectedEmployee.salary || ''}
                        disabled={dialogMode === 'view'}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth disabled={dialogMode === 'view'}>
                        <InputLabel>Employment Status</InputLabel>
                        <Select value={selectedEmployee.employment_status || 'active'} label="Employment Status">
                          <MenuItem value="active">Active</MenuItem>
                          <MenuItem value="inactive">Inactive</MenuItem>
                          <MenuItem value="terminated">Terminated</MenuItem>
                          <MenuItem value="on_leave">On Leave</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {/* KYC Documents Tab */}
              {dialogTabValue === 2 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom color="primary">
                    KYC Documents (Indian Requirements)
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Aadhaar Number"
                        value={selectedEmployee.aadhaar_number || ''}
                        disabled={dialogMode === 'view'}
                        inputProps={{ maxLength: 12 }}
                        helperText="12-digit Aadhaar number"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="PAN Number"
                        value={selectedEmployee.pan_number || ''}
                        disabled={dialogMode === 'view'}
                        inputProps={{ maxLength: 10 }}
                        helperText="10-character PAN number"
                        style={{ textTransform: 'uppercase' }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Employee State Insurance (ESI) Number"
                        value={selectedEmployee.esi_number || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Provident Fund (PF) Number"
                        value={selectedEmployee.pf_number || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="UAN (Universal Account Number)"
                        value={selectedEmployee.uan_number || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Driving License Number"
                        value={selectedEmployee.driving_license || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Passport Number"
                        value={selectedEmployee.passport_number || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Bank Account Number"
                        value={selectedEmployee.bank_account || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="IFSC Code"
                        value={selectedEmployee.ifsc_code || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Bank Name"
                        value={selectedEmployee.bank_name || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    
                    {/* Document Upload Section */}
                    <Grid item xs={12}>
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                        Document Uploads
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                          <Button
                            variant="outlined"
                            component="label"
                            fullWidth
                            disabled={dialogMode === 'view'}
                            startIcon={<UploadIcon />}
                          >
                            Upload Aadhaar Card
                            <input type="file" hidden accept=".pdf,.jpg,.jpeg,.png" />
                          </Button>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Button
                            variant="outlined"
                            component="label"
                            fullWidth
                            disabled={dialogMode === 'view'}
                            startIcon={<UploadIcon />}
                          >
                            Upload PAN Card
                            <input type="file" hidden accept=".pdf,.jpg,.jpeg,.png" />
                          </Button>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Button
                            variant="outlined"
                            component="label"
                            fullWidth
                            disabled={dialogMode === 'view'}
                            startIcon={<PhotoCameraIcon />}
                          >
                            Upload Photo
                            <input type="file" hidden accept=".jpg,.jpeg,.png" />
                          </Button>
                        </Grid>
                      </Grid>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {/* Contact & Address Tab */}
              {dialogTabValue === 3 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Contact Information
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Emergency Contact Name"
                        value={selectedEmployee.emergency_contact_name || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Emergency Contact Number"
                        value={selectedEmployee.emergency_contact_phone || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Relationship"
                        value={selectedEmployee.emergency_contact_relation || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                  </Grid>
                  
                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    Current Address
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Address Line 1"
                        value={selectedEmployee.address_line1 || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Address Line 2"
                        value={selectedEmployee.address_line2 || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="City"
                        value={selectedEmployee.city || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="State"
                        value={selectedEmployee.state || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="PIN Code"
                        value={selectedEmployee.pin_code || ''}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Country"
                        value={selectedEmployee.country || 'India'}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                  </Grid>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === 'view' ? 'Close' : 'Cancel'}
          </Button>
          {dialogMode !== 'view' && (
            <Button variant="contained" onClick={handleCloseDialog}>
              {dialogMode === 'create' ? 'Create' : 'Save'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EmployeesManagement;