// frontend/src/components/ManufacturingShortageAlert.tsx
import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  AlertTitle,
  Tooltip,
  IconButton,
  Divider,
} from "@mui/material";
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  ShoppingCart as ShoppingCartIcon,
} from "@mui/icons-material";

interface ShortageItem {
  product_id: number;
  product_name: string;
  required: number;
  available: number;
  shortage: number;
  unit: string;
  severity?: "critical" | "warning";
  purchase_order_status?: {
    has_order: boolean;
    on_order_quantity: number;
    orders: Array<{
      po_number: string;
      po_id: number;
      quantity: number;
      status: string;
      delivery_date?: string;
    }>;
  };
}

interface Recommendation {
  type: "critical" | "warning" | "success" | "info";
  message: string;
  action: string;
}

interface ManufacturingShortageAlertProps {
  open: boolean;
  onClose: () => void;
  onProceed?: () => void;
  moNumber?: string;
  isAvailable: boolean;
  shortages: ShortageItem[];
  recommendations: Recommendation[];
  title?: string;
  proceedButtonText?: string;
  showProceedButton?: boolean;
}

const ManufacturingShortageAlert: React.FC<ManufacturingShortageAlertProps> = ({
  open,
  onClose,
  onProceed,
  moNumber,
  isAvailable,
  shortages,
  recommendations,
  title = "Material Shortage Alert",
  proceedButtonText = "Proceed Anyway",
  showProceedButton = true,
}) => {
  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "critical":
        return "error";
      case "warning":
        return "warning";
      default:
        return "default";
    }
  };

  const getSeverityIcon = (severity?: string) => {
    switch (severity) {
      case "critical":
        return <ErrorIcon />;
      case "warning":
        return <WarningIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const getRecommendationSeverity = (type: string) => {
    switch (type) {
      case "critical":
        return "error";
      case "warning":
        return "warning";
      case "success":
        return "success";
      default:
        return "info";
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Not specified";
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return "Invalid date";
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          {isAvailable ? (
            <CheckCircleIcon color="success" />
          ) : (
            <WarningIcon color="error" />
          )}
          <Typography variant="h6">{title}</Typography>
        </Box>
        {moNumber && (
          <Typography variant="subtitle2" color="text.secondary">
            Manufacturing Order: {moNumber}
          </Typography>
        )}
      </DialogTitle>

      <DialogContent dividers>
        {/* Summary */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Summary
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Chip
              label={`Total Items: ${shortages.length}`}
              color={shortages.length > 0 ? "error" : "success"}
              variant="outlined"
            />
            <Chip
              label={`Critical: ${shortages.filter((s) => s.severity === "critical").length}`}
              color="error"
              variant={
                shortages.filter((s) => s.severity === "critical").length > 0
                  ? "filled"
                  : "outlined"
              }
            />
            <Chip
              label={`Warning: ${shortages.filter((s) => s.severity === "warning").length}`}
              color="warning"
              variant={
                shortages.filter((s) => s.severity === "warning").length > 0
                  ? "filled"
                  : "outlined"
              }
            />
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <Box mb={3}>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            {recommendations.map((rec, index) => (
              <Alert
                key={index}
                severity={getRecommendationSeverity(rec.type) as any}
                sx={{ mb: 1 }}
              >
                <AlertTitle>{rec.message}</AlertTitle>
                {rec.action}
              </Alert>
            ))}
          </Box>
        )}

        {/* Shortage Details Table */}
        {shortages.length > 0 ? (
          <>
            <Typography variant="h6" gutterBottom>
              Shortage Details
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Material</TableCell>
                    <TableCell align="right">Required</TableCell>
                    <TableCell align="right">Available</TableCell>
                    <TableCell align="right">Shortage</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>PO Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {shortages.map((item, index) => (
                    <TableRow
                      key={index}
                      sx={{
                        backgroundColor:
                          item.severity === "critical"
                            ? "rgba(211, 47, 47, 0.08)"
                            : item.severity === "warning"
                              ? "rgba(237, 108, 2, 0.08)"
                              : "inherit",
                      }}
                    >
                      <TableCell>
                        <Tooltip
                          title={
                            item.severity === "critical"
                              ? "No purchase order placed"
                              : "Purchase order placed, awaiting delivery"
                          }
                        >
                          <Chip
                            size="small"
                            icon={getSeverityIcon(item.severity)}
                            label={
                              item.severity === "critical"
                                ? "Critical"
                                : "Warning"
                            }
                            color={getSeverityColor(item.severity) as any}
                          />
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {item.product_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ID: {item.product_id}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {item.required.toFixed(2)}
                      </TableCell>
                      <TableCell align="right">
                        {item.available.toFixed(2)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography
                          variant="body2"
                          color="error"
                          fontWeight="bold"
                        >
                          {item.shortage.toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>{item.unit}</TableCell>
                      <TableCell>
                        {item.purchase_order_status?.has_order ? (
                          <Box>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              <ShoppingCartIcon
                                fontSize="small"
                                color="primary"
                              />
                              <Typography variant="body2" color="primary">
                                {item.purchase_order_status.orders.length} PO(s)
                              </Typography>
                            </Box>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              On Order:{" "}
                              {item.purchase_order_status.on_order_quantity.toFixed(
                                2,
                              )}{" "}
                              {item.unit}
                            </Typography>
                            {item.purchase_order_status.orders.map(
                              (po, poIndex) => (
                                <Box key={poIndex} mt={0.5}>
                                  <Chip
                                    size="small"
                                    label={`${po.po_number} (${po.quantity.toFixed(2)} ${item.unit})`}
                                    variant="outlined"
                                  />
                                  {po.delivery_date && (
                                    <Typography
                                      variant="caption"
                                      display="block"
                                      color="text.secondary"
                                    >
                                      ETA: {formatDate(po.delivery_date)}
                                    </Typography>
                                  )}
                                </Box>
                              ),
                            )}
                          </Box>
                        ) : (
                          <Chip
                            size="small"
                            label="No PO"
                            color="error"
                            variant="outlined"
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        ) : (
          <Alert severity="success">
            <AlertTitle>All materials available</AlertTitle>
            All required materials are in stock. You can proceed with
            manufacturing.
          </Alert>
        )}

        {/* Color Legend */}
        {shortages.length > 0 && (
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom>
              Color Coding:
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  width={20}
                  height={20}
                  bgcolor="rgba(211, 47, 47, 0.2)"
                  borderRadius={1}
                />
                <Typography variant="caption">
                  Critical - No purchase order placed
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  width={20}
                  height={20}
                  bgcolor="rgba(237, 108, 2, 0.2)"
                  borderRadius={1}
                />
                <Typography variant="caption">
                  Warning - Purchase order placed, awaiting delivery
                </Typography>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>
        {showProceedButton && onProceed && (
          <Button
            onClick={onProceed}
            variant="contained"
            color={isAvailable ? "primary" : "warning"}
            disabled={isAvailable && shortages.length === 0}
          >
            {proceedButtonText}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ManufacturingShortageAlert;
