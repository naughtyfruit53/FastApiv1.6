"use client";
import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  MonetizationOn as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarIcon,
  Assessment as AssessmentIcon,
} from "@mui/icons-material";
import AddCommissionModal from "../../components/AddCommissionModal";
interface Commission {
  id: number;
  sales_person_id: number;
  sales_person_name?: string;
  opportunity_id?: number;
  lead_id?: number;
  commission_type: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount: number;
  commission_date: string;
  payment_status: string;
  notes?: string;
  created_at: string;
}
const CommissionTracking: React.FC = () => {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  // Fetch commissions from backend
  const fetchCommissions = async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Implement commission service when backend endpoint is available
      // For now, show empty state
      setCommissions([]);
    } catch (err) {
      console.error("Error fetching commissions:", err);
      setError("Failed to load commissions. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchCommissions();
  }, []);
  const handleAddCommission = async (commissionData: any) => {
    try {
      setAddLoading(true);
      // TODO: Implement commission creation when backend endpoint is available
      console.log("Commission data:", commissionData);
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // Mock adding to state for now
      const newCommission: Commission = {
        id: Date.now(),
        ...commissionData,
        created_at: new Date().toISOString(),
      };
      setCommissions((prev) => [newCommission, ...prev]);
      setDialogOpen(false);
    } catch (err) {
      console.error("Error adding commission:", err);
      throw err;
    } finally {
      setAddLoading(false);
    }
  };
  const filteredCommissions = commissions.filter((commission) => {
    const matchesSearch =
      (commission.sales_person_name || "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      (commission.notes || "").toLowerCase().includes(searchTerm.toLowerCase());
    // TODO: Define or import filterStatus
    const matchesStatus =
      filterStatus === "all" || commission.payment_status === filterStatus;
    return matchesSearch && matchesStatus;
  });
  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "warning";
      case "approved":
        return "info";
      case "paid":
        return "success";
      case "rejected":
        return "error";
      case "on_hold":
        return "default";
      default:
        return "default";
    }
  };
  const totalCommissions = commissions.reduce(
    (sum, c) => sum + (c.commission_amount || 0),
    0,
  );
  const pendingCommissions = commissions
    .filter((c) => c.payment_status === "pending")
    .reduce((sum, c) => sum + (c.commission_amount || 0), 0);
  const paidCommissions = commissions
    .filter((c) => c.payment_status === "paid")
    .reduce((sum, c) => sum + (c.commission_amount || 0), 0);
  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }
  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Commission Tracking
      </Typography>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <MoneyIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Commissions</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                ${totalCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <CalendarIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Pending</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                ${pendingCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Awaiting payment
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <AssessmentIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Paid</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                ${paidCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed payments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Records</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {commissions.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total records
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Actions Bar */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <TextField
          placeholder="Search commissions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Add Commission
        </Button>
      </Box>
      {/* Commissions Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Sales Person</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Base Amount</TableCell>
                <TableCell align="right">Rate/Amount</TableCell>
                <TableCell align="right">Commission</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCommissions.map((commission) => (
                <TableRow key={commission.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2">
                        User ID: {commission.sales_person_id}
                      </Typography>
                      {commission.sales_person_name && (
                        <Typography variant="body2" color="text.secondary">
                          {commission.sales_person_name}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={commission.commission_type
                        .replace("_", " ")
                        .toUpperCase()}
                      size="small"
                      variant="outlined"
                      sx={{ textTransform: "capitalize" }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    ${commission.base_amount.toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    {commission.commission_type === "percentage"
                      ? `${commission.commission_rate}%`
                      : `$${commission.commission_amount?.toLocaleString() || 0}`}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" color="primary">
                      $
                      {(
                        commission.commission_amount ||
                        (commission.commission_rate
                          ? (commission.base_amount *
                              commission.commission_rate) /
                            100
                          : 0)
                      ).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {new Date(commission.commission_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={commission.payment_status
                        .replace("_", " ")
                        .toUpperCase()}
                      color={getStatusColor(commission.payment_status) as any}
                      size="small"
                      sx={{ textTransform: "capitalize" }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <IconButton size="small" title="View">
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" title="Edit">
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {filteredCommissions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ py: 4 }}
                    >
                      {commissions.length === 0
                        ? "No commission records found. Start by adding your first commission record!"
                        : "No records match your search criteria."}
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
      {/* Add Commission Modal */}
      <AddCommissionModal
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onAdd={handleAddCommission}
        loading={addLoading}
      />
    </Container>
  );
};
export default CommissionTracking;
