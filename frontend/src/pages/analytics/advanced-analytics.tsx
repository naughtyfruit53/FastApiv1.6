// pages/analytics/advanced-analytics.tsx
// Advanced ML/AI Analytics page with predictive models and anomaly detection
import React, { useState, useEffect } from "react";
import { NextPage } from "next";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  Tabs,
  Tab,
  Paper,
} from "@mui/material";
import {
  AutoAwesome,
  TrendingUp,
  Warning,
  Storage,
  InsightsOutlined,
} from "@mui/icons-material";
import { useAuth } from "../../hooks/useAuth";
import { canManageUsers } from "../../types/user.types";
import PredictiveDashboard from "../../components/PredictiveDashboard";

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
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const AdvancedAnalyticsPage: NextPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (!user || !canManageUsers(user)) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view advanced analytics.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 2 }}
        >
          <AutoAwesome color="primary" />
          Advanced ML/AI Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Leverage machine learning and AI for predictive insights, anomaly
          detection, and advanced analytics to drive data-driven decisions.
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Overview Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <TrendingUp color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Predictive Models</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Forecast future trends
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Warning color="warning" fontSize="large" />
                <Box>
                  <Typography variant="h6">Anomaly Detection</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Identify unusual patterns
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Storage color="info" fontSize="large" />
                <Box>
                  <Typography variant="h6">Data Integration</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Connect external sources
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <InsightsOutlined color="success" fontSize="large" />
                <Box>
                  <Typography variant="h6">AI Insights</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Automated recommendations
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="advanced analytics tabs"
          variant="fullWidth"
        >
          <Tab label="Dashboard" id="analytics-tab-0" />
          <Tab label="Predictive Models" id="analytics-tab-1" />
          <Tab label="Anomaly Detection" id="analytics-tab-2" />
          <Tab label="Data Sources" id="analytics-tab-3" />
          <Tab label="Insights" id="analytics-tab-4" />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <PredictiveDashboard />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Predictive Models
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Manage and deploy predictive models for forecasting sales,
              demand, revenue, and more.
            </Typography>
            {/* TODO: Add predictive models management component */}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Anomaly Detection
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Configure and monitor anomaly detection for revenue, inventory,
              transactions, and operational metrics.
            </Typography>
            {/* TODO: Add anomaly detection component */}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              External Data Sources
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Connect and manage external data sources for enhanced analytics
              and predictions.
            </Typography>
            {/* TODO: Add data sources management component */}
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI-Powered Insights
            </Typography>
            <Typography variant="body2" color="text.secondary">
              View automated insights and recommendations generated by AI
              models.
            </Typography>
            {/* TODO: Add AI insights component */}
          </CardContent>
        </Card>
      </TabPanel>
    </Container>
  );
};

export default AdvancedAnalyticsPage;
