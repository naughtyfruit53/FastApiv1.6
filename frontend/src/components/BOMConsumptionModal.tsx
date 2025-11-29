// frontend/src/components/BOMConsumptionModal.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

interface BOMConsumptionModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: Array<{ componentId: number; actualQty: number; wastageQty: number }>) => void;
  plannedQuantity: number;
  components: Array<{
    componentId: number;
    name: string;
    plannedQty: number;
    actualQty: number;
    wastageQty: number;
  }>;
}

const BOMConsumptionModal: React.FC<BOMConsumptionModalProps> = ({
  open,
  onClose,
  onSubmit,
  plannedQuantity,
  components: initialComponents,
}) => {
  const [components, setComponents] = useState(initialComponents);

  const handleChange = (index: number, field: 'actualQty' | 'wastageQty', value: number) => {
    const updated = [...components];
    updated[index][field] = value;
    setComponents(updated);
  };

  const handleSubmit = () => {
    const submitData = components.map(({ componentId, actualQty, wastageQty }) => ({
      componentId,
      actualQty,
      wastageQty,
    }));
    onSubmit(submitData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>BOM Consumption</DialogTitle>
      <DialogContent>
        <Typography variant="subtitle1" gutterBottom>
          Planned Quantity: {plannedQuantity}
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Component Name</TableCell>
                <TableCell>Planned Qty</TableCell>
                <TableCell>Actual Used Qty</TableCell>
                <TableCell>Wastage Qty</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {components.map((comp, index) => (
                <TableRow key={comp.componentId}>
                  <TableCell>{comp.name}</TableCell>
                  <TableCell>{comp.plannedQty}</TableCell>
                  <TableCell>
                    <TextField
                      type="number"
                      value={comp.actualQty}
                      onChange={(e) => handleChange(index, 'actualQty', Number(e.target.value))}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      type="number"
                      value={comp.wastageQty}
                      onChange={(e) => handleChange(index, 'wastageQty', Number(e.target.value))}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default BOMConsumptionModal;