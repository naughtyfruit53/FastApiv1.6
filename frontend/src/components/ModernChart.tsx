import React from "react";
import { Box, Typography, Paper } from "@mui/material";
export interface ModernChartProps {
  title: string;
  data: any[];
  type: "bar" | "line" | "pie" | "area";
  height?: number;
  color?: "primary" | "success" | "warning" | "error" | "info";
  loading?: boolean;
}
const ModernChart: React.FC<ModernChartProps> = ({
  title,
  data,
  type,
  height = 300,
  color = "primary",
  loading = false,
}) => {
  const getColorScheme = () => {
    switch (color) {
      case "success":
        return [
          "var(--success-500)",
          "var(--success-600)",
          "var(--success-700)",
        ];
      case "warning":
        return [
          "var(--warning-500)",
          "var(--warning-600)",
          "var(--warning-700)",
        ];
      case "error":
        return ["var(--error-500)", "var(--error-600)", "var(--error-700)"];
      case "info":
        return ["var(--info-500)", "var(--info-600)", "var(--info-700)"];
      case "primary":
      default:
        return [
          "var(--primary-500)",
          "var(--primary-600)",
          "var(--primary-700)",
        ];
    }
  };

  const _options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            family: "var(--font-family-sans)",
            size: 12,
            weight: "500",
          },
        },
      },
      tooltip: {
        backgroundColor: "var(--bg-surface)",
        titleColor: "var(--text-primary)",
        bodyColor: "var(--text-secondary)",
        borderColor: "var(--border-primary)",
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        titleFont: {
          family: "var(--font-family-sans)",
          size: 14,
          weight: "600",
        },
        bodyFont: {
          family: "var(--font-family-sans)",
          size: 13,
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: "var(--border-primary)",
          borderDash: [3, 3],
        },
        ticks: {
          color: "var(--text-secondary)",
          font: {
            family: "var(--font-family-sans)",
            size: 11,
          },
        },
      },
      y: {
        grid: {
          color: "var(--border-primary)",
          borderDash: [3, 3],
        },
        ticks: {
          color: "var(--text-secondary)",
          font: {
            family: "var(--font-family-sans)",
            size: 11,
          },
        },
      },
    },
  };
  if (loading) {
    return (
      <Paper className="modern-card" sx={{ p: 3 }}>
        <Typography className="modern-card-title" variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box
          className="modern-skeleton"
          sx={{
            height: height,
            borderRadius: "var(--radius-md)",
            mt: 2,
          }}
        />
      </Paper>
    );
  }
  return (
    <Paper className="modern-card" sx={{ p: 3 }}>
      <Typography className="modern-card-title" variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box
        sx={{
          height: height,
          mt: 2,
          "& canvas": {
            borderRadius: "var(--radius-md)",
          },
        }}
      >
        {/* Chart component would be rendered here */}
        {/* This is a placeholder for chart libraries like Chart.js, Recharts, etc. */}
        <Box
          sx={{
            width: "100%",
            height: "100%",
            background: `linear-gradient(135deg, ${getColorScheme()[0]}20, ${getColorScheme()[1]}10)`,
            borderRadius: "var(--radius-md)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "1px solid var(--border-primary)",
          }}
        >
          <Typography variant="body2" color="textSecondary">
            {type.toUpperCase()} Chart - {data.length} data points
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};
export default ModernChart;
