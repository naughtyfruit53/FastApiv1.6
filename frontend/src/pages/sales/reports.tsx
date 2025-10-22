"use client";
import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  LinearProgress,
  ButtonGroup,
} from "@mui/material";
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  MonetizationOn as MoneyIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  Print as PrintIcon,
  FileDownload as ExcelIcon,
  PictureAsPdf as PdfIcon,
} from "@mui/icons-material";
import * as XLSX from "exceljs";
import { saveAs } from "file-saver";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { formatCurrency } from "../../utils/currencyUtils";
interface SalesData {
  period: string;
  revenue: number;
  deals: number;
  averageDealSize: number;
  conversionRate: number;
  growth: number;
}
interface SalespersonPerformance {
  name: string;
  revenue: number;
  deals: number;
  quota: number;
  achievement: number;
  commission: number;
}
interface ProductPerformance {
  product: string;
  revenue: number;
  units: number;
  margin: number;
  growth: number;
}
interface RegionPerformance {
  region: string;
  revenue: number;
  deals: number;
  growth: number;
}
const SalesReports: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState("last_quarter");
  const [tabValue, setTabValue] = useState(0);
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [salespersonData, setSalespersonData] = useState<
    SalespersonPerformance[]
  >([]);
  const [productData, setProductData] = useState<ProductPerformance[]>([]);
  const [regionData, setRegionData] = useState<RegionPerformance[]>([]);
  
  // Fetch real data from API
  useEffect(() => {
    const fetchReportData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Calculate date range based on timeRange selection
        const endDate = new Date();
        const startDate = new Date();
        
        switch (timeRange) {
          case "last_week":
            startDate.setDate(endDate.getDate() - 7);
            break;
          case "last_month":
            startDate.setMonth(endDate.getMonth() - 1);
            break;
          case "last_quarter":
            startDate.setMonth(endDate.getMonth() - 3);
            break;
          case "last_year":
            startDate.setFullYear(endDate.getFullYear() - 1);
            break;
          default:
            startDate.setMonth(endDate.getMonth() - 3);
        }
        
        // TODO: Implement API endpoints for comprehensive sales analytics
        // For now, initialize with empty arrays to show proper empty states
        setSalesData([]);
        setSalespersonData([]);
        setProductData([]);
        setRegionData([]);
        
      } catch (err) {
        setError("Failed to load report data");
        console.error("Error fetching reports:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReportData();
  }, [timeRange]);
  const totalRevenue = salesData.reduce((sum, data) => sum + data.revenue, 0);
  const totalDeals = salesData.reduce((sum, data) => sum + data.deals, 0);
  const avgDealSize = totalDeals > 0 ? totalRevenue / totalDeals : 0;
  const avgConversionRate =
    salesData.length > 0
      ? salesData.reduce((sum, data) => sum + data.conversionRate, 0) /
        salesData.length
      : 0;
  const handleExport = async (format: "excel" | "pdf") => {
    try {
      if (format === "excel") {
        await exportToExcel();
      } else if (format === "pdf") {
        await exportToPDF();
      }
    } catch (err) {
      console.error("Export error:", err);
    }
  };
  const exportToExcel = async () => {
    const workbook = new XLSX.Workbook();
    // Sales Overview Sheet
    const overviewSheet = workbook.addWorksheet("Sales Overview");
    // Add headers
    overviewSheet.addRow(["Metric", "Value"]);
    overviewSheet.addRow([
      "Total Revenue",
      formatCurrency(totalRevenue),
    ]);
    overviewSheet.addRow(["Total Deals", totalDeals.toString()]);
    overviewSheet.addRow(["Average Deal Size", formatCurrency(avgDealSize)]);
    overviewSheet.addRow(["Average Conversion Rate", `${avgConversionRate.toFixed(1)}%`]);
    overviewSheet.addRow(["Export Date", new Date().toLocaleDateString()]);
    overviewSheet.addRow([
      "Time Range",
      timeRange.replace("_", " ").toUpperCase(),
    ]);
    // Style the header row
    overviewSheet.getRow(1).font = { bold: true };
    overviewSheet.getColumn(1).width = 20;
    overviewSheet.getColumn(2).width = 20;
    // Sales Data Sheet
    const dataSheet = workbook.addWorksheet("Sales Data");
    // Add headers for sales data
    dataSheet.addRow([
      "Period",
      "Revenue",
      "Deals",
      "Avg Deal Size",
      "Conversion Rate (%)",
      "Growth (%)",
    ]);
    // Add sales data
    salesData.forEach((data) => {
      dataSheet.addRow([
        data.period,
        data.revenue,
        data.leads,
        data.customers,
        data.conversionRate,
        data.growth,
      ]);
    });
    // Style the header row
    dataSheet.getRow(1).font = { bold: true };
    dataSheet.columns.forEach((column) => {
      column.width = 15;
    });
    // Generate buffer and save file
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    saveAs(
      blob,
      `sales-report-${timeRange}-${new Date().toISOString().split("T")[0]}.xlsx`,
    );
  };
  const exportToPDF = () => {
    const doc = new jsPDF();
    // Add title
    doc.setFontSize(20);
    doc.text("Sales Report", 20, 20);
    // Add metadata
    doc.setFontSize(12);
    doc.text(
      `Time Range: ${timeRange.replace("_", " ").toUpperCase()}`,
      20,
      35,
    );
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 45);
    // Add summary metrics
    doc.setFontSize(14);
    doc.text("Summary Metrics:", 20, 65);
    doc.setFontSize(11);
    doc.text(`Total Revenue: $${totalRevenue.toLocaleString()}`, 20, 75);
    // TODO: Define or import avgGrowth
    doc.text(`Revenue Growth: ${avgGrowth.toFixed(1)}%`, 20, 85);
    // TODO: Define or import avgConversion
    doc.text(`Conversion Rate: ${avgConversion.toFixed(1)}%`, 20, 95);
    // TODO: Define or import totalLeads
    doc.text(`Total Leads: ${totalLeads}`, 20, 105);
    // Add sales data table
    const tableData = salesData.map((data) => [
      data.period,
      formatCurrency(data.revenue),
      data.deals.toString(),
      data.averageDealSize.toString(),
      `${data.conversionRate}%`,
      `${data.growth}%`,
    ]);
    (doc as any).autoTable({
      head: [
        [
          "Period",
          "Revenue",
          "Leads",
          "Customers",
          "Conversion Rate",
          "Growth",
        ],
      ],
      body: tableData,
      startY: 120,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [41, 128, 185] },
    });
    // Save the PDF
    doc.save(
      `sales-report-${timeRange}-${new Date().toISOString().split("T")[0]}.pdf`,
    );
  };
  const handlePrint = () => {
    window.print();
  };
  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }
  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4">Sales Reports</Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="last_week">Last Week</MenuItem>
              <MenuItem value="last_month">Last Month</MenuItem>
              <MenuItem value="last_quarter">Last Quarter</MenuItem>
              <MenuItem value="last_year">Last Year</MenuItem>
              <MenuItem value="ytd">Year to Date</MenuItem>
            </Select>
          </FormControl>
          <ButtonGroup variant="outlined" size="small">
            <Button
              startIcon={<ExcelIcon />}
              onClick={() => handleExport("excel")}
            >
              Excel
            </Button>
            <Button startIcon={<PdfIcon />} onClick={() => handleExport("pdf")}>
              PDF
            </Button>
            <Button startIcon={<PrintIcon />} onClick={handlePrint}>
              Print
            </Button>
          </ButtonGroup>
        </Box>
      </Box>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <MoneyIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Revenue
                  </Typography>
                  <Typography variant="h4">
                    ${(totalRevenue / 1000000).toFixed(1)}M
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />
                    +12.5% vs last period
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <AssessmentIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Deals
                  </Typography>
                  <Typography variant="h4">{totalDeals}</Typography>
                  <Typography variant="body2" color="primary.main">
                    Closed deals
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <TimelineIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Deal Size
                  </Typography>
                  <Typography variant="h4">
                    ${Math.round(avgDealSize).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="warning.main">
                    <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />
                    +8.3% improvement
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <BarChartIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Conversion Rate
                  </Typography>
                  <Typography variant="h4">
                    {avgConversionRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="info.main">
                    Average rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Tabs for different report types */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
        >
          <Tab label="Sales Trends" />
          <Tab label="Salesperson Performance" />
          <Tab label="Product Performance" />
          <Tab label="Regional Analysis" />
        </Tabs>
      </Paper>
      {/* Sales Trends Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monthly Sales Performance
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Period</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                        <TableCell align="right">Deals</TableCell>
                        <TableCell align="right">Avg Deal Size</TableCell>
                        <TableCell align="right">Conversion Rate</TableCell>
                        <TableCell align="right">Growth</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {salesData.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={6} align="center">
                            <Box sx={{ py: 4 }}>
                              <AssessmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                              <Typography variant="h6" color="text.secondary" gutterBottom>
                                No Sales Data Available
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Sales data will appear here once you have closed deals in the selected time period.
                              </Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ) : (
                        salesData.map((data, index) => (
                          <TableRow key={index} hover>
                            <TableCell>{data.period}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(data.revenue)}
                            </TableCell>
                            <TableCell align="right">{data.deals}</TableCell>
                            <TableCell align="right">
                              {formatCurrency(data.averageDealSize)}
                            </TableCell>
                            <TableCell align="right">
                              {data.conversionRate}%
                            </TableCell>
                            <TableCell align="right">
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "flex-end",
                                }}
                              >
                                {data.growth >= 0 ? (
                                  <TrendingUpIcon
                                    color="success"
                                    sx={{ mr: 0.5, fontSize: 16 }}
                                  />
                                ) : (
                                  <TrendingDownIcon
                                    color="error"
                                    sx={{ mr: 0.5, fontSize: 16 }}
                                  />
                                )}
                                <Typography
                                  color={
                                    data.growth >= 0
                                      ? "success.main"
                                      : "error.main"
                                  }
                                  variant="body2"
                                >
                                  {data.growth > 0 ? "+" : ""}
                                  {data.growth}%
                                </Typography>
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      {/* Salesperson Performance Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Salesperson Performance
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Salesperson</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                        <TableCell align="right">Deals</TableCell>
                        <TableCell align="right">Quota</TableCell>
                        <TableCell align="right">Achievement</TableCell>
                        <TableCell align="right">Commission</TableCell>
                        <TableCell>Quota Progress</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {salespersonData.map((person, index) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              <PersonIcon
                                sx={{ mr: 1, color: "primary.main" }}
                              />
                              {person.name}
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(person.revenue)}
                          </TableCell>
                          <TableCell align="right">{person.deals}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(person.quota)}
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              color={
                                person.achievement >= 100
                                  ? "success.main"
                                  : "warning.main"
                              }
                              variant="body2"
                              sx={{ fontWeight: "bold" }}
                            >
                              {person.achievement}%
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(person.commission)}
                          </TableCell>
                          <TableCell>
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                minWidth: 120,
                              }}
                            >
                              <LinearProgress
                                variant="determinate"
                                value={Math.min(person.achievement, 100)}
                                sx={{
                                  flexGrow: 1,
                                  mr: 1,
                                  height: 8,
                                  borderRadius: 4,
                                }}
                                color={
                                  person.achievement >= 100
                                    ? "success"
                                    : "primary"
                                }
                              />
                              <Typography variant="body2" color="textSecondary">
                                {Math.round(person.achievement)}%
                              </Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      {/* Product Performance Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Product Performance
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                        <TableCell align="right">Units Sold</TableCell>
                        <TableCell align="right">Profit Margin</TableCell>
                        <TableCell align="right">Growth</TableCell>
                        <TableCell align="right">Avg Price</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {productData.map((product, index) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              <BusinessIcon
                                sx={{ mr: 1, color: "secondary.main" }}
                              />
                              {product.product}
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(product.revenue)}
                          </TableCell>
                          <TableCell align="right">{product.units}</TableCell>
                          <TableCell align="right">
                            <Typography
                              color={
                                product.margin >= 60
                                  ? "success.main"
                                  : product.margin >= 40
                                    ? "warning.main"
                                    : "error.main"
                              }
                              variant="body2"
                            >
                              {product.margin}%
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "flex-end",
                              }}
                            >
                              {product.growth >= 0 ? (
                                <TrendingUpIcon
                                  color="success"
                                  sx={{ mr: 0.5, fontSize: 16 }}
                                />
                              ) : (
                                <TrendingDownIcon
                                  color="error"
                                  sx={{ mr: 0.5, fontSize: 16 }}
                                />
                              )}
                              <Typography
                                color={
                                  product.growth >= 0
                                    ? "success.main"
                                    : "error.main"
                                }
                                variant="body2"
                              >
                                {product.growth > 0 ? "+" : ""}
                                {product.growth}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(Math.round(product.revenue / product.units))}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      {/* Regional Analysis Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Regional Performance
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Region</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                        <TableCell align="right">Deals</TableCell>
                        <TableCell align="right">Avg Deal Size</TableCell>
                        <TableCell align="right">Growth</TableCell>
                        <TableCell>Performance</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {regionData.map((region, index) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            <Typography variant="subtitle2">
                              {region.region}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(region.revenue)}
                          </TableCell>
                          <TableCell align="right">{region.deals}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(Math.round(region.revenue / region.deals))}
                          </TableCell>
                          <TableCell align="right">
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "flex-end",
                              }}
                            >
                              {region.growth >= 0 ? (
                                <TrendingUpIcon
                                  color="success"
                                  sx={{ mr: 0.5, fontSize: 16 }}
                                />
                              ) : (
                                <TrendingDownIcon
                                  color="error"
                                  sx={{ mr: 0.5, fontSize: 16 }}
                                />
                              )}
                              <Typography
                                color={
                                  region.growth >= 0
                                    ? "success.main"
                                    : "error.main"
                                }
                                variant="body2"
                              >
                                {region.growth > 0 ? "+" : ""}
                                {region.growth}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <LinearProgress
                              variant="determinate"
                              value={
                                (region.revenue /
                                  Math.max(
                                    ...regionData.map((r) => r.revenue),
                                  )) *
                                100
                              }
                              sx={{ height: 8, borderRadius: 4 }}
                              color="primary"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};
export default SalesReports;
