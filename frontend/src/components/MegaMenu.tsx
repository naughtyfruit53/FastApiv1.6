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
  Chip,
  Lock as LockIcon,
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
import { useAuth } from '../context/AuthContext';
import { usePermissions } from '../context/PermissionContext';
import useSharedPermissions from '../hooks/useSharedPermissions';
import { useEntitlements } from '../hooks/useEntitlements';
import { evalMenuItemAccess, getMenuItemBadge, getMenuItemTooltip } from '../permissions/menuAccess';

interface MegaMenuProps {
  user?: any;
  onLogout: () => void;
  isVisible?: boolean;
}

const MegaMenu: React.FC<MegaMenuProps> = ({ user, onLogout, isVisible = true }) => {
  const { hasPermission, permissions: contextUserPermissions } = usePermissions();
  const { hasModuleAccess, hasSubmoduleAccess } = useSharedPermissions();
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
  const { data: userServicePermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getUserPermissions,
    enabled: !!user && !isAppSuperAdmin(user),
    retry: false,
    staleTime: 0,
    onSuccess: (data) => {
      console.log('User permissions fetched:', data);
    },
  });

  const isSuperAdmin = isAppSuperAdmin(user);
  const isGodSuperAdmin = user?.email === 'naughtyfruit53@gmail.com';
  const isAdminLike = isSuperAdmin || isOrgSuperAdmin(user);

  // Fetch entitlements for menu access control
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
  const { entitlements, isLoading: entitlementsLoading } = useEntitlements(
    organizationData?.id,
    authToken || undefined
  );

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

  // Auto-select first section when menu opens if none is selected
  useEffect(() => {
    if (anchorEl && activeMenu && !selectedSection) {
      const menuItem = menuItems[activeMenu as keyof typeof menuItems];
      const sections = activeMenu === 'menu' ? mainMenuSections(isSuperAdmin) : menuItem?.sections || [];
      if (sections.length > 0) {
        setSelectedSection(sections[0].title);
      }
    }
  }, [anchorEl, activeMenu, selectedSection, isSuperAdmin]);

  if (!isVisible) return null;

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, menuName: string) => {
    const menuItem = menuItems[menuName as keyof typeof menuItems];
    // Check if the menu item has a direct path and no subsections
    if (menuItem && 'path' in menuItem && menuItem.path && (!menuItem.sections || menuItem.sections.length === 0)) {
      router.push(menuItem.path); // Navigate directly to the path
    } else {
      setAnchorEl(event.currentTarget);
      setActiveMenu(menuName);
      // Auto-select first section if not selected (improves UX)
      if (!selectedSection && !isMobile) {
        const sections = menuName === 'menu' ? mainMenuSections(isSuperAdmin) : menuItem?.sections || [];
        if (sections.length > 0) {
          setSelectedSection(sections[0].title);
        }
      }
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

  const hasServicePermission = (permission: string): boolean => {
    try {
      return contextUserPermissions.includes(permission);
    } catch {
      return false;
    }
  };

  const hasAnyServicePermission = (permissions: string[]): boolean => {
    return permissions.some((permission) => contextUserPermissions.includes(permission));
  };

  const isModuleEnabled = (module: string): boolean => {
    if (isSuperAdmin) return true;
    const normalizedModule = module.toUpperCase();
    const enabled = organizationData?.enabled_modules?.[normalizedModule] ?? true;
    console.log(`Module check - ${module} (normalized: ${normalizedModule}):`, enabled, {
      allModules: organizationData?.enabled_modules,
      timestamp: new Date().toISOString(),
    });
    return enabled;
  };

  const _openDemoMode = () => {
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

  const _handleCreateLicense = () => {
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
      return subSection.items
        .filter((item: any) => {
          // Filter out items that require god superadmin access
          if (item.godSuperAdminOnly && !isGodSuperAdmin) {
            return false;
          }
          // Filter out items that require superadmin access (unless they are super admin)
          if (item.superAdminOnly && !isSuperAdmin) {
            return false;
          }
          // Hide org-specific permission items for app superadmin
          if (item.servicePermission && isSuperAdmin) return false;
          // Hide org-role specific items for app superadmin
          if (item.role && isSuperAdmin) return false;
          
          // For super admins, allow all items that aren't explicitly restricted
          if (isSuperAdmin) {
            return true;
          }
          
          // Use evalMenuItemAccess for entitlement-based access control
          const accessResult = evalMenuItemAccess({
            requireModule: item.requireModule,
            requireSubmodule: item.requireSubmodule,
            entitlements: entitlements,
            isAdmin: isAdminLike,
            isSuperAdmin: isSuperAdmin,
          });
          
          // If access is 'hidden', hide for non-admin users
          if (accessResult.result === 'hidden' && !isAdminLike) {
            return false;
          }
          
          // Check RBAC permissions if specified
          if (item.permission) {
            const [module, action] = item.permission.split('.');
            if (!hasPermission(module, action)) {
              console.log(`Permission check failed for item ${item.name}: requires ${item.permission}`);
              return true; // Still show, but will be disabled below
            }
          }
          
          return true; // Show item (may be disabled based on access result)
        })
        .map((item: any) => {
          // Evaluate access for each item
          const accessResult = evalMenuItemAccess({
            requireModule: item.requireModule,
            requireSubmodule: item.requireSubmodule,
            entitlements: entitlements,
            isAdmin: isAdminLike,
            isSuperAdmin: isSuperAdmin,
          });
          
          const disabled =
            accessResult.result === 'disabled' ||
            (item.role && !canManageUsers(user)) ||
            (item.servicePermission && !(isModuleEnabled('service') || hasServicePermission(item.servicePermission)));
          
          const badge = getMenuItemBadge({
            requireModule: item.requireModule,
            requireSubmodule: item.requireSubmodule,
            entitlements: entitlements,
            isAdmin: isAdminLike,
            isSuperAdmin: isSuperAdmin,
          });
          
          const tooltip = getMenuItemTooltip({
            requireModule: item.requireModule,
            requireSubmodule: item.requireSubmodule,
            entitlements: entitlements,
            isAdmin: isAdminLike,
            isSuperAdmin: isSuperAdmin,
          });
          
          return { 
            ...item, 
            __disabled: Boolean(disabled),
            __badge: badge,
            __tooltip: tooltip,
            __accessResult: accessResult,
          };
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

    // Filter sections - include all sections for visibility, even if empty (but filter items inside)
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
          .filter((subSection: any) => true); // Keep all subsections visible, even if no items

        return {
          ...section,
          subSections: processedSubSections,
          hasDirectPath: hasDirectPath,
        };
      })
      .filter((section: any) => true); // Keep all sections visible

    if (filteredSections.length === 0) {
      console.warn(`No items in submenu for ${activeMenu} - user may not have required permissions or modules enabled`);
      // Show a helpful message instead of returning null
      return (
        <Popover
          open={Boolean(anchorEl)}
          anchorEl={anchorEl}
          onClose={handleMenuClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          transformOrigin={{ vertical: 'top', horizontal: 'left' }}
          PaperProps={{
            sx: {
              width: 'auto',
              minWidth: 400,
              maxWidth: 600,
              left: '20px !important',
              borderRadius: 2,
              boxShadow: '0 14px 40px rgba(0,0,0,0.16)',
              border: '1px solid',
              borderColor: 'divider',
              p: 3,
            },
          }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              No Menu Items Available
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              You don't have permission to access any items in this menu, or the required modules are not enabled for your organization.
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Contact your administrator to request access or enable required modules.
            </Typography>
          </Box>
        </Popover>
      );
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
                    // Check if this section has a direct path (e.g., Email)
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
                    <ListItemButton key={i} onClick={() => navigateTo(item.path)} disabled={item.__disabled}>
                      <ListItemText primary={item.name} />
                    </ListItemButton>
                  ))}
                </List>
              </Box>
            ) : (
              <>
                {selectedSection ? (
                  <Grid container spacing= {2}>
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
                              const disabled =
                                (item.role && !canManageUsers(user)) ||
                                (item.servicePermission && !(isModuleEnabled('service') || hasServicePermission(item.servicePermission))) ||
                                item.__disabled;
                              const tooltipText = item.__tooltip || (disabled ? 'Module not enabled. Contact your administrator.' : '');
                              return (
                                <Tooltip key={itemIndex} title={tooltipText} arrow>
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
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        {disabled && isAdminLike && <LockIcon fontSize="small" color="disabled" />}
                                        <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                                        <ListItemText primary={item.name} />
                                        {item.__badge && (
                                          <Chip 
                                            label={item.__badge} 
                                            size="small" 
                                            color="warning" 
                                            sx={{ height: 20, fontSize: '0.7rem' }}
                                          />
                                        )}
                                      </Box>
                                      {item.subItems ? <ChevronRight /> : null}
                                    </ListItemButton>

                                    {disabled && isAdminLike && (
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
              disabled={subItem.__disabled}
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
    if (filteredMenuItems.length > 0) return null;
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
          <MenuItem key={index} onClick={() => navigateTo(item.path)} disabled={item.__disabled}>
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
                endIcon={<ExpandMore />}
                onClick={(e) => handleMenuClick(e, 'email')}
                className="modern-menu-button"
                sx={modernButtonStyle}
                aria-haspopup="true"
                aria-expanded={Boolean(anchorEl)}
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