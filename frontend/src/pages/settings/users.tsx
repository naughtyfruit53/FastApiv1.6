// pages/settings/users.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import { 
  People, 
  PersonAdd, 
  Edit, 
  Delete, 
  Security,
  Block,
  CheckCircle
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

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
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const UserManagementPage: React.FC = () => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const sampleUsers = [
    { id: 1, name: 'John Doe', email: 'john@company.com', role: 'Admin', status: 'Active' },
    { id: 2, name: 'Jane Smith', email: 'jane@company.com', role: 'Manager', status: 'Active' },
    { id: 3, name: 'Bob Johnson', email: 'bob@company.com', role: 'User', status: 'Inactive' },
  ];

  const sampleRoles = [
    { id: 1, name: 'Super Admin', users: 1, permissions: 'All' },
    { id: 2, name: 'Admin', users: 2, permissions: 'Most' },
    { id: 3, name: 'Manager', users: 5, permissions: 'Department' },
    { id: 4, name: 'User', users: 15, permissions: 'Limited' },
  ];

  return (
    <DashboardLayout
      title="User Management"
      subtitle="Manage users, roles, and permissions"
      actions={
        <Button 
          variant="contained" 
          startIcon={<PersonAdd />}
          href="/settings/add-user"
        >
          Add User
        </Button>
      }
    >
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Users" />
            <Tab label="Roles & Permissions" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Manage organization users and their access levels. Changes take effect immediately.
          </Alert>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sampleUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <People sx={{ mr: 1, color: 'primary.main' }} />
                        {user.name}
                      </Box>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip 
                        label={user.role} 
                        color={user.role === 'Admin' ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={user.status}
                        color={user.status === 'Active' ? 'success' : 'default'}
                        size="small"
                        icon={user.status === 'Active' ? <CheckCircle /> : <Block />}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            Role changes affect user permissions across all modules. Please review carefully.
          </Alert>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Role Name</TableCell>
                  <TableCell>Users Assigned</TableCell>
                  <TableCell>Permission Level</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sampleRoles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Security sx={{ mr: 1, color: 'primary.main' }} />
                        {role.name}
                      </Box>
                    </TableCell>
                    <TableCell>{role.users} users</TableCell>
                    <TableCell>
                      <Chip 
                        label={role.permissions}
                        color={role.permissions === 'All' ? 'error' : 
                               role.permissions === 'Most' ? 'warning' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small" variant="outlined">
                        Configure
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Card>
    </DashboardLayout>
  );
};

export default UserManagementPage;