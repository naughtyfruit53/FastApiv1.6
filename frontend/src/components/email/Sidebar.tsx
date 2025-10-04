import React from 'react';
import { Box, Button, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Inbox as InboxIcon, Send as SentIcon, Archive as ArchiveIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { MailAccount } from '../../services/emailService';

interface SidebarProps {
  accounts: MailAccount[];
  currentFolder: string;
  onFolderSelect: (folder: string) => void;
  onCompose: () => void;
  onSelectAccount: (accountId: number) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentFolder, onFolderSelect, onCompose }) => {
  const folders = [
    { key: 'INBOX', label: 'Inbox', icon: <InboxIcon /> },
    { key: 'SENT', label: 'Sent', icon: <SentIcon /> },
    { key: 'ARCHIVED', label: 'Archived', icon: <ArchiveIcon /> },
    { key: 'DELETED', label: 'Trash', icon: <DeleteIcon /> },
  ];

  return (
    <Box sx={{ width: 240, borderRight: 1, borderColor: 'divider', bgcolor: 'background.paper', height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onCompose}
          sx={{ mb: 2 }}
        >
          Compose
        </Button>
      </Box>

      <List dense>
        {folders.map((folder) => (
          <ListItem key={folder.key} disablePadding>
            <ListItemButton
              selected={currentFolder === folder.key}
              onClick={() => onFolderSelect(folder.key)}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {folder.icon}
              </ListItemIcon>
              <ListItemText primary={folder.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default Sidebar;