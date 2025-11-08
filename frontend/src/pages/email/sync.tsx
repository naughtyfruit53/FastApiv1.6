'use client';

/**
 * Email Sync Status Page
 * Monitor email synchronization status
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Sync as SyncIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { getMailAccounts, MailAccount } from '../../services/emailService';
import { ProtectedPage } from '../../components/ProtectedPage';

const SyncStatus: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);

  const { data: accounts = [], isLoading, error, refetch } = useQuery({
    queryKey: ['mailAccounts'],
    queryFn: getMailAccounts,
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const getSyncStatus = (account: MailAccount) => {
    if (!account.sync_enabled) {
      return { label: 'Disabled', color: 'default' as const, icon: null };
    }
    if (account.last_sync_at) {
      return { 
        label: 'Synced', 
        color: 'success' as const, 
        icon: <CheckCircleIcon fontSize="small" /> 
      };
    }
    return { 
      label: 'Pending', 
      color: 'warning' as const, 
      icon: <SyncIcon fontSize="small" /> 
    };
  };

  const formatLastSync = (lastSync: string | null) => {
    if (!lastSync) return 'Never';
    const date = new Date(lastSync);
    return date.toLocaleString();
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Failed to load sync status. Please try again later.</Alert>
      </Box>
    );
  }

  return (
    <ProtectedPage moduleKey="email" action="read">
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Email Sync Status
        </Typography>
        <Button
          variant="outlined"
          startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          Refresh
        </Button>
      </Box>

      {accounts.length === 0 ? (
        <Alert severity="info">
          No email accounts configured. Add an account to start syncing emails.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Account</strong></TableCell>
                <TableCell><strong>Email Address</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Last Sync</strong></TableCell>
                <TableCell><strong>Total Emails</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {accounts.map((account) => {
                const status = getSyncStatus(account);
                return (
                  <TableRow key={account.id}>
                    <TableCell>{account.display_name || account.name || 'Unnamed'}</TableCell>
                    <TableCell>{account.email_address}</TableCell>
                    <TableCell>
                      <Chip
                        label={status.label}
                        color={status.color}
                        size="small"
                        icon={status.icon || undefined}
                      />
                    </TableCell>
                    <TableCell>{formatLastSync(account.last_sync_at)}</TableCell>
                    <TableCell>
                      {account.total_emails || 0}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          About Email Sync
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Email synchronization runs automatically in the background to keep your inbox up to date.
          The system checks for new emails at regular intervals based on your account settings.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Sync Frequency:</strong> Every 5 minutes for active accounts
        </Typography>
      </Paper>
    </Box>
    </ProtectedPage>
  );
};

export default SyncStatus;
