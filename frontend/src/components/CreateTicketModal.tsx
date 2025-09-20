// frontend/src/components/CreateTicketModal.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import CustomerAutocomplete from '@/components/CustomerAutocomplete';
import AddEmployeeModal from '@/components/AddEmployeeModal';
import { serviceDeskService } from '@/services/serviceDeskService';
import { userService } from '@/services/userService';

interface CreateTicketModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  organizationId: number;
}

export default function CreateTicketModal({ open, onClose, onSuccess, organizationId }: CreateTicketModalProps) {
  const [ticketForm, setTicketForm] = useState({
    problem: '',
    description: '',
    priority: 'medium',
    category: 'support',
    customer_id: null as number | null,
    requested_by: '',
    requested_email: '',
    requested_phone: '',
    assigned_to: null as number | null,
    address: '',
  });
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [openAddEmployeeModal, setOpenAddEmployeeModal] = useState(false);

  useEffect(() => {
    if (open && organizationId) {
      loadUsers();
    }
  }, [open, organizationId]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const userData = await userService.getOrganizationUsers(organizationId);
      setUsers(userData);
      console.log('Loaded users for Assigned To:', userData); // Added for debugging
    } catch (err) {
      console.error("Error loading users", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setTicketForm({ ...ticketForm, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (e: any) => {
    const value = e.target.value;
    if (value === 'add_new') {
      setOpenAddEmployeeModal(true);
    } else {
      setTicketForm({ ...ticketForm, [e.target.name]: value });
    }
  };

  const handleCreateTicket = async () => {
    try {
      const ticketData = {
        title: ticketForm.problem,
        ...ticketForm,
        customer_id: selectedCustomer?.id || null,
      };
      await serviceDeskService.createTicket(ticketData);
      onClose();
      onSuccess();
      // Reset form
      setTicketForm({
        problem: '',
        description: '',
        priority: 'medium',
        category: 'support',
        customer_id: null,
        requested_by: '',
        requested_email: '',
        requested_phone: '',
        assigned_to: null,
        address: '',
      });
      setSelectedCustomer(null);
    } catch (err) {
      console.error("Error creating ticket", err);
    }
  };

  if (loading) {
    return null; // Or a spinner
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
    >
      <DialogTitle>Create New Ticket</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'stretch' }}>
          <CustomerAutocomplete
            value={selectedCustomer}
            onChange={(event, newValue) => {
              setSelectedCustomer(newValue);
              setTicketForm({
                ...ticketForm,
                customer_id: newValue?.id || null,
                requested_by: newValue?.name || '',
                requested_email: newValue?.email || '',
                requested_phone: newValue?.phone || '',
                address: newValue?.address || '',
              });
            }}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
          <TextField
            label="Address"
            name="address"
            value={ticketForm.address}
            onChange={handleFormChange}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
          <FormControl sx={{ width: '3.5in', alignSelf: 'center' }}>
            <InputLabel>Category</InputLabel>
            <Select
              name="category"
              value={ticketForm.category}
              onChange={handleSelectChange}
            >
              <MenuItem value="support">Support</MenuItem>
              <MenuItem value="maintenance">Maintenance</MenuItem>
              <MenuItem value="installation">Installation</MenuItem>
              <MenuItem value="complaint">Complaint</MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="Problem"
            name="problem"
            value={ticketForm.problem}
            onChange={handleFormChange}
            sx={{ width: '3.5in', alignSelf: 'center' }}
            required
          />
          <TextField
            label="Requester Name"
            name="requested_by"
            value={ticketForm.requested_by}
            onChange={handleFormChange}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
          <TextField
            label="Requester Phone"
            name="requested_phone"
            value={ticketForm.requested_phone}
            onChange={handleFormChange}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
          <TextField
            label="Requester Email"
            name="requested_email"
            value={ticketForm.requested_email}
            onChange={handleFormChange}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
          <FormControl sx={{ width: '3.5in', alignSelf: 'center' }}>
            <InputLabel>Priority</InputLabel>
            <Select
              name="priority"
              value={ticketForm.priority}
              onChange={handleSelectChange}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ width: '3.5in', alignSelf: 'center' }}>
            <InputLabel>Assigned To</InputLabel>
            <Select
              name="assigned_to"
              value={ticketForm.assigned_to || ''}
              onChange={handleSelectChange}
            >
              <MenuItem value="">Unassigned</MenuItem>
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name || user.username}
                </MenuItem>
              ))}
              <MenuItem value="add_new">
                <AddIcon sx={{ mr: 1 }} /> Add Technician
              </MenuItem>
            </Select>
          </FormControl>
          <TextField
            label="Description"
            name="description"
            value={ticketForm.description}
            onChange={handleFormChange}
            multiline
            rows={4}
            sx={{ width: '3.5in', alignSelf: 'center' }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleCreateTicket}
        >
          Create Ticket
        </Button>
      </DialogActions>
      <AddEmployeeModal
        open={openAddEmployeeModal}
        onClose={() => setOpenAddEmployeeModal(false)}
        onAdd={loadUsers} // Reload users after adding employee
        initialData={null}
        mode="create"
      />
    </Dialog>
  );
}