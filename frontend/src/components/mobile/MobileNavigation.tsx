import React from 'react';
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Box, Typography, Divider, TextField, InputAdornment, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import { Search, Dashboard, Receipt, Inventory, People, Business, Assessment, Settings, ShoppingCart, AccountBalance, Campaign, SupportAgent } from '@mui/icons-material';
import { useState } from 'react';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { menuItems, mainMenuSections } from '../menuConfig';
import ExpandMore from '@mui/icons-material/ExpandMore';

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
      'Master Data': menuItems.masterData.icon,
      'ERP': menuItems.erp.icon,
      'Finance': menuItems.finance.icon,
      'Accounting': <AccountBalance />,
      'Reports & Analytics': <Assessment />,
      'Sales': menuItems.sales.icon,
      'Marketing': menuItems.marketing.icon,
      'Service': menuItems.service.icon,
      'Projects': <Assignment />,
      'HR Management': <Groups />,
      'Tasks & Calendar': <Task />,
      'Email': <Email />,
      'Settings': menuItems.settings.icon,
    };
    return iconMap[sectionTitle] || <Receipt />;
  };

  const sections = mainMenuSections(isSuperAdmin);

  // Add settings separately if not super admin
  if (!isSuperAdmin) {
    sections.push({
      title: 'Settings',
      subSections: menuItems.settings.sections,
    });
  }

  const renderMenuItem = (item: any) => (
    <ListItemButton 
      onClick={() => item.subItems ? handleSectionToggle(item.name) : navigateTo(item.path)}
      sx={{ pl: 4 }}
    >
      <ListItemIcon>{item.icon}</ListItemIcon>
      <ListItemText primary={item.name} />
      {item.subItems && <ExpandMore sx={{ transform: expandedSections.includes(item.name) ? 'rotate(180deg)' : 'rotate(0deg)' }} />}
    </ListItemButton>
  );

  const renderSubItems = (subItems: any[]) => (
    <AccordionDetails sx={{ p: 0 }}>
      <List disablePadding>
        {subItems.map((subItem, subIndex) => (
          <ListItemButton 
            key={subIndex}
            onClick={() => navigateTo(subItem.path)}
            sx={{ pl: 6 }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>{subItem.icon}</ListItemIcon>
            <ListItemText primary={subItem.name} />
          </ListItemButton>
        ))}
      </List>
    </AccordionDetails>
  );

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

            {sections.map((section, index) => (
              <Accordion 
                key={index}
                expanded={expandedSections.includes(section.title)}
                onChange={() => handleSectionToggle(section.title)}
                disableGutters
                elevation={0}
                sx={{
                  '&:before': { display: 'none' },
                  m: 0,
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMore />}
                  sx={{
                    px: 2,
                    minHeight: 48,
                    '& .MuiAccordionSummary-content': {
                      margin: 0,
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
                      fontWeight: 'medium'
                    }}
                  />
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0 }}>
                  {section.subSections?.map((subSection: any, subIndex: number) => (
                    <Box key={subIndex}>
                      {subSection.title && (
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            px: 3, 
                            py: 1, 
                            color: 'text.secondary',
                            fontWeight: 'medium',
                            backgroundColor: 'action.hover'
                          }}
                        >
                          {subSection.title}
                        </Typography>
                      )}
                      <List disablePadding>
                        {subSection.items.map((item: any, itemIndex: number) => (
                          <React.Fragment key={itemIndex}>
                            {renderMenuItem(item)}
                            {item.subItems && expandedSections.includes(item.name) && renderSubItems(item.subItems)}
                          </React.Fragment>
                        ))}
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