/**
 * Main Email Module Page
 * Coordinates Inbox, ThreadView, and Composer components
 */

import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer } from '@mui/material';
import { Menu as MenuIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { emailService, Email, MailAccount } from '../../services/emailService';
import Inbox from './Inbox';
import ThreadView from './ThreadView';
import Composer from './Composer';

type View = 'inbox' | 'thread' | 'compose';

const EmailModule: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>('inbox');
  const [selectedAccount, setSelectedAccount] = useState<MailAccount | undefined>();
  const [selectedEmail, setSelectedEmail] = useState<Email | undefined>();
  const [selectedThreadId, setSelectedThreadId] = useState<number | undefined>();
  const [composerMode, setComposerMode] = useState<'new' | 'reply' | 'replyAll' | 'forward'>('new');
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Fetch mail accounts and set default
  const { data: accounts = [] } = useQuery({
    queryKey: ['mail-accounts'],
    queryFn: emailService.getMailAccounts,
    onSuccess: (data) => {
      if (data.length > 0 && !selectedAccount) {
        setSelectedAccount(data[0]);
      }
    }
  });

  const handleEmailSelect = (email: Email) => {
    setSelectedEmail(email);
    if (email.thread_id) {
      setSelectedThreadId(email.thread_id);
      setCurrentView('thread');
    } else {
      // For single emails, we could show a detail view or open in thread view
      setCurrentView('thread');
    }
  };

  const handleThreadSelect = (threadId: number) => {
    setSelectedThreadId(threadId);
    setCurrentView('thread');
  };

  const handleCompose = (mode: 'new' | 'reply' | 'replyAll' | 'forward' = 'new', email?: Email) => {
    setComposerMode(mode);
    if (email) {
      setSelectedEmail(email);
    }
    setCurrentView('compose');
  };

  const handleBackToInbox = () => {
    setCurrentView('inbox');
    setSelectedEmail(undefined);
    setSelectedThreadId(undefined);
  };

  const handleEmailSent = (_emailId: number) => {
    // Email sent successfully, return to inbox
    setCurrentView('inbox');
  };

  const handleAccountSelect = (account: MailAccount) => {
    setSelectedAccount(account);
    setCurrentView('inbox');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'inbox':
        return (
          <Inbox
            selectedAccount={selectedAccount}
            onEmailSelect={handleEmailSelect}
            onThreadSelect={handleThreadSelect}
            onCompose={() => handleCompose('new')}
          />
        );
      
      case 'thread':
        return selectedThreadId ? (
          <ThreadView
            threadId={selectedThreadId}
            onBack={handleBackToInbox}
            onReply={(email) => handleCompose('reply', email)}
            onReplyAll={(email) => handleCompose('replyAll', email)}
            onForward={(email) => handleCompose('forward', email)}
          />
        ) : null;
      
      case 'compose':
        return (
          <Composer
            mode={composerMode}
            originalEmail={selectedEmail}
            selectedAccount={selectedAccount}
            onClose={handleBackToInbox}
            onSent={handleEmailSent}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Email - {selectedAccount?.display_name || selectedAccount?.email_address || 'No Account Selected'}
          </Typography>
          
          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {renderCurrentView()}
      </Box>

      {/* Account Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 280, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Email Accounts
          </Typography>
          
          {accounts.map((account) => (
            <Box
              key={account.id}
              sx={{
                p: 2,
                mb: 1,
                borderRadius: 1,
                border: 1,
                borderColor: selectedAccount?.id === account.id ? 'primary.main' : 'divider',
                bgcolor: selectedAccount?.id === account.id ? 'primary.light' : 'background.paper',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
              onClick={() => {
                handleAccountSelect(account);
                setDrawerOpen(false);
              }}
            >
              <Typography variant="body2" fontWeight="bold" noWrap>
                {account.display_name || account.email_address}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {account.email_address}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                {account.sync_enabled ? 'Sync enabled' : 'Sync disabled'} • {account.total_messages_synced} messages
              </Typography>
            </Box>
          ))}
          
          {accounts.length === 0 && (
            <Typography color="text.secondary">
              No email accounts configured. Click "Connect Your Email Account" to get started.
            </Typography>
          )}
        </Box>
      </Drawer>
    </Box>
  );
};

export default EmailModule;