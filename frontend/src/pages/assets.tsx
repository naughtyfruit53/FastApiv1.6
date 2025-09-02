// pages/assets.tsx
// Asset Management page with comprehensive asset lifecycle management
import React, { useState } from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Tooltip,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  Build as BuildIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import { useAuth } from "../hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { assetService } from "../services/assetService";
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
      id={`asset-tabpanel-${index}`}
      aria-labelledby={`asset-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}
const AssetManagementPage: NextPage = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  // Fetch dashboard summary
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ["assetDashboard"],
    queryFn: assetService.getDashboardSummary,
    enabled: !!user,
  });
  // Fetch assets
  const { data: assets, isLoading: assetsLoading } = useQuery({
    queryKey: ["assets"],
    queryFn: () => assetService.getAssets(),
    enabled: !!user,
  });
  // Fetch maintenance schedules
  const { data: maintenanceSchedules, isLoading: schedulesLoading } = useQuery({
    queryKey: ["maintenanceSchedules"],
    queryFn: () => assetService.getMaintenanceSchedules(),
    enabled: !!user,
  });
  // Fetch due maintenance
  const { data: dueMaintenance, isLoading: dueMaintenanceLoading } = useQuery({
    queryKey: ["dueMaintenance"],
    queryFn: () => assetService.getDueMaintenance(),
    enabled: !!user,
  });
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "success";
      case "maintenance":
        return "warning";
      case "inactive":
        return "default";
      case "retired":
        return "error";
      default:
        return "default";
    }
  };
  const getConditionColor = (condition: string) => {
    switch (condition.toLowerCase()) {
      case "excellent":
        return "success";
      case "good":
        return "success";
      case "fair":
        return "warning";
      case "poor":
        return "error";
      case "critical":
        return "error";
      default:
        return "default";
    }
  };
  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Please log in to access Asset Management.
        </Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <SettingsIcon color="primary" />
          Asset Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive asset lifecycle management, maintenance scheduling, and
          depreciation tracking
        </Typography>
      </Box>
      {/* Dashboard Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Assets
                  </Typography>
                  <Typography variant="h4">
                    {dashboardLoading ? (
                      <CircularProgress size={24} />
                    ) : (
                      dashboardData?.total_assets || 0
                    )}
                  </Typography>
                </Box>
                <SettingsIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Assets
                  </Typography>
                  <Typography variant="h4">
                    {dashboardLoading ? (
                      <CircularProgress size={24} />
                    ) : (
                      dashboardData?.active_assets || 0
                    )}
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Due Maintenance
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {dashboardLoading ? (
                      <CircularProgress size={24} />
                    ) : (
                      dashboardData?.due_maintenance || 0
                    )}
                  </Typography>
                </Box>
                <ScheduleIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overdue
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {dashboardLoading ? (
                      <CircularProgress size={24} />
                    ) : (
                      dashboardData?.overdue_maintenance || 0
                    )}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Asset Value
                  </Typography>
                  <Typography variant="h6">
                    {dashboardLoading ? (
                      <CircularProgress size={24} />
                    ) : (
                      `$${(dashboardData?.total_asset_value || 0).toLocaleString()}`
                    )}
                  </Typography>
                </Box>
                <AssessmentIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Asset Register" />
          <Tab label="Maintenance Schedules" />
          <Tab label="Maintenance Records" />
          <Tab label="Due Maintenance" />
          <Tab label="Reports" />
        </Tabs>
      </Paper>
      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        {/* Assets List */}
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
          <Typography variant="h6">Asset Register</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            // TODO: Define or import setOpenDialog
            onClick={() => setOpenDialog("create")}
          >
            Add Asset
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Asset Code</TableCell>
                <TableCell>Asset Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Condition</TableCell>
                <TableCell>Purchase Cost</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assetsLoading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                assets?.map((asset: any) => (
                  <TableRow key={asset.id}>
                    <TableCell>{asset.asset_code}</TableCell>
                    <TableCell>{asset.asset_name}</TableCell>
                    <TableCell>{asset.category}</TableCell>
                    <TableCell>{asset.location || "-"}</TableCell>
                    <TableCell>
                      <Chip
                        label={asset.status}
                        color={getStatusColor(asset.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={asset.condition}
                        color={getConditionColor(asset.condition) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {asset.purchase_cost
                        ? `$${asset.purchase_cost.toLocaleString()}`
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => {
                            // TODO: Define or import setSelectedAsset
                            setSelectedAsset(asset);
                            // TODO: Define or import setOpenDialog
                            setOpenDialog("edit");
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Maintenance">
                        <IconButton
                          size="small"
                          onClick={() => {
                            // TODO: Define or import setSelectedAsset
                            setSelectedAsset(asset);
                            // TODO: Define or import setOpenDialog
                            setOpenDialog("maintenance");
                          }}
                        >
                          <BuildIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        {/* Maintenance Schedules */}
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
          <Typography variant="h6">Maintenance Schedules</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            // TODO: Define or import setOpenDialog
            onClick={() => setOpenDialog("create")}
          >
            Add Schedule
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Schedule Name</TableCell>
                <TableCell>Asset</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Next Due</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {schedulesLoading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                maintenanceSchedules?.map((schedule: any) => (
                  <TableRow key={schedule.id}>
                    <TableCell>{schedule.schedule_name}</TableCell>
                    <TableCell>{schedule.asset_id}</TableCell>
                    <TableCell>
                      <Chip
                        label={schedule.maintenance_type}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{schedule.frequency_type}</TableCell>
                    <TableCell>
                      {schedule.next_due_date
                        ? new Date(schedule.next_due_date).toLocaleDateString()
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={schedule.priority}
                        color={
                          schedule.priority === "high"
                            ? "error"
                            : schedule.priority === "medium"
                              ? "warning"
                              : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={schedule.is_active ? "Active" : "Inactive"}
                        color={schedule.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        {/* Maintenance Records */}
        <Typography variant="h6" sx={{ mb: 2 }}>
          Maintenance Records
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Historical maintenance work orders and records
        </Typography>
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        {/* Due Maintenance */}
        <Typography variant="h6" sx={{ mb: 2 }}>
          Due Maintenance
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Asset</TableCell>
                <TableCell>Schedule</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {dueMaintenanceLoading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                dueMaintenance?.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.asset_id}</TableCell>
                    <TableCell>{item.schedule_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.maintenance_type}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography
                        color={
                          new Date(item.next_due_date) < new Date()
                            ? "error"
                            : "text.primary"
                        }
                      >
                        {new Date(item.next_due_date).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={item.priority}
                        color={
                          item.priority === "high"
                            ? "error"
                            : item.priority === "medium"
                              ? "warning"
                              : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(item.next_due_date) < new Date() ? (
                        <Chip label="Overdue" color="error" size="small" />
                      ) : (
                        <Chip label="Due" color="warning" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Button size="small" variant="outlined">
                        Create Work Order
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={4}>
        {/* Reports */}
        <Typography variant="h6" sx={{ mb: 2 }}>
          Asset Reports
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Asset Depreciation Report
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Calculate and view asset depreciation by period
                </Typography>
                <Button variant="outlined">Generate Report</Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Maintenance Cost Analysis
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Analyze maintenance costs and trends
                </Typography>
                <Button variant="outlined">Generate Report</Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Container>
  );
};
export default AssetManagementPage;
