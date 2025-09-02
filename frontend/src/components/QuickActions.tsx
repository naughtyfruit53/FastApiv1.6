import React from "react";
import { Box, Button, Paper, Typography } from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Download,
  Upload,
  Share,
} from "@mui/icons-material";

export interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactElement;
  color?: "primary" | "secondary" | "success" | "warning" | "error" | "info";
  variant?: "contained" | "outlined" | "text";
  onClick: () => void;
  disabled?: boolean;
}

export interface QuickActionsProps {
  title?: string;
  actions: QuickAction[];
  layout?: "horizontal" | "vertical" | "grid";
  size?: "small" | "medium" | "large";
  className?: string;
}

const QuickActions: React.FC<QuickActionsProps> = ({
  title = "Quick Actions",
  actions,
  layout = "grid",
  size = "medium",
  className = "",
}) => {
  const getButtonSize = () => {
    switch (size) {
      case "small":
        return "small" as const;
      case "large":
        return "large" as const;
      case "medium":
      default:
        return "medium" as const;
    }
  };

  const getLayoutStyles = () => {
    switch (layout) {
      case "horizontal":
        return {
          display: "flex",
          flexWrap: "wrap",
          gap: 2,
          alignItems: "center",
        };
      case "vertical":
        return {
          display: "flex",
          flexDirection: "column",
          gap: 2,
        };
      case "grid":
      default:
        return {
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: 2,
        };
    }
  };

  return (
    <Paper className={`modern-card ${className}`} sx={{ p: 3 }}>
      {title && (
        <Typography className="modern-card-title" variant="h6" gutterBottom>
          {title}
        </Typography>
      )}

      <Box sx={getLayoutStyles()}>
        {actions.map((action) => (
          <Button
            key={action.id}
            variant={action.variant || "outlined"}
            color={action.color || "primary"}
            size={getButtonSize()}
            startIcon={action.icon}
            onClick={action.onClick}
            disabled={action.disabled}
            className="modern-btn"
            sx={{
              minHeight: size === "large" ? 48 : size === "small" ? 32 : 40,
              justifyContent: layout === "grid" ? "flex-start" : "center",
              textTransform: "none",
              fontWeight: 500,
              borderRadius: "var(--radius-md)",
              transition: "all var(--transition-fast)",
              "&:hover": {
                transform: "translateY(-1px)",
                boxShadow: "var(--shadow-md)",
              },
              "&.MuiButton-containedPrimary": {
                backgroundColor: "var(--primary-600)",
                "&:hover": {
                  backgroundColor: "var(--primary-700)",
                },
              },
              "&.MuiButton-containedSecondary": {
                backgroundColor: "var(--secondary-600)",
                "&:hover": {
                  backgroundColor: "var(--secondary-700)",
                },
              },
              "&.MuiButton-containedSuccess": {
                backgroundColor: "var(--success-600)",
                "&:hover": {
                  backgroundColor: "var(--success-700)",
                },
              },
              "&.MuiButton-containedWarning": {
                backgroundColor: "var(--warning-600)",
                "&:hover": {
                  backgroundColor: "var(--warning-700)",
                },
              },
              "&.MuiButton-containedError": {
                backgroundColor: "var(--error-600)",
                "&:hover": {
                  backgroundColor: "var(--error-700)",
                },
              },
              "&.MuiButton-outlinedPrimary": {
                borderColor: "var(--primary-600)",
                color: "var(--primary-600)",
                "&:hover": {
                  backgroundColor: "var(--primary-50)",
                  borderColor: "var(--primary-700)",
                },
              },
            }}
          >
            {action.label}
          </Button>
        ))}
      </Box>
    </Paper>
  );
};

// Predefined common quick actions
export const commonQuickActions = {
  add: (onClick: () => void): QuickAction => ({
    id: "add",
    label: "Add New",
    icon: <Add />,
    color: "primary",
    variant: "contained",
    onClick,
  }),
  edit: (onClick: () => void): QuickAction => ({
    id: "edit",
    label: "Edit",
    icon: <Edit />,
    color: "secondary",
    variant: "outlined",
    onClick,
  }),
  delete: (onClick: () => void): QuickAction => ({
    id: "delete",
    label: "Delete",
    icon: <Delete />,
    color: "error",
    variant: "outlined",
    onClick,
  }),
  download: (onClick: () => void): QuickAction => ({
    id: "download",
    label: "Download",
    icon: <Download />,
    color: "info",
    variant: "outlined",
    onClick,
  }),
  upload: (onClick: () => void): QuickAction => ({
    id: "upload",
    label: "Upload",
    icon: <Upload />,
    color: "success",
    variant: "outlined",
    onClick,
  }),
  share: (onClick: () => void): QuickAction => ({
    id: "share",
    label: "Share",
    icon: <Share />,
    color: "info",
    variant: "text",
    onClick,
  }),
};

export default QuickActions;
