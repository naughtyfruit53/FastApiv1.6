// frontend/src/components/AddTechnicianModal.tsx
import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import { userService } from '@/services/userService';

interface AddTechnicianModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  organizationId: number;
  editingTech?: any | null;
}

export default function AddTechnicianModal({ open, onClose, onSuccess, organizationId, editingTech }: AddTechnicianModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    role: 'executive', // Assuming 'executive' is the technician role; adjust as needed
    phone: '',
    password: '', // For new users
  });

  useEffect(() => {
    if (editingTech) {
      setFormData({
        name: editingTech.name || '',
        username: editingTech.username || '',
        email: editingTech.email || '',
        role: editingTech.role || 'executive',
        phone: editingTech.phone || '',
        password: '', // Don't prefill password
      });
    } else {
      setFormData({
        name: '',
        username: '',
        email: '',
        role: 'executive',
        phone: '',
        password: '',
      });
    }
  }, [editingTech]);

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      if (editingTech) {
        // Update existing technician
        await userService.updateUser(organizationId, editingTech.id, formData);
      } else {
        // Create new technician
        await userService.createUser(organizationId, { ...formData, is_active: true });
      }
      onClose();
      onSuccess();
    } catch (err) {
      console.error('Error saving technician', err);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{editingTech ? 'Edit Technician' : 'Add Technician'}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'stretch' }}>
          <TextField label="Name" name="name" value={formData.name} onChange={handleFormChange} fullWidth />
          <TextField label="Username" name="username" value={formData.username} onChange={handleFormChange} fullWidth />
          <TextField label="Email" name="email" value={formData.email} onChange={handleFormChange} fullWidth />
          <TextField label="Phone" name="phone" value={formData.phone} onChange={handleFormChange} fullWidth />
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select name="role" value={formData.role} onChange={handleSelectChange}>
              <MenuItem value="executive">Technician (Executive)</MenuItem>
              {/* Add other roles if needed, but limit to technician-relevant */}
            </Select>
          </FormControl>
          {!editingTech && (
            <TextField label="Password" name="password" type="password" value={formData.password} onChange={handleFormChange} fullWidth />
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit}>
          {editingTech ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}