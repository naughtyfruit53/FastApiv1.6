/**
 * Email Account Selector Component
 * Allows selecting an email token/account
 */

import React from 'react';
import { List, ListItem, ListItemButton, ListItemText, ListItemAvatar, Avatar, Chip } from '@mui/material';
import { Email as EmailIcon, Sync as SyncIcon, SyncDisabled as SyncDisabledIcon } from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../lib/api';

interface EmailSelectorProps {
  accounts: MailAccount[];
  onSelect: (accountId: number) => void;
}

const EmailSelector: React.FC<EmailSelectorProps> = ({ accounts, onSelect }) => {
  const queryClient = useQueryClient();
  
  const toggleSyncMutation = useMutation({
    mutationFn: async (accountId: number) => {
      const account = accounts.find(a => a.id === accountId);
      if (!account) throw new Error('Account not found');
      
      const response = await api.put(`/email/accounts/${accountId}`, {
        sync_enabled: !account.sync_enabled
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mail-accounts'] });
    }
  });

  const handleToggleSync = (accountId: number) => {
    toggleSyncMutation.mutate(accountId);
  };

  return (
    <List>
      {accounts.map(account => (
        <ListItem key={account.id} disablePadding>
          <ListItemButton onClick={() => onSelect(account.id)}>
            <ListItemAvatar>
              <Avatar>
                <EmailIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText 
              primary={account.email_address}
              secondary={`${account.provider?.toUpperCase() || 'CUSTOM'} - ${account.display_name || 'No name'}`}
            />
            <Chip
              label={account.sync_enabled ? 'Sync Enabled' : 'Sync Disabled'}
              color={account.sync_enabled ? 'success' : 'default'}
              size="small"
              icon={account.sync_enabled ? <SyncIcon /> : <SyncDisabledIcon />}
              onClick={(e) => {
                e.stopPropagation();
                handleToggleSync(account.id);
              }}
              sx={{ cursor: 'pointer' }}
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default EmailSelector;