'use client';

/**
 * Main Email Module Page
 * Coordinates Inbox, ThreadView, and Composer components
 */

import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer, Alert, CircularProgress, Button } from '@mui/material';
import { Menu as MenuIcon, Settings as SettingsIcon, Add as AddIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMailAccounts, Email, MailAccount } from '../../services/emailService';
import { useOAuth } from '../../hooks/useOAuth';
import { useEmail } from '../../context/EmailContext';
import Inbox from './Inbox';
import ThreadView from './ThreadView';
import Composer from './Composer';
import Sidebar from '../../components/email/Sidebar';
import EmailSelector from '../../components/email/EmailSelector';
import OAuthLoginButton from '../../components/OAuthLoginButton';
import { useRouter } from 'next/router';

type View = 'inbox' | 'thread' | 'compose' | 'select-account' | 'settings' | 'search' | 'attachments';

const EmailModule: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { getUserTokens } = useOAuth();
  const { selectedAccountId, setSelectedAccountId } = useEmail();

  const [currentView, setCurrentView] = useState<View>('inbox');
  const [selectedEmail, setSelectedEmail] = useState<Email | undefined>();
  const [selectedThreadId, setSelectedThreadId] = useState<number | undefined>();
  const [composerMode, setComposerMode] = useState<'new' | 'reply' | 'replyAll' | 'forward'>('new');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState('INBOX');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);

  // Fetch OAuth tokens
  const { data: tokens = [], isLoading: tokensLoading, error: tokensError } = useQuery({
    queryKey: ['oauth-tokens'],
    queryFn: getUserTokens
  });

  // Fetch mail accounts
  const { data: accounts = [], isLoading: accountsLoading, error: accountsError } = useQuery({
    queryKey: ['mail-accounts'],
    queryFn: getMailAccounts,
    onSuccess: (data) => {
      console.log('[EmailModule] Mail accounts loaded:', data);
      // Auto-select if none selected and accounts available
      if (data.length > 0 && !selectedAccountId) {
        setSelectedAccountId(data[0].id);
      }
    },
    onError: (error) => {
      console.error('[EmailModule] Error loading mail accounts:', error);
    }
  });

  // Find selected account based on account ID
  const selectedAccount = accounts.find(acc => acc.id === selectedAccountId);

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: (accountId: number) => emailService.triggerSync(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    }
  });

  // Auto-sync if account selected and no previous sync
  React.useEffect(() => {
    if (selectedAccount && !selectedAccount.last_sync_at && !syncMutation.isPending) {
      syncMutation.mutate(selectedAccount.id);
    }
  }, [selectedAccount, syncMutation]);

  const handleEmailSelect = (email: Email) => {
    setSelectedEmail(email);
    if (email.thread_id) {
      setSelectedThreadId(email.thread_id);
    }
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

  const handleSelectAccount = (accountId: number) => {
    setSelectedAccountId(accountId);
    setCurrentView('inbox');
    queryClient.invalidateQueries({ queryKey: ['emails'] });
  };

  const handleFolderSelect = (folder: string) => {
    setCurrentFolder(folder);
    setPage(1); // Reset page when changing folder
    setCurrentView('inbox'); // Ensure switch back to inbox view
  };

  const renderMainContent = () => {
    switch (currentView) {
      case 'inbox':
        return (
          <Inbox
            selectedAccount={selectedAccount}
            onEmailSelect={handleEmailSelect}
            onThreadSelect={setSelectedThreadId}
            onCompose={() => handleCompose('new')}
            onAccountSelect={handleSelectAccount}
            currentFolder={currentFolder}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            page={page}
            setPage={setPage}
          />
        );
      case 'thread':
        return (
          <ThreadView
            threadId={selectedThreadId}
            initialEmail={selectedEmail}
            onBack={handleBackToInbox}
            onReply={(email) => handleCompose('reply', email)}
            onReplyAll={(email) => handleCompose('replyAll', email)}
            onForward={(email) => handleCompose('forward', email)}
          />
        );
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

  if (accountsError) {
    return <Alert severity="error">Failed to load mail accounts: {(accountsError as Error).message}</Alert>;
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

  if (!selectedAccountId || !selectedAccount) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Select Email Account
        </Typography>
        <EmailSelector 
          accounts={accounts} 
          onSelect={handleSelectAccount}
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
          <IconButton color="inherit" onClick={() => router.push('/email/accounts')}>
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar
          accounts={accounts}
          currentFolder={currentFolder}
          onFolderSelect={handleFolderSelect}
          onCompose={() => handleCompose('new')}
          onSelectAccount={handleSelectAccount}
        />
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {renderMainContent()}
        </Box>
      </Box>

      <Drawer anchor="left" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 250, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Accounts
          </Typography>
          <EmailSelector 
            accounts={accounts} 
            onSelect={(id) => {
              handleSelectAccount(id);
              setDrawerOpen(false);
            }} 
          />
        </Box>
      </Drawer>
    </Box>
  );
};

export default EmailModule;