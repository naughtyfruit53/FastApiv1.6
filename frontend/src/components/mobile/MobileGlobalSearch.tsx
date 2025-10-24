import React, { useState, useMemo, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  InputAdornment,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Chip,
  Divider,
  IconButton,
  Fade,
  Paper
} from '@mui/material';
import {
  Search,
  Close,
  Dashboard,
  Receipt,
  People,
  Business,
  Assessment,
  AccountBalance,
  Inventory,
  Campaign,
  SupportAgent,
  Assignment,
  Groups,
  Task,
  Email,
  Settings,
  History,
  TrendingUp,
  NavigateNext
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { mainMenuSections } from '../menuConfig';

interface SearchResult {
  id: string;
  title: string;
  subtitle?: string;
  path: string;
  mobileRoute?: string;
  icon: React.ReactElement;
  category: string;
  keywords: string[];
  priority: number;
}

interface MobileGlobalSearchProps {
  open: boolean;
  onClose: () => void;
  user?: any;
}

const MobileGlobalSearch: React.FC<MobileGlobalSearchProps> = ({
  open,
  onClose,
  user
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const router = useRouter();
  const { isMobile } = useMobileDetection();
  const isSuperAdmin = user?.role === 'APP_SUPER_ADMIN';

  // Build comprehensive search index
  const searchIndex = useMemo(() => {
    const sections = mainMenuSections(isSuperAdmin);
    const results: SearchResult[] = [];

    // Add core mobile pages with high priority
    const corePages = [
      {
        id: 'dashboard',
        title: 'Dashboard',
        subtitle: 'Overview and metrics',
        path: '/dashboard',
        mobileRoute: '/mobile/dashboard',
        icon: <Dashboard />,
        category: 'Core',
        keywords: ['dashboard', 'overview', 'metrics', 'home', 'main'],
        priority: 10
      },
      {
        id: 'sales',
        title: 'Sales',
        subtitle: 'Leads and opportunities',
        path: '/sales/dashboard',
        mobileRoute: '/mobile/sales',
        icon: <Receipt />,
        category: 'Core',
        keywords: ['sales', 'leads', 'opportunities', 'revenue', 'deals'],
        priority: 9
      },
      {
        id: 'crm',
        title: 'CRM',
        subtitle: 'Customer management',
        path: '/crm',
        mobileRoute: '/mobile/crm',
        icon: <People />,
        category: 'Core',
        keywords: ['crm', 'customers', 'contacts', 'relations', 'clients'],
        priority: 9
      },
      {
        id: 'finance',
        title: 'Finance',
        subtitle: 'Financial management',
        path: '/finance-dashboard',
        mobileRoute: '/mobile/finance',
        icon: <AccountBalance />,
        category: 'Core',
        keywords: ['finance', 'accounting', 'money', 'transactions', 'budget'],
        priority: 8
      },
      {
        id: 'inventory',
        title: 'Inventory',
        subtitle: 'Stock management',
        path: '/inventory',
        mobileRoute: '/mobile/inventory',
        icon: <Inventory />,
        category: 'Core',
        keywords: ['inventory', 'stock', 'warehouse', 'products', 'items'],
        priority: 8
      },
      {
        id: 'hr',
        title: 'HR Management',
        subtitle: 'Employee management',
        path: '/hr/dashboard',
        mobileRoute: '/mobile/hr',
        icon: <Groups />,
        category: 'Core',
        keywords: ['hr', 'human resources', 'employees', 'staff', 'payroll'],
        priority: 7
      },
      {
        id: 'service',
        title: 'Service',
        subtitle: 'Service management',
        path: '/service/dashboard',
        mobileRoute: '/mobile/service',
        icon: <SupportAgent />,
        category: 'Core',
        keywords: ['service', 'support', 'tickets', 'helpdesk', 'technician'],
        priority: 7
      },
      {
        id: 'reports',
        title: 'Reports',
        subtitle: 'Analytics and reports',
        path: '/reports',
        mobileRoute: '/mobile/reports',
        icon: <Assessment />,
        category: 'Core',
        keywords: ['reports', 'analytics', 'insights', 'data', 'charts'],
        priority: 6
      }
    ];

    results.push(...corePages);

    // Add desktop menu items with lower priority
    sections.forEach(section => {
      section.subSections?.forEach(subSection => {
        subSection.items.forEach(item => {
          results.push({
            id: `${section.title}-${item.name}`.toLowerCase().replace(/\s+/g, '-'),
            title: item.name,
            subtitle: `${section.title} • ${subSection.title || ''}`,
            path: item.path,
            icon: item.icon || <Business />,
            category: section.title,
            keywords: [
              item.name.toLowerCase(),
              section.title.toLowerCase(),
              ...(subSection.title ? [subSection.title.toLowerCase()] : []),
              item.path.toLowerCase()
            ],
            priority: 3
          });
        });
      });
    });

    return results;
  }, [isSuperAdmin]);

  // Filter search results
  const filteredResults = useMemo(() => {
    if (!searchQuery.trim()) return [];

    const query = searchQuery.toLowerCase().trim();
    const queryWords = query.split(/\s+/);

    return searchIndex
      .filter(result => {
        // Check if all query words match
        return queryWords.every(word =>
          result.title.toLowerCase().includes(word) ||
          result.subtitle?.toLowerCase().includes(word) ||
          result.keywords.some(keyword => keyword.includes(word))
        );
      })
      .sort((a, b) => {
        // Sort by priority first, then by relevance
        if (a.priority !== b.priority) {
          return b.priority - a.priority;
        }
        
        // Exact title match has higher priority
        const aExactMatch = a.title.toLowerCase() === query;
        const bExactMatch = b.title.toLowerCase() === query;
        if (aExactMatch && !bExactMatch) return -1;
        if (!aExactMatch && bExactMatch) return 1;

        // Title starts with query
        const aStartsWith = a.title.toLowerCase().startsWith(query);
        const bStartsWith = b.title.toLowerCase().startsWith(query);
        if (aStartsWith && !bStartsWith) return -1;
        if (!aStartsWith && bStartsWith) return 1;

        return a.title.localeCompare(b.title);
      })
      .slice(0, 10); // Limit results for mobile
  }, [searchQuery, searchIndex]);

  // Group results by category
  const groupedResults = useMemo(() => {
    const groups: { [key: string]: SearchResult[] } = {};
    filteredResults.forEach(result => {
      if (!groups[result.category]) {
        groups[result.category] = [];
      }
      groups[result.category].push(result);
    });
    return groups;
  }, [filteredResults]);

  const handleNavigate = (result: SearchResult) => {
    const targetRoute = result.mobileRoute || result.path;
    
    // Add to recent searches
    setRecentSearches(prev => {
      const updated = [result.title, ...prev.filter(item => item !== result.title)];
      return updated.slice(0, 5); // Keep only 5 recent searches
    });
    
    router.push(targetRoute);
    onClose();
    setSearchQuery('');
  };

  const handleRecentSearch = (searchTerm: string) => {
    setSearchQuery(searchTerm);
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
  };

  // Clear search when dialog closes
  useEffect(() => {
    if (!open) {
      setSearchQuery('');
    }
  }, [open]);

  const getCategoryIcon = (category: string) => {
    const iconMap: { [key: string]: React.ReactElement } = {
      'Core': <TrendingUp />,
      'Master Data': <Business />,
      'ERP': <Receipt />,
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
    };
    return iconMap[category] || <Business />;
  };

  // Early return after all hooks (moved here to ensure consistent hook calls)
  if (!isMobile) {
    return null;
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullScreen
      TransitionComponent={Fade}
      TransitionProps={{ timeout: 300 }}
      PaperProps={{
        sx: {
          backgroundColor: 'background.default',
        }
      }}
    >
      <DialogContent sx={{ p: 0, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Search Header */}
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          p: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper'
        }}>
          <TextField
            fullWidth
            autoFocus
            variant="outlined"
            placeholder="Search modules, features, pages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                backgroundColor: 'action.hover',
              }
            }}
          />
          <IconButton onClick={onClose} size="large">
            <Close />
          </IconButton>
        </Box>

        {/* Search Results or Recent Searches */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {searchQuery.trim() ? (
            // Search Results
            <Box sx={{ p: 2 }}>
              {filteredResults.length > 0 ? (
                <>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {filteredResults.length} result{filteredResults.length !== 1 ? 's' : ''} found
                  </Typography>
                  {Object.entries(groupedResults).map(([category, results]) => (
                    <Box key={category} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getCategoryIcon(category)}
                        <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 600 }}>
                          {category}
                        </Typography>
                        <Chip label={results.length} size="small" variant="outlined" />
                      </Box>
                      <Paper elevation={1} sx={{ borderRadius: 2, overflow: 'hidden' }}>
                        <List disablePadding>
                          {results.map((result, index) => (
                            <React.Fragment key={result.id}>
                              <ListItemButton
                                onClick={() => handleNavigate(result)}
                                sx={{
                                  py: 1.5,
                                  '&:hover': {
                                    backgroundColor: 'action.hover',
                                  }
                                }}
                              >
                                <ListItemIcon>
                                  {result.icon}
                                </ListItemIcon>
                                <ListItemText
                                  primary={result.title}
                                  secondary={result.subtitle}
                                  primaryTypographyProps={{
                                    fontWeight: 600,
                                    color: 'text.primary'
                                  }}
                                  secondaryTypographyProps={{
                                    variant: 'caption',
                                    color: 'text.secondary'
                                  }}
                                />
                                {result.mobileRoute && (
                                  <Chip
                                    label="Mobile"
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                    sx={{ fontSize: '0.7rem', mr: 1 }}
                                  />
                                )}
                                <NavigateNext sx={{ color: 'text.secondary' }} />
                              </ListItemButton>
                              {index < results.length - 1 && <Divider />}
                            </React.Fragment>
                          ))}
                        </List>
                      </Paper>
                    </Box>
                  ))}
                </>
              ) : (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Search sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No results found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Try different keywords or check the spelling
                  </Typography>
                </Box>
              )}
            </Box>
          ) : (
            // Recent Searches and Suggestions
            <Box sx={{ p: 2 }}>
              {recentSearches.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 600 }}>
                      Recent Searches
                    </Typography>
                    <Typography
                      variant="caption"
                      color="primary"
                      sx={{ cursor: 'pointer', textDecoration: 'underline' }}
                      onClick={clearRecentSearches}
                    >
                      Clear
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {recentSearches.map((search, index) => (
                      <Chip
                        key={index}
                        label={search}
                        icon={<History />}
                        variant="outlined"
                        onClick={() => handleRecentSearch(search)}
                        sx={{
                          borderRadius: 2,
                          '&:hover': {
                            backgroundColor: 'action.hover',
                          }
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}

              <Box>
                <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 600, mb: 2 }}>
                  Quick Access
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['Dashboard', 'Sales', 'CRM', 'Finance', 'Inventory', 'Reports'].map((item) => (
                    <Chip
                      key={item}
                      label={item}
                      variant="outlined"
                      color="primary"
                      onClick={() => handleRecentSearch(item)}
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
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default MobileGlobalSearch;