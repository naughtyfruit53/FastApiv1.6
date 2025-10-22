// frontend/src/components/AuditLogViewer.tsx
/**
 * Audit Log Viewer Component
 * Displays audit logs with filtering and search capabilities
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Stack,
} from '@mui/material';
import {
  Refresh,
  FilterList,
  Search,
  Info,
} from '@mui/icons-material';
import { format } from 'date-fns';

export interface AuditLog {
  id: number;
  timestamp: string;
  user: string;
  action: string;
  entity_type: string;
  entity_id: number | string;
  details?: string;
  ip_address?: string;
  status: 'success' | 'failure' | 'warning';
}

interface AuditLogViewerProps {
  logs: AuditLog[];
  loading?: boolean;
  onRefresh?: () => void;
  onPageChange?: (page: number, pageSize: number) => void;
  totalCount?: number;
}

const AuditLogViewer: React.FC<AuditLogViewerProps> = ({
  logs,
  loading = false,
  onRefresh,
  onPageChange,
  totalCount = 0,
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAction, setFilterAction] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filteredLogs, setFilteredLogs] = useState<AuditLog[]>(logs);

  useEffect(() => {
    let result = logs;

    // Search filter
    if (searchTerm) {
      result = result.filter(
        (log) =>
          log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.entity_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.details?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Action filter
    if (filterAction !== 'all') {
      result = result.filter((log) => log.action === filterAction);
    }

    // Status filter
    if (filterStatus !== 'all') {
      result = result.filter((log) => log.status === filterStatus);
    }

    setFilteredLogs(result);
  }, [logs, searchTerm, filterAction, filterStatus]);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    if (onPageChange) {
      onPageChange(newPage, rowsPerPage);
    }
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    if (onPageChange) {
      onPageChange(0, newRowsPerPage);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failure':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  const uniqueActions = Array.from(new Set(logs.map((log) => log.action)));

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {/* Filters and Search */}
      <Box sx={{ p: 2, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Audit Logs
        </Typography>
        
        <TextField
          size="small"
          placeholder="Search logs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
          sx={{ minWidth: 200 }}
        />

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Action</InputLabel>
          <Select
            value={filterAction}
            label="Action"
            onChange={(e) => setFilterAction(e.target.value)}
          >
            <MenuItem value="all">All Actions</MenuItem>
            {uniqueActions.map((action) => (
              <MenuItem key={action} value={action}>
                {action}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filterStatus}
            label="Status"
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="success">Success</MenuItem>
            <MenuItem value="failure">Failure</MenuItem>
            <MenuItem value="warning">Warning</MenuItem>
          </Select>
        </FormControl>

        {onRefresh && (
          <Tooltip title="Refresh">
            <IconButton
              onClick={onRefresh}
              disabled={loading}
              sx={{ minWidth: 44, minHeight: 44 }}
            >
              <Refresh
                sx={{
                  animation: loading ? 'spin 1s linear infinite' : 'none',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {/* Table */}
      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Entity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography color="text.secondary">Loading...</Typography>
                </TableCell>
              </TableRow>
            ) : filteredLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography color="text.secondary">No audit logs found</Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredLogs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      {format(new Date(log.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                    </TableCell>
                    <TableCell>{log.user}</TableCell>
                    <TableCell>
                      <Chip label={log.action} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      {log.entity_type} (ID: {log.entity_id})
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.status}
                        size="small"
                        color={getStatusColor(log.status)}
                      />
                    </TableCell>
                    <TableCell>{log.ip_address || 'N/A'}</TableCell>
                    <TableCell>
                      {log.details && (
                        <Tooltip title={log.details}>
                          <IconButton size="small">
                            <Info fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={totalCount || filteredLogs.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};

export default AuditLogViewer;
