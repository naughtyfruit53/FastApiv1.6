// frontend/src/components/MegaMenu.tsx
'use client';
import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  List,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  ListItemButton,
  Grid,
  InputBase,
  Popover,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Settings,
  AccountCircle,
  ExpandMore,
  ChevronRight,
  Menu as MenuIcon,
  Search as SearchIcon,
  Email,
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
  const searchRef = useRef<HTMLDivElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const router = useRouter();
  const { isMobile } = useMobileDetection();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Common button style for enhanced UI/UX
  const modernButtonStyle = {
    mx: 1,
    transition: 'all 0.18s ease-in-out',
    borderRadius: 2,
    '&:hover': {
      transform: 'translateY(-2px)',
      backgroundColor: 'rgba(59, 130, 246, 0.08)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.06)',
    },
    '&:focus': {
      outline: '2px solid',
      outlineColor: 'primary.main',
      outlineOffset: '2px',
    },
  };

  // Query for current organization (to get enabled_modules)
  const { data: organizationData } = useQuery({
    queryKey: ['currentOrganization'],
    queryFn: organizationService.getCurrentOrganization,
    enabled: !isAppSuperAdmin(user),
    retry: false,
    staleTime: 0,
    refetchOnWindowFocus: true,
    refetchInterval: 10000,
    onSuccess: (data) => {
      console.log('Organization data fetched:', {
        enabled_modules: data.enabled_modules,
        timestamp: new Date().toISOString(),
      });
    },
    onError: (error) => {
      console.error('Error fetching organization data:', error);
    },
  });

  // Query for current user's service permissions
  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user && !isAppSuperAdmin(user),
    retry: false,
    staleTime: 0,
    onSuccess: (data) => {
      console.log('User permissions fetched:', data);
    },
  });

  // Keyboard: Esc closes menus; Ctrl/Cmd+K focuses search
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (anchorEl) handleMenuClose();
        if (userMenuAnchor) handleUserMenuClose();
        if (subAnchorEl) handleSubClose();
        if (mobileDrawerOpen) setMobileDrawerOpen(false);
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        if (isMobile) {
          setMobileDrawerOpen(true);
        } else {
          if (!anchorEl) setActiveMenu('menu');
          setTimeout(() => searchInputRef.current?.focus(), 80);
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [anchorEl, userMenuAnchor, subAnchorEl, mobileDrawerOpen, isMobile]);

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

  // Auto-focus search when popover opens on desktop
  useEffect(() => {
    if (anchorEl && !isMobile) {
      const t = setTimeout(() => searchInputRef.current?.focus(), 120);
      return () => clearTimeout(t);
    }
  }, [anchorEl, isMobile]);

  if (!isVisible) return null;

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    const menuItem = menuItems[menuName as keyof typeof menuItems];
    // Check if the menu item has a direct path and no subsections
    if (menuItem && 'path' in menuItem && menuItem.path && (!menuItem.sections || menuItem.sections.length === 0)) {
      router.push(menuItem.path); // Navigate directly to the path
    } else {
      setAnchorEl(event.currentTarget);
      setActiveMenu(menuName);
      setSelectedSection(null);
    }
  };

  const handleSubClick = (event: React.MouseEvent<HTMLElement>, category: any) => {
    setSubAnchorEl(event.currentTarget);
    setActiveSubCategory(category);
  };

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const navigateTo = (path: string) => {
    if (!path) return;
    router.push(path);
    handleMenuClose();
    handleSubClose();
    setMobileDrawerOpen(false);
  };

  const navigateToHome = () => {
    router.push('/dashboard');
    handleMenuClose();
  };

  const isSuperAdmin = isAppSuperAdmin(user);

  const hasServicePermission = (permission: string): boolean => {
    try {
      return userPermissions.includes(permission);
    } catch {
      return false;
    }
  };

  const hasAnyServicePermission = (permissions: string[]): boolean => {
    return permissions.some((permission) => userPermissions.includes(permission));
  };

  const canAccessService = (): boolean => {
    const hasAccess = hasAnyServicePermission([
      SERVICE_PERMISSIONS.SERVICE_READ,
      SERVICE_PERMISSIONS.APPOINTMENT_READ,
      SERVICE_PERMISSIONS.TECHNICIAN_READ,
      SERVICE_PERMISSIONS.WORK_ORDER_READ,
    ]);
    console.log('Permission check - canAccessService:', hasAccess, {
      userPermissions,
      timestamp: new Date().toISOString(),
    });
    return hasAccess;
  };

  const canAccessServiceReports = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.SERVICE_REPORTS_READ);
  };

  const canAccessCRMAdmin = (): boolean => {
    return hasServicePermission(SERVICE_PERMISSIONS.CRM_ADMIN) || isOrgSuperAdmin(user);
  };

  const isModuleEnabled = (module: string): boolean => {
    if (isSuperAdmin) return true;
    const enabled = organizationData?.enabled_modules?.[module] ?? false;
    console.log(`Module check - ${module}:`, enabled, {
      allModules: organizationData?.enabled_modules,
      timestamp: new Date().toISOString(),
    });
    return enabled;
  };

  const openDemoMode = () => {
    router.push('/demo');
    handleMenuClose();
  };

  const requestModuleActivation = () => {
    window.location.href =
      'mailto:support@tritiq.com?subject=Module Activation Request&body=Please activate the Service CRM module for my organization.';
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
    setFilteredMenuItems([]);
    setSearchQuery('');
  };

  const handleCreateLicense = () => {
    setCreateLicenseModalOpen(true);
    handleMenuClose();
  };

  const flattenMenuItems = (menu: any) => {
    let items: any[] = [];
    menu.sections.forEach((section: any) => {
      (section.subSections || []).forEach((subSection: any) => {
        (subSection.items || []).forEach((item: any) => {
          if (item.subItems) {
            item.subItems.forEach((subItem: any) => items.push(subItem));
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
      const filtered = allItems.filter((item) =>
        item.name && item.name.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredMenuItems(filtered);
      if (filtered.length > 0 && !anchorEl && !isMobile) {
        setActiveMenu('menu');
      }
    } else {
      setFilteredMenuItems([]);
    }
  };

  const renderMegaMenu = () => {
    if (isMobile) return null;
    if (!activeMenu || !menuItems[activeMenu as keyof typeof menuItems]) return null;

    let menu = menuItems[activeMenu as keyof typeof menuItems];
    if (activeMenu === 'menu') {
      menu = {
        ...menu,
        sections: mainMenuSections(isSuperAdmin),
      };
    }

    // If the menu has a direct path and no subsections, do not render the popover
    if ('path' in menu && menu.path && (!menu.sections || menu.sections.length === 0)) {
      return null;
    }

    const filterMenuItems = (subSection: any) => {
      return subSection.items.map((item: any) => {
        const disabled =
          (item.role && !canManageUsers(user)) ||
          (item.superAdminOnly && !isSuperAdmin) ||
          (item.servicePermission && !hasServicePermission(item.servicePermission));
        return { ...item, __disabled: Boolean(disabled) };
      });
    };

    const normalizedSections = menu.sections.map((section: any) => {
      if (!section.subSections) {
        return {
          ...section,
          subSections: [
            {
              title: '',
              items: section.items || [],
            },
          ],
        };
      }
      return section;
    });

    // Modified filter to include sections with direct paths even if subSections are empty
    const filteredSections = normalizedSections
      .map((section: any) => {
        // Check if this section has a direct path (e.g., Email)
        const menuItemKey = Object.keys(menuItems).find(
          (key) => menuItems[key as keyof typeof menuItems]?.title === section.title
        );
        const menuItemWithPath = menuItemKey ? menuItems[menuItemKey as keyof typeof menuItems] : null;
        const hasDirectPath = menuItemWithPath && 'path' in menuItemWithPath && menuItemWithPath.path;

        const processedSubSections = section.subSections
          .map((subSection: any) => ({
            ...subSection,
            items: filterMenuItems(subSection),
          }))
          .filter((subSection: any) => subSection.items.length > 0);

        return {
          ...section,
          subSections: processedSubSections,
          hasDirectPath: hasDirectPath,
        };
      })
      .filter((section: any) => section.subSections.length > 0 || section.hasDirectPath);

    if (filteredSections.length === 0) {
      console.log(`No items in submenu for ${activeMenu} - permissions may be missing`);
      return null;
    }

    return (
      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{
          sx: {
            width: 'calc(100% - 40px)',
            maxWidth: '1400px',
            left: '20px !important',
            right: '20px !important',
            maxHeight: '70vh',
            overflow: 'hidden',
            borderRadius: 2,
            boxShadow: '0 14px 40px rgba(0,0,0,0.16)',
            border: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            Menu
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Box ref={searchRef} sx={{ display: 'flex', alignItems: 'center', bgcolor: 'action.hover', px: 1, py: 0.5, borderRadius: 1 }}>
            <SearchIcon fontSize="small" />
            <InputBase
              inputRef={searchInputRef}
              placeholder="Search… (Press ⌘/Ctrl+K)"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              sx={{ ml: 1, width: 300 }}
              inputProps={{ 'aria-label': 'Search menu' }}
            />
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flex: 1, minHeight: 0 }}>
          <Box sx={{ width: 280, borderRight: '1px solid', borderColor: 'divider', overflowY: 'auto', flexShrink: 0 }}>
            <List sx={{ position: 'sticky', top: 0, background: 'transparent', py: 1 }}>
              {filteredSections.map((section: any, index: number) => (
                <ListItemButton
                  key={index}
                  selected={selectedSection === section.title}
                  onClick={() => {
                    // Check if this section corresponds to a menu item with a direct path (like Email)
                    const menuItemKey = Object.keys(menuItems).find(
                      (key) => menuItems[key as keyof typeof menuItems]?.title === section.title
                    );
                    const menuItemWithPath = menuItemKey ? menuItems[menuItemKey as keyof typeof menuItems] : null;

                    if (menuItemWithPath && 'path' in menuItemWithPath && menuItemWithPath.path) {
                      // Navigate directly if menu item has a path
                      navigateTo(menuItemWithPath.path);
                    } else {
                      // Default behavior - set selected section
                      setSelectedSection(section.title);
                    }
                  }}
                  sx={{
                    mb: 0.5,
                    borderRadius: 1,
                    px: 2,
                    justifyContent: 'space-between',
                  }}
                  role="menuitem"
                  aria-haspopup="true"
                >
                  <ListItemText primary={section.title} />
                  {section.hasDirectPath ? null : <ChevronRight />}
                </ListItemButton>
              ))}
            </List>
          </Box>

          <Box sx={{ flex: 1, p: 2, overflowY: 'auto', minHeight: 0 }}>
            {filteredMenuItems.length > 0 ? (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Search results</Typography>
                <List dense>
                  {filteredMenuItems.map((item, i) => (
                    <ListItemButton key={i} onClick={() => navigateTo(item.path)}>
                      <ListItemText primary={item.name} />
                    </ListItemButton>
                  ))}
                </List>
              </Box>
            ) : (
              <>
                {selectedSection ? (
                  <Grid container spacing={2}>
                    {filteredSections
                      .find((s: any) => s.title === selectedSection)
                      ?.subSections.map((subSection: any, subIndex: number) => (
                        <Grid item xs={12} sm={6} md={4} key={subIndex}>
                          {subSection.title && (
                            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                              {subSection.title}
                            </Typography>
                          )}
                          <List dense>
                            {subSection.items.map((item: any, itemIndex: number) => {
                              const disabled = item.__disabled;
                              return (
                                <Tooltip key={itemIndex} title={disabled ? 'You do not have permission. Click Request.' : ''} arrow>
                                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                                    <ListItemButton
                                      disabled={disabled}
                                      onClick={(e) => {
                                        if (!disabled) {
                                          if (item.subItems) {
                                            handleSubClick(e as any, item);
                                          } else {
                                            navigateTo(item.path);
                                          }
                                        }
                                      }}
                                      sx={{
                                        borderRadius: 1,
                                        width: '100%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                      }}
                                      role="menuitem"
                                    >
                                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                                        <ListItemText primary={item.name} />
                                      </Box>
                                      {item.subItems ? <ChevronRight /> : null}
                                    </ListItemButton>

                                    {disabled && (
                                      <Button size="small" onClick={requestModuleActivation} sx={{ ml: 1 }}>
                                        Request
                                      </Button>
                                    )}
                                  </Box>
                                </Tooltip>
                              );
                            })}
                          </List>
                        </Grid>
                      ))}
                  </Grid>
                ) : (
                  <Typography variant="body2" color="text.secondary">Select a category on the left to view submenu items.</Typography>
                )}
              </>
            )}
          </Box>
        </Box>

        <Box sx={{ px: 2, py: 1, borderTop: '1px solid', borderColor: 'divider', display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button size="small" onClick={() => navigateTo('/create-invoice')}>
            Create Invoice
          </Button>
          <Button size="small" onClick={() => navigateTo('/quotes')}>
            New Quote
          </Button>
          <Button size="small" onClick={requestModuleActivation}>
            Request Module
          </Button>
          <Box sx={{ flex: 1 }} />
          <Typography variant="caption" color="text.secondary">Press Esc to close</Typography>
        </Box>
      </Popover>
    );
  };

  const renderSubMenu = () => {
    if (isMobile) return null;
    if (!activeSubCategory) return null;
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
              },
            },
          },
        }}
        MenuListProps={{
          sx: {
            padding: 1,
          },
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
                  color: 'primary.contrastText',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{subItem.icon}</ListItemIcon>
              <ListItemText primary={subItem.name} />
            </ListItemButton>
          ))}
        </List>
      </Menu>
    );
  };

  const renderSearchResults = () => {
    if (filteredMenuItems.length === 0) return null;
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
          },
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
          borderBottom: '1px solid var(--border-primary)',
        }}
      >
        <Toolbar>
          {isMobile ? (
            <IconButton color="inherit" onClick={() => setMobileDrawerOpen(true)} sx={modernButtonStyle}>
              <MenuIcon />
            </IconButton>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Button
                color="inherit"
                startIcon={<MenuIcon />}
                endIcon={<ExpandMore />}
                onClick={(e) => handleMenuClick(e, 'menu')}
                className="modern-menu-button"
                sx={modernButtonStyle}
                aria-haspopup="true"
                aria-expanded={Boolean(anchorEl)}
                aria-controls="mega-menu-popover"
              >
                Menu
              </Button>
              <Button
                color="inherit"
                startIcon={<Email />}
                onClick={(e) => handleMenuClick(e, 'email')}
                className="modern-menu-button"
                sx={modernButtonStyle}
                aria-haspopup="true"
              >
                Email
              </Button>
              <Button
                color="inherit"
                startIcon={<Settings />}
                endIcon={<ExpandMore />}
                onClick={(e) => handleMenuClick(e, 'settings')}
                className="modern-menu-button"
                sx={modernButtonStyle}
                aria-haspopup="true"
                aria-expanded={Boolean(anchorEl)}
              >
                Settings
              </Button>
            </Box>
          )}

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              flexGrow: 1,
              justifyContent: 'center',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                borderRadius: 1,
              },
              p: 1,
              borderRadius: 1,
              transition: 'background-color 0.2s',
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
                objectFit: 'contain',
              }}
            />
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {organizationData?.name || 'ERP'}
            </Typography>
          </Box>

          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', position: 'relative', ml: 2 }} ref={searchRef}>
              <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: 'action.hover', px: 1, py: 0.4, borderRadius: 1 }}>
                <SearchIcon fontSize="small" />
                <InputBase
                  inputRef={searchInputRef}
                  placeholder="Search…"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  sx={{
                    color: 'inherit',
                    ml: 1,
                    '& .MuiInputBase-input': {
                      padding: '6px 6px',
                      transition: 'width 0.3s',
                      width: searchQuery ? '260px' : '180px',
                    },
                  }}
                />
              </Box>
              {renderSearchResults()}
            </Box>
          )}

          <IconButton
            color="inherit"
            onClick={handleUserMenuClick}
            sx={{
              ml: 2,
              minWidth: 44,
              minHeight: 44,
            }}
            aria-haspopup="true"
            aria-expanded={Boolean(userMenuAnchor)}
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
              },
            },
          },
        }}
        MenuListProps={{
          sx: {
            padding: 1,
          },
        }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2">{user?.full_name || user?.email || 'User'}</Typography>
        </MenuItem>
        <MenuItem onClick={handleUserMenuClose}>
          <Typography variant="body2" color="textSecondary">
            Role: {user?.role || 'Standard User'}
          </Typography>
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            handleUserMenuClose();
            router.push('/profile');
          }}
        >
          Profile Settings
        </MenuItem>
        <MenuItem onClick={onLogout}>Logout</MenuItem>
      </Menu>

      <MobileNav
        open={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
        user={user}
        onLogout={onLogout}
        menuItems={menuItems}
      />

      <CreateOrganizationLicenseModal
        open={createLicenseModalOpen}
        onClose={() => setCreateLicenseModalOpen(false)}
        onSuccess={(result) => {
          console.log('License created:', result);
        }}
      />
    </>
  );
};

export default MegaMenu;