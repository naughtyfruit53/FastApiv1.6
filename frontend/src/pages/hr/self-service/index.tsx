// pages/hr/self-service/index.tsx
// Employee Self-Service Portal - Leave Requests, Attendance, Payslips
import React, { useState, useEffect } from "react";
import { NextPage } from "next";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  EventNote as LeaveIcon,
  AccessTime as AttendanceIcon,
  Receipt as PayslipIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  CheckCircle as ApprovedIcon,
  HourglassEmpty as PendingIcon,
  Cancel as RejectedIcon,
  PlayArrow as ClockInIcon,
  Stop as ClockOutIcon,
} from "@mui/icons-material";
import { useAuth } from "../../../hooks/useAuth";
import {
  hrService,
  LeaveApplication,
  LeaveType,
  AttendanceRecord,
} from "../../../services";
import { ProtectedPage } from "../../../components/ProtectedPage";

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
      id={`self-service-tabpanel-${index}`}
      aria-labelledby={`self-service-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SelfServicePortal: NextPage = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Leave state
  const [leaveApplications, setLeaveApplications] = useState<LeaveApplication[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeaveType[]>([]);
  const [leaveDialogOpen, setLeaveDialogOpen] = useState(false);
  const [newLeave, setNewLeave] = useState({
    leave_type_id: 0,
    start_date: "",
    end_date: "",
    reason: "",
    is_half_day: false,
  });

  // Attendance state
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [clockedIn, setClockedIn] = useState(false);
  const [currentAttendance, setCurrentAttendance] = useState<AttendanceRecord | null>(null);

  useEffect(() => {
    fetchData();
  }, [tabValue]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      if (tabValue === 0) {
        // Fetch leave data
        const [applications, types] = await Promise.all([
          hrService.getLeaveApplications(undefined, undefined, undefined, undefined, 0, 50),
          hrService.getLeaveTypes(true),
        ]);
        setLeaveApplications(applications);
        setLeaveTypes(types);
      } else if (tabValue === 1) {
        // Fetch attendance data
        const records = await hrService.getAttendanceRecords(
          undefined,
          undefined,
          undefined,
          undefined,
          0,
          30
        );
        setAttendanceRecords(records);
        
        // Check if clocked in today
        const today = new Date().toISOString().split("T")[0];
        const todayRecord = records.find(r => r.attendance_date === today);
        if (todayRecord) {
          setCurrentAttendance(todayRecord);
          setClockedIn(!!todayRecord.check_in_time && !todayRecord.check_out_time);
        }
      }
    } catch (err: unknown) {
      console.error("Error fetching data:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to load data";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      // Calculate total days
      const start = new Date(newLeave.start_date);
      const end = new Date(newLeave.end_date);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      const totalDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

      await hrService.createLeaveApplication({
        employee_id: user?.id || 0,
        leave_type_id: newLeave.leave_type_id,
        start_date: newLeave.start_date,
        end_date: newLeave.end_date,
        total_days: newLeave.is_half_day ? 0.5 : totalDays,
        reason: newLeave.reason,
        is_half_day: newLeave.is_half_day,
      });

      setSuccess("Leave application submitted successfully");
      setLeaveDialogOpen(false);
      setNewLeave({
        leave_type_id: 0,
        start_date: "",
        end_date: "",
        reason: "",
        is_half_day: false,
      });
      fetchData();
    } catch (err: unknown) {
      console.error("Error submitting leave:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to submit leave application";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async () => {
    try {
      setLoading(true);
      setError(null);

      const record = await hrService.clockIn({
        employee_id: user?.id || 0,
        work_type: "office",
      });

      setCurrentAttendance(record);
      setClockedIn(true);
      setSuccess("Clocked in successfully");
      fetchData();
    } catch (err: unknown) {
      console.error("Error clocking in:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to clock in";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClockOut = async () => {
    try {
      setLoading(true);
      setError(null);

      const record = await hrService.clockOut({
        employee_id: user?.id || 0,
      });

      setCurrentAttendance(record);
      setClockedIn(false);
      setSuccess("Clocked out successfully");
      fetchData();
    } catch (err: unknown) {
      console.error("Error clocking out:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to clock out";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case "approved":
        return <Chip icon={<ApprovedIcon />} label="Approved" color="success" size="small" />;
      case "pending":
        return <Chip icon={<PendingIcon />} label="Pending" color="warning" size="small" />;
      case "rejected":
        return <Chip icon={<RejectedIcon />} label="Rejected" color="error" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const getAttendanceStatusChip = (status: string) => {
    switch (status) {
      case "present":
        return <Chip label="Present" color="success" size="small" />;
      case "absent":
        return <Chip label="Absent" color="error" size="small" />;
      case "half_day":
        return <Chip label="Half Day" color="warning" size="small" />;
      case "on_leave":
        return <Chip label="On Leave" color="info" size="small" />;
      case "late":
        return <Chip label="Late" color="warning" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  return (
    <ProtectedPage module="hr" action="read">
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Employee Self-Service Portal
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Paper sx={{ width: "100%" }}>
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<LeaveIcon />} label="Leave Requests" />
            <Tab icon={<AttendanceIcon />} label="Attendance" />
            <Tab icon={<PayslipIcon />} label="Payslips" />
          </Tabs>

          {/* Leave Requests Tab */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
              <Typography variant="h6">My Leave Applications</Typography>
              <Box>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={fetchData}
                  sx={{ mr: 1 }}
                >
                  Refresh
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setLeaveDialogOpen(true)}
                >
                  Apply Leave
                </Button>
              </Box>
            </Box>

            {loading ? (
              <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Leave Type</TableCell>
                      <TableCell>From</TableCell>
                      <TableCell>To</TableCell>
                      <TableCell>Days</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Applied On</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {leaveApplications.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          No leave applications found
                        </TableCell>
                      </TableRow>
                    ) : (
                      leaveApplications.map((leave) => (
                        <TableRow key={leave.id}>
                          <TableCell>
                            {leaveTypes.find((t) => t.id === leave.leave_type_id)?.name || "-"}
                          </TableCell>
                          <TableCell>{leave.start_date}</TableCell>
                          <TableCell>{leave.end_date}</TableCell>
                          <TableCell>{leave.total_days}</TableCell>
                          <TableCell>{leave.reason}</TableCell>
                          <TableCell>{getStatusChip(leave.status)}</TableCell>
                          <TableCell>
                            {new Date(leave.applied_date).toLocaleDateString()}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          {/* Attendance Tab */}
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              {/* Clock In/Out Card */}
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Today&apos;s Attendance
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {new Date().toLocaleDateString("en-US", {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </Typography>

                    {currentAttendance ? (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          Check In: {currentAttendance.check_in_time || "-"}
                        </Typography>
                        <Typography variant="body2">
                          Check Out: {currentAttendance.check_out_time || "-"}
                        </Typography>
                        {currentAttendance.total_hours && (
                          <Typography variant="body2">
                            Total Hours: {currentAttendance.total_hours}
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" sx={{ mt: 2 }}>
                        Not clocked in yet
                      </Typography>
                    )}

                    <Box sx={{ mt: 3 }}>
                      {!clockedIn ? (
                        <Button
                          variant="contained"
                          color="success"
                          startIcon={<ClockInIcon />}
                          onClick={handleClockIn}
                          disabled={loading}
                          fullWidth
                        >
                          Clock In
                        </Button>
                      ) : (
                        <Button
                          variant="contained"
                          color="error"
                          startIcon={<ClockOutIcon />}
                          onClick={handleClockOut}
                          disabled={loading}
                          fullWidth
                        >
                          Clock Out
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Attendance History */}
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  Attendance History
                </Typography>
                {loading ? (
                  <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Check In</TableCell>
                          <TableCell>Check Out</TableCell>
                          <TableCell>Hours</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {attendanceRecords.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={5} align="center">
                              No attendance records found
                            </TableCell>
                          </TableRow>
                        ) : (
                          attendanceRecords.map((record) => (
                            <TableRow key={record.id}>
                              <TableCell>{record.attendance_date}</TableCell>
                              <TableCell>{record.check_in_time || "-"}</TableCell>
                              <TableCell>{record.check_out_time || "-"}</TableCell>
                              <TableCell>{record.total_hours || "-"}</TableCell>
                              <TableCell>
                                {getAttendanceStatusChip(record.attendance_status)}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Grid>
            </Grid>
          </TabPanel>

          {/* Payslips Tab */}
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>
              My Payslips
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Payslip downloads will be available once payroll is processed for the period.
            </Alert>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Period</TableCell>
                    <TableCell>Pay Date</TableCell>
                    <TableCell>Gross Pay</TableCell>
                    <TableCell>Deductions</TableCell>
                    <TableCell>Net Pay</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Payslip feature coming soon
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </Paper>

        {/* Leave Application Dialog */}
        <Dialog
          open={leaveDialogOpen}
          onClose={() => setLeaveDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Apply for Leave</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Leave Type</InputLabel>
                  <Select
                    value={newLeave.leave_type_id}
                    label="Leave Type"
                    onChange={(e) =>
                      setNewLeave({ ...newLeave, leave_type_id: Number(e.target.value) })
                    }
                  >
                    {leaveTypes.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="From Date"
                  type="date"
                  value={newLeave.start_date}
                  onChange={(e) =>
                    setNewLeave({ ...newLeave, start_date: e.target.value })
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="To Date"
                  type="date"
                  value={newLeave.end_date}
                  onChange={(e) =>
                    setNewLeave({ ...newLeave, end_date: e.target.value })
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Reason"
                  multiline
                  rows={3}
                  value={newLeave.reason}
                  onChange={(e) =>
                    setNewLeave({ ...newLeave, reason: e.target.value })
                  }
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setLeaveDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleLeaveSubmit}
              disabled={
                loading ||
                !newLeave.leave_type_id ||
                !newLeave.start_date ||
                !newLeave.end_date ||
                !newLeave.reason
              }
            >
              Submit
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </ProtectedPage>
  );
};

export default SelfServicePortal;
