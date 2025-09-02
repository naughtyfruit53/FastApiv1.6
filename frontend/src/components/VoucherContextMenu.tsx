// frontend/src/components/VoucherContextMenu.tsx
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
  onView: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
  onPrint?: (id: number, mode: 'print' | 'download') => void;
  onEmail?: (id: number) => void;
  onDuplicate?: (id: number) => void;
  onCreateDispatch?: (id: number) => void;
  showKebab?: boolean;
  contextMenu?: { mouseX: number; mouseY: number; voucher: any } | null;
  onClose: () => void;
  open?: boolean;
  anchorPosition?: { left: number; top: number };
  anchorReference?: 'anchorPosition' | 'anchorEl' | 'none';
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
  open = false,
  anchorPosition = null,
  anchorReference,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const effectiveVoucher = voucher || (contextMenu ? contextMenu.voucher : null);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    onClose();
  };

  const handleAction = (action: (id: number) => void) => () => {
    if (effectiveVoucher) {
      action(effectiveVoucher.id);
    }
    handleMenuClose();
  };

  const handlePrintAction = (mode: 'print' | 'download') => () => {
    if (onPrint && effectiveVoucher) {
      onPrint(effectiveVoucher.id, mode);
    }
    handleMenuClose();
  };

  // Determine email recipient based on voucher type
  const getEmailRecipient = () => {
    if (!effectiveVoucher) {
      return '';
    }
    if (!voucherType) {
      return '';
    }
    const lowerType = voucherType.toLowerCase();
    if (lowerType.includes('sales')) {
      return effectiveVoucher.customer?.email || '';
    } else if (lowerType.includes('purchase') || lowerType.includes('financial') || lowerType.includes('payment')) {
      return effectiveVoucher.vendor?.email || '';
    } else if (lowerType.includes('receipt')) {
      return effectiveVoucher.customer?.email || '';
    }
    return '';
  };

  const handleEmailClick = () => {
    if (onEmail && effectiveVoucher) {
      const recipient = getEmailRecipient();
      if (recipient) {
        onEmail(effectiveVoucher.id);
      } else {
        alert('No email recipient found for this voucher type.');
      }
    }
    handleMenuClose();
  };

  const menuProps = anchorPosition && anchorReference ? {
    open: open || Boolean(anchorEl),
    onClose: handleMenuClose,
    anchorReference: anchorReference,
    anchorPosition,
  } : {
    open: Boolean(anchorEl),
    anchorEl,
    onClose: handleMenuClose,
  };

  const hasEmail = !!onEmail && !!getEmailRecipient();
  const isDeliveryChallan = voucherType.toLowerCase().includes('delivery challan');
  const isPurchaseOrder = voucherType.toLowerCase().includes('purchase order');

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
          <MenuItem onClick={handlePrintAction('print')}>
            <Print sx={{ mr: 1 }} /> Print {voucherType}
          </MenuItem>
        )}
        {onPrint && (
          <MenuItem onClick={handlePrintAction('download')}>
            <SaveAlt sx={{ mr: 1 }} /> Save {voucherType} as PDF
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