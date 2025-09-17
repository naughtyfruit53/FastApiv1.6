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
  Email, 
  ContentCopy,
  LocalShipping,
  History,  // New icon for revise
} from '@mui/icons-material';

interface VoucherContextMenuProps {
  voucher?: any;
  voucherType: string;
  onView: (voucher: any) => void;
  onEdit: (voucher: any) => void;
  onDelete: (voucher: any) => void;
  onPrint?: (voucher: any) => void;
  onEmail?: (voucher: any) => void;
  onDuplicate?: (voucher: any) => void;
  onCreateDispatch?: (voucher: any) => void;
  onRevise?: (voucher: any) => void;  // New prop for revise
  showKebab?: boolean;
  contextMenu?: { mouseX: number; mouseY: number; voucher?: any } | null;
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
  onRevise,
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

  const currentVoucher = voucher || contextMenu?.voucher;

  const handleAction = (action: (voucher: any) => void) => () => {
    action(currentVoucher);
    handleMenuClose();
  };

  // Determine email recipient based on voucher type (kept from original)
  const getEmailRecipient = () => {
    if (!currentVoucher) return '';
    const lowerType = voucherType?.toLowerCase() || '';
    if (lowerType.includes('sales')) {
      return currentVoucher.customer?.email || '';
    } else if (lowerType.includes('purchase') || lowerType.includes('financial') || lowerType.includes('payment')) {
      return currentVoucher.vendor?.email || '';
    } else if (lowerType.includes('receipt')) {
      return currentVoucher.customer?.email || '';
    }
    return '';
  };

  const handleEmailClick = () => {
    if (onEmail && currentVoucher) {
      const recipient = getEmailRecipient();
      if (recipient) {
        onEmail(currentVoucher);
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
          <MenuItem onClick={handleAction(onPrint)}>
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
        {onRevise && (
          <MenuItem onClick={handleAction(onRevise)}>
            <History sx={{ mr: 1 }} /> Create Revision
          </MenuItem>
        )}
      </Menu>
    </>
  );
};

export default VoucherContextMenu;