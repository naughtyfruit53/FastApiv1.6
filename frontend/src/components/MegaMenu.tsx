// frontend/src/components/MegaMenu.tsx
'use client';
import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Menu,
  MenuItem,
  Box,
  List,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  ListItemButton,
  Grid,
  InputBase
} from '@mui/material';
import {
  Settings,
  AccountCircle,
  ExpandMore,
  ChevronRight,
  Menu as MenuIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import CreateOrganizationLicenseModal from './CreateOrganizationLicenseModal';
import { isAppSuperAdmin, isOrgSuperAdmin, canManageUsers } from '../types/user.types';
import { useQuery } from '@tanstack/react-query';
import { rbacService, SERVICE_PERMISSIONS } from '../services/rbacService';
import { organizationService } from '../services/organizationService';
import MobileNav from './MobileNav';
import { useMobileDetection } from '../hooks/useMobileDetection';
import { menuItems, mainMenuSections } from './menuConfig';

interface MegaMenuProps {
  user?: any;
  onLogout: () => void;
  isVisible?: boolean;
}

const MegaMenu: React.FC<MegaMenuProps> = ({ user, onLogout, isVisible = true }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [subAnchorEl, setSubAnchorEl] = useState<null | HTMLElement>(null);
  const [activeSubCategory, setActiveSubCategory] = useState<any>(null);
  const [createLicenseModalOpen, setCreateLicenseModalOpen] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filteredMenuItems, setFilteredMenuItems] = useState<any[]>([]);
  const searchRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const { isMobile } = useMobileDetection();

  // Common button style for enhanced UI/UX
  const modernButtonStyle = {
    mx: 1,
    transition: 'all 0.2s ease-in-out',
    borderRadius: 2,
    '&:hover': {
      transform: 'translateY(-2px)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    },
    '&:focus': {
      outline: '2px solid',
      outlineColor: 'primary.main',
      outlineOffset: '2px',
    },
    '&:active': {
      transform: 'translateY(0) scale(0.98)',
    }
  };

  // Query for current organization (to get enabled_modules)
  const { data: organizationData } = useQuery({
    queryKey: ['currentOrganization'],
    queryFn: organizationService.getCurrentOrganization,
    enabled: !isAppSuperAdmin(user), // Only for organization users
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: true, // Refetch when window regains focus
    refetchInterval: 10000, // Auto-refetch every 10 seconds for testing
    onSuccess: (data) => {
      console.log('Organization data fetched:', {
        enabled_modules: data.enabled_modules,
        timestamp: new Date().toISOString()
      });
    },
    onError: (error) => {
      console.error('Error fetching organization data:', error);
    }
  });

  // Query for current user's service permissions
  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user && !isAppSuperAdmin(user), // Only fetch for organization users
    retry: false,
    staleTime: 0, // 5 minutes
    onSuccess: (data) => {
      console.log('User permissions fetched:', data);
    }
  });

  // Add keyboard event listener for Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (anchorEl) {
          handleMenuClose();
        }
        if (userMenuAnchor) {
          handleUserMenuClose();
        }
        if (subAnchorEl) {
          handleSubClose();
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [anchorEl, userMenuAnchor, subAnchorEl]);

  // Click outside to close search results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchQuery('');
        setFilteredMenuItems([]);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [searchRef]);

  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    setAnchorEl(event.currentTarget);
    setActiveMenu(menuName);
    setSelectedSection(null);
  };

  const handleSubClick = (event: React.MouseEvent<HTMLElement>, category: any) => {
    setSubAnchorEl(event.currentTarget);
    setActiveSubCategory(category);
  };

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const navigateTo = (path: string) => {
    router.push(path);
    handleMenuClose();
    handleSubClose();
  };

  // Enhanced logo navigation function
  const navigateToHome = () => {
    router.push('/dashboard');
    handleMenuClose();
  };

  // Check user roles using proper utility functions
  const isSuperAdmin = isAppSuperAdmin(user);

  // Service permission helper functions
  const hasServicePermission = (permission: string): boolean => {
    return userPermissions.includes(permission);
  };

  const hasAnyServicePermission = (permissions: string[]): boolean => {
    return permissions.some(permission => userPermissions.includes(permission));
  };

  const canAccessService = (): boolean => {
    const hasAccess = hasAnyServicePermission([
      SERVICE_PERMISSIONS.SERVICE_READ,
      SERVICE_PERMISSIONS.APPOINTMENT_READ,
      SERVICE_PERMISSIONS.TECHNICIAN_READ,
      SERVICE_PERMISSIONS.WORK_ORDER_READ
    ]);
    console.log('Permission check - canAccessService:', hasAccess, {
      userPermissions,
      timestamp: new Date().toISOString()
    });
    return hasAccess;
  };

  const canAccessServiceReports = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.SERVICE_REPORTS_READ);
  };

  const canAccessCRMAdmin = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.CRM_ADMIN) || isOrgSuperAdmin(user);
  };

  // Helper to check if a module is enabled for the organization
  const isModuleEnabled = (module: string): boolean => {
    if (isSuperAdmin) {return true;} // Super admins see all
    const enabled = organizationData?.enabled_modules?.[module] ?? false;
    console.log(`Module check - ${module}:`, enabled, {
      allModules: organizationData?.enabled_modules,
      timestamp: new Date().toISOString()
    });
    return enabled;
  };

  const openDemoMode = () => {
    // Navigate to demo page
    router.push('/demo');
    handleMenuClose();
  };

  const requestModuleActivation = () => {
    // In production, this could open a support ticket form or email client
    window.location.href = 'mailto:support@tritiq.com?subject=Module Activation Request&body=Please activate the Service CRM module for my organization.';
  };

  const handleSubClose = () => {
    setSubAnchorEl(null);
    setActiveSubCategory(null);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setActiveMenu(null);
    setSelectedSection(null);
  };

  const handleCreateLicense = () => {
    // For now, we'll use a state to control the modal
    // In a full implementation, this would be managed by parent component
    setCreateLicenseModalOpen(true);
    handleMenuClose();
  };

  const flattenMenuItems = (menu: any) => {
    let items = [];
    menu.sections.forEach(section => {
      section.subSections.forEach(subSection => {
        subSection.items.forEach(item => {
          if (item.subItems) {
            item.subItems.forEach(subItem => items.push(subItem));
          } else {
            items.push(item);
          }
        });
      });
    });
    return items;
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.length >= 2) {
      const allItems = flattenMenuItems(menuItems.menu);
      const filtered = allItems.filter(item => item.name.toLowerCase().includes(query.toLowerCase()));
      setFilteredMenuItems(filtered);
    } else {
      setFilteredMenuItems([]);
    }
  };

  const renderMegaMenu = () => {
    // Don't render mega menu on mobile (MobileNav handles navigation)
    if (isMobile) {
      return null;
    }
    
    if (!activeMenu || !menuItems[activeMenu as keyof typeof menuItems]) {
      return null;
    }
    let menu = menuItems[activeMenu as keyof typeof menuItems];
    if (activeMenu === 'menu') {
      menu = {
        ...menu,
        sections: mainMenuSections(isSuperAdmin)
      };
    }
    // Filter menu items based on user permissions
    const filterMenuItems = (subSection: any) => {
      return subSection.items.filter((item: any) => {
        // Check role-based permissions
        if (item.role && !canManageUsers(user)) {
          return false;
        }
        // Check super admin only items
        if (item.superAdminOnly && !isSuperAdmin) {
          return false;
        }
        // Check service permissions
        if (item.servicePermission && !hasServicePermission(item.servicePermission)) {
          return false;
        }
        return true;
      });
    };
    const normalizedSections = menu.sections.map(section => {
      if (!section.subSections) {
        return {
          ...section,
          subSections: [{
            title: '',
            items: section.items || []
          }]
        };
      }
      return section;
    });
    const filteredSections = normalizedSections.map(section => ({
      ...section,
      subSections: section.subSections.map((subSection: any) => ({
        ...subSection,
        items: filterMenuItems(subSection)
      })).filter((subSection: any) => subSection.items.length > 0)
    })).filter(section => section.subSections.length > 0);
    if (filteredSections.length === 0) {
      console.log(`No items in submenu for ${activeMenu} - permissions may be missing`);
      return null;
    }
    return (
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            width: selectedSection ? 'calc(100vw - 40px)' : 'auto',
            maxWidth: selectedSection ? 'calc(100vw - 40px)' : 'auto',
            maxHeight: 'calc(120vh - 120px)' ,
            overflowY: 'hidden',
            mt: 0,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            left: '20px !important',
            right: 'auto',
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            },
            '@media (max-width: 768px)': {
              width: 'calc(100vw - 20px)',
              left: '10px !important',
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        disableAutoFocusItem
      >
        <Grid container>
          <Grid item xs={3}>
            <List sx={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'visible', minHeight: filteredSections.length * 50 + 'px' }}>
              {filteredSections.map((section, index) => (
                <ListItemButton
                  key={index}
                  selected={selectedSection === section.title}
                  onClick={() => setSelectedSection(section.title)}
                  sx={{
                    backgroundColor: selectedSection === section.title ? 'primary.light' : 'transparent',
                    color: selectedSection === section.title ? 'primary.contrastText' : 'text.primary',
                    '&:hover': {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                    },
                    minHeight: '50px'
                  }}
                >
                  <ListItemText primary={section.title} />
                  <ChevronRight />
                </ListItemButton>
              ))}
            </List>
          </Grid>
          <Grid item xs={9} sx={{ pl: 2 }}>
            {selectedSection && (
              <Grid container spacing={2}>
                {filteredSections.find(s => s.title === selectedSection)?.subSections.map((subSection: any, subIndex: number) => (
                  <Grid item xs={12} sm={6} md={4} key={subIndex}>
                    {subSection.title && (
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'secondary.main' }}>
                        {subSection.title}
                      </Typography>
                    )}
                    <List dense>
                      {subSection.items.map((item: any, itemIndex: number) => (
                        <ListItemButton
                          key={itemIndex}
                          onClick={(e) => item.subItems ? handleSubClick(e, item) : navigateTo(item.path)}
                          sx={{
                            borderRadius: 1,
                            mb: 0.5,
                            '&:hover': {
                              backgroundColor: 'secondary.light',
                              color: 'secondary.contrastText'
                            }
                          }}
                        >
                          <ListItemIcon sx={{ minWidth: 36 }}>
                            {item.icon}
                          </ListItemIcon>
                          <ListItemText primary={item.name} />
                          {item.subItems && <ChevronRight />}
                        </ListItemButton>
                      ))}
                    </List>
                  </Grid>
                ))}
              </Grid>
            )}
          </Grid>
        </Grid>
      </Menu>
    );
  };

  const renderSubMenu = () => {
    // Don't render sub menu on mobile
    if (isMobile) {
      return null;
    }
    
    if (!activeSubCategory) {return null;}
    return (
      <Menu
        anchorEl={subAnchorEl}
        open={Boolean(subAnchorEl)}
        onClose={handleSubClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{
          sx: {
            ml: 1,
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
      >
        <Typography variant="subtitle2" sx={{ px: 2, py: 1, fontWeight: 'bold' }}>
          {activeSubCategory.name}
        </Typography>
        <Divider />
        <List dense>
          {activeSubCategory.subItems.map((subItem: any, subIndex: number) => (
            <ListItemButton
              key={subIndex}
              onClick={() => navigateTo(subItem.path)}
              sx={{
                px: 3,
                py: 1,
                minWidth: 200,
                '&:hover': {
                  backgroundColor: 'primary.light',
                  color: 'primary.contrastText'
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                {subItem.icon}
              </ListItemIcon>
              <ListItemText primary={subItem.name} />
            </ListItemButton>
          ))}
        </List>
      </Menu>
    );
  };

  const renderSearchResults = () => {
    if (filteredMenuItems.length === 0) {return null;}
    return (
      <Menu
        open={filteredMenuItems.length > 0}
        onClose={() => setSearchQuery('')}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: {
            width: 300,
            maxHeight: 400,
          }
        }}
      >
        {filteredMenuItems.map((item, index) => (
          <MenuItem key={index} onClick={() => navigateTo(item.path)}>
            {item.name}
          </MenuItem>
        ))}
      </Menu>
    );
  };

  return (
    <>
      <AppBar
        position="static"
        className="modern-nav"
        sx={{
          backgroundColor: '#001F3F',
          color: 'white',
          boxShadow: 'var(--shadow-sm)',
          borderBottom: '1px solid var(--border-primary)'
        }}
      >
        <Toolbar>
          {/* Mobile Navigation or Desktop Menu */}
          {isMobile ? (
            <MobileNav
              user={user}
              onLogout={onLogout}
              menuItems={menuItems}
              isVisible={isVisible}
            />
          ) : (
            /* Menu and Settings on the left */
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Button
                color="inherit"
                startIcon={<MenuIcon />}
                endIcon={<ExpandMore />}
                onClick={(e) => handleMenuClick(e, 'menu')}
                className="modern-menu-button"
                sx={modernButtonStyle}
              >
                Menu
              </Button>
              <Button
                color="inherit"
                startIcon={<Settings />}
                endIcon={<ExpandMore />}
                onClick={(e) => handleMenuClick(e, 'settings')}
                className="modern-menu-button"
                sx={modernButtonStyle}
              >
                Settings
              </Button>
            </Box>
          )}
          {/* Enhanced Logo Section in the center */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              flexGrow: 1,
              justifyContent: 'center',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 1
              },
              p: 1,
              borderRadius: 1,
              transition: 'background-color 0.2s'
            }}
            onClick={navigateToHome}
          >
            <Box
              component="img"
              src="/Tritiq.png"
              alt="TritiQ"
              sx={{
                width: 40,
                height: 40,
                mr: 1,
                objectFit: 'contain'
              }}
            />
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {organizationData?.name || 'ERP'}
            </Typography>
          </Box>
          {/* Search bar on the right - Desktop only */}
          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative', ml: 2 }} ref={searchRef}>
              <InputBase
                placeholder="Search…"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                startAdornment={<SearchIcon />}
                sx={{
                  color: 'inherit',
                  ml: 1,
                  '& .MuiInputBase-input': {
                    padding: '8px 8px 8px 0',
                    transition: 'width 0.3s',
                    width: searchQuery ? '300px' : '200px',
                  },
                }}
              />
              {renderSearchResults()}
            </Box>
          )}
          {/* User Menu - Always visible */}
          <IconButton
            color="inherit"
            onClick={handleUserMenuClick}
            sx={{ 
              ml: 2,
              minWidth: 44,
              minHeight: 44,
            }}
          >
            <AccountCircle />
          </IconButton>
        </Toolbar>
      </AppBar>
      {renderMegaMenu()}
      {renderSubMenu()}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
            minWidth: 200,
            '& .MuiMenuItem-root': {
              borderRadius: 1,
              margin: '2px 8px',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'primary.50',
                transform: 'translateX(4px)',
              }
            }
          }
        }}
        MenuListProps={{
          sx: {
            padding: 1
          }
        }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2">
            {user?.full_name || user?.email || 'User'}
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2" color="textSecondary">
            Role: {user?.role || 'Standard User'}
          </Typography>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => router.push('/profile')}>
          Profile Settings
        </MenuItem>
        <MenuItem onClick={onLogout}>
          Logout
        </MenuItem>
      </Menu>
      {/* Organization License Creation Modal */}
      <CreateOrganizationLicenseModal
        open={createLicenseModalOpen}
        onClose={() => setCreateLicenseModalOpen(false)}
        onSuccess={(result) => {
          console.log('License created:', result);
          // You might want to show a success notification here
        }}
      />
    </>
  );
};

export default MegaMenu;