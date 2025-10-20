"use client";
import React, { useState } from "react";
import {
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  CircularProgress,
} from "@mui/material";
import {
  FileDownload as DownloadIcon,
  FileUpload as UploadIcon,
  GetApp as TemplateIcon,
  ExpandMore as ExpandMoreIcon,
} from "@mui/icons-material";
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";

interface LeadsImportExportDropdownProps {
  leads: any[];
  onImport: (importedLeads: any[]) => void;
}

const LeadsImportExportDropdown: React.FC<LeadsImportExportDropdownProps> = ({
  leads,
  onImport,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const downloadTemplate = async () => {
    try {
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet("Leads Template");

      // Define columns
      worksheet.columns = [
        { header: "first_name", key: "first_name", width: 15 },
        { header: "last_name", key: "last_name", width: 15 },
        { header: "email", key: "email", width: 25 },
        { header: "phone", key: "phone", width: 15 },
        { header: "company", key: "company", width: 20 },
        { header: "job_title", key: "job_title", width: 20 },
        { header: "source", key: "source", width: 15 },
        { header: "status", key: "status", width: 15 },
        { header: "score", key: "score", width: 10 },
        { header: "estimated_value", key: "estimated_value", width: 15 },
        { header: "expected_close_date", key: "expected_close_date", width: 20 },
      ];

      // Add sample row
      worksheet.addRow({
        first_name: "John",
        last_name: "Doe",
        email: "john.doe@example.com",
        phone: "+1-555-0123",
        company: "Example Corp",
        job_title: "CEO",
        source: "website",
        status: "new",
        score: 75,
        estimated_value: 50000,
        expected_close_date: "2024-12-31",
      });

      // Generate and download file
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      saveAs(blob, "leads_import_template.xlsx");
    } catch (error) {
      console.error("Error creating template:", error);
    }

    handleClose();
  };

  const handleImportClick = () => {
    setImportDialogOpen(true);
    handleClose();
  };

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setImporting(true);
      setImportError(null);

      // Read the file
      const buffer = await file.arrayBuffer();
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.load(buffer);

      // Get first sheet
      const worksheet = workbook.worksheets[0];

      // Convert to JSON
      const jsonData: any[] = [];
      worksheet.eachRow((row, rowNumber) => {
        if (rowNumber === 1) return; // Skip header row

        const rowData: any = {};
        row.eachCell((cell, colNumber) => {
          const header = worksheet.getRow(1).getCell(colNumber).value as string;
          rowData[header] = cell.value;
        });
        jsonData.push(rowData);
      });

      if (jsonData.length === 0) {
        setImportError("The file is empty. Please upload a valid file.");
        return;
      }

      // Validate and pass to parent
      onImport(jsonData);
      setImportDialogOpen(false);
    } catch (error) {
      console.error("Error importing leads:", error);
      setImportError(
        "Failed to import leads. Please check the file format and try again.",
      );
    } finally {
      setImporting(false);
    }
  };

  const exportLeads = async () => {
    if (leads.length === 0) {
      alert("No leads to export");
      return;
    }

    try {
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet("Leads");

      // Define columns
      worksheet.columns = [
        { header: "first_name", key: "first_name", width: 15 },
        { header: "last_name", key: "last_name", width: 15 },
        { header: "email", key: "email", width: 25 },
        { header: "phone", key: "phone", width: 15 },
        { header: "company", key: "company", width: 20 },
        { header: "job_title", key: "job_title", width: 20 },
        { header: "source", key: "source", width: 15 },
        { header: "status", key: "status", width: 15 },
        { header: "score", key: "score", width: 10 },
        { header: "estimated_value", key: "estimated_value", width: 15 },
        { header: "expected_close_date", key: "expected_close_date", width: 20 },
        { header: "created_at", key: "created_at", width: 20 },
      ];

      // Add data rows
      leads.forEach((lead) => {
        worksheet.addRow({
          first_name: lead.first_name || "",
          last_name: lead.last_name || "",
          email: lead.email || "",
          phone: lead.phone || "",
          company: lead.company || "",
          job_title: lead.job_title || "",
          source: lead.source || "",
          status: lead.status || "",
          score: lead.score || 0,
          estimated_value: lead.estimated_value || 0,
          expected_close_date: lead.expected_close_date || "",
          created_at: lead.created_at || "",
        });
      });

      // Generate and download file
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const timestamp = new Date().toISOString().split("T")[0];
      saveAs(blob, `leads_export_${timestamp}.xlsx`);
    } catch (error) {
      console.error("Error exporting leads:", error);
      alert("Failed to export leads. Please try again.");
    }

    handleClose();
  };

  return (
    <>
      <Button
        variant="outlined"
        onClick={handleClick}
        endIcon={<ExpandMoreIcon />}
      >
        Import/Export
      </Button>
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
        <MenuItem onClick={downloadTemplate}>
          <ListItemIcon>
            <TemplateIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Download Template</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleImportClick}>
          <ListItemIcon>
            <UploadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Import Leads</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportLeads}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Leads</ListItemText>
        </MenuItem>
      </Menu>

      {/* Import Dialog */}
      <Dialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Import Leads</DialogTitle>
        <DialogContent>
          <Box sx={{ py: 2 }}>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Upload an Excel file (.xlsx, .xls) or CSV file with lead data.
              Make sure your file follows the template format.
            </Typography>
            {importError && (
              <Typography color="error" variant="body2" sx={{ mb: 2 }}>
                {importError}
              </Typography>
            )}
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileSelect}
              disabled={importing}
              style={{ width: "100%" }}
            />
            {importing && (
              <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2">Importing leads...</Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default LeadsImportExportDropdown;
