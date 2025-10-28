// frontend/src/pages/settings/user-permissions/[userId].tsx
"use client";
import React, { useState } from "react";
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  IconButton,
  Breadcrumbs,
  Link,
  Chip,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Divider,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from "@mui/material";
import {
  ArrowBack,
  Person,
  Security,
  Save,
  Cancel,
  Check,
  Close,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationService } from "../../../services/organizationService";
import { useAuth } from "../../../context/AuthContext";
import { getDisplayRole } from "../../../types/user.types";
import { Module, MODULE_DISPLAY_NAMES, Action } from "../../../types/rbac.types";

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_super_admin?: boolean;
  department?: string;
  designation?: string;
  is_active: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`permissions-tabpanel-${index}`}
      aria-labelledby={`permissions-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const UserPermissionsPage: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedModules, setSelectedModules] = useState<Set<string>>(new Set());
  const [selectedSubmodules, setSelectedSubmodules] = useState<Record<string, Set<string>>>({});

  // Get userId from URL
  const userId = typeof window !== 'undefined' 
    ? parseInt(window.location.pathname.split('/').pop() || '0')
    : 0;

  // Fetch user details
  const { data: user, isLoading: userLoading } = useQuery<User>({
    queryKey: ["user", userId],
    queryFn: async () => {
      const users = await organizationService.getOrganizationUsers(currentUser?.organization_id!);
      const foundUser = users.find((u: User) => u.id === userId);
      if (!foundUser) throw new Error("User not found");
      return foundUser;
    },
    enabled: !!currentUser?.organization_id && userId > 0,
  });

  // Initialize selected modules when user data loads
  React.useEffect(() => {
    if (user) {
      // TODO: Fetch user's current module assignments from backend
      // For now, initialize empty
      setSelectedModules(new Set());
      setSelectedSubmodules({});
    }
  }, [user]);

  const handleModuleToggle = (module: string) => {
    const newModules = new Set(selectedModules);
    if (newModules.has(module)) {
      newModules.delete(module);
      // Also remove all submodules for this module
      const newSubmodules = { ...selectedSubmodules };
      delete newSubmodules[module];
      setSelectedSubmodules(newSubmodules);
    } else {
      newModules.add(module);
    }
    setSelectedModules(newModules);
  };

  const handleSubmoduleToggle = (module: string, submodule: string) => {
    const moduleSubmodules = selectedSubmodules[module] || new Set();
    const newSubmodules = new Set(moduleSubmodules);
    
    if (newSubmodules.has(submodule)) {
      newSubmodules.delete(submodule);
    } else {
      newSubmodules.add(submodule);
    }
    
    setSelectedSubmodules({
      ...selectedSubmodules,
      [module]: newSubmodules,
    });
  };

  const handleSave = async () => {
    // TODO: Implement save logic to backend
    console.log("Saving permissions:", {
      userId,
      modules: Array.from(selectedModules),
      submodules: Object.fromEntries(
        Object.entries(selectedSubmodules).map(([k, v]) => [k, Array.from(v)])
      ),
    });
    router.push("/settings/user-management");
  };

  const handleCancel = () => {
    router.push("/settings/user-management");
  };

  if (userLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">User not found</Alert>
        <Button
          startIcon={<ArrowBack />}
          onClick={handleCancel}
          sx={{ mt: 2 }}
        >
          Back to User Management
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          underline="hover"
          color="inherit"
          onClick={() => router.push("/dashboard")}
          sx={{ cursor: 'pointer' }}
        >
          Dashboard
        </Link>
        <Link
          underline="hover"
          color="inherit"
          onClick={() => router.push("/settings/user-management")}
          sx={{ cursor: 'pointer' }}
        >
          User Management
        </Link>
        <Typography color="text.primary">Permissions</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={handleCancel}>
              <ArrowBack />
            </IconButton>
            <Person sx={{ fontSize: 40, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" component="h1">
                {user.full_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                @{user.username} • {user.email}
              </Typography>
              <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                <Chip
                  label={getDisplayRole(user.role, user.is_super_admin)}
                  color="primary"
                  size="small"
                />
                <Chip
                  label={user.is_active ? "Active" : "Inactive"}
                  color={user.is_active ? "success" : "default"}
                  size="small"
                  icon={user.is_active ? <Check /> : <Close />}
                />
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<Cancel />}
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save Changes
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Permissions Management */}
      <Paper sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
            <Tab label="Module Access" />
            <Tab label="Submodule Access" />
            <Tab label="Role Assignment" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <Typography variant="h6" gutterBottom>
            Module Access
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select which modules this user can access. Module access is the first level of permission.
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(Module).map(([key, value]) => (
              <Grid item xs={12} sm={6} md={4} key={value}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Checkbox
                        checked={selectedModules.has(value)}
                        onChange={() => handleModuleToggle(value)}
                      />
                      <Box>
                        <Typography variant="subtitle1">
                          {MODULE_DISPLAY_NAMES[value as Module]}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {value}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>
            Submodule Access
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Fine-tune access by selecting specific submodules within each enabled module.
          </Typography>
          
          {Array.from(selectedModules).length === 0 ? (
            <Alert severity="info">
              No modules selected. Please select modules first from the Module Access tab.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {Array.from(selectedModules).map((module) => (
                <Grid item xs={12} key={module}>
                  <Card variant="outlined">
                    <CardHeader
                      title={MODULE_DISPLAY_NAMES[module as Module]}
                      subheader={`Submodule permissions for ${module}`}
                    />
                    <Divider />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        Submodule management for {module} will be implemented here.
                      </Typography>
                      {/* TODO: Add actual submodule checkboxes based on module */}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>
            Role Assignment
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Assign RBAC roles to this user for pre-configured permission sets.
          </Typography>
          <Alert severity="info">
            Role assignment functionality will be integrated with the RBAC service.
          </Alert>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default UserPermissionsPage;
