// frontend/src/pages/settings/index.tsx

import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useRouter } from 'next/navigation';
import { ProtectedPage } from '../../components/ProtectedPage';

const SettingsPage = () => {
  const router = useRouter();

  return (
    <ProtectedPage moduleKey="settings" action="read">
      <Box sx={{ p: 4 }}>
      <Typography variant="h4" sx={{ mb: 4 }}>
        Settings Dashboard
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button variant="contained" onClick={() => router.push('/settings/general-settings')}>
          General Settings
        </Button>
        <Button variant="contained" onClick={() => router.push('/settings/company')}>
          Company Profile
        </Button>
        <Button variant="contained" onClick={() => router.push('/settings/voucher-settings')}>
          Voucher Settings
        </Button>
        <Button variant="contained" onClick={() => router.push('/settings/DataManagement')}>
          Data Management
        </Button>
        <Button variant="contained" onClick={() => router.push('/settings/FactoryReset')}>
          Factory Reset
        </Button>
      </Box>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Administration
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" onClick={() => router.push('/admin/app-user-management')}>
            App Users
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/manage-organizations')}>
            Organization Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/organizations')}>
            Organization List
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/organizations/create')}>
            Create Organization
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/license-management')}>
            License Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/rbac')}>
            Role Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/service-settings')}>
            Service Settings
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/audit-logs')}>
            Audit Logs
          </Button>
          <Button variant="outlined" onClick={() => router.push('/admin/notifications')}>
            Notification Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/settings/user-management')}>
            User Management
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          System & Utilities
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" onClick={() => router.push('/reports')}>
            System Reports
          </Button>
          <Button variant="outlined" onClick={() => router.push('/migration/management')}>
            Migration Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/ui-test')}>
            UI Testing
          </Button>
          <Button variant="outlined" onClick={() => router.push('/notification-demo')}>
            Notification Demo
          </Button>
          <Button variant="outlined" onClick={() => router.push('/transport')}>
            Transport Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/assets')}>
            Assets Management
          </Button>
          <Button variant="outlined" onClick={() => router.push('/bank-accounts')}>
            Bank Accounts
          </Button>
        </Box>
      </Box>
    </Box>
    </ProtectedPage>
  );
};

export default SettingsPage;