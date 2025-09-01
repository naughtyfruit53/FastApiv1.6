// frontend/src/pages/masters/bom.tsx
import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Container, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip
} from '@mui/material';
import { 
  Add, 
  Visibility, 
  Edit, 
  Delete 
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../lib/api';
import AddBOMModal from '../../components/AddBOMModal';
const BOMManagement: React.FC = () => {
  const [mode, setMode] = useState<'list' | 'view'>('list');
  const [selectedBOM, setSelectedBOM] = useState<any>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editMode, setEditMode] = useState<'create' | 'edit'>('create');
  const queryClient = useQueryClient();
  // Fetch BOMs
  const { data: bomList, isLoading: isLoadingBOMs } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/bom').then(res => res.data),
  });
  // Delete BOM mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/bom/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boms'] });
      setShowDeleteDialog(false);
      setSelectedBOM(null);
    },
    onError: (error: any) => {
      console.error(msg, err);
    }
  });
  const handleView = (bom: any) => {
    setSelectedBOM(bom);
    setMode('view');
  };
  const handleEdit = (bom: any) => {
    setSelectedBOM(bom);
    setEditMode('edit');
    setShowAddModal(true);
  };
  const handleDelete = (bom: any) => {
    setSelectedBOM(bom);
    setShowDeleteDialog(true);
  };
  const confirmDelete = () => {
    if (selectedBOM?.id) {
      deleteMutation.mutate(selectedBOM.id);
    }
  };
    setShowAddModal(false);
    setSelectedBOM(null);
  };
  const handleCreate = () => {
    setEditMode('create');
    setShowAddModal(true);
  };
  if (isLoadingBOMs) {
    return <CircularProgress />;
  }
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Bill of Materials (BOM)</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreate}
          >
            Create BOM
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>BOM Name</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Output Item</TableCell>
                <TableCell>Output Qty</TableCell>
                <TableCell>Total Cost</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bomList?.map((bom: any) => (
                <TableRow key={bom.id}>
                  <TableCell>{bom.bom_name}</TableCell>
                  <TableCell>{bom.version}</TableCell>
                  <TableCell>{bom.output_item?.product_name || 'Unknown'}</TableCell>
                  <TableCell>{bom.output_quantity}</TableCell>
                  <TableCell>{bom.total_cost.toFixed(2)}</TableCell>
                  <TableCell>
                    <Chip 
                      label={bom.is_active ? 'Active' : 'Inactive'} 
                      color={bom.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleView(bom)} size="small">
                      <Visibility />
                    </IconButton>
                    <IconButton onClick={() => handleEdit(bom)} size="small">
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(bom)} size="small" color="error">
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the BOM "{selectedBOM?.bom_name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      {/* Add/Edit BOM Modal */}
      <AddBOMModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddBOM}
        initialData={editMode === 'edit' ? selectedBOM : undefined}
        mode={editMode}
      />
    </Container>
  );
};
export default BOMManagement;