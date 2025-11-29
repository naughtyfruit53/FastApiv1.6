// frontend/src/components/MobileNav.tsx
// TritIQ BOS Brand Kit v1
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
  Box,
  Typography,
  Divider,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
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
  ChevronRight,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useMobileDetection } from '../hooks/useMobileDetection';
import { isAppSuperAdmin } from '../types/user.types';
import { mainMenuSections } from './menuConfig';

// TritIQ BOS Brand Tagline
const TRITIQ_TAGLINE = "Business Made Simple";

interface MobileNavProps {
  open: boolean;  // Changed to controlled open prop
  onClose: () => void;  // Added onClose prop
  user?: any;
  onLogout: () => void;
  menuItems: any;
}

const MobileNav: React.FC<MobileNavProps> = ({ 
  open, 
  onClose, 
  user, 
  onLogout, 
  menuItems 
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [expandedSubSections, setExpandedSubSections] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const { isMobile } = useMobileDetection();
  const isSuperAdmin = isAppSuperAdmin(user);

  // Don't render on desktop
  if (!isMobile) {
    return null;
  }

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionTitle) 
        ? prev.filter(s => s !== sectionTitle)
        : [...prev, sectionTitle]
    );
  };

  const handleSubSectionToggle = (subSectionName: string) => {
    setExpandedSubSections(prev => 
      prev.includes(subSectionName) 
        ? prev.filter(s => s !== subSectionName)
        : [...prev, subSectionName]
    );
  };

  const navigateTo = (path: string) => {
    router.push(path);
    onClose(); // Close drawer after navigation
  };

  const handleLogout = () => {
    onLogout();
    onClose();
  };

  const filterMenuItems = (items: any[], query: string) => {
    if (!query) return items;
    return items.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase()) ||
      (item.subItems && item.subItems.some((subItem: any) => 
        subItem.name.toLowerCase().includes(query.toLowerCase())
      )) ||
      (item.items && item.items.some((subItem: any) => 
        subItem.name.toLowerCase().includes(query.toLowerCase()) ||
        (subItem.subItems && subItem.subItems.some((nestedItem: any) => 
          nestedItem.name.toLowerCase().includes(query.toLowerCase())
        ))
      ))
    );
  };

  const renderMenuItems = () => {
    const sections = mainMenuSections(isSuperAdmin);
    const filteredSections = filterMenuItems(sections, searchQuery);

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
                  item.subItems ? (
                    <Box key={itemIndex}>
                      <ListItemButton
                        onClick={() => handleSubSectionToggle(item.name)}
                        sx={{
                          pl: 6,
                          minHeight: 44,
                          '&:hover': {
                            backgroundColor: 'secondary.light',
                          }
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {item.icon || <ChevronRight />}
                        </ListItemIcon>
                        <ListItemText 
                          primary={item.name}
                          primaryTypographyProps={{
                            fontSize: '0.9rem',
                          }}
                        />
                        {expandedSubSections.includes(item.name) ? <ExpandLess /> : <ExpandMore />}
                      </ListItemButton>
                      <Collapse in={expandedSubSections.includes(item.name)} timeout="auto" unmountOnExit>
                        <List component="div" disablePadding>
                          {item.subItems.map((subItem: any, subItemIndex: number) => (
                            <ListItemButton
                              key={subItemIndex}
                              onClick={() => navigateTo(subItem.path)}
                              sx={{
                                pl: 8,
                                minHeight: 40,
                                '&:hover': {
                                  backgroundColor: 'action.hover',
                                }
                              }}
                            >
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                {subItem.icon}
                              </ListItemIcon>
                              <ListItemText 
                                primary={subItem.name}
                                primaryTypographyProps={{
                                  fontSize: '0.85rem',
                                }}
                              />
                            </ListItemButton>
                          ))}
                        </List>
                      </Collapse>
                    </Box>
                  ) : (
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
                  )
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
    // Removed the toggle button, as it's now in the header
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
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center',
          p: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: '#0A2A43',
          color: 'white'
        }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            TritIQ BOS
          </Typography>
          <Typography variant="caption" sx={{ fontWeight: 300, opacity: 0.9, fontStyle: 'italic' }}>
            {TRITIQ_TAGLINE}
          </Typography>
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
          <Typography 
            variant="caption" 
            sx={{ 
              display: 'block', 
              textAlign: 'center', 
              mt: 2, 
              color: 'text.secondary' 
            }}
          >
            TritIQ BOS — {TRITIQ_TAGLINE}
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default MobileNav;