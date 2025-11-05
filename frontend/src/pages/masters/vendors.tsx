// frontend/src/pages/masters/vendors.tsx
import React, { useState, useCallback, useMemo, useEffect } from "react";
import { useRouter } from "next/router";
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  TableSortLabel,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Email,
  Phone,
  Search as SearchIcon,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as masterDataService from "../../services/masterService";
import ExcelImportExport from "../../components/ExcelImportExport";
import { useCompany } from "../../context/CompanyContext";
import AddVendorModal from "../../components/AddVendorModal";
import { ProtectedPage } from "../../components/ProtectedPage";

const VendorsPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isCompanySetupNeeded, isLoading: companyLoading, company, error: companyError } = useCompany();
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [editVendor, setEditVendor] = useState<any | null>(null);
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const sortBy = "name";
  const queryClient = useQueryClient();

  const vendorsEnabled = !isCompanySetupNeeded && !companyLoading;

  const { data: vendors, isLoading: vendorsLoading, error: vendorsError } = useQuery({
    queryKey: ["vendors"],
    queryFn: () => masterDataService.getVendors(),
    enabled: vendorsEnabled,
  });

  const filteredAndSortedVendors = useMemo(() => {
    if (!vendors) {
      return [];
    }
    const filtered = vendors.filter(
      (vendor: any) =>
        vendor.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vendor.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vendor.contact_person?.toLowerCase().includes(searchTerm.toLowerCase()),
    );
    if (sortBy === "name") {
      filtered.sort((a: any, b: any) => {
        const nameA = a.name?.toLowerCase() || "";
        const nameB = b.name?.toLowerCase() || "";
        if (sortOrder === "asc") {
          return nameA.localeCompare(nameB);
        } else {
          return nameB.localeCompare(nameB);
        }
      });
    }
    return filtered;
  }, [vendors, searchTerm, sortBy, sortOrder]);

  const handleSort = () => {
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  };

  const handleVendorAdd = async (vendorData: any) => {
    setAddVendorLoading(true);
    try {
      // Validate required fields
      const requiredFields = ['name', 'contact_number', 'address1', 'city', 'state', 'pin_code', 'state_code'];
      for (const field of requiredFields) {
        if (!vendorData[field] || String(vendorData[field]).trim() === '') {
          throw new Error(`${field.replace('_', ' ')} is required`);
        }
      }
      // Add organization_id from company context
      const vendorDataWithOrg = {
        ...vendorData,
        organization_id: company?.organization_id,
      };
      const response = await masterDataService.createVendor(vendorDataWithOrg);
      const newVendor = response;
      queryClient.setQueryData(["vendors"], (old: any) =>
        old ? [...old, newVendor] : [newVendor],
      );
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
      setShowAddVendorModal(false);
      alert("Vendor added successfully!");
    } catch (error: any) {
      console.error("Error adding vendor", error);
      let errorMsg = "Error adding vendor";
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((err: any) => `${err.loc ? err.loc.join(' -> ') + ': ' : ''}${err.msg || err}`).join(", ");
        } else if (typeof detail === "string") {
          errorMsg = detail;
        } else {
          errorMsg = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMsg = error.message;
      }
      setErrorMessage(errorMsg);
    } finally {
      setAddVendorLoading(false);
    }
  };

  const handleVendorUpdate = async (vendorData: any) => {
    if (!editVendor?.id) return;
    setAddVendorLoading(true);
    try {
      // Validate required fields
      const requiredFields = ['name', 'contact_number', 'address1', 'city', 'state', 'pin_code', 'state_code'];
      for (const field of requiredFields) {
        if (!vendorData[field] || String(vendorData[field]).trim() === '') {
          throw new Error(`${field.replace('_', ' ')} is required`);
        }
      }
      // Add organization_id from company context
      const vendorDataWithOrg = {
        ...vendorData,
        organization_id: company?.organization_id,
      };
      const response = await masterDataService.updateVendor(editVendor.id, vendorDataWithOrg);
      queryClient.setQueryData(["vendors"], (old: any) =>
        old ? old.map((v: any) => (v.id === editVendor.id ? response : v)) : [response],
      );
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
      setShowAddVendorModal(false);
      setEditVendor(null);
      alert("Vendor updated successfully!");
    } catch (error: any) {
      console.error("Error updating vendor", error);
      let errorMsg = "Error updating vendor";
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((err: any) => `${err.loc ? err.loc.join(' -> ') + ': ' : ''}${err.msg || err}`).join(", ");
        } else if (typeof detail === "string") {
          errorMsg = detail;
        } else {
          errorMsg = JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMsg = error.message;
      }
      setErrorMessage(errorMsg);
    } finally {
      setAddVendorLoading(false);
    }
  };

  const deleteItemMutation = useMutation({
    mutationFn: (id: number) => masterDataService.deleteVendor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
    },
    onError: (error: any) => {
      console.error("Error deleting vendor", error);
      setErrorMessage(
        error.response?.data?.detail || "Failed to delete vendor",
      );
    },
  });

  const openAddVendorModal = useCallback(() => {
    setErrorMessage("");
    setEditVendor(null);
    setShowAddVendorModal(true);
  }, []);

  const openEditVendorModal = useCallback((vendor: any) => {
    setErrorMessage("");
    setEditVendor(vendor);
    setShowAddVendorModal(true);
  }, []);

  React.useEffect(() => {
    if (action === "add") {
      openAddVendorModal();
    }
  }, [action, openAddVendorModal]);

  useEffect(() => {
    console.log("[VendorsPage] Company setup needed:", isCompanySetupNeeded);
    console.log("[VendorsPage] Company loading:", companyLoading);
    console.log("[VendorsPage] Vendors query enabled:", vendorsEnabled);
    console.log("[VendorsPage] Company data:", company);
    console.log("[VendorsPage] Company error:", companyError);
    console.log("[VendorsPage] Vendors data:", vendors);
    console.log("[VendorsPage] Vendors loading:", vendorsLoading);
    console.log("[VendorsPage] Vendors error:", vendorsError);
  }, [isCompanySetupNeeded, companyLoading, vendorsEnabled, company, companyError, vendors, vendorsLoading, vendorsError]);

  useEffect(() => {
    if (isCompanySetupNeeded && !companyLoading) {
      console.log("[VendorsPage] Redirecting to company setup as setup is needed");
      router.push("/masters/company-details");
    }
  }, [isCompanySetupNeeded, companyLoading, router]);

  if (companyLoading || vendorsLoading) {
    return <div>Loading...</div>;
  }

  if (isCompanySetupNeeded) {
    return <div>Please complete company setup first to view vendors.</div>;
  }

  if (vendorsError) {
    return <div>Error loading vendors: {vendorsError.message}</div>;
  }

  return (
    <ProtectedPage moduleKey="masters" action="read">
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom>
            Vendor Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openAddVendorModal}
            sx={{ ml: 2 }}
          >
            Add Vendor
          </Button>
        </Box>
        {errorMessage && (
          <Box sx={{ mb: 2 }}>
            <Alert severity="error">{errorMessage}</Alert>
          </Box>
        )}
        <Paper sx={{ p: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">All Vendors</Typography>
            <ExcelImportExport
              data={vendors || []}
              entity="Vendors"
              onImport={masterDataService.bulkImportVendors}
            />
          </Box>
          <Box sx={{ mb: 3 }}>
            <TextField
              placeholder="Search vendors by name, email, or contact person..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ width: 400 }}
            />
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === "name"}
                      direction={sortBy === "name" ? sortOrder : "asc"}
                      onClick={handleSort}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>GST Number</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredAndSortedVendors?.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {item.address1}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Phone
                          sx={{ fontSize: 16, mr: 1, color: "text.secondary" }}
                        />
                        {item.contact_number}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Email
                          sx={{ fontSize: 16, mr: 1, color: "text.secondary" }}
                        />
                        {item.email || "N/A"}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {item.city}, {item.state}
                    </TableCell>
                    <TableCell>{item.gst_number || "N/A"}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.is_active ? "Active" : "Inactive"}
                        color={item.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        onClick={() => openEditVendorModal(item)}
                        size="small"
                        title="Edit Vendor"
                      >
                        <Edit />
                      </IconButton>
                      <IconButton
                        onClick={() => deleteItemMutation.mutate(item.id)}
                        size="small"
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {filteredAndSortedVendors.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      No vendors found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        <AddVendorModal
          open={showAddVendorModal}
          onClose={() => {
            setShowAddVendorModal(false);
            setEditVendor(null);
          }}
          onSave={editVendor ? handleVendorUpdate : handleVendorAdd}
          loading={addVendorLoading}
          initialData={editVendor || {}}
        />
      </Box>
    </Container>
    </ProtectedPage>
  );
};

export default VendorsPage;