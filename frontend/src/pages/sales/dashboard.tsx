"use client";

import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
} from "@mui/material";
import {
  MonetizationOn,
  TrendingUp,
  People,
  Assessment,
} from "@mui/icons-material";
import { crmService } from "../../services/crmService";

interface DashboardStats {
  totalRevenue: number;
  activeOpportunities: number;
  newLeads: number;
  conversionRate: number;
}

const SalesDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalRevenue: 0,
    activeOpportunities: 0,
    newLeads: 0,
    conversionRate: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch basic data from API
        const [leads, opportunities] = await Promise.all([
          crmService.getLeads(0, 1000), // Get more leads for accurate count
          crmService.getOpportunities(0, 1000), // Get more opportunities for accurate count
        ]);

        // Calculate stats
        const totalRevenue = opportunities
          .filter((opp) => opp.stage === "closed_won")
          .reduce((sum, opp) => sum + opp.amount, 0);

        const activeOpportunities = opportunities.filter(
          (opp) => !["closed_won", "closed_lost"].includes(opp.stage),
        ).length;

        const newLeads = leads.filter((lead) => lead.status === "new").length;

        const convertedLeads = leads.filter(
          (lead) => lead.status === "converted",
        ).length;
        const conversionRate =
          leads.length > 0 ? (convertedLeads / leads.length) * 100 : 0;

        setStats({
          totalRevenue,
          activeOpportunities,
          newLeads,
          conversionRate,
        });
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Sales CRM Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage your sales pipeline, leads, and customer relationships
        </Typography>

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <MonetizationOn color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Revenue</Typography>
                  </Box>
                  <Typography variant="h4" color="primary">
                    ${stats.totalRevenue.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Closed won deals
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <TrendingUp color="success.main" sx={{ mr: 1 }} />
                    <Typography variant="h6">Opportunities</Typography>
                  </Box>
                  <Typography variant="h4" color="success.main">
                    {stats.activeOpportunities}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active opportunities
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <People color="info.main" sx={{ mr: 1 }} />
                    <Typography variant="h6">Leads</Typography>
                  </Box>
                  <Typography variant="h4" color="info.main">
                    {stats.newLeads}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    New leads
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Assessment color="warning.main" sx={{ mr: 1 }} />
                    <Typography variant="h6">Conversion</Typography>
                  </Box>
                  <Typography variant="h4" color="warning.main">
                    {stats.conversionRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Lead to customer
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        <Box sx={{ mt: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Start managing your sales pipeline with these common actions.
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Button
                    variant="contained"
                    onClick={() => (window.location.href = "/sales/leads")}
                    startIcon={<People />}
                  >
                    Manage Leads
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="contained"
                    onClick={() =>
                      (window.location.href = "/sales/opportunities")
                    }
                    startIcon={<TrendingUp />}
                  >
                    Track Opportunities
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="outlined"
                    onClick={() => (window.location.href = "/sales/pipeline")}
                    startIcon={<Assessment />}
                  >
                    View Pipeline
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="outlined"
                    onClick={() => (window.location.href = "/sales/customers")}
                    startIcon={<People />}
                  >
                    Customer Database
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  );
};

export default SalesDashboard;