// frontend/src/pages/inventory/movements.tsx
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getStockMovements } from "../../services/stockService";
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControlLabel,
  Checkbox,
  Grid,
} from "@mui/material";
import { Search } from "@mui/icons-material";
import { useAuth } from "../../context/AuthContext";
const StockMovements: React.FC = () => {
  const { isOrgContextReady } = useAuth();
  const [searchText, setSearchText] = useState("");
  const [showOnlyRecent, setShowOnlyRecent] = useState(true);
  const { data: movements, isLoading } = useQuery({
    queryKey: [
      "stockMovements",
      { search: searchText, recent: showOnlyRecent },
    ],
    queryFn: ({ queryKey }) => getStockMovements(queryKey[1]),
    enabled: isOrgContextReady,
  });
  if (isLoading) {
    return <Typography>Loading stock movements...</Typography>;
  }
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Stock Movements
      </Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              label="Search movements"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={showOnlyRecent}
                  onChange={(e) => setShowOnlyRecent(e.target.checked)}
                />
              }
              label="Show only recent movements (last 30 days)"
            />
          </Grid>
        </Grid>
      </Paper>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Product</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Notes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {movements?.map((movement) => (
              <TableRow key={movement.id}>
                <TableCell>
                  {new Date(movement.transaction_date).toLocaleString()}
                </TableCell>
                <TableCell>{movement.product_name}</TableCell>
                <TableCell>{movement.transaction_type}</TableCell>
                <TableCell>{movement.quantity}</TableCell>
                <TableCell>{movement.reference_number || "-"}</TableCell>
                <TableCell>{movement.notes || "-"}</TableCell>
              </TableRow>
            ))}
            {movements?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No movements found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};
export default StockMovements;
