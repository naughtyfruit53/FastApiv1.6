// frontend/src/components/VoucherHeaderActions.tsx
'use client';

import React from 'react';
import { Box, Button } from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Close as CloseIcon } from '@mui/icons-material';
import { useRouter } from 'next/navigation';

interface VoucherHeaderActionsProps {
  mode: 'create' | 'edit' | 'view';
  voucherType: string; // e.g., 'Purchase Order', 'Sales Voucher', etc.
  voucherRoute: string; // The base route for this voucher type
  currentId?: number; // Current voucher ID (for edit route)
  onEdit?: () => void;
  onCreate?: () => void;
  onCancel?: () => void;
  // Additional props for compatibility
  onModeChange?: (mode: 'create' | 'edit' | 'view') => void;
  onModalOpen?: () => void;
  voucherList?: any[];
  onView?: (voucher: any) => void;
  isLoading?: boolean;
}

const VoucherHeaderActions: React.FC<VoucherHeaderActionsProps> = ({
  mode,
  voucherType,
  voucherRoute,
  currentId,
  onEdit,
  onCreate,
  onCancel,
  // Additional props for compatibility (ignored for now)
  onModeChange,
  onModalOpen,
  voucherList,
  onView,
  isLoading,
}) => {
  const router = useRouter();

  const handleEditFallback = () => {
    if (currentId) {
      router.push(`${voucherRoute}?mode=edit&id=${currentId}`);
    }
  };

  const handleCreateFallback = () => {
    router.push(`${voucherRoute}?mode=create`);
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {mode === 'view' && (
        <>
          <Button 
            variant="contained" 
            color="success" 
            startIcon={<AddIcon />}
            onClick={onCreate ? onCreate : handleCreateFallback}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<EditIcon />}
            onClick={onEdit ? onEdit : handleEditFallback}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Edit {voucherType.toLowerCase()}
          </Button>
        </>
      )}
      {mode === 'edit' && (
        <>
          <Button 
            variant="contained" 
            color="success" 
            startIcon={<AddIcon />}
            onClick={onCreate ? onCreate : handleCreateFallback}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button 
            form="voucherForm" 
            type="submit" 
            variant="contained" 
            color="primary" 
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Save
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<CloseIcon />}
            onClick={onCancel}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Cancel
          </Button>
        </>
      )}
      {mode === 'create' && (
        <Button 
          form="voucherForm" 
          type="submit" 
          variant="contained" 
          color="primary" 
          sx={{ fontSize: 12, textTransform: 'uppercase' }}
        >
          Save
        </Button>
      )}
    </Box>
  );
};

export default VoucherHeaderActions;