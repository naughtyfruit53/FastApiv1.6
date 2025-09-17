// frontend/src/components/VoucherHeaderActions.tsx
"use client";
import React from "react";
import { Box, Button } from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Save as SaveIcon,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import VoucherPDFButton from "./VoucherPDFButton";

interface VoucherHeaderActionsProps {
  mode: "create" | "edit" | "view" | "revise";
  voucherType: string; // e.g., 'Purchase Order', 'Sales Voucher', etc.
  voucherRoute: string; // The base route for this voucher type
  currentId?: number; // Current voucher ID (for edit route)
  onEdit?: () => void;
  onCreate?: () => void;
  onCancel?: () => void;
  // Additional props for compatibility
  onModeChange?: (_mode: "create" | "edit" | "view" | "revise") => void;
  onModalOpen?: () => void;
  voucherList?: any[];
  onView?: (_voucher: any) => void;
  isLoading?: boolean;
  // PDF generation props
  voucherNumber?: string;
  showPDFButton?: boolean;
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
  onModeChange: _onModeChange,
  onModalOpen: _onModalOpen,
  voucherList: _voucherList,
  onView: _onView,
  isLoading,
  // PDF generation props
  voucherNumber,
  showPDFButton = true,
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

  // Map voucher type to PDF generation type
  const getPDFVoucherType = (voucherType: string): string => {
    const lowerType = voucherType.toLowerCase();
    if (lowerType.includes('purchase')) return 'purchase';
    if (lowerType.includes('sales') || lowerType.includes('invoice')) return 'sales';
    if (lowerType.includes('quotation')) return 'quotation';
    if (lowerType.includes('sales order')) return 'sales_order';
    if (lowerType.includes('proforma')) return 'proforma';
    return 'sales'; // Default fallback
  };

  const pdfVoucherType = getPDFVoucherType(voucherType);

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
      {mode === "view" && (
        <>
          <Button
            variant="contained"
            color="success"
            startIcon={<AddIcon />}
            onClick={onCreate ? onCreate : handleCreateFallback}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<EditIcon />}
            onClick={onEdit ? onEdit : handleEditFallback}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Edit {voucherType.toLowerCase()}
          </Button>
          {showPDFButton && currentId && (
            <VoucherPDFButton
              voucherType={pdfVoucherType as any}
              voucherId={currentId}
              voucherNumber={voucherNumber}
              variant="menu"
              size="medium"
            />
          )}
        </>
      )}
      {mode === "edit" && (
        <>
          <Button
            variant="contained"
            color="success"
            startIcon={<AddIcon />}
            onClick={onCreate ? onCreate : handleCreateFallback}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button
            form="voucherForm"
            type="submit"
            variant="contained"
            color="primary"
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Save
          </Button>
          <Button
            variant="outlined"
            startIcon={<CloseIcon />}
            onClick={onCancel}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Cancel
          </Button>
          {showPDFButton && currentId && (
            <VoucherPDFButton
              voucherType={pdfVoucherType as any}
              voucherId={currentId}
              voucherNumber={voucherNumber}
              variant="button"
              size="medium"
            />
          )}
        </>
      )}
      {mode === "create" && (
        <Button
          form="voucherForm"
          type="submit"
          variant="contained"
          color="primary"
          sx={{ fontSize: 12, textTransform: "uppercase" }}
        >
          Save
        </Button>
      )}
      {mode === "revise" && (
        <>
          <Button
            variant="contained"
            color="success"
            startIcon={<AddIcon />}
            onClick={onCreate ? onCreate : handleCreateFallback}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button
            form="voucherForm"
            type="submit"
            variant="contained"
            color="primary"
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Save Revision
          </Button>
          <Button
            variant="outlined"
            startIcon={<CloseIcon />}
            onClick={onCancel}
            sx={{ fontSize: 12, textTransform: "uppercase" }}
          >
            Cancel
          </Button>
        </>
      )}
    </Box>
  );
};

export default VoucherHeaderActions;