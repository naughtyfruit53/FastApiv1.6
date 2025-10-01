/**
 * Email Account Selector Component
 * Allows selecting an email token/account
 */

import React from 'react';
import { List, ListItem, ListItemButton, ListItemText, ListItemAvatar, Avatar, Typography } from '@mui/material';
import { Email as EmailIcon } from '@mui/icons-material';

interface EmailSelectorProps {
  accounts: MailAccount[];
  onSelect: (accountId: number) => void;
}

const EmailSelector: React.FC<EmailSelectorProps> = ({ accounts, onSelect }) => {
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
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default EmailSelector;