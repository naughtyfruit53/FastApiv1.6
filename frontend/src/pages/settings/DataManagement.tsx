import React from "react";
import { Box, Button, Typography, Alert, Container, Paper } from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { Security } from "@mui/icons-material";
import { ProtectedPage } from "../../components/ProtectedPage";

const DataManagement: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const isGodSuperAdmin = user?.email === 'naughtyfruit53@gmail.com';

  // Restrict to god superadmin only
  if (!isGodSuperAdmin) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Security sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Access Restricted
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Data management and factory reset operations are only available to the god superadmin account (naughtyfruit53@gmail.com).
          </Typography>
          <Button variant="contained" onClick={() => router.push('/dashboard')}>
            Return to Dashboard
          </Button>
        </Paper>
      </Container>
    );
  }

  // Placeholder mutation - would need to add factoryDefault method to organizationService
  const factoryResetMutation = useMutation({
    mutationFn: () =>
      fetch("/api/v1/organizations/factory-default", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json",
        },
      }).then((res) => res.json()),
    onSuccess: () =>
      alert("Factory default reset completed. All data has been erased."),
  });

  const handleFactoryDefault = () => {
    if (
      window.confirm(
        "Are you sure? This will delete ALL data in the entire app, including all organizations and licenses. This action cannot be undone.",
      )
    ) {
      factoryResetMutation.mutate();
    }
  };

  return (
    <ProtectedPage
      moduleKey="admin"
      action="write"
      customCheck={(pc) => pc.checkIsSuperAdmin()}
      accessDeniedMessage="Only super admins can access data management"
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Data Management
        </Typography>
        <Alert severity="warning" sx={{ mb: 2 }}>
          As super admin, you can perform a factory default reset which erases all app data.
          This operation requires special permissions and cannot be undone.
        </Alert>
        <Button variant="contained" color="error" onClick={handleFactoryDefault}>
          Factory Default - Reset Entire App
        </Button>
      </Box>
    </ProtectedPage>
  );
};

export default DataManagement;
