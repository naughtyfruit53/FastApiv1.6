// frontend/src/components/EmailAttachmentDisplay.tsx

/**
 * Email Attachment Display Component (Requirement 4)
 * Shows exact count, dropdown list, and click-to-download functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AttachFile as AttachFileIcon,
  Download as DownloadIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  Description as DocIcon,
  TableChart as ExcelIcon,
  Archive as ZipIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';

interface Attachment {
  id: string | number;
  filename: string;
  size?: number;
  mime_type?: string;
  download_url?: string;
}

interface EmailAttachmentDisplayProps {
  attachments: Attachment[];
  onDownload?: (attachment: Attachment) => void;
  variant?: 'button' | 'chip' | 'compact';
}

const EmailAttachmentDisplay: React.FC<EmailAttachmentDisplayProps> = ({
  attachments,
  onDownload,
  variant = 'button'
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDownload = (attachment: Attachment) => {
    if (onDownload) {
      onDownload(attachment);
    } else if (attachment.download_url) {
      // Default download behavior
      const link = document.createElement('a');
      link.href = attachment.download_url;
      link.download = attachment.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
    handleClose();
  };

  const getFileIcon = (mimeType?: string, filename?: string) => {
    if (!mimeType && filename) {
      const ext = filename.split('.').pop()?.toLowerCase();
      if (ext === 'pdf') return <PdfIcon />;
      if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext || '')) return <ImageIcon />;
      if (['doc', 'docx'].includes(ext || '')) return <DocIcon />;
      if (['xls', 'xlsx', 'csv'].includes(ext || '')) return <ExcelIcon />;
      if (['zip', 'rar', '7z'].includes(ext || '')) return <ZipIcon />;
    }

    if (mimeType?.includes('pdf')) return <PdfIcon />;
    if (mimeType?.includes('image')) return <ImageIcon />;
    if (mimeType?.includes('word') || mimeType?.includes('document')) return <DocIcon />;
    if (mimeType?.includes('excel') || mimeType?.includes('spreadsheet')) return <ExcelIcon />;
    if (mimeType?.includes('zip') || mimeType?.includes('compressed')) return <ZipIcon />;
    
    return <FileIcon />;
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!attachments || attachments.length === 0) {
    return null;
  }

  const attachmentCount = attachments.length;
  const totalSize = attachments.reduce((sum, att) => sum + (att.size || 0), 0);

  if (variant === 'chip') {
    return (
      <>
        <Chip
          icon={<AttachFileIcon />}
          label={`${attachmentCount} attachment${attachmentCount !== 1 ? 's' : ''}`}
          onClick={handleClick}
          size="small"
          variant="outlined"
          sx={{ cursor: 'pointer' }}
        />
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          PaperProps={{
            sx: { minWidth: 250, maxWidth: 400 }
          }}
        >
          {attachments.map((attachment) => (
            <MenuItem
              key={attachment.id}
              onClick={() => handleDownload(attachment)}
              sx={{ py: 1.5 }}
            >
              <ListItemIcon>
                {getFileIcon(attachment.mime_type, attachment.filename)}
              </ListItemIcon>
              <ListItemText
                primary={attachment.filename}
                secondary={formatFileSize(attachment.size)}
                primaryTypographyProps={{ noWrap: true }}
              />
              <DownloadIcon fontSize="small" sx={{ ml: 1, color: 'action.active' }} />
            </MenuItem>
          ))}
        </Menu>
      </>
    );
  }

  if (variant === 'compact') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <AttachFileIcon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
          {attachmentCount} attachment{attachmentCount !== 1 ? 's' : ''}
          {totalSize > 0 && ` (${formatFileSize(totalSize)})`}
        </Typography>
        <IconButton size="small" onClick={handleClick}>
          <ExpandMoreIcon />
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          PaperProps={{
            sx: { minWidth: 250, maxWidth: 400 }
          }}
        >
          {attachments.map((attachment) => (
            <MenuItem
              key={attachment.id}
              onClick={() => handleDownload(attachment)}
              sx={{ py: 1.5 }}
            >
              <ListItemIcon>
                {getFileIcon(attachment.mime_type, attachment.filename)}
              </ListItemIcon>
              <ListItemText
                primary={attachment.filename}
                secondary={formatFileSize(attachment.size)}
                primaryTypographyProps={{ noWrap: true }}
              />
              <DownloadIcon fontSize="small" sx={{ ml: 1, color: 'action.active' }} />
            </MenuItem>
          ))}
        </Menu>
      </Box>
    );
  }

  // Default button variant
  return (
    <>
      <Tooltip title="View and download attachments">
        <Button
          startIcon={<AttachFileIcon />}
          endIcon={<ExpandMoreIcon />}
          onClick={handleClick}
          variant="outlined"
          size="small"
        >
          {attachmentCount} attachment{attachmentCount !== 1 ? 's' : ''}
          {totalSize > 0 && ` (${formatFileSize(totalSize)})`}
        </Button>
      </Tooltip>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: { minWidth: 300, maxWidth: 450 }
        }}
      >
        <Box sx={{ px: 2, py: 1, bgcolor: 'grey.50' }}>
          <Typography variant="subtitle2" color="text.secondary">
            Attachments ({attachmentCount})
          </Typography>
        </Box>
        {attachments.map((attachment) => (
          <MenuItem
            key={attachment.id}
            onClick={() => handleDownload(attachment)}
            sx={{ py: 1.5, px: 2 }}
          >
            <ListItemIcon>
              {getFileIcon(attachment.mime_type, attachment.filename)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Typography variant="body2" noWrap>
                  {attachment.filename}
                </Typography>
              }
              secondary={
                <Typography variant="caption" color="text.secondary">
                  {formatFileSize(attachment.size)}
                </Typography>
              }
            />
            <Tooltip title="Download">
              <IconButton size="small" sx={{ ml: 1 }}>
                <DownloadIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default EmailAttachmentDisplay;
