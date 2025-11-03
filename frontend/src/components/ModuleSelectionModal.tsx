// frontend/src/components/ModuleSelectionModal.tsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Alert,
  Box,
  Typography,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  MODULE_BUNDLES,
  getSelectedBundlesFromModules,
  computeModuleChanges,
} from '../config/moduleBundleMap';
import {
  fetchOrgEntitlementsAdmin,
  updateOrgEntitlements,
  UpdateEntitlementsRequest,
} from '../services/entitlementsApi';
import { useInvalidateEntitlements } from '../hooks/useEntitlements';

interface ModuleSelectionModalProps {
  open: boolean;
  onClose: () => void;
  orgId?: number;
  orgName?: string;
  token?: string; // Auth token for API calls (optional, fallback to localStorage)
  isSuperAdmin?: boolean; // Whether the current user is a super admin
}

const ModuleSelectionModal: React.FC<ModuleSelectionModalProps> = ({
  open,
  onClose,
  orgId,
  orgName,
  token: propToken,
  isSuperAdmin = false,
}) => {
  const [selectedBundles, setSelectedBundles] = useState<Set<string>>(new Set());
  const { invalidateEntitlements } = useInvalidateEntitlements();
  const localToken = localStorage.getItem('access_token') || ''; // Fallback if no prop token
  const authToken = propToken || localToken;

  // Fetch current entitlements
  const { data: entitlementsData, isLoading, isError } = useQuery({
    queryKey: ['admin-entitlements', orgId],
    queryFn: () => {
      if (!orgId || !authToken) throw new Error('Missing orgId or token');
      return fetchOrgEntitlementsAdmin(orgId, authToken);
    },
    enabled: open && !!orgId && !!authToken,
    onError: (error: any) => {
      toast.error(error.message || 'Failed to load current modules');
    },
  });

  // Initialize selected bundles from current entitlements
  useEffect(() => {
    if (entitlementsData) {
      const enabledModules = entitlementsData.entitlements
        .filter((ent) => ent.status === 'enabled' || ent.status === 'trial')
        .map((ent) => ent.module_key);
      
      const bundles = getSelectedBundlesFromModules(enabledModules);
      setSelectedBundles(new Set(bundles));
    }
  }, [entitlementsData]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async (request: UpdateEntitlementsRequest) => {
      if (!orgId || !authToken) throw new Error('Missing orgId or token');
      return updateOrgEntitlements(orgId, request, authToken);
    },
    onSuccess: () => {
      toast.success('Modules updated successfully');
      if (orgId) {
        invalidateEntitlements(orgId);
      }
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update modules');
    },
  });

  const handleBundleToggle = (bundleKey: string) => {
    const newSelected = new Set(selectedBundles);
    if (newSelected.has(bundleKey)) {
      newSelected.delete(bundleKey);
    } else {
      newSelected.add(bundleKey);
    }
    setSelectedBundles(newSelected);
  };

  const handleSave = () => {
    if (!entitlementsData) {
      toast.warn('Cannot save: Current module data not loaded');
      return;
    }

    // Get current enabled modules
    const currentModules = entitlementsData.entitlements
      .filter((ent) => ent.status === 'enabled' || ent.status === 'trial')
      .map((ent) => ent.module_key);

    // Compute changes
    const targetBundles = Array.from(selectedBundles);
    const changes = computeModuleChanges(currentModules, targetBundles);

    if (changes.length === 0) {
      toast.info('No changes detected');
      onClose();
      return;
    }

    // Build update request
    const request: UpdateEntitlementsRequest = {
      reason: 'ModuleSelectionModal update',
      changes: {
        modules: changes.map((change) => ({
          module_key: change.module_key,
          status: change.status,
          trial_expires_at: null,
          source: 'manual',  // Add source here
        })),
        submodules: [],
      },
    };

    updateMutation.mutate(request);
  };

  // Computed property for checkbox disabled state
  const isCheckboxDisabled = !isSuperAdmin || isLoading || updateMutation.isPending;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Module Bundle Selection {orgName ? `- ${orgName}` : ''}
      </DialogTitle>
      <DialogContent>
        {!isSuperAdmin && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" fontWeight="bold" sx={{ mb: 0.5 }}>
              Super Admin Access Required
            </Typography>
            <Typography variant="body2">
              Module entitlement management is restricted to platform administrators only.
              Organization administrators cannot activate or deactivate modules.
              Please contact your platform administrator to request module changes.
            </Typography>
          </Alert>
        )}
        
        {isLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : isError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            Failed to load current modules
          </Alert>
        ) : !authToken ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            Missing authentication token - please log in again
          </Alert>
        ) : null}

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {isSuperAdmin 
            ? 'Select the module bundles to enable for this organization. Each bundle activates multiple related modules.'
            : 'View the current module bundles for this organization. Only super admins can modify module entitlements.'
          }
        </Typography>

        <FormGroup>
          {MODULE_BUNDLES.map((bundle) => (
            <FormControlLabel
              key={bundle.key}
              control={
                <Checkbox
                  checked={selectedBundles.has(bundle.key)}
                  onChange={() => handleBundleToggle(bundle.key)}
                  color="primary"
                  disabled={isCheckboxDisabled}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">{bundle.displayName}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {bundle.submodules.join(', ')}
                  </Typography>
                </Box>
              }
            />
          ))}
        </FormGroup>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={updateMutation.isPending}>
          {isSuperAdmin ? 'Cancel' : 'Close'}
        </Button>
        {isSuperAdmin && (
          <Button
            onClick={handleSave}
            variant="contained"
            color="primary"
            disabled={isLoading || updateMutation.isPending || !authToken}
          >
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ModuleSelectionModal;