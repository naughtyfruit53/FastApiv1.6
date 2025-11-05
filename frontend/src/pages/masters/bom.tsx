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
  Delete,
  FileDownload,
  FileUpload,
  GetApp
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../lib/api';
import AddBOMModal from '../../components/AddBOMModal';
import { ProtectedPage } from '../../components/ProtectedPage';

const BOMManagement: React.FC = () => {
  const [mode, setMode] = useState<'list' | 'view'>('list');
  const [selectedBOM, setSelectedBOM] = useState<any>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editMode, setEditMode] = useState<'create' | 'edit'>('create');
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [importMessage, setImportMessage] = useState<string | null>(null);

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
      console.error('Error deleting BOM:', error);
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

  const handleAddBOM = () => {
    setShowAddModal(false);
    setSelectedBOM(null);
  };

  const handleCreate = () => {
    setEditMode('create');
    setShowAddModal(true);
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/bom/export/template', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'BOM_Import_Template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading template:', error);
      alert('Failed to download template');
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setImporting(true);
    setImportMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/bom/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setImportMessage(
        `Successfully imported ${response.data.imported_count} BOMs` +
        (response.data.errors?.length ? `\n\nErrors: ${response.data.errors.join('\n')}` : '')
      );
      
      queryClient.invalidateQueries({ queryKey: ['boms'] });
    } catch (error: any) {
      console.error('Error importing BOMs:', error);
      setImportMessage(
        'Failed to import BOMs: ' + 
        (error.response?.data?.detail || error.message)
      );
    } finally {
      setImporting(false);
      event.target.value = ''; // Reset file input
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await api.get('/bom/export', {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'BOM_Export.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Error exporting BOMs:', error);
      alert('Failed to export BOMs: ' + (error.response?.data?.detail || error.message));
    } finally {
      setExporting(false);
    }
  };

  if (isLoadingBOMs) {
    return (
      <ProtectedPage moduleKey="masters" action="read">
      <CircularProgress />
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage moduleKey="masters" action="read">
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Bill of Materials (BOM)</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<GetApp />}
              onClick={handleDownloadTemplate}
            >
              Template
            </Button>
            <Button
              variant="outlined"
              component="label"
              startIcon={importing ? <CircularProgress size={20} /> : <FileUpload />}
              disabled={importing}
            >
              Import
              <input
                type="file"
                hidden
                accept=".xlsx,.xls"
                onChange={handleImport}
              />
            </Button>
            <Button
              variant="outlined"
              startIcon={exporting ? <CircularProgress size={20} /> : <FileDownload />}
              onClick={handleExport}
              disabled={exporting || !bomList?.length}
            >
              Export
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreate}
            >
              Create BOM
            </Button>
          </Box>
        </Box>
        {importMessage && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
            <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
              {importMessage}
            </Typography>
          </Box>
        )}
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
    </ProtectedPage>
  );
};

export default BOMManagement;