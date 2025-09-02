import React from "react";
import { Box, CircularProgress, Typography, Skeleton } from "@mui/material";

export interface ModernLoadingProps {
  type?: "spinner" | "skeleton" | "custom";
  size?: "small" | "medium" | "large";
  message?: string;
  fullScreen?: boolean;
  skeletonType?: "card" | "list" | "text" | "dashboard";
  count?: number;
}

const ModernLoading: React.FC<ModernLoadingProps> = ({
  type = "spinner",
  size = "medium",
  message = "Loading...",
  fullScreen = false,
  skeletonType = "card",
  count = 3,
}) => {
  const getSpinnerSize = () => {
    switch (size) {
      case "small":
        return 24;
      case "large":
        return 48;
      case "medium":
      default:
        return 32;
    }
  };

  const containerStyles = fullScreen
    ? {
        position: "fixed" as const,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "rgba(248, 250, 252, 0.8)",
        backdropFilter: "blur(4px)",
        zIndex: 9999,
      }
    : {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "200px",
        flexDirection: "column" as const,
        gap: 2,
      };

  const renderSkeleton = () => {
    switch (skeletonType) {
      case "dashboard":
        return (
          <Box
            className="modern-grid cols-3"
            sx={{ width: "100%", maxWidth: 1200 }}
          >
            {Array.from({ length: count }).map((_, index) => (
              <Box key={index} className="modern-metric-card" sx={{ p: 3 }}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <Skeleton
                    variant="circular"
                    width={48}
                    height={48}
                    sx={{ mr: 2 }}
                  />
                  <Box sx={{ flex: 1 }}>
                    <Skeleton variant="text" width="60%" height={16} />
                    <Skeleton
                      variant="text"
                      width="80%"
                      height={24}
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </Box>
                <Skeleton variant="text" width="90%" height={12} />
              </Box>
            ))}
          </Box>
        );

      case "card":
        return (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 2,
              width: "100%",
            }}
          >
            {Array.from({ length: count }).map((_, index) => (
              <Box key={index} className="modern-card" sx={{ p: 3 }}>
                <Skeleton
                  variant="text"
                  width="40%"
                  height={24}
                  sx={{ mb: 2 }}
                />
                <Skeleton
                  variant="rectangular"
                  width="100%"
                  height={120}
                  sx={{ mb: 2 }}
                />
                <Skeleton variant="text" width="60%" height={16} />
              </Box>
            ))}
          </Box>
        );

      case "list":
        return (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 1,
              width: "100%",
            }}
          >
            {Array.from({ length: count }).map((_, index) => (
              <Box
                key={index}
                sx={{ display: "flex", alignItems: "center", p: 2 }}
              >
                <Skeleton
                  variant="circular"
                  width={40}
                  height={40}
                  sx={{ mr: 2 }}
                />
                <Box sx={{ flex: 1 }}>
                  <Skeleton variant="text" width="70%" height={20} />
                  <Skeleton
                    variant="text"
                    width="50%"
                    height={16}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              </Box>
            ))}
          </Box>
        );

      case "text":
      default:
        return (
          <Box sx={{ width: "100%" }}>
            {Array.from({ length: count }).map((_, index) => (
              <Skeleton
                key={index}
                variant="text"
                width="100%"
                height={20}
                sx={{ mb: 1 }}
              />
            ))}
          </Box>
        );
    }
  };

  if (type === "skeleton") {
    return <Box sx={containerStyles}>{renderSkeleton()}</Box>;
  }

  if (type === "custom") {
    return (
      <Box sx={containerStyles}>
        <Box
          className="animate-pulse"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 2,
          }}
        >
          <Box
            sx={{
              width: getSpinnerSize() * 2,
              height: getSpinnerSize() * 2,
              borderRadius: "50%",
              background:
                "linear-gradient(45deg, var(--primary-500), var(--secondary-500))",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Box
              sx={{
                width: getSpinnerSize(),
                height: getSpinnerSize(),
                borderRadius: "50%",
                backgroundColor: "var(--bg-surface)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CircularProgress size={getSpinnerSize() / 2} thickness={4} />
            </Box>
          </Box>
          <Typography
            variant="body2"
            color="textSecondary"
            sx={{ fontWeight: 500 }}
          >
            {message}
          </Typography>
        </Box>
      </Box>
    );
  }

  // Default spinner type
  return (
    <Box sx={containerStyles}>
      <CircularProgress
        size={getSpinnerSize()}
        thickness={4}
        sx={{
          color: "var(--primary-600)",
          "& .MuiCircularProgress-circle": {
            strokeLinecap: "round",
          },
        }}
      />
      {message && (
        <Typography
          variant="body2"
          color="textSecondary"
          sx={{
            mt: 2,
            fontWeight: 500,
            fontSize: size === "small" ? "0.75rem" : "0.875rem",
          }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default ModernLoading;
