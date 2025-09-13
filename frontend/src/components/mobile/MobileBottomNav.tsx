import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import {
  Dashboard,
  Receipt,
  People,
  Assessment,
  Settings,
  AccountBalance,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface BottomNavItem {
  label: string;
  icon: React.ReactElement;
  path: string;
  value: string;
}

const bottomNavItems: BottomNavItem[] = [
  {
    label: 'Dashboard',
    icon: <Dashboard />,
    path: '/mobile/dashboard',
    value: 'dashboard',
  },
  {
    label: 'Sales',
    icon: <Receipt />,
    path: '/mobile/sales',
    value: 'sales',
  },
  {
    label: 'Finance',
    icon: <AccountBalance />,
    path: '/mobile/finance',
    value: 'finance',
  },
  {
    label: 'CRM',
    icon: <People />,
    path: '/mobile/crm',
    value: 'crm',
  },
  {
    label: 'Settings',
    icon: <Settings />,
    path: '/mobile/settings',
    value: 'settings',
  },
];

const MobileBottomNav: React.FC = () => {
  const router = useRouter();
  const { isMobile } = useMobileDetection();

  if (!isMobile) return null;

  // Determine active tab based on current route
  const getCurrentValue = (): string => {
    const path = router.pathname;
    if (path.includes('/dashboard')) return 'dashboard';
    if (path.includes('/sales')) return 'sales';
    if (path.includes('/finance')) return 'finance';
    if (path.includes('/crm')) return 'crm';
    if (path.includes('/settings')) return 'settings';
    return 'dashboard';
  };

  const handleNavigation = (event: React.SyntheticEvent, newValue: string) => {
    const item = bottomNavItems.find(item => item.value === newValue);
    if (item) {
      router.push(item.path);
    }
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        borderTop: '1px solid',
        borderColor: 'divider',
        boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.1)',
      }}
      elevation={3}
    >
      <BottomNavigation
        value={getCurrentValue()}
        onChange={handleNavigation}
        sx={{
          height: 60,
          '& .MuiBottomNavigationAction-root': {
            minWidth: 'auto',
            paddingTop: 1,
            paddingBottom: 1,
            '&.Mui-selected': {
              color: 'primary.main',
            },
          },
          '& .MuiBottomNavigationAction-label': {
            fontSize: '0.75rem',
            fontWeight: 500,
            marginTop: 0.5,
            '&.Mui-selected': {
              fontSize: '0.75rem',
            },
          },
        }}
      >
        {bottomNavItems.map((item) => (
          <BottomNavigationAction
            key={item.value}
            label={item.label}
            value={item.value}
            icon={item.icon}
          />
        ))}
      </BottomNavigation>
    </Paper>
  );
};

export default MobileBottomNav;