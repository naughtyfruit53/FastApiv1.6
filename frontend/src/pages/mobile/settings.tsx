import React, { useState } from 'react';
import { Box, Grid, Typography, Switch, Avatar, ListItem, ListItemAvatar, ListItemText } from '@mui/material';
import { 
  Person, 
  Notifications, 
  Security, 
  Language, 
  Palette, 
  Storage,
  Help,
  Info,
  ChevronRight
} from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton 
} from '../../components/mobile';
import { useAuth } from '../../context/AuthContext';

// TODO: CRITICAL - Integrate with real user management and settings APIs
// TODO: Connect with user profile services for real user data and preferences
// TODO: Implement mobile user management interface with role assignment
// TODO: Create organized settings navigation with search and categorization
// TODO: Add permission management interface for mobile admin users
// TODO: Implement granular notification preferences with push notification settings
// TODO: Create mobile-optimized admin tools and system dashboards
// TODO: Add system monitoring dashboard with mobile-friendly metrics
// TODO: Implement mobile backup/restore functionality with progress tracking
// TODO: Create comprehensive user profile management with photo upload
// TODO: Add mobile-specific security settings (biometric auth, device management)
// TODO: Implement theme customization and dark mode support
// TODO: Create language and localization settings for mobile
// TODO: Add data management tools (export, import, cleanup)
// TODO: Implement help and support integration with chat/ticket system

// Settings categories - INTEGRATE WITH REAL USER PREFERENCES API
const settingsCategories = [
  {
    title: 'Account',
    items: [
      { 
        label: 'Profile Settings', 
        icon: <Person />, 
        description: 'Update your personal information',
        action: 'navigate'
      },
      { 
        label: 'Security', 
        icon: <Security />, 
        description: 'Password and security settings',
        action: 'navigate'
      },
    ],
  },
  {
    title: 'Preferences',
    items: [
      { 
        label: 'Notifications', 
        icon: <Notifications />, 
        description: 'Manage notification preferences',
        action: 'toggle',
        enabled: true
      },
      { 
        label: 'Dark Mode', 
        icon: <Palette />, 
        description: 'Toggle dark/light theme',
        action: 'toggle',
        enabled: false
      },
      { 
        label: 'Language', 
        icon: <Language />, 
        description: 'English (US)',
        action: 'navigate'
      },
    ],
  },
  {
    title: 'Data & Storage',
    items: [
      { 
        label: 'Offline Data', 
        icon: <Storage />, 
        description: 'Manage offline data storage',
        action: 'navigate'
      },
      { 
        label: 'Cache Settings', 
        icon: <Storage />, 
        description: 'Clear app cache and data',
        action: 'navigate'
      },
    ],
  },
  {
    title: 'Support',
    items: [
      { 
        label: 'Help Center', 
        icon: <Help />, 
        description: 'Get help and support',
        action: 'navigate'
      },
      { 
        label: 'About', 
        icon: <Info />, 
        description: 'App version and information',
        action: 'navigate'
      },
    ],
  },
];

const MobileSettings: React.FC = () => {
  const { user, logout } = useAuth();
  const [toggleStates, setToggleStates] = useState<{[key: string]: boolean}>({
    'Notifications': true,
    'Dark Mode': false,
  });

  const handleToggle = (label: string) => {
    setToggleStates(prev => ({
      ...prev,
      [label]: !prev[label]
    }));
  };

  const handleItemClick = (item: any) => {
    if (item.action === 'toggle') {
      handleToggle(item.label);
    } else {
      console.log('Navigate to:', item.label);
    }
  };

  return (
    <MobileDashboardLayout
      title="Settings"
      subtitle="App Preferences & Account"
      showBottomNav={true}
    >
      {/* User Profile Card */}
      <MobileCard>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main', fontSize: '1.5rem' }}>
            {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {user?.name || 'User Name'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email || 'user@example.com'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.role || 'User'} • FastAPI v1.6
            </Typography>
          </Box>
        </Box>
        <MobileButton variant="outlined" fullWidth>
          Edit Profile
        </MobileButton>
      </MobileCard>

      {/* App Statistics */}
      <MobileCard title="Usage Statistics">
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                47
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Days Active
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                234
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Transactions
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                12MB
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Data Used
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </MobileCard>

      {/* Settings Categories */}
      {settingsCategories.map((category, categoryIndex) => (
        <MobileCard key={categoryIndex} title={category.title}>
          <Box>
            {category.items.map((item, itemIndex) => (
              <ListItem
                key={itemIndex}
                onClick={() => handleItemClick(item)}
                sx={{
                  cursor: 'pointer',
                  borderRadius: 2,
                  marginBottom: 1,
                  padding: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:active': {
                    backgroundColor: 'action.hover',
                  },
                  '&:last-child': {
                    marginBottom: 0,
                  },
                  transition: 'background-color 0.2s ease',
                }}
              >
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.main' }}>
                    {item.icon}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {item.label}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="body2" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {item.action === 'toggle' ? (
                    <Switch
                      checked={toggleStates[item.label] || false}
                      onChange={() => handleToggle(item.label)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <ChevronRight color="action" />
                  )}
                </Box>
              </ListItem>
            ))}
          </Box>
        </MobileCard>
      ))}

      {/* Logout Section */}
      <MobileCard>
        <MobileButton
          variant="outlined"
          fullWidth
          onClick={logout}
          sx={{
            color: 'error.main',
            borderColor: 'error.main',
            '&:hover': {
              backgroundColor: 'error.light',
              borderColor: 'error.main',
            }
          }}
        >
          Sign Out
        </MobileButton>
      </MobileCard>

      {/* App Info */}
      <MobileCard>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            FastAPI ERP v1.6.0
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Build 2024.01.15 • Made with ❤️
          </Typography>
        </Box>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileSettings;