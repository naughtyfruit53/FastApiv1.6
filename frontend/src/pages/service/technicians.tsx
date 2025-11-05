// frontend/src/pages/service/technicians.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';
import { userService } from '@/services/userService';
import AddEmployeeModal from '@/components/AddEmployeeModal';

import { ProtectedPage } from '../components/ProtectedPage';
interface Technician {
  id: number;
  name: string;
  username: string;
  email: string;
  role: string;
  phone?: string;
  status: 'active' | 'inactive';
}

export default function TechniciansManagement() {
  const { user } = useAuth();
  const organizationId = user?.organization_id || 0;
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [openAddModal, setOpenAddModal] = useState(false);
  const [editingTech, setEditingTech] = useState<Technician | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (organizationId) {
      loadTechnicians();
    }
  }, [organizationId]);

  const loadTechnicians = async () => {
    setLoading(true);
    try {
      const allUsers = await userService.getOrganizationUsers(organizationId);
      // Filter to show only technicians (e.g., role 'executive' or add your technician role)
      const techUsers = allUsers.filter((u: any) => u.role === 'executive'); // Adjust filter as per your roles
      setTechnicians(techUsers.map((u: any) => ({
        id: u.id,
        name: u.name || '',
        username: u.username,
        email: u.email,
        role: u.role,
        phone: u.phone || '',
        status: u.is_active ? 'active' : 'inactive', // Assuming user has is_active field; adjust if needed
      })));
    } catch (err) {
      console.error('Error loading technicians', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (tech: Technician) => {
    setEditingTech(tech);
    setOpenAddModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this technician?')) {
      try {
        await userService.deleteUser(organizationId, id);
        loadTechnicians();
      } catch (err) {
        console.error('Error deleting technician', err);
      }
    }
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <ProtectedPage moduleKey="service" action="read">
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Technicians Management
      </Typography>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => setOpenAddModal(true)}
        sx={{ mb: 3 }}
      >
        Add Technician
      </Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {technicians.map((tech) => (
              <TableRow key={tech.id}>
                <TableCell>{tech.name}</TableCell>
                <TableCell>{tech.username}</TableCell>
                <TableCell>{tech.email}</TableCell>
                <TableCell>{tech.phone}</TableCell>
                <TableCell>{tech.role}</TableCell>
                <TableCell>{tech.status}</TableCell>
                <TableCell>
                  <Button startIcon={<EditIcon />} onClick={() => handleEdit(tech)} />
                  <Button startIcon={<DeleteIcon />} onClick={() => handleDelete(tech.id)} color="error" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <AddEmployeeModal
        open={openAddModal}
        onClose={() => {
          setOpenAddModal(false);
          setEditingTech(null);
        }}
        onAdd={loadTechnicians}
        initialData={editingTech ? { ...editingTech, full_name: editingTech.name } : null} // Map fields if needed
        mode={editingTech ? 'edit' : 'create'}
      />
    </Box>
    </ProtectedPage>

  );
}