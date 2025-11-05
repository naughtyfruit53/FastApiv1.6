import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Avatar,
  Stack,
} from "@mui/material";
import { Edit, Business } from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companyService } from "../../services/authService";
import CompanyDetailsModal from "../../components/CompanyDetailsModal";
import Grid from "@mui/material/Grid";
import { ProtectedPage } from "../../components/ProtectedPage";

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const CompanyDetails: React.FC = () => {
  const [openModal, setOpenModal] = useState(false);
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["company"],
    queryFn: companyService.getCurrentCompany,
  });

  const createCompanyMutation = useMutation({
    mutationFn: companyService.createCompany,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["company"] });
    },
  });
  const handleOpenModal = () => setOpenModal(true);
  const handleCloseModal = () => setOpenModal(false);
  const handleSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ["company"] });
    handleCloseModal();
  };
  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }
  if (isError || !data || !data.id) {
    console.error("Failed to fetch company details or data is invalid");
    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Company Details
        </Typography>
        <Alert severity="info">
          No company details found. Please set up your company information.
        </Alert>
        <Button
          variant="contained"
          startIcon={<Edit />}
          sx={{ mt: 3 }}
          onClick={handleOpenModal}
        >
          Set Up Company Details
        </Button>
        <CompanyDetailsModal
          open={openModal}
          onClose={handleCloseModal}
          onSuccess={handleSuccess}
          isRequired={false}
          mode="create"
        />
      </Box>
    );
  }
  return (
    <ProtectedPage moduleKey="masters" action="read">
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Company Details
      </Typography>
      <Paper sx={{ p: 2 }}>
        {/* Company Logo and Basic Info */}
        <Stack direction="row" spacing={3} alignItems="center" sx={{ mb: 3 }}>
          <Avatar
            src={
              data?.logo_path && data?.id
                ? `${API_URL}${data.logo_path}`
                : undefined
            }
            sx={{
              width: 80,
              height: 80,
              bgcolor: "grey.200",
              border: "2px solid",
              borderColor: "grey.300",
            }}
          >
            {!data?.logo_path && (
              <Business sx={{ fontSize: 40, color: "grey.500" }} />
            )}
          </Avatar>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: "bold" }}>
              {data?.name || "N/A"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {data?.business_type || "N/A"} - {data?.industry || "N/A"}
            </Typography>
          </Box>
        </Stack>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">Business Type</Typography>
            <Typography>{data?.business_type || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">Industry</Typography>
            <Typography>{data?.industry || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">Website</Typography>
            <Typography>{data?.website || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">GST Number</Typography>
            <Typography>{data?.gst_number || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">PAN Number</Typography>
            <Typography>{data?.pan_number || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">Primary Email</Typography>
            <Typography>{data?.email || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">Primary Phone</Typography>
            <Typography>{data?.contact_number || "N/A"}</Typography>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Typography variant="subtitle2">State</Typography>
            <Typography>
              {data?.state || "N/A"} ({data?.state_code || "N/A"})
            </Typography>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2">Address</Typography>
            <Typography>
              {data?.address1 || ""}
              {data?.address2 ? `, ${data?.address2}` : ""},{" "}
              {data?.city || "N/A"}, {data?.state || "N/A"} -{" "}
              {data?.pin_code || "N/A"}
            </Typography>
          </Grid>
        </Grid>
        <Button
          variant="contained"
          startIcon={<Edit />}
          sx={{ mt: 3 }}
          onClick={handleOpenModal}
        >
          Edit Company Details
        </Button>
      </Paper>
      <CompanyDetailsModal
        open={openModal}
        onClose={handleCloseModal}
        onSuccess={handleSuccess}
        isRequired={false}
        companyData={data}
        mode="edit"
      />
    </Box>
    </ProtectedPage>
  );
};
export default CompanyDetails;