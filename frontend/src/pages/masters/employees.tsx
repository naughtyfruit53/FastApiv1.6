import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Grid,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Email,
  Phone,
  Search,
  Person
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEmployees, createEmployee } from '../../services/masterService';
import AddEmployeeModal from '../../components/AddEmployeeModal';
const EmployeesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    employee_id: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    department: '',
    designation: '',
    salary: 0
  });
  const queryClient = useQueryClient();
  // Fetch employees
  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees', searchTerm],
    queryFn: getEmployees
  });
  // Create employee mutation
  const createMutation = useMutation({
    mutationFn: createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setAddModalOpen(false);
      resetForm();
    },
    onError: (error: any) => {
      console.error('Error creating employee:', error);
    }
  });
  const resetForm = () => {
    setFormData({
      name: '',
      employee_id: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      department: '',
      designation: '',
      salary: 0
    });
  };
  const handleAddClick = () => {
    resetForm();
    setAddModalOpen(true);
  };
  const handleEditClick = (employee: any) => {
    setSelectedEmployee(employee);
    setFormData({
      name: employee.name || '',
      employee_id: employee.employee_id || '',
      email: employee.email || '',
      phone: employee.phone || '',
      address: employee.address || '',
      city: employee.city || '',
      state: employee.state || '',
      pincode: employee.pincode || '',
      department: employee.department || '',
      designation: employee.designation || '',
      salary: employee.salary || 0
    });
    setEditDialog(true);
  };
  const handleSubmit = () => {
    if (selectedEmployee) {
      // TODO: Implement update mutation
      console.log('Update employee:', selectedEmployee.id, formData);
    } else {
      createMutation.mutate(formData);
    }
  };
  const handleDeleteClick = (employee: any) => {
    // TODO: Implement delete functionality
    console.log('Delete employee:', employee.id);
  };
  const handleAddEmployee = async (data: any) => {
    createMutation.mutate(data);
  };
  const filteredEmployees = employees?.filter((employee: any) =>
    employee.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    employee.employee_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    employee.department?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Employees
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Employee
          </Button>
        </Box>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search employees by name, ID, or department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>
        {isLoading ? (
          <Typography>Loading employees...</Typography>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Employee ID</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Designation</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredEmployees.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 3 }}>
                        <Person sx={{ fontSize: 48, color: 'action.disabled', mb: 2 }} />
                        <Typography variant="h6" color="textSecondary">
                          No employees found
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Add your first employee to get started
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredEmployees.map((employee: any) => (
                    <TableRow key={employee.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                            {employee.name?.charAt(0) || '?'}
                          </Avatar>
                          {employee.name}
                        </Box>
                      </TableCell>
                      <TableCell>{employee.employee_id || 'N/A'}</TableCell>
                      <TableCell>{employee.department || 'N/A'}</TableCell>
                      <TableCell>{employee.designation || 'N/A'}</TableCell>
                      <TableCell>{employee.email || 'N/A'}</TableCell>
                      <TableCell>{employee.phone || 'N/A'}</TableCell>
                      <TableCell>
                        <Chip
                          label={employee.is_active ? 'Active' : 'Inactive'}
                          color={employee.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" color="primary" onClick={() => handleEditClick(employee)}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" color="info">
                          <Email />
                        </IconButton>
                        <IconButton size="small" color="secondary">
                          <Phone />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteClick(employee)}>
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        {/* Add Employee Modal */}
        <AddEmployeeModal
          open={addModalOpen}
          onClose={() => setAddModalOpen(false)}
          onAdd={handleAddEmployee}
          mode="create"
        />
        {/* Edit Employee Dialog */}
        <Dialog 
          open={editDialog} 
          onClose={() => setEditDialog(false)}
          maxWidth="md" 
          fullWidth
        >
          <DialogTitle>
            Edit Employee
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Full Name *"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={formData.employee_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, employee_id: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  value={formData.address}
                  onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="City"
                  value={formData.city}
                  onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="State"
                  value={formData.state}
                  onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Pincode"
                  value={formData.pincode}
                  onChange={(e) => setFormData(prev => ({ ...prev, pincode: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Department"
                  value={formData.department}
                  onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Designation"
                  value={formData.designation}
                  onChange={(e) => setFormData(prev => ({ ...prev, designation: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Salary"
                  type="number"
                  value={formData.salary}
                  onChange={(e) => setFormData(prev => ({ ...prev, salary: parseFloat(e.target.value) || 0 }))}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              Update
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};
export default EmployeesPage;