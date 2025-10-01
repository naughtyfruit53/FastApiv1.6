'use client';

/**
 * Main Email Module Page
 * Coordinates Inbox, ThreadView, and Composer components
 */

import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer, Alert, CircularProgress, Button } from '@mui/material';
import { Menu as MenuIcon, Settings as SettingsIcon, Add as AddIcon } from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { emailService, Email, MailAccount } from '../../services/emailService';
import { useOAuth } from '../../hooks/useOAuth';
import { useEmail } from '../../context/EmailContext';
import Inbox from './Inbox';
import ThreadView from './ThreadView';
import Composer from './Composer';
import EmailSelector from '../../components/email/EmailSelector';
import OAuthLoginButton from '../../components/OAuthLoginButton';

type View = 'inbox' | 'thread' | 'compose' | 'select-account' | 'settings' | 'search' | 'attachments';

const EmailModule: React.FC = () => {
  const queryClient = useQueryClient();
  const { getUserTokens } = useOAuth();
  const { selectedToken, setSelectedToken } = useEmail();

  const [currentView, setCurrentView] = useState<View>('inbox');
  const [selectedEmail, setSelectedEmail] = useState<Email | undefined>();
  const [selectedThreadId, setSelectedThreadId] = useState<number | undefined>();
  const [composerMode, setComposerMode] = useState<'new' | 'reply' | 'replyAll' | 'forward'>('new');
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Fetch OAuth tokens
  const { data: tokens = [], isLoading: tokensLoading, error: tokensError } = useQuery({
    queryKey: ['oauth-tokens'],
    queryFn: getUserTokens
  });

  // Fetch mail accounts
  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['mail-accounts'],
    queryFn: emailService.getMailAccounts,
    onSuccess: (data) => {
      // Auto-select if none selected and accounts available
      if (data.length > 0 && !selectedToken) {
        const defaultToken = tokens.find(t => t.email_address === data[0].email_address);
        if (defaultToken) {
          setSelectedToken(defaultToken.id);
        } else if (tokens.length > 0) {
          setSelectedToken(tokens[0].id);
        }
      }
    }
  });

  // Find selected account based on token
  const selectedAccount = accounts.find(acc => acc.oauth_token_id === selectedToken);

  const handleEmailSelect = (email: Email) => {
    setSelectedEmail(email);
    if (email.thread_id) {
      setSelectedThreadId(email.thread_id);
      setCurrentView('thread');
    } else {
      setCurrentView('thread');
    }
  };

  const handleThreadSelect = (threadId: number) => {
    setSelectedThreadId(threadId);
    setCurrentView('thread');
  };

  const handleCompose = (mode: 'new' | 'reply' | 'replyAll' | 'forward' = 'new', email?: Email) => {
    setComposerMode(mode);
    if (email) setSelectedEmail(email);
    setCurrentView('compose');
  };

  const handleBackToInbox = () => {
    setCurrentView('inbox');
    setSelectedEmail(undefined);
    setSelectedThreadId(undefined);
  };

  const handleSelectToken = (tokenId: number) => {
    setSelectedToken(tokenId);
    setCurrentView('inbox');
    queryClient.invalidateQueries({ queryKey: ['emails'] });
  };

  const handleAccountSelect = (accountId: number) => {
    // Find the token associated with this account
    const account = accounts.find(acc => acc.id === accountId);
    if (account && account.oauth_token_id) {
      handleSelectToken(account.oauth_token_id);
    }
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
            onAccountSelect={handleAccountSelect}
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
            onSent={handleBackToInbox}
          />
        );
      case 'settings':
        return (
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Email Settings</Typography>
            <Typography variant="body2" color="text.secondary">
              Manage your email accounts, sync settings, and preferences
            </Typography>
            <Button variant="outlined" onClick={handleBackToInbox} sx={{ mt: 2 }}>
              Back to Inbox
            </Button>
          </Box>
        );
      case 'search':
        return (
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Email Search</Typography>
            <Typography variant="body2" color="text.secondary">
              Search across all your emails and attachments
            </Typography>
            <Button variant="outlined" onClick={handleBackToInbox} sx={{ mt: 2 }}>
              Back to Inbox
            </Button>
          </Box>
        );
      case 'attachments':
        return (
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Email Attachments</Typography>
            <Typography variant="body2" color="text.secondary">
              View and manage all email attachments
            </Typography>
            <Button variant="outlined" onClick={handleBackToInbox} sx={{ mt: 2 }}>
              Back to Inbox
            </Button>
          </Box>
        );
      default:
        return null;
    }
  };

  if (tokensLoading || accountsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (tokensError) {
    return <Alert severity="error">Failed to load email accounts: {(tokensError as Error).message}</Alert>;
  }

  if (tokens.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          No Email Accounts Connected
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Connect your email account to get started
        </Typography>
        <OAuthLoginButton />
      </Box>
    );
  }

  if (!selectedToken || !selectedAccount) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Select Email Account
        </Typography>
        <EmailSelector 
          tokens={tokens} 
          onSelect={handleSelectToken}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => setDrawerOpen(true)} sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Email - {selectedAccount.display_name || selectedAccount.email_address}
          </Typography>
          <IconButton color="inherit" onClick={() => handleCompose('new')}>
            <AddIcon />
          </IconButton>
          <IconButton color="inherit" onClick={() => setCurrentView('settings')}>
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {renderCurrentView()}
      </Box>

      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 250, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Accounts
          </Typography>
          <EmailSelector 
            tokens={tokens} 
            onSelect={(id) => {
              handleSelectToken(id);
              setDrawerOpen(false);
            }} 
          />
        </Box>
      </Drawer>
    </Box>
  );
};

export default EmailModule;