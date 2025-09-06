// frontend/src/pages/masters/vendors.tsx
import React, { useState, useCallback, useMemo } from "react";
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
import { masterDataService } from "../../services/masterService";
import ExcelImportExport from "../../components/ExcelImportExport";
import { bulkImportVendors } from "../../services/masterService";
import { useAuth } from "../../context/AuthContext";
import AddVendorModal from "../../components/AddVendorModal";

const VendorsPage: React.FC = () => {
  const router = useRouter();
  const { action } = router.query;
  const { isOrgContextReady } = useAuth();
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [editVendor, setEditVendor] = useState<any | null>(null);
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const sortBy = "name";
  const queryClient = useQueryClient();

  const { data: vendors, isLoading } = useQuery({
    queryKey: ["vendors"],
    queryFn: () => masterDataService.getVendors(),
    enabled: isOrgContextReady,
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
          return nameB.localeCompare(nameA);
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
      const response = await masterDataService.createVendor(vendorData);
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
          errorMsg = detail.map((err: any) => err.msg || err).join(", ");
        } else if (typeof detail === "string") {
          errorMsg = detail;
        }
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
      const response = await masterDataService.updateVendor(editVendor.id, vendorData);
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
          errorMsg = detail.map((err: any) => err.msg || err).join(", ");
        } else if (typeof detail === "string") {
          errorMsg = detail;
        }
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

  if (!isOrgContextReady) {
    return <div>Loading...</div>;
  }

  return (
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
              onImport={bulkImportVendors}
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
          onAdd={editVendor ? handleVendorUpdate : handleVendorAdd}
          loading={addVendorLoading}
          initialData={editVendor} // Pass full vendor data for editing
        />
      </Box>
    </Container>
  );
};

export default VendorsPage;