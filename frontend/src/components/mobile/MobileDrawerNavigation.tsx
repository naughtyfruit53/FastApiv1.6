import React, { useState, useMemo } from 'react';
import { 
  Drawer, 
  List, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Box, 
  Typography, 
  Divider, 
  TextField, 
  InputAdornment, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Chip,
  Fab
} from '@mui/material';
import { 
  Search, 
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
  Assignment,
  Groups,
  Task,
  Email,
  ExpandMore,
  Close,
  Star,
  Bookmark
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { menuItems, mainMenuSections } from '../menuConfig';

interface MobileDrawerNavigationProps {
  open: boolean;
  onClose: () => void;
  user?: any;
  onLogout: () => void;
}

interface NavigationItem {
  name: string;
  path: string;
  icon: React.ReactElement;
  subItems?: NavigationItem[];
  mobileRoute?: string;
  badge?: string;
  favorite?: boolean;
}

const MobileDrawerNavigation: React.FC<MobileDrawerNavigationProps> = ({
  open,
  onClose,
  user,
  onLogout,
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['Dashboard']);
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState<string[]>(['Dashboard', 'Sales', 'CRM']);
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

  const navigateTo = (path: string, mobileRoute?: string) => {
    // Prefer mobile route if available, otherwise use desktop route
    const targetRoute = mobileRoute || path;
    router.push(targetRoute);
    onClose();
  };

  const toggleFavorite = (itemName: string) => {
    setFavorites(prev => 
      prev.includes(itemName) 
        ? prev.filter(f => f !== itemName)
        : [...prev, itemName]
    );
  };

  const getIconForSection = (sectionTitle: string) => {
    const iconMap: { [key: string]: React.ReactElement } = {
      'Dashboard': <Dashboard />,
      'Master Data': <Business />,
      'ERP': <ShoppingCart />,
      'Finance & Accounting': <AccountBalance />,
      'Reports & Analytics': <Assessment />,
      'Sales': <Receipt />,
      'Marketing': <Campaign />,
      'Service': <SupportAgent />,
      'Projects': <Assignment />,
      'HR Management': <Groups />,
      'Tasks & Calendar': <Task />,
      'Email': <Email />,
      'Settings': <Settings />,
      'Administration': <Settings />,
    };
    return iconMap[sectionTitle] || <Business />;
  };

  // Enhanced mobile navigation structure with mobile-specific routes
  const mobileNavigationItems = useMemo(() => {
    const sections = mainMenuSections(isSuperAdmin);
    
    // Add mobile-optimized dashboard and quick access items
    const mobileEnhancedSections = [
      {
        title: 'Dashboard',
        subSections: [{
          title: 'Overview',
          items: [
            { 
              name: 'Mobile Dashboard', 
              path: '/dashboard', 
              mobileRoute: '/mobile/dashboard',
              icon: <Dashboard />,
              favorite: favorites.includes('Dashboard')
            }
          ]
        }]
      },
      {
        title: 'Quick Access',
        subSections: [{
          title: 'Core Modules',
          items: [
            { 
              name: 'Sales', 
              path: '/sales/dashboard', 
              mobileRoute: '/mobile/sales',
              icon: <Receipt />,
              favorite: favorites.includes('Sales'),
              badge: 'Mobile'
            },
            { 
              name: 'CRM', 
              path: '/crm', 
              mobileRoute: '/mobile/crm',
              icon: <People />,
              favorite: favorites.includes('CRM'),
              badge: 'Mobile'
            },
            { 
              name: 'Finance', 
              path: '/finance-dashboard', 
              mobileRoute: '/mobile/finance',
              icon: <AccountBalance />,
              favorite: favorites.includes('Finance'),
              badge: 'Mobile'
            },
            { 
              name: 'Inventory', 
              path: '/inventory', 
              mobileRoute: '/mobile/inventory',
              icon: <Inventory />,
              favorite: favorites.includes('Inventory'),
              badge: 'Mobile'
            },
            { 
              name: 'HR', 
              path: '/hr/dashboard', 
              mobileRoute: '/mobile/hr',
              icon: <Groups />,
              favorite: favorites.includes('HR'),
              badge: 'Mobile'
            },
            { 
              name: 'Service', 
              path: '/service/dashboard', 
              mobileRoute: '/mobile/service',
              icon: <SupportAgent />,
              favorite: favorites.includes('Service'),
              badge: 'Mobile'
            },
            { 
              name: 'Reports', 
              path: '/reports', 
              mobileRoute: '/mobile/reports',
              icon: <Assessment />,
              favorite: favorites.includes('Reports'),
              badge: 'Mobile'
            }
          ]
        }]
      },
      ...sections
    ];

    return mobileEnhancedSections;
  }, [isSuperAdmin, favorites]);

  // Filter items based on search query
  const filteredSections = useMemo(() => {
    if (!searchQuery.trim()) return mobileNavigationItems;

    const query = searchQuery.toLowerCase();
    return mobileNavigationItems.map(section => ({
      ...section,
      subSections: section.subSections?.map(subSection => ({
        ...subSection,
        items: subSection.items.filter(item => 
          item.name.toLowerCase().includes(query) ||
          item.path.toLowerCase().includes(query)
        )
      })).filter(subSection => subSection.items.length > 0)
    })).filter(section => section.subSections && section.subSections.length > 0);
  }, [mobileNavigationItems, searchQuery]);

  const renderMenuItem = (item: NavigationItem) => (
    <ListItemButton 
      key={item.name}
      onClick={() => navigateTo(item.path, item.mobileRoute)}
      sx={{ 
        pl: 4,
        py: 1.5,
        borderRadius: 1,
        mx: 1,
        mb: 0.5,
        '&:hover': {
          bgcolor: 'action.hover',
        }
      }}
    >
      <ListItemIcon sx={{ minWidth: 40 }}>
        {item.icon}
      </ListItemIcon>
      <ListItemText 
        primary={item.name}
        primaryTypographyProps={{
          variant: 'body2',
          fontWeight: item.favorite ? 600 : 400
        }}
      />
      {item.badge && (
        <Chip 
          label={item.badge} 
          size="small" 
          color="primary" 
          variant="outlined"
          sx={{ fontSize: '0.7rem', height: 20 }}
        />
      )}
      {item.favorite && (
        <Star sx={{ fontSize: '1rem', color: 'warning.main', ml: 1 }} />
      )}
    </ListItemButton>
  );

  const favoriteItems = useMemo(() => {
    const allItems: NavigationItem[] = [];
    mobileNavigationItems.forEach(section => {
      section.subSections?.forEach(subSection => {
        allItems.push(...subSection.items);
      });
    });
    return allItems.filter(item => favorites.includes(item.name));
  }, [mobileNavigationItems, favorites]);

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 360,
          backgroundColor: 'background.paper',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
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
          background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
          color: 'white'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                FastAPI v1.6
              </Typography>
              {user && (
                <Typography variant="body2" sx={{ opacity: 0.9, marginTop: 0.5 }}>
                  {user.name || user.email}
                </Typography>
              )}
            </Box>
            <Fab
              size="small"
              onClick={onClose}
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                }
              }}
            >
              <Close />
            </Fab>
          </Box>
        </Box>

        {/* Search */}
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search modules, features..."
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
                borderRadius: 3,
                backgroundColor: 'action.hover',
                '&:hover': {
                  backgroundColor: 'action.selected',
                }
              }
            }}
          />
        </Box>

        {/* Favorites Section */}
        {favoriteItems.length > 0 && !searchQuery && (
          <Box sx={{ px: 2, pb: 1 }}>
            <Typography variant="subtitle2" sx={{ 
              color: 'text.secondary', 
              fontWeight: 600,
              mb: 1,
              display: 'flex',
              alignItems: 'center'
            }}>
              <Bookmark sx={{ fontSize: '1rem', mr: 1 }} />
              Favorites
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {favoriteItems.map(item => (
                <Chip
                  key={item.name}
                  label={item.name}
                  icon={item.icon}
                  onClick={() => navigateTo(item.path, item.mobileRoute)}
                  size="small"
                  variant="outlined"
                  color="primary"
                  sx={{ 
                    borderRadius: 2,
                    '&:hover': {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText'
                    }
                  }}
                />
              ))}
            </Box>
            <Divider sx={{ mt: 2 }} />
          </Box>
        )}

        {/* Menu Items */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 1 }}>
          <List sx={{ p: 0 }}>
            {filteredSections.map((section, index) => (
              <Accordion 
                key={index}
                expanded={expandedSections.includes(section.title)}
                onChange={() => handleSectionToggle(section.title)}
                disableGutters
                elevation={0}
                sx={{
                  '&:before': { display: 'none' },
                  m: 0,
                  mb: 1,
                  borderRadius: 2,
                  overflow: 'hidden',
                  '&.Mui-expanded': {
                    backgroundColor: 'action.hover',
                  }
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMore />}
                  sx={{
                    px: 2,
                    minHeight: 56,
                    '& .MuiAccordionSummary-content': {
                      margin: 0,
                      alignItems: 'center'
                    },
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    {getIconForSection(section.title)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={section.title}
                    primaryTypographyProps={{
                      variant: 'subtitle2',
                      fontWeight: 600
                    }}
                  />
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0, pb: 1 }}>
                  {section.subSections?.map((subSection: any, subIndex: number) => (
                    <Box key={subIndex}>
                      {subSection.title && subSection.title !== 'Overview' && subSection.title !== 'Core Modules' && (
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            px: 3, 
                            py: 1, 
                            color: 'text.secondary',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            display: 'block'
                          }}
                        >
                          {subSection.title}
                        </Typography>
                      )}
                      <List disablePadding>
                        {subSection.items.map((item: NavigationItem) => renderMenuItem(item))}
                      </List>
                    </Box>
                  ))}
                </AccordionDetails>
              </Accordion>
            ))}
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
              borderRadius: 2,
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

export default MobileDrawerNavigation;