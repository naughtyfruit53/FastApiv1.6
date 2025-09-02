import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Alert,
  Tooltip,
} from "@mui/material";
import {
  Add,
  Edit,
  Business,
  PersonAdd,
  AdminPanelSettings,
  Delete,
  Groups,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companyService } from "../../services/authService";
import CompanyDetailsModal from "../../components/CompanyDetailsModal";
interface Company {
  id: number;
  name: string;
  address1: string;
  city: string;
  state: string;
  gst_number?: string;
  business_type?: string;
  industry?: string;
  created_at: string;
}
interface UserCompanyAssignment {
  id: number;
  user_id: number;
  company_id: number;
  is_active: boolean;
  is_company_admin: boolean;
  user_email: string;
  user_full_name: string;
}
const MultiCompanyManagement: React.FC = () => {
  const [openCompanyModal, setOpenCompanyModal] = useState(false);
  const [openUserAssignModal, setOpenUserAssignModal] = useState(false);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(
    null,
  );
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const queryClient = useQueryClient();
  // Fetch all companies
  const {
    data: companies,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["companies"],
    queryFn: companyService.getCompanies,
  });
  // Fetch organization info to check max_companies
  const { data: orgInfo } = useQuery({
    queryKey: ["organization-info"],
    queryFn: companyService.getOrganizationInfo,
  });
  // Fetch users assigned to selected company
  const { data: companyUsers } = useQuery({
    queryKey: ["company-users", selectedCompanyId],
    queryFn: () =>
      selectedCompanyId
        ? companyService.getCompanyUsers(selectedCompanyId)
        : Promise.resolve([]),
    enabled: !!selectedCompanyId,
  });

  // Create company mutation
  const createCompanyMutation = useMutation({
    mutationFn: companyService.createCompany,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      setOpenCompanyModal(false);
    },
  });

  // Assign user to company mutation
  const assignUserMutation = useMutation({
    mutationFn: ({
      companyId,
      userId,
      isAdmin,
    }: {
      companyId: number;
      userId: number;
      isAdmin: boolean;
    }) =>
      companyService.assignUserToCompany(companyId, {
        user_id: userId,
        company_id: companyId,
        is_company_admin: isAdmin,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["company-users", selectedCompanyId],
      });
    },
  });
  const updateUserAssignmentMutation = useMutation({
    mutationFn: ({
      companyId,
      userId,
      updates,
    }: {
      companyId: number;
      userId: number;
      updates: any;
    }) =>
      companyService.updateUserCompanyAssignment(companyId, userId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["company-users", selectedCompanyId],
      });
    },
  });
  const removeUserMutation = useMutation({
    mutationFn: ({
      companyId,
      userId,
    }: {
      companyId: number;
      userId: number;
    }) => companyService.removeUserFromCompany(companyId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["company-users", selectedCompanyId],
      });
    },
  });
  const handleCreateCompany = () => {
    setSelectedCompany(null);
    setOpenCompanyModal(true);
  };
  const handleEditCompany = (company: Company) => {
    setSelectedCompany(company);
    setOpenCompanyModal(true);
  };
  const handleManageUsers = (company: Company) => {
    setSelectedCompany(company);
    setSelectedCompanyId(company.id);
    setOpenUserAssignModal(true);
  };
  const handleToggleAdmin = (assignment: UserCompanyAssignment) => {
    updateUserAssignmentMutation.mutate({
      companyId: assignment.company_id,
      userId: assignment.user_id,
      updates: { is_company_admin: !assignment.is_company_admin },
    });
  };
  const handleRemoveUser = (assignment: UserCompanyAssignment) => {
    if (
      window.confirm(
        `Remove ${assignment.user_full_name} from ${selectedCompany?.name}?`,
      )
    ) {
      removeUserMutation.mutate({
        companyId: assignment.company_id,
        userId: assignment.user_id,
      });
    }
  };
  const canCreateCompany = () => {
    if (!companies || !orgInfo) {
      return false;
    }
    return companies.length < (orgInfo.max_companies || 1);
  };
  if (isLoading) {
    return <Typography>Loading companies...</Typography>;
  }
  if (error) {
    return <Alert severity="error">Failed to load companies</Alert>;
  }
  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h5">Company Management</Typography>
        <Box>
          <Typography variant="body2" color="text.secondary" mr={2}>
            {companies?.length || 0} / {orgInfo?.max_companies || 1} companies
          </Typography>
          {canCreateCompany() && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateCompany}
            >
              Add Company
            </Button>
          )}
        </Box>
      </Box>
      {!canCreateCompany() && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          You have reached the maximum number of companies (
          {orgInfo?.max_companies || 1}) for your organization. Contact your
          administrator to increase the limit.
        </Alert>
      )}
      <Grid container spacing={3}>
        {companies?.map((company: Company) => (
          <Grid item xs={12} md={6} lg={4} key={company.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Business color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {company.name}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {company.address1}, {company.city}, {company.state}
                </Typography>
                {company.business_type && (
                  <Chip
                    label={company.business_type}
                    size="small"
                    sx={{ mt: 1, mr: 1 }}
                  />
                )}
                {company.industry && (
                  <Chip
                    label={company.industry}
                    size="small"
                    sx={{ mt: 1 }}
                    variant="outlined"
                  />
                )}
                {company.gst_number && (
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    GST: {company.gst_number}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEditCompany(company)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  startIcon={<Groups />}
                  onClick={() => handleManageUsers(company)}
                >
                  Users
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      {(!companies || companies.length === 0) && (
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <Business sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No companies found
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Create your first company to get started with managing your
            organization.
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateCompany}
          >
            Create Company
          </Button>
        </Paper>
      )}
      {/* Company Creation/Edit Modal */}
      <CompanyDetailsModal
        open={openCompanyModal}
        onClose={() => setOpenCompanyModal(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ["companies"] });
          setOpenCompanyModal(false);
        }}
        companyData={selectedCompany}
        mode={selectedCompany ? "edit" : "create"}
      />
      {/* User Assignment Modal */}
      <Dialog
        open={openUserAssignModal}
        onClose={() => setOpenUserAssignModal(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Manage Users - {selectedCompany?.name}</DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Button
              variant="outlined"
              startIcon={<PersonAdd />}
              onClick={() => {
                /* TODO: Open user assignment dialog */
              }}
            >
              Assign User
            </Button>
          </Box>
          <List>
            {companyUsers?.map((assignment: UserCompanyAssignment) => (
              <ListItem key={assignment.id}>
                <ListItemText
                  primary={assignment.user_full_name}
                  secondary={assignment.user_email}
                />
                <ListItemSecondaryAction>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Tooltip title="Company Admin">
                      <IconButton
                        color={
                          assignment.is_company_admin ? "primary" : "default"
                        }
                        onClick={() => handleToggleAdmin(assignment)}
                      >
                        <AdminPanelSettings />
                      </IconButton>
                    </Tooltip>
                    <IconButton
                      color="error"
                      onClick={() => handleRemoveUser(assignment)}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
          {(!companyUsers || companyUsers.length === 0) && (
            <Typography
              variant="body2"
              color="text.secondary"
              textAlign="center"
              py={3}
            >
              No users assigned to this company
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUserAssignModal(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
export default MultiCompanyManagement;
