// frontend/src/pages/help.tsx
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Chip,
  Grid,
  Paper,
  IconButton,
  Collapse
} from '@mui/material';
import {
  Search,
  Dashboard as DashboardIcon,
  Inventory,
  Receipt,
  Engineering,
  AccountBalance,
  Settings,
  Help as HelpIcon,
  KeyboardArrowDown,
  KeyboardArrowUp,
  Book,
  VideoLibrary,
  ContactSupport
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';

interface HelpSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
  topics: { title: string; content: string }[];
}

const HelpPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const helpSections: HelpSection[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: <HelpIcon color="primary" />,
      description: 'Learn the basics of using the ERP system',
      topics: [
        {
          title: 'First Time Login',
          content: 'Access the system with your credentials, navigate to the dashboard, and explore the mega menu for all features.'
        },
        {
          title: 'Navigation Basics',
          content: 'Use the mega menu for all modules, search bar for quick access, and breadcrumbs to track your location.'
        },
        {
          title: 'Dashboard Overview',
          content: 'Your dashboard shows key metrics including sales overview, inventory alerts, pending tasks, and quick actions.'
        }
      ]
    },
    {
      id: 'master-data',
      title: 'Master Data Management',
      icon: <DashboardIcon color="primary" />,
      description: 'Manage vendors, customers, products, and chart of accounts',
      topics: [
        {
          title: 'Managing Vendors',
          content: 'Create vendors by navigating to Master Data → Vendors. Enter name, contact info, GST number, and payment terms. Always verify GST numbers and set default payment terms.'
        },
        {
          title: 'Managing Customers',
          content: 'Add customers with accurate billing and shipping addresses. Set appropriate credit limits and maintain GST details for compliance.'
        },
        {
          title: 'Product Management',
          content: 'Add products with HSN/SAC codes, units, stock levels, and GST rates. Organize into categories and set reorder levels.'
        },
        {
          title: 'Chart of Accounts',
          content: 'The CoA is organized into Assets, Liabilities, Income, Expenses, and Equity. Create accounts under appropriate parent groups.'
        }
      ]
    },
    {
      id: 'inventory',
      title: 'Inventory Management',
      icon: <Inventory color="primary" />,
      description: 'Track stock levels, movements, and set alerts',
      topics: [
        {
          title: 'Current Stock View',
          content: 'View real-time stock levels at Inventory → Current Stock. Filter by category, warehouse, or product. Export to Excel for analysis.'
        },
        {
          title: 'Stock Movements',
          content: 'All stock transactions are automatically recorded. View movement history for any product to identify trends.'
        },
        {
          title: 'Low Stock Alerts',
          content: 'Set minimum stock levels in product master data. System alerts when stock falls below threshold.'
        }
      ]
    },
    {
      id: 'vouchers',
      title: 'Voucher Management',
      icon: <Receipt color="primary" />,
      description: 'Create and manage all types of vouchers with PDF generation',
      topics: [
        {
          title: 'Purchase Vouchers',
          content: 'Create purchase orders, invoices, returns, and GRNs. Navigate to Vouchers → Purchase Vouchers → New. Select vendor, add items, system calculates GST automatically.'
        },
        {
          title: 'Sales Invoices',
          content: 'Go to Vouchers → Sales Invoices → New. Select customer, add products with quantities. System calculates GST based on state (CGST/SGST or IGST). Generate PDF or email to customer.'
        },
        {
          title: 'PDF Templates',
          content: 'Choose from 4 professional templates: Standard (default), Modern (gradient design), Classic (traditional), and Minimal (clean). All templates include bank details and terms & conditions.'
        },
        {
          title: 'Terms & Conditions',
          content: 'Configure specific terms for each voucher type in Settings → Voucher Settings. Terms automatically appear on voucher PDFs.'
        }
      ]
    },
    {
      id: 'manufacturing',
      title: 'Manufacturing',
      icon: <Engineering color="primary" />,
      description: 'Production planning, BOMs, and work orders',
      topics: [
        {
          title: 'Production Orders',
          content: 'Create production orders at Manufacturing → Production Order. Select finished product, enter quantity, system shows required raw materials from BOM.'
        },
        {
          title: 'Bill of Materials',
          content: 'Manage BOMs at Master Data → BOM. Add components with quantities and wastage percentage.'
        },
        {
          title: 'Work Orders',
          content: 'Track manufacturing progress with work orders. Assign to work centers and monitor status (Pending, In Progress, Completed).'
        }
      ]
    },
    {
      id: 'finance',
      title: 'Finance & Accounting',
      icon: <AccountBalance color="primary" />,
      description: 'Accounts payable, cost centers, budgets, and cost analysis',
      topics: [
        {
          title: 'Accounts Payable',
          content: 'Monitor all vendor payables at Finance → Accounts Payable. View total payable, overdue amounts, and bills due this week/month. Click Make Payment to settle bills.'
        },
        {
          title: 'Cost Centers',
          content: 'Create cost centers with auto-generated codes or choose from 12 standard names (Admin, Sales, Production, R&D, IT, HR, Finance, Operations, Maintenance, Logistics, Customer Service, Legal). Track expenses by department.'
        },
        {
          title: 'Budget Management',
          content: 'Create and track budgets at Finance → Budget Management. Monitor total budget, allocated, spent, and remaining amounts. Track utilization with progress bars.'
        },
        {
          title: 'Cost Analysis',
          content: 'Get AI-powered insights at Finance → Cost Analysis. System identifies budget overruns, underutilization, and provides actionable recommendations (High/Medium/Low priority).'
        }
      ]
    },
    {
      id: 'settings',
      title: 'Settings & Configuration',
      icon: <Settings color="primary" />,
      description: 'Configure system settings, users, and integrations',
      topics: [
        {
          title: 'Voucher Settings',
          content: 'Configure at Settings → Voucher Settings. Set voucher prefix (max 5 chars), choose counter reset period (Never/Monthly/Quarterly/Annually), select PDF template style, and add terms & conditions for each voucher type.'
        },
        {
          title: 'Tally Integration',
          content: 'Connect to Tally ERP at Settings → General Settings → Tally Integration. Enter Tally server host (e.g., localhost), port (default 9000), and company name. Prerequisites: Tally running with ODBC server enabled (F12 → Configure). Use Sync Now for real-time sync, Import from Tally, or Export to Tally.'
        },
        {
          title: 'User Management',
          content: 'Add users at Settings → User Management. Assign roles and permissions for role-based access control (RBAC).'
        }
      ]
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      icon: <ContactSupport color="primary" />,
      description: 'Common issues and solutions',
      topics: [
        {
          title: 'Cannot Login',
          content: 'Verify credentials, check internet connection, clear browser cache, try incognito mode. Contact administrator if issue persists.'
        },
        {
          title: 'PDF Not Generating',
          content: 'Check browser pop-up settings, ensure voucher has required data, try different browser, contact support.'
        },
        {
          title: 'Tally Sync Failing',
          content: 'Verify Tally is running, check ODBC server is enabled, confirm company name matches exactly, test connection, check firewall settings.'
        }
      ]
    }
  ];

  const handleSectionClick = (sectionId: string) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
  };

  const filteredSections = helpSections.filter(section =>
    section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.topics.some(topic =>
      topic.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      topic.content.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <DashboardLayout
      title="Help & User Guide"
      subtitle="Comprehensive guide to using the ERP system"
    >
      <Grid container spacing={3}>
        {/* Quick Links */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Links
              </Typography>
              <List>
                <ListItemButton component="a" href="/docs/USER_GUIDE.md" target="_blank">
                  <Book sx={{ mr: 2 }} color="primary" />
                  <ListItemText
                    primary="Complete User Guide"
                    secondary="Download full documentation"
                  />
                </ListItemButton>
                <Divider />
                <ListItemButton>
                  <VideoLibrary sx={{ mr: 2 }} color="primary" />
                  <ListItemText
                    primary="Video Tutorials"
                    secondary="Coming soon"
                  />
                </ListItemButton>
                <Divider />
                <ListItemButton>
                  <ContactSupport sx={{ mr: 2 }} color="primary" />
                  <ListItemText
                    primary="Contact Support"
                    secondary="support@tritiq.com"
                  />
                </ListItemButton>
              </List>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Keyboard Shortcuts
              </Typography>
              <List dense>
                <ListItem>
                  <Typography variant="body2">
                    <Chip label="Ctrl+S" size="small" sx={{ mr: 1 }} />
                    Save
                  </Typography>
                </ListItem>
                <ListItem>
                  <Typography variant="body2">
                    <Chip label="Ctrl+P" size="small" sx={{ mr: 1 }} />
                    Print
                  </Typography>
                </ListItem>
                <ListItem>
                  <Typography variant="body2">
                    <Chip label="Ctrl+F" size="small" sx={{ mr: 1 }} />
                    Search
                  </Typography>
                </ListItem>
                <ListItem>
                  <Typography variant="body2">
                    <Chip label="/" size="small" sx={{ mr: 1 }} />
                    Focus search
                  </Typography>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Help Content */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box mb={3}>
                <TextField
                  fullWidth
                  placeholder="Search help topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    )
                  }}
                />
              </Box>

              <List>
                {filteredSections.map((section) => (
                  <React.Fragment key={section.id}>
                    <ListItemButton onClick={() => handleSectionClick(section.id)}>
                      <Box sx={{ mr: 2 }}>{section.icon}</Box>
                      <ListItemText
                        primary={
                          <Typography variant="h6">{section.title}</Typography>
                        }
                        secondary={section.description}
                      />
                      <IconButton>
                        {expandedSection === section.id ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                      </IconButton>
                    </ListItemButton>

                    <Collapse in={expandedSection === section.id}>
                      <Box sx={{ pl: 4, pr: 2, pb: 2 }}>
                        {section.topics.map((topic, index) => (
                          <Paper key={index} sx={{ p: 2, mb: 2 }}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                              {topic.title}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {topic.content}
                            </Typography>
                          </Paper>
                        ))}
                      </Box>
                    </Collapse>

                    <Divider />
                  </React.Fragment>
                ))}
              </List>

              {filteredSections.length === 0 && (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary">
                    No help topics found matching your search.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default HelpPage;
