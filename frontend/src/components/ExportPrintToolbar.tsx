'use client';

import React, { useState } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Download,
  Print,
  GetApp,
  TableChart,
  Description
} from '@mui/icons-material';
import { saveAs } from 'file-saver';

interface ExportPrintToolbarProps {
  onExportExcel?: () => Promise<Blob | void>;
  onExportCSV?: () => Promise<Blob | void>;
  onPrint?: () => void;
  showExcel?: boolean;
  showCSV?: boolean;
  showPrint?: boolean;
  disabled?: boolean;
  loading?: boolean;
  filename?: string;
}

const ExportPrintToolbar: React.FC<ExportPrintToolbarProps> = ({
  onExportExcel,
  onExportCSV,
  onPrint,
  showExcel = true,
  showCSV = true,
  showPrint = true,
  disabled = false,
  loading = false,
  filename = 'report'
}) => {
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const handleExportClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const handleExcelExport = async () => {
    if (!onExportExcel) return;
    
    setIsExporting(true);
    try {
      const blob = await onExportExcel();
      if (blob) {
        saveAs(blob, `${filename}.xlsx`);
      }
    } catch (error) {
      console.error('Error exporting Excel:', error);
      // You might want to show a toast notification here
    } finally {
      setIsExporting(false);
      handleExportClose();
    }
  };

  const handleCSVExport = async () => {
    if (!onExportCSV) return;
    
    setIsExporting(true);
    try {
      const blob = await onExportCSV();
      if (blob) {
        saveAs(blob, `${filename}.csv`);
      }
    } catch (error) {
      console.error('Error exporting CSV:', error);
      // You might want to show a toast notification here
    } finally {
      setIsExporting(false);
      handleExportClose();
    }
  };

  const handlePrint = () => {
    if (onPrint) {
      onPrint();
    } else {
      // Default print behavior
      window.print();
    }
  };

  const hasExportOptions = (showExcel && onExportExcel) || (showCSV && onExportCSV);

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      {hasExportOptions && (
        <>
          <Button
            startIcon={loading || isExporting ? <CircularProgress size={16} /> : <Download />}
            size="small"
            variant="outlined"
            onClick={handleExportClick}
            disabled={disabled || loading || isExporting}
            aria-label="Export options"
          >
            Export
          </Button>
          <Menu
            anchorEl={exportAnchorEl}
            open={Boolean(exportAnchorEl)}
            onClose={handleExportClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'left',
            }}
          >
            {showExcel && onExportExcel && (
              <MenuItem onClick={handleExcelExport} disabled={isExporting}>
                <TableChart sx={{ mr: 1 }} fontSize="small" />
                Export to Excel
              </MenuItem>
            )}
            {showCSV && onExportCSV && (
              <MenuItem onClick={handleCSVExport} disabled={isExporting}>
                <Description sx={{ mr: 1 }} fontSize="small" />
                Export to CSV
              </MenuItem>
            )}
          </Menu>
        </>
      )}
      
      {showPrint && (
        <Tooltip title="Print Report">
          <IconButton
            size="small"
            onClick={handlePrint}
            disabled={disabled || loading}
            aria-label="Print report"
          >
            <Print />
          </IconButton>
        </Tooltip>
      )}
    </Box>
  );
};

export default ExportPrintToolbar;