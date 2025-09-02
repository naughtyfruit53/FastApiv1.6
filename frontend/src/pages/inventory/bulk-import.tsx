// pages/inventory/bulk-import.tsx
// Stock Bulk Import page

import React from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  Paper,
} from "@mui/material";
import {
  CloudUpload,
  Inventory,
  Warning,
  CheckCircle,
} from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import StockBulkImport from "../../components/StockBulkImport";
import { canManageUsers } from "../../types/user.types";

const StockBulkImportPage: NextPage = () => {
  const { user } = useAuth();

  const canImportStock = canManageUsers(user); // Typically admin-level permission

  if (!user || !canImportStock) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to perform bulk stock
          imports. Contact your administrator for access.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <CloudUpload color="primary" />
          Stock Bulk Import
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Import large quantities of stock data efficiently using Excel/CSV
          files.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Instructions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}
              >
                <Inventory color="primary" fontSize="large" />
                <Typography variant="h6">Prepare Data</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Organize your stock data in the required format with product
                codes, quantities, and locations.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}
              >
                <Warning color="warning" fontSize="large" />
                <Typography variant="h6">Validate Format</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Ensure your file follows the template format to avoid import
                errors and data inconsistencies.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}
              >
                <CheckCircle color="success" fontSize="large" />
                <Typography variant="h6">Import & Verify</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Upload your file and review the import results before finalizing
                the stock updates.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Import Component */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <StockBulkImport />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default StockBulkImportPage;
