// frontend/src/pages/admin/users/index.tsx
import React, { useEffect, useState } from "react";
import { Box, Typography, Button, Paper, Alert } from "@mui/material";
import { PlayArrow, Add } from "@mui/icons-material";
import { useAuth } from "../../../context/AuthContext";
import api from "../../../lib/api";
import RoleGate from "../../../components/RoleGate";
import DemoModeDialog from "../../../components/DemoModeDialog";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/router";
import AddUserDialog from "../../../components/AddUserDialog";

import { ProtectedPage } from '../../../../components/ProtectedPage';
interface User {
  id: number;
  email: string;
  role: string;
  organization_id?: number;
}

const columns: GridColDef[] = [
  { field: "id", headerName: "ID", width: 90 },
  { field: "email", headerName: "Email", width: 200 },
  { field: "role", headerName: "Role", width: 150 },
  { field: "organization_id", headerName: "Organization ID", width: 150 },
];

const UsersPage: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [demoModeOpen, setDemoModeOpen] = useState(false);
  const [addUserOpen, setAddUserOpen] = useState(false);
  const queryClient = useQueryClient();

  const {
    data: users,
    isLoading,
  } = useQuery<User[]>({
    queryKey: ["users"],
    queryFn: async () => {
      const endpoint = user?.role === "super_admin" ? "/users" : "/users/org";
      const response = await api.get(endpoint);
      return response.data;
    },
    enabled: !!user,
  });

  const createUserMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post(`/organizations/${user?.organization_id}/users`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setAddUserOpen(false);
    },
  });

  // Handle loading state with useEffect instead of onSettled
  useEffect(() => {
    if (!isLoading) {
      setLoading(false);
    }
  }, [isLoading]);

  const handleDemoStart = async (token: string, loginResponse?: any) => {
    // Set demo mode flags
    localStorage.setItem("demoMode", "true");
    if (loginResponse?.demo_mode) {
      localStorage.setItem("isDemoTempUser", "true");
    }
    // Navigate to demo page
    router.push("/demo");
  };

  const handleAddUser = (data: any) => {
    createUserMutation.mutate(data);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <ProtectedPage moduleKey="admin" action="read">
    <Box sx={{ p: 3 }}>
      <RoleGate allowedRoles={["super_admin", "org_admin"]}>
        <Paper sx={{ p: 3 }}>
          {/* Header with Demo Button */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 3,
            }}
          >
            <Typography variant="h4" component="h1">
              User Management
            </Typography>
            <Box sx={{ display: "flex", gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<PlayArrow />}
                onClick={() => setDemoModeOpen(true)}
                sx={{
                  borderRadius: 2,
                  px: 3,
                  py: 1,
                  borderColor: "primary.light",
                  "&:hover": {
                    borderColor: "primary.main",
                    backgroundColor: "primary.light",
                    color: "primary.contrastText",
                  },
                }}
              >
                Try Demo Mode
              </Button>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setAddUserOpen(true)}
              >
                Add User
              </Button>
            </Box>
          </Box>
          {/* Demo Mode Info Alert */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Demo Mode Available:</strong> Experience all user
              management features with sample data. No real user data will be
              affected during the demo.
            </Typography>
          </Alert>
          {/* Users Data Grid */}
          <Box sx={{ height: 400, width: "100%" }}>
            <DataGrid
              rows={users || []}
              columns={columns}
              disableRowSelectionOnClick
              sx={{
                "& .MuiDataGrid-cell": {
                  borderBottom: "1px solid #f0f0f0",
                },
                "& .MuiDataGrid-columnHeaders": {
                  backgroundColor: "#f5f5f5",
                  borderBottom: "2px solid #e0e0e0",
                },
              }}
            />
          </Box>
        </Paper>
        {/* Demo Mode Dialog */}
        <DemoModeDialog
          open={demoModeOpen}
          onClose={() => setDemoModeOpen(false)}
          onDemoStart={handleDemoStart}
        />
        {/* Add User Dialog */}
        <AddUserDialog
          open={addUserOpen}
          onClose={() => setAddUserOpen(false)}
          onAdd={handleAddUser}
          loading={createUserMutation.isPending}
          organizationId={user?.organization_id || 0}
        />
      </RoleGate>
    </Box>
    </ProtectedPage>

  );
};

export default UsersPage;
