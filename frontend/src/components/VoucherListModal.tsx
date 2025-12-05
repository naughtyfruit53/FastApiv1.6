// frontend/src/components/VoucherListModal.tsx
// Reusable modal component for displaying voucher lists with clickable functionality
import React, { useState } from "react";
import {
  Modal,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Chip,
  IconButton,
} from "@mui/material";
import { Close, Search } from "@mui/icons-material";
import VoucherContextMenu from "./VoucherContextMenu";
import SortableTable, { HeadCell, Order, getComparator, stableSort } from "./SortableTable";
import ExportPrintToolbar from "./ExportPrintToolbar";
import autoTable from "jspdf-autotable";
import jsPDF from "jspdf";
interface VoucherListModalProps {
  open: boolean;
  onClose: () => void;
  voucherType: string;
  vouchers: any[];
  onVoucherClick: (voucher: any) => void;
  onEdit?: (id: number) => void;
  onView?: (id: number) => void;
  onDelete?: (id: number) => void;
  onGeneratePDF?: (voucher: any) => void;
  onDuplicate?: (voucher: any) => void;
  onCreateDispatch?: (voucher: any) => void;
  onRevise?: (voucher: any) => void;
  onCreateGRN?: (voucher: any) => void;
  onEditTracking?: (voucher: any) => void;
  onCreatePurchaseVoucher?: (voucher: any) => void;
  onCreateRejectionNote?: (voucher: any) => void;
  onChangeStatus?: (voucher: any) => void;
  customerList?: any[];
  vendorList?: any[];
  rowSx?: (row: any) => object;  // NEW: For color coding
}
const VoucherListModal: React.FC<VoucherListModalProps> = ({
  open,
  onClose,
  voucherType,
  vouchers,
  onVoucherClick,
  onEdit,
  onView,
  onDelete,
  onGeneratePDF,
  onDuplicate,
  onCreateDispatch,
  onRevise,
  onCreateGRN,
  onEditTracking,
  onCreatePurchaseVoucher,
  onCreateRejectionNote,
  onChangeStatus,
  customerList = [],
  vendorList = [],
  rowSx,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    voucher: any;
  } | null>(null);
  const [order, setOrder] = useState<Order>("desc");
  const [orderBy, setOrderBy] = useState<keyof any>("date");
  const getEntityName = (voucher: any) => {
    if (voucher.customer_id && customerList.length > 0) {
      return (
        customerList.find((c: any) => c.id === voucher.customer_id)?.name ||
        "N/A"
      );
    }
    if (voucher.vendor_id && vendorList.length > 0) {
      return (
        vendorList.find((v: any) => v.id === voucher.vendor_id)?.name || "N/A"
      );
    }
    return "N/A";
  };
  // Filter vouchers based on search criteria
  const filteredVouchers = vouchers.filter((voucher) => {
    const matchesSearch =
      searchTerm === "" ||
      voucher.voucher_number
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      voucher.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      voucher.notes?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      getEntityName(voucher).toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFromDate =
      fromDate === "" || new Date(voucher.date) >= new Date(fromDate);
    const matchesToDate =
      toDate === "" || new Date(voucher.date) <= new Date(toDate);
    return matchesSearch && matchesFromDate && matchesToDate;
  });
  const sortedFilteredVouchers = stableSort(filteredVouchers, getComparator(order, orderBy));
  const handleRequestSort = (property: keyof any) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };
  const handleContextMenu = (event: React.MouseEvent, voucher: any) => {
    event.preventDefault();
    setContextMenu(
      contextMenu === null
        ? { mouseX: event.clientX, mouseY: event.clientY, voucher }
        : null,
    );
  };
  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };
  const formatDate = (dateString: string) => {
    if (!dateString) {
      return "N/A";
    }
    return new Date(dateString).toLocaleDateString();
  };
  const headCells: HeadCell<any>[] = [
    {
      id: "voucher_number",
      label: "Voucher No.",
      numeric: false,
      sortable: true,
      width: "150px",
    },
    {
      id: "date",
      label: "Date",
      numeric: false,
      sortable: true,
      width: "120px",
      render: (value) => formatDate(value),
    },
    {
      id: "entity",
      label: "Customer",
      numeric: false,
      sortable: true,
      width: "200px",
      render: (_, row) => getEntityName(row),
    },
    {
      id: "total_amount",
      label: "Amount",
      numeric: true,
      sortable: true,
      width: "120px",
      render: (value) => `Rs.${value?.toLocaleString() || "0"}`,
    },
  ];
  const handleExportPDF = async () => {
    try {
      const doc = new jsPDF();
      let yPosition = 10;
      doc.setFontSize(16);
      doc.text(`All ${voucherType} Report`, 105, yPosition, { align: "center" });
      yPosition += 15;

      doc.setFontSize(10);
      doc.text(
        `Generated on: ${new Date().toLocaleDateString()}`,
        10,
        yPosition
      );
      doc.text(`Total Vouchers: ${filteredVouchers.length}`, 150, yPosition);
      yPosition += 10;

      const tableData = sortedFilteredVouchers.map((voucher) => [
        voucher.voucher_number,
        formatDate(voucher.date),
        getEntityName(voucher),
        `Rs.${voucher.total_amount?.toLocaleString() || "0"}`,
      ]);

      autoTable(doc, {
        startY: yPosition,
        head: [["Voucher No.", "Date", "Customer", "Amount"]],
        body: tableData,
        theme: "striped",
        headStyles: { fillColor: [22, 160, 133] },
        margin: { top: 10 },
      });

      doc.save(`all-${voucherType.toLowerCase()}-report.pdf`);
    } catch (error) {
      console.error("Error exporting PDF:", error);
      alert("Failed to export PDF");
    }
  };
  const modalStyle = {
    position: "absolute" as const,
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: "90%",
    maxWidth: 1000,
    bgcolor: "background.paper",
    boxShadow: 24,
    p: 4,
    borderRadius: 2,
    maxHeight: "90vh",
    overflow: "auto",
  };
  return (
    <>
      <Modal open={open} onClose={onClose}>
        <Box sx={modalStyle}>
          {/* Header */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">All {voucherType}</Typography>
            <IconButton onClick={onClose}>
              <Close />
            </IconButton>
          </Box>
          {/* Search Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="Voucher number, reference, notes..."
                InputProps={{
                  startAdornment: (
                    <Search sx={{ mr: 1, color: "text.secondary" }} />
                  ),
                }}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <TextField
                label="From Date"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <TextField
                label="To Date"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid size={{ xs: 12, md: 2 }}>
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchTerm("");
                  setFromDate("");
                  setToDate("");
                }}
                fullWidth
              >
                Clear
              </Button>
            </Grid>
          </Grid>
          {/* Results Summary and Export in same row */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Chip
              label={`${filteredVouchers.length} of ${vouchers.length} vouchers`}
              color="primary"
              variant="outlined"
            />
            <Box sx={{ width: { xs: 'auto', md: '168px' } }}> {/* Approximate width for md:2 grid column */}
              <ExportPrintToolbar
                showExcel={false}
                showCSV={false}
                showPrint={false}
                onExportPDF={handleExportPDF}
              />
            </Box>
          </Box>
          {/* Voucher Table */}
          <SortableTable
            data={sortedFilteredVouchers}
            headCells={headCells}
            defaultOrderBy="date"
            defaultOrder="desc"
            title={`All ${voucherType}`}
            onRowClick={(row) => { onView?.(row.id); onClose(); }} // NEW: Close modal after left-click view
            onRowContextMenu={handleContextMenu} // NEW: Pass handler for right-click on row
            actions={(row) => (
              <VoucherContextMenu
                voucher={row}
                voucherType={voucherType}
                onView={onView || (() => {})}
                onEdit={onEdit || (() => {})}
                onDelete={onDelete || (() => {})}
                onPrint={
                  onGeneratePDF
                    ? () => onGeneratePDF(row)
                    : undefined
                }
                onDuplicate={onDuplicate}
                onCreateDispatch={onCreateDispatch}
                onRevise={onRevise}
                onCreateGRN={onCreateGRN}
                onEditTracking={onEditTracking}
                onCreatePurchaseVoucher={onCreatePurchaseVoucher}
                onCreateRejectionNote={onCreateRejectionNote}
                onChangeStatus={onChangeStatus}
                open={false}
                onClose={() => {}}
                showKebab={true}
              />
            )}
            maxHeight={400}
            dense={true}
            stickyHeader={true}
            onRequestSort={handleRequestSort}
            rowSx={rowSx}
          />
        </Box>
      </Modal>
      {/* Context Menu */}
      {contextMenu && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType={voucherType}
          onView={onView || (() => {})}
          onEdit={onEdit || (() => {})}
          onDelete={onDelete || (() => {})}
          onPrint={
            onGeneratePDF ? () => onGeneratePDF(contextMenu.voucher) : undefined
          }
          onDuplicate={onDuplicate}
          onCreateDispatch={onCreateDispatch}
          onRevise={onRevise}
          onCreateGRN={onCreateGRN}
          onEditTracking={onEditTracking}
          onCreatePurchaseVoucher={onCreatePurchaseVoucher}
          onCreateRejectionNote={onCreateRejectionNote}
          onChangeStatus={onChangeStatus}
          open={true}
          onClose={handleCloseContextMenu}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}
    </>
  );
};
export default VoucherListModal;
