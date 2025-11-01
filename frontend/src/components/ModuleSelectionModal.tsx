// frontend/src/components/ModuleSelectionModal.tsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { organizationService } from '../services/organizationService';

interface ModuleSelectionModalProps {
  open: boolean;
  onClose: () => void;
  selectedModules: { [key: string]: boolean };
  onChange: (modules: { [key: string]: boolean }) => void;
  orgId?: number; // Optional for org management
  orgName?: string; // For title
}

const availableModules = ['crm', 'erp', 'manufacturing', 'finance', 'service', 'hr', 'analytics']; // Hardcoded 7 modules

const ModuleSelectionModal: React.FC<ModuleSelectionModalProps> = ({ open, onClose, selectedModules, onChange, orgId, orgName }) => {
  const queryClient = useQueryClient();
  const updateMutation = useMutation({
    mutationFn: async (modules: { [key: string]: boolean }) => {
      if (!orgId) throw new Error('No organization ID');
      return organizationService.updateOrganizationById(orgId, { enabled_modules: modules });
    },
    onSuccess: () => {
      console.log('Modules updated in real-time');
      queryClient.invalidateQueries({ queryKey: ['currentOrganization'] }); // Invalidate for real-time refetch
    },
  });

  const handleCheckboxChange = (module: string, checked: boolean) => {
    const newSelected = { ...selectedModules, [module]: checked };
    onChange(newSelected);
    if (orgId) {
      updateMutation.mutate(newSelected); // Real-time update on change
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>Module Management {orgName ? `- ${orgName}` : ''}</DialogTitle>
      <DialogContent>
        <FormGroup>
          {availableModules.map((module) => (
            <FormControlLabel
              key={module}
              control={
                <Checkbox
                  checked={selectedModules[module] || false}
                  onChange={(e) => handleCheckboxChange(module, e.target.checked)}
                  color="primary"
                  disabled={updateMutation.isPending}
                />
              }
              label={module.toUpperCase()}
            />
          ))}
        </FormGroup>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={updateMutation.isPending}>Done</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModuleSelectionModal;