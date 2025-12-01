import React, { useState } from 'react';
import { BottomNavigation, BottomNavigationAction, Paper, Menu, MenuItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import {
  Dashboard,
  Receipt,
  People,
  Settings,
  AccountBalance,
  Menu as MenuIcon,
  Inventory,
  Engineering,
  Email,
  SupportAgent,
  Campaign,
  Assessment,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface BottomNavItem {
  label: string;
  icon: React.ReactElement;
  path: string;
  value: string;
}

// Primary bottom navigation items (5 max for mobile UX)
const bottomNavItems: BottomNavItem[] = [
  {
    label: 'Home',
    icon: <Dashboard />,
    path: '/dashboard',
    value: 'dashboard',
  },
  {
    label: 'Sales',
    icon: <Receipt />,
    path: '/sales/dashboard',
    value: 'sales',
  },
  {
    label: 'Finance',
    icon: <AccountBalance />,
    path: '/finance-dashboard',
    value: 'finance',
  },
  {
    label: 'CRM',
    icon: <People />,
    path: '/crm',
    value: 'crm',
  },
  {
    label: 'More',
    icon: <MenuIcon />,
    path: '',
    value: 'more',
  },
];

// Overflow menu items for "More"
const moreMenuItems: BottomNavItem[] = [
  { label: 'Inventory', icon: <Inventory />, path: '/inventory', value: 'inventory' },
  { label: 'Manufacturing', icon: <Engineering />, path: '/order-book', value: 'manufacturing' },
  { label: 'Service', icon: <SupportAgent />, path: '/service/dashboard', value: 'service' },
  { label: 'Marketing', icon: <Campaign />, path: '/marketing', value: 'marketing' },
  { label: 'Reports', icon: <Assessment />, path: '/reports', value: 'reports' },
  { label: 'Email', icon: <Email />, path: '/email', value: 'email' },
  { label: 'Settings', icon: <Settings />, path: '/settings', value: 'settings' },
];

const MobileBottomNav: React.FC = () => {
  const router = useRouter();
  const { isMobile } = useMobileDetection();
  const [moreMenuAnchor, setMoreMenuAnchor] = useState<null | HTMLElement>(null);

  if (!isMobile) return null;

  // Determine active tab based on current route
  const getCurrentValue = (): string => {
    const path = router.pathname;
    if (path.includes('/dashboard') && !path.includes('/mobile')) return 'dashboard';
    if (path.includes('/sales')) return 'sales';
    if (path.includes('/finance')) return 'finance';
    if (path.includes('/crm')) return 'crm';
    if (path.includes('/inventory')) return 'inventory';
    if (path.includes('/manufacturing') || path.includes('/order-book')) return 'manufacturing';
    if (path.includes('/service')) return 'service';
    if (path.includes('/marketing')) return 'marketing';
    if (path.includes('/reports')) return 'reports';
    if (path.includes('/email')) return 'email';
    if (path.includes('/settings')) return 'settings';
    return 'dashboard';
  };

  const currentValue = getCurrentValue();
  // Check if current value is in more menu
  const isInMoreMenu = moreMenuItems.some(item => item.value === currentValue);

  const handleNavigation = (event: React.SyntheticEvent, newValue: string) => {
    if (newValue === 'more') {
      setMoreMenuAnchor(event.currentTarget as HTMLElement);
      return;
    }
    const item = bottomNavItems.find(item => item.value === newValue);
    if (item && item.path) {
      router.push(item.path);
    }
  };

  const handleMoreMenuClose = () => {
    setMoreMenuAnchor(null);
  };

  const handleMoreMenuItemClick = (item: BottomNavItem) => {
    router.push(item.path);
    handleMoreMenuClose();
  };

  return (
    <>
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
          paddingBottom: 'max(env(safe-area-inset-bottom), constant(safe-area-inset-bottom))',
        }}
        elevation={3}
      >
        <BottomNavigation
          value={isInMoreMenu ? 'more' : currentValue}
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
              fontSize: '0.7rem',
              fontWeight: 500,
              marginTop: 0.5,
              '&.Mui-selected': {
                fontSize: '0.7rem',
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

      {/* More Menu */}
      <Menu
        anchorEl={moreMenuAnchor}
        open={Boolean(moreMenuAnchor)}
        onClose={handleMoreMenuClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        PaperProps={{
          sx: {
            borderRadius: 2,
            minWidth: 200,
            mb: 1,
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
          }
        }}
      >
        {moreMenuItems.map((item, index) => (
          <MenuItem 
            key={item.value}
            onClick={() => handleMoreMenuItemClick(item)}
            selected={currentValue === item.value}
            sx={{
              py: 1.5,
              borderRadius: 1,
              mx: 0.5,
              '&.Mui-selected': {
                bgcolor: 'primary.lighter',
              }
            }}
          >
            <ListItemIcon sx={{ color: currentValue === item.value ? 'primary.main' : 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.label}
              primaryTypographyProps={{
                fontWeight: currentValue === item.value ? 600 : 400,
              }}
            />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default MobileBottomNav;