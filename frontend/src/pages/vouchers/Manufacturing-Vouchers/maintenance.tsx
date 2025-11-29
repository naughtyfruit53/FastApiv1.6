// frontend/src/pages/vouchers/Manufacturing-Vouchers/maintenance.tsx
import React, { useState } from "react";
import { Typography, Container, Box, Tabs, Tab } from "@mui/material";
import * as yup from "yup";
import { ProtectedPage } from "../../../components/ProtectedPage";

const machineSchema = yup.object().shape({
  name: yup.string().required(),
  code: yup.string().required(),
  location: yup.string().required(),
  model: yup.string().required(),
  supplier: yup.string(),
  amcDetails: yup.string(),
});

const preventiveSchema = yup.object().shape({
  machineId: yup.number().required(),
  frequency: yup.string().required(),
  tasks: yup.string().required(),
  assignedTechnician: yup.string(),
  nextDueDate: yup.date().required(),
});

const breakdownSchema = yup.object().shape({
  machineId: yup.number().required(),
  breakdownType: yup.string().required(),
  date: yup.date().required(),
  reportedBy: yup.string().required(),
  description: yup.string().required(),
  rootCause: yup.string(),
  timeToFix: yup.number(),
  sparePartsUsed: yup.string(),
  cost: yup.number(),
  downtimeHours: yup.number(),
});

const logSchema = yup.object().shape({
  machineId: yup.number().required(),
  date: yup.date().required(),
  runtimeHours: yup.number().required(),
  idleHours: yup.number().required(),
  efficiencyPercentage: yup.number().required(),
  errorCodes: yup.string(),
});

const spareSchema = yup.object().shape({
  machineId: yup.number().required(),
  name: yup.string().required(),
  code: yup.string().required(),
  quantity: yup.number().required(),
  minLevel: yup.number(),
  reorderLevel: yup.number(),
  unitCost: yup.number(),
});

const MachineMaintenance: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  // Add forms for each tab using useForm
  // ... implement tabs for Machine Master, Preventive, Breakdown, Logs, Spares

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Machine Maintenance
          </Typography>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab label="Machine Master" />
            <Tab label="Preventive Schedule" />
            <Tab label="Breakdown" />
            <Tab label="Performance Logs" />
            <Tab label="Spare Parts" />
          </Tabs>
          {/* Conditional render forms based on tabValue */}
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default MachineMaintenance;