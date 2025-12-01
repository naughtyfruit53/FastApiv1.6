// frontend/src/components/LogoBadge.tsx
/**
 * LogoBadge - Global bottom-left logo badge component
 * 
 * Displays a small logo/branding badge at the bottom-left corner of the screen.
 * Features:
 * - Fixed position at bottom-left
 * - Does not interfere with toasts (positioned to avoid toast areas)
 * - Hidden during print/PDF export
 * - Responsive sizing for mobile
 */

import React from "react";
import { Box, Typography, useTheme, useMediaQuery } from "@mui/material";
import Image from "next/image";

interface LogoBadgeProps {
  /** Logo image source (optional, uses text if not provided) */
  logoSrc?: string;
  /** Alt text for logo */
  logoAlt?: string;
  /** Text to display (if no logo) */
  text?: string;
  /** Whether to show the badge */
  visible?: boolean;
  /** Custom styling */
  sx?: object;
}

const LogoBadge: React.FC<LogoBadgeProps> = ({
  logoSrc = "/Tritiq.png",
  logoAlt = "Logo",
  text = "TritiQ",
  visible = true,
  sx = {},
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  if (!visible) return null;

  return (
    <Box
      className="logo-badge-container"
      sx={{
        position: "fixed",
        bottom: isMobile ? 70 : 16, // Higher on mobile to avoid bottom nav
        left: 16,
        zIndex: 1000, // Below toasts (usually 1400+) but above most content
        display: "flex",
        alignItems: "center",
        gap: 1,
        padding: isMobile ? "6px 10px" : "8px 12px",
        backgroundColor: "transparent",
        backdropFilter: "none",
        borderRadius: "8px",
        boxShadow: "none",
        border: "none",
        transition: "opacity 0.2s ease-in-out",
        // Hide during print/PDF
        "@media print": {
          display: "none !important",
        },
        // Responsive adjustments
        opacity: 0.85,
        "&:hover": {
          opacity: 1,
        },
        ...sx,
      }}
    >
      {logoSrc ? (
        <Image
          src={logoSrc}
          alt={logoAlt}
          width={98.4} // 25mm ≈ 98.4px
          height={98.4} // 25mm ≈ 98.4px
          style={{ objectFit: "contain", opacity: 0.5 }} // 80% transparent
        />
      ) : (
        <Box
          sx={{
            width: isMobile ? 20 : 24,
            height: isMobile ? 20 : 24,
            borderRadius: "4px",
            backgroundColor: "primary.main",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: "white",
              fontWeight: 700,
              fontSize: isMobile ? "10px" : "12px",
            }}
          >
            {text.charAt(0)}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default LogoBadge;
