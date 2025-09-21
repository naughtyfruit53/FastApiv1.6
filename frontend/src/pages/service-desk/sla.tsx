// frontend/src/pages/service-desk/sla.tsx
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  Add,
  Edit,
  Delete,
  Schedule,
  CheckCircle,
  Warning
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import { serviceDeskService } from '../../services/serviceDeskService';

const ServiceDeskSlaPage: React.FC = () => {
  const [slaPolicies, setSlaPolicies] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: '',
    ticket_type: '',
    customer_tier: '',
    response_time_hours: 0,
    resolution_time_hours: 0,
    escalation_enabled: true,
    escalation_threshold_percent: 80,
    is_active: true,
    is_default: false
  });

  useEffect(() => {
    fetchSlaPolicies();
  }, []);

  const fetchSlaPolicies = async () => {
    try {
      const policies = await serviceDeskService.getSLAPolicies();
      setSlaPolicies(policies);
    } catch (error) {
      console.error('Error fetching SLA policies:', error);
    }
  };

  const handleOpenModal = (policy = null) => {
    if (policy) {
      setEditMode(true);
      setSelectedPolicy(policy);
      setFormData(policy);
    } else {
      setEditMode(false);
      setSelectedPolicy(null);
      setFormData({
        name: '',
        description: '',
        priority: '',
        ticket_type: '',
        customer_tier: '',
        response_time_hours: 0,
        resolution_time_hours: 0,
        escalation_enabled: true,
        escalation_threshold_percent: 80,
        is_active: true,
        is_default: false
      });
    }
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    setOpenModal(false);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async () => {
    try {
      if (editMode) {
        await serviceDeskService.updateSLAPolicy(selectedPolicy.id, formData);
      } else {
        await serviceDeskService.createSLAPolicy(formData);
      }
      handleCloseModal();
      fetchSlaPolicies();
    } catch (error) {
      console.error('Error submitting SLA policy:', error);
    }
  };

  const handleDelete = async (policyId) => {
    if (window.confirm('Are you sure you want to delete this SLA policy?')) {
      try {
        await serviceDeskService.deleteSLAPolicy(policyId);
        fetchSlaPolicies();
      } catch (error) {
        console.error('Error deleting SLA policy:', error);
      }
    }
  };

  return (
    <DashboardLayout
      title="SLA Management"
      subtitle="Manage service level agreements"
      actions={
        <Button 
          variant="contained" 
          startIcon={<Add />}
          onClick={() => handleOpenModal()}
        >
          Create Policy
        </Button>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SLA Policies
              </Typography>
              <TableContainer>
                <Table sx={{ width: '100%', tableLayout: 'fixed' }}>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Ticket Type</TableCell>
                      <TableCell>Response Time (hours)</TableCell>
                      <TableCell>Resolution Time (hours)</TableCell>
                      <TableCell>Active</TableCell>
                      <TableCell>Default</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {slaPolicies.map((policy) => (
                      <TableRow key={policy.id}>
                        <TableCell>{policy.name}</TableCell>
                        <TableCell>{policy.priority || 'All'}</TableCell>
                        <TableCell>{policy.ticket_type || 'All'}</TableCell>
                        <TableCell>{policy.response_time_hours}</TableCell>
                        <TableCell>{policy.resolution_time_hours}</TableCell>
                        <TableCell>
                          {policy.is_active ? <CheckCircle color="success" /> : <Warning color="error" />}
                        </TableCell>
                        <TableCell>{policy.is_default ? 'Yes' : 'No'}</TableCell>
                        <TableCell align="right">
                          <IconButton onClick={() => handleOpenModal(policy)}>
                            <Edit />
                          </IconButton>
                          <IconButton onClick={() => handleDelete(policy.id)}>
                            <Delete />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={openModal} onClose={handleCloseModal} maxWidth="xs" fullWidth>
        <DialogTitle>{editMode ? 'Edit SLA Policy' : 'Create SLA Policy'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              required
            />
            <TextField
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleFormChange}
              multiline
              rows={3}
            />
            <FormControl>
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formData.priority}
                onChange={handleFormChange}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
            <FormControl>
              <InputLabel>Ticket Type</InputLabel>
              <Select
                name="ticket_type"
                value={formData.ticket_type}
                onChange={handleFormChange}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="support">Support</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
                <MenuItem value="installation">Installation</MenuItem>
                <MenuItem value="complaint">Complaint</MenuItem>
              </Select>
            </FormControl>
            <FormControl>
              <InputLabel>Customer Tier</InputLabel>
              <Select
                name="customer_tier"
                value={formData.customer_tier}
                onChange={handleFormChange}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="premium">Premium</MenuItem>
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="basic">Basic</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Response Time (hours)"
              name="response_time_hours"
              type="number"
              value={formData.response_time_hours}
              onChange={handleFormChange}
              required
            />
            <TextField
              label="Resolution Time (hours)"
              name="resolution_time_hours"
              type="number"
              value={formData.resolution_time_hours}
              onChange={handleFormChange}
              required
            />
            <FormControl>
              <InputLabel>Escalation Threshold (%)</InputLabel>
              <Select
                name="escalation_threshold_percent"
                value={formData.escalation_threshold_percent}
                onChange={handleFormChange}
              >
                <MenuItem value={50}>50%</MenuItem>
                <MenuItem value={60}>60%</MenuItem>
                <MenuItem value={70}>70%</MenuItem>
                <MenuItem value={80}>80%</MenuItem>
                <MenuItem value={90}>90%</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModal}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editMode ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </DashboardLayout>
  );
};

export default ServiceDeskSlaPage