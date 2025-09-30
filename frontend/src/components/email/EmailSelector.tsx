/**
 * Email Account Selector Component
 * Allows selecting an email token/account
 */

import React from 'react';
import { List, ListItem, ListItemButton, ListItemText, ListItemAvatar, Avatar, Typography } from '@mui/material';
import { Email as EmailIcon } from '@mui/icons-material';

interface EmailSelectorProps {
  tokens: UserEmailToken[];
  onSelect: (tokenId: number) => void;
}

const EmailSelector: React.FC<EmailSelectorProps> = ({ tokens, onSelect }) => {
  return (
    <List>
      {tokens.map(token => (
        <ListItem key={token.id} disablePadding>
          <ListItemButton onClick={() => onSelect(token.id)}>
            <ListItemAvatar>
              <Avatar>
                <EmailIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText 
              primary={token.email_address}
              secondary={
                <>
                  <Typography component="span" variant="body2">
                    {token.provider.toUpperCase()}
                  </Typography>
                  {token.display_name && ` - ${token.display_name}`}
                </>
              }
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default EmailSelector;