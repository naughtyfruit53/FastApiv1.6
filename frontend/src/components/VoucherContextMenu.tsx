// src/components/VoucherContextMenu.tsx
// Merged version: Comprehensive context menu with duplicate and all existing features.
import React, { useState } from 'react';
import { Menu, MenuItem, IconButton } from '@mui/material';
import { 
  MoreVert as MoreVertIcon, 
  Visibility, 
  Edit, 
  Delete, 
  Print, 
  SaveAlt, 
  Email, 
  ContentCopy,
  LocalShipping 
} from '@mui/icons-material';

interface VoucherContextMenuProps {
  voucher?: any;
  voucherType: string;
  onView: (voucher: any) => void;
  onEdit: (voucher: any) => void;
  onDelete: (voucher: any) => void;
  onPrint?: (voucher: any) => void;
  onEmail?: (id: number) => void;
  onDuplicate?: (id: number) => void;
  onCreateDispatch?: (id: number) => void;
  showKebab?: boolean;
  contextMenu?: { mouseX: number; mouseY: number } | null;
  onClose: () => void;
}

const VoucherContextMenu: React.FC<VoucherContextMenuProps> = ({
  voucher,
  voucherType,
  onView,
  onEdit,
  onDelete,
  onPrint,
  onEmail,
  onDuplicate,
  onCreateDispatch,
  showKebab = false,
  contextMenu = null,
  onClose,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    onClose();
  };

  const handleAction = (action: (voucher: any) => void) => () => {
    if (voucher) {
      action(voucher);
    }
    handleMenuClose();
  };

  const handlePrintAction = () => () => {
    if (onPrint && voucher) {
      onPrint(voucher);
    }
    handleMenuClose();
  };

  // Determine email recipient based on voucher type (kept from original)
  const getEmailRecipient = () => {
    if (!voucher) return '';
    const lowerType = voucherType?.toLowerCase() || '';
    if (lowerType.includes('sales')) {
      return voucher.customer?.email || '';
    } else if (lowerType.includes('purchase') || lowerType.includes('financial') || lowerType.includes('payment')) {
      return voucher.vendor?.email || '';
    } else if (lowerType.includes('receipt')) {
      return voucher.customer?.email || '';
    }
    return '';
  };

  const handleEmailClick = () => {
    if (onEmail && voucher) {
      const recipient = getEmailRecipient();
      if (recipient) {
        onEmail(voucher.id);
      } else {
        alert('No email recipient found for this voucher type.');
      }
    }
    handleMenuClose();
  };

  const menuProps = contextMenu ? {
    open: contextMenu !== null,
    onClose: handleMenuClose,
    anchorReference: "anchorPosition" as const,
    anchorPosition: contextMenu ? { top: contextMenu.mouseY, left: contextMenu.mouseX } : undefined,
  } : {
    open: Boolean(anchorEl),
    anchorEl,
    onClose: handleMenuClose,
  };

  const hasEmail = !!onEmail && !!getEmailRecipient();
  const isDeliveryChallan = voucherType?.toLowerCase().includes('delivery challan');

  return (
    <>
      {showKebab && (
        <IconButton onClick={handleClick}>
          <MoreVertIcon />
        </IconButton>
      )}
      <Menu {...menuProps}>
        <MenuItem onClick={handleAction(onView)}>
          <Visibility sx={{ mr: 1 }} /> View {voucherType}
        </MenuItem>
        <MenuItem onClick={handleAction(onEdit)}>
          <Edit sx={{ mr: 1 }} /> Edit {voucherType}
        </MenuItem>
        {onDuplicate && (
          <MenuItem onClick={handleAction(onDuplicate)}>
            <ContentCopy sx={{ mr: 1 }} /> Duplicate {voucherType}
          </MenuItem>
        )}
        <MenuItem onClick={handleAction(onDelete)}>
          <Delete sx={{ mr: 1 }} /> Delete {voucherType}
        </MenuItem>
        {onPrint && (
          <MenuItem onClick={handlePrintAction()}>
            <Print sx={{ mr: 1 }} /> Print {voucherType}
          </MenuItem>
        )}
        {hasEmail && (
          <MenuItem onClick={handleEmailClick}>
            <Email sx={{ mr: 1 }} /> Email {voucherType}
          </MenuItem>
        )}
        {isDeliveryChallan && onCreateDispatch && (
          <MenuItem onClick={handleAction(onCreateDispatch)}>
            <LocalShipping sx={{ mr: 1 }} /> Create Dispatch Order
          </MenuItem>
        )}
      </Menu>
    </>
  );
};

export default VoucherContextMenu;