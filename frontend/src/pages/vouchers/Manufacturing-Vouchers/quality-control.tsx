// frontend/src/pages/vouchers/Manufacturing-Vouchers/quality-control.tsx
import React, { useState } from "react";
import { Typography, Container, Box, Tabs, Tab } from "@mui/material";
import { ProtectedPage } from "../../../components/ProtectedPage";

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