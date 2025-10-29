// frontend/src/components/DashboardLayout.tsx
import React from "react";
import { Box, Typography, Container } from "@mui/material";
import MegaMenu from "./MegaMenu";
import { useAuth } from "../context/AuthContext";

export interface DashboardLayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  maxWidth?: "xs" | "sm" | "md" | "lg" | "xl" | false;
  className?: string;
  showMegaMenu?: boolean;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  title,
  subtitle,
  children,
  actions,
  maxWidth = "lg",
  className = "",
  showMegaMenu = true,
}) => {
  const { user, logout } = useAuth();

  return (
    <>
      {showMegaMenu && (
        <MegaMenu
          user={user}
          onLogout={logout}
          isVisible={true}
        />
      )}
      <Box
        className={`modern-dashboard ${className}`}
        sx={{
          opacity: 0,
          animation: "fadeInUp 0.6s ease-out forwards",
          "@keyframes fadeInUp": {
            from: {
              opacity: 0,
              transform: "translateY(30px)",
            },
            to: {
              opacity: 1,
              transform: "translateY(0)",
            },
          },
          mt: showMegaMenu ? 2 : 0,
        }}
      >
        <Container maxWidth={maxWidth} className="modern-dashboard-container">
          <Box
            className="modern-dashboard-header"
            sx={{
              mb: 4,
              position: "relative",
              "&::after": {
                content: '""',
                position: "absolute",
                bottom: "-16px",
                left: 0,
                width: "60px",
                height: "3px",
                background:
                  "linear-gradient(90deg, var(--primary-500), var(--primary-100))",
                borderRadius: "2px",
              },
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                flexWrap: "wrap",
                gap: 2,
              }}
            >
              <Box>
                <Typography className="modern-dashboard-title" variant="h3">
                  {title}
                </Typography>
                {subtitle && (
                  <Typography className="modern-dashboard-subtitle" variant="h6">
                    {subtitle}
                  </Typography>
                )}
              </Box>
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                {actions}
              </Box>
            </Box>
          </Box>
          <Box
            sx={{
              minHeight: "60vh",
              position: "relative",
              overflow: "visible",
              "& > *": {
                opacity: 0,
                animation: "fadeInUp 0.8s ease-out 0.2s forwards",
              },
            }}
          >
            {children}
          </Box>
        </Container>
      </Box>
    </>
  );
};

export default DashboardLayout;