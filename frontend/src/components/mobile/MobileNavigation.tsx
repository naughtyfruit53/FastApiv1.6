import React from 'react';
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Box, Typography, Divider, Collapse, TextField, InputAdornment } from '@mui/material';
import { ExpandLess, ExpandMore, Search, Dashboard, Receipt, Inventory, People, Business, Assessment, Settings, ShoppingCart, AccountBalance, Campaign, SupportAgent, ChevronRight } from '@mui/icons-material';
import { useState } from 'react';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { isAppSuperAdmin } from '../../types/user.types';

interface MobileNavigationProps {
  open: boolean;
  onClose: () => void;
  user?: any;
  onLogout: () => void;
  menuItems: any;
}

const MobileNavigation: React.FC<MobileNavigationProps> = ({
  open,
  onClose,
  user,
  onLogout,
  menuItems,
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const { isMobile } = useMobileDetection();
  const isSuperAdmin = user?.role === 'APP_SUPER_ADMIN';

  if (!isMobile) return null;

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionTitle) 
        ? prev.filter(s => s !== sectionTitle)
        : [...prev, sectionTitle]
    );
  };

  const navigateTo = (path: string) => {
    router.push(path);
    onClose();
  };

  const getIconForSection = (sectionTitle: string) => {
    const iconMap: { [key: string]: React.ReactElement } = {
      'Dashboard': <Dashboard />,
      'Sales': <Receipt />,
      'Purchase': <ShoppingCart />,
      'Inventory': <Inventory />,
      'Finance': <AccountBalance />,
      'CRM': <People />,
      'Marketing': <Campaign />,
      'Service': <SupportAgent />,
      'Reports': <Assessment />,
      'Masters': <Business />,
      'Administration': <Settings />,
    };
    return iconMap[sectionTitle] || <Receipt />;
  };

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 320,
          backgroundColor: 'background.paper',
        }
      }}
      ModalProps={{
        keepMounted: true, // Better performance on mobile
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100%',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <Box sx={{ 
          padding: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'primary.main',
          color: 'primary.contrastText'
        }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            FastAPI v1.6
          </Typography>
          {user && (
            <Typography variant="body2" sx={{ opacity: 0.9, marginTop: 0.5 }}>
              {user.name || user.email}
            </Typography>
          )}
        </Box>

        {/* Search */}
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search menu items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ fontSize: '1.2rem' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />
        </Box>

        {/* Menu Items */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <List sx={{ p: 0 }}>
            {/* Mobile Dashboard */}
            <ListItemButton onClick={() => navigateTo('/mobile/dashboard')}>
              <ListItemIcon>
                <Dashboard />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItemButton>
            <Divider />

            {/* Mobile Sales */}
            <ListItemButton onClick={() => navigateTo('/mobile/sales')}>
              <ListItemIcon>
                <Receipt />
              </ListItemIcon>
              <ListItemText primary="Sales" />
            </ListItemButton>
            <Divider />

            {/* Mobile CRM */}
            <ListItemButton onClick={() => navigateTo('/mobile/crm')}>
              <ListItemIcon>
                <People />
              </ListItemIcon>
              <ListItemText primary="CRM" />
            </ListItemButton>
            <Divider />

            {/* Mobile Inventory */}
            <ListItemButton onClick={() => navigateTo('/mobile/inventory')}>
              <ListItemIcon>
                <Inventory />
              </ListItemIcon>
              <ListItemText primary="Inventory" />
            </ListItemButton>
            <Divider />

            {/* Mobile Finance */}
            <ListItemButton onClick={() => navigateTo('/mobile/finance')}>
              <ListItemIcon>
                <AccountBalance />
              </ListItemIcon>
              <ListItemText primary="Finance" />
            </ListItemButton>
            <Divider />

            {/* Mobile Reports */}
            <ListItemButton onClick={() => navigateTo('/mobile/reports')}>
              <ListItemIcon>
                <Assessment />
              </ListItemIcon>
              <ListItemText primary="Reports" />
            </ListItemButton>
            <Divider />

            {/* Mobile Settings */}
            <ListItemButton onClick={() => navigateTo('/mobile/settings')}>
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItemButton>
          </List>
        </Box>

        {/* Footer Actions */}
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <ListItemButton
            onClick={() => {
              onLogout();
              onClose();
            }}
            sx={{
              borderRadius: 1,
              backgroundColor: 'error.light',
              color: 'error.contrastText',
              minHeight: 48,
              '&:hover': {
                backgroundColor: 'error.main',
              }
            }}
          >
            <ListItemText 
              primary="Logout"
              primaryTypographyProps={{
                textAlign: 'center',
                fontWeight: 'bold',
              }}
            />
          </ListItemButton>
        </Box>
      </Box>
    </Drawer>
  );
};

export default MobileNavigation;