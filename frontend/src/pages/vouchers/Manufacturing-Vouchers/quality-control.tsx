// frontend/src/pages/vouchers/Manufacturing-Vouchers/quality-control.tsx
import React, { useState, useEffect } from "react";
import { Typography, Container, Box, Button, Grid, TextField, Select, MenuItem, FormControl, InputLabel, CircularProgress, Tabs, Tab } from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { ProtectedPage } from "../../../components/ProtectedPage";
import { useAuth } from "../../../context/AuthContext";
import api from "../../../services/api/client"; 

// Schemas for each type
// ... implement tabs for Incoming QC, In-Process, Finished Goods

const QualityControl: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  // Forms for templates, inspections, rejections

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Quality Control
          </Typography>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab label="QC Templates" />
            <Tab label="Inspections" />
            <Tab label="Rejections" />
          </Tabs>
          {/* Conditional forms */}
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default QualityControl;