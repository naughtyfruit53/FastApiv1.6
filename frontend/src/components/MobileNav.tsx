'use client';

import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton,
  Box,
  Typography,
  Divider,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  ExpandLess,
  ExpandMore,
  Search as SearchIcon,
  Dashboard,
  Receipt,
  Inventory,
  People,
  Business,
  Assessment,
  Settings,
  ShoppingCart,
  AccountBalance,
  Campaign,
  SupportAgent,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useMobileDetection } from '../hooks/useMobileDetection';

interface MobileNavProps {
  user?: any;
  onLogout: () => void;
  menuItems: any;
  isVisible?: boolean;
}

const MobileNav: React.FC<MobileNavProps> = ({ 
  user, 
  onLogout, 
  menuItems, 
  isVisible = true 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const { isMobile } = useMobileDetection();

  // Don't render on desktop
  if (!isMobile || !isVisible) {
    return null;
  }

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionTitle) 
        ? prev.filter(s => s !== sectionTitle)
        : [...prev, sectionTitle]
    );
  };

  const navigateTo = (path: string) => {
    router.push(path);
    setIsOpen(false); // Close drawer after navigation
  };

  const handleLogout = () => {
    onLogout();
    setIsOpen(false);
  };

  const filterMenuItems = (items: any[], query: string) => {
    if (!query) return items;
    return items.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase()) ||
      (item.items && item.items.some((subItem: any) => 
        subItem.name.toLowerCase().includes(query.toLowerCase())
      ))
    );
  };

  const renderMenuItems = () => {
    if (!menuItems?.menu?.sections) return null;

    const filteredSections = filterMenuItems(menuItems.menu.sections, searchQuery);

    return filteredSections.map((section: any, index: number) => (
      <Box key={index}>
        <ListItemButton
          onClick={() => handleSectionToggle(section.title)}
          sx={{
            minHeight: 48,
            px: 2,
            py: 1.5,
            '&:hover': {
              backgroundColor: 'primary.light',
            }
          }}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>
            {getIconForSection(section.title)}
          </ListItemIcon>
          <ListItemText 
            primary={section.title}
            primaryTypographyProps={{
              fontSize: '1rem',
              fontWeight: 500,
            }}
          />
          {expandedSections.includes(section.title) ? <ExpandLess /> : <ExpandMore />}
        </ListItemButton>

        <Collapse in={expandedSections.includes(section.title)} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {section.subSections?.map((subSection: any, subIndex: number) => (
              <Box key={subIndex}>
                {subSection.title && (
                  <ListItem sx={{ pl: 4, py: 0.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight="bold">
                      {subSection.title}
                    </Typography>
                  </ListItem>
                )}
                {subSection.items?.map((item: any, itemIndex: number) => (
                  <ListItemButton
                    key={itemIndex}
                    onClick={() => navigateTo(item.path)}
                    sx={{
                      pl: 6,
                      minHeight: 44,
                      '&:hover': {
                        backgroundColor: 'secondary.light',
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.name}
                      primaryTypographyProps={{
                        fontSize: '0.9rem',
                      }}
                    />
                  </ListItemButton>
                ))}
              </Box>
            ))}
          </List>
        </Collapse>
        <Divider />
      </Box>
    ));
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
    <>
      {/* Mobile Menu Toggle Button */}
      <IconButton
        color="inherit"
        aria-label="open mobile menu"
        onClick={toggleDrawer}
        sx={{
          display: { xs: 'block', md: 'none' },
          minWidth: 44,
          minHeight: 44,
        }}
      >
        <MenuIcon />
      </IconButton>

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="left"
        open={isOpen}
        onClose={toggleDrawer}
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
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            p: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'primary.main',
            color: 'primary.contrastText'
          }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              FastAPI v1.6
            </Typography>
            <IconButton
              onClick={toggleDrawer}
              sx={{ 
                color: 'primary.contrastText',
                minWidth: 44,
                minHeight: 44,
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* User Info */}
          {user && (
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="body2" color="text.secondary">
                Welcome, {user.name || user.email}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user.role || 'User'}
              </Typography>
            </Box>
          )}

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
                    <SearchIcon sx={{ fontSize: '1.2rem' }} />
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
              {renderMenuItems()}
            </List>
          </Box>

          {/* Footer Actions */}
          <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <ListItemButton
              onClick={handleLogout}
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
    </>
  );
};

export default MobileNav;