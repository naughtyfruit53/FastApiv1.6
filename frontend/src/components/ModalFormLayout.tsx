// frontend/src/components/ModalFormLayout.tsx
/**
 * ModalFormLayout - A consistent layout component for modal forms
 * 
 * Provides a stacked single-column layout for form fields inside modals,
 * ensuring consistent spacing, styling, and responsive behavior across
 * all modal forms in the application.
 * 
 * Features:
 * - Stacked single-column fields for better mobile experience
 * - Consistent spacing and padding
 * - Optional sections with headers
 * - Responsive design
 * - Hidden for print/PDF
 */

import React from "react";
import {
  Box,
  Typography,
  Divider,
  useTheme,
  useMediaQuery,
} from "@mui/material";

interface FormSectionProps {
  /** Section title */
  title?: string;
  /** Section description */
  description?: string;
  /** Child form fields */
  children: React.ReactNode;
  /** Whether to show a divider after this section */
  showDivider?: boolean;
}

/**
 * FormSection - Groups related form fields with an optional title
 */
export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  showDivider = false,
}) => {
  return (
    <Box sx={{ mb: 3 }}>
      {title && (
        <Typography
          variant="subtitle1"
          fontWeight={600}
          color="text.primary"
          sx={{ mb: 1 }}
        >
          {title}
        </Typography>
      )}
      {description && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          {description}
        </Typography>
      )}
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {children}
      </Box>
      {showDivider && <Divider sx={{ mt: 3 }} />}
    </Box>
  );
};

interface ModalFormLayoutProps {
  /** Form content */
  children: React.ReactNode;
  /** Maximum width for the form (default: 100%) */
  maxWidth?: number | string;
  /** Additional padding (default: 2 = 16px) */
  padding?: number;
  /** Custom styling */
  sx?: object;
}

/**
 * ModalFormLayout - Main layout wrapper for modal forms
 * 
 * Usage:
 * ```tsx
 * <ModalFormLayout>
 *   <FormSection title="Basic Information">
 *     <TextField label="Name" fullWidth />
 *     <TextField label="Email" fullWidth />
 *   </FormSection>
 *   <FormSection title="Address" showDivider>
 *     <TextField label="Street" fullWidth />
 *     <TextField label="City" fullWidth />
 *   </FormSection>
 * </ModalFormLayout>
 * ```
 */
const ModalFormLayout: React.FC<ModalFormLayoutProps> = ({
  children,
  maxWidth = "100%",
  padding = 2,
  sx = {},
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        maxWidth: maxWidth,
        mx: "auto",
        p: padding,
        // Hide for print/PDF
        "@media print": {
          display: "none",
        },
        // Responsive adjustments
        ...(isMobile && {
          p: 1.5,
        }),
        ...sx,
      }}
    >
      {children}
    </Box>
  );
};

/**
 * FieldRow - A single row for form fields
 * Can contain one or more fields that will stack on mobile
 */
interface FieldRowProps {
  /** Child fields */
  children: React.ReactNode;
  /** Number of columns on desktop (1-4, default: 1) */
  columns?: 1 | 2 | 3 | 4;
  /** Gap between fields (default: 2 = 16px) */
  gap?: number;
}

export const FieldRow: React.FC<FieldRowProps> = ({
  children,
  columns = 1,
  gap = 2,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  // On mobile, always stack vertically
  const effectiveColumns = isMobile ? 1 : columns;

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: `repeat(${effectiveColumns}, 1fr)`,
        gap: gap,
        width: "100%",
      }}
    >
      {children}
    </Box>
  );
};

/**
 * FormActions - Container for form action buttons
 * Provides consistent styling for form submission buttons
 */
interface FormActionsProps {
  /** Action buttons */
  children: React.ReactNode;
  /** Alignment: left, center, right, or space-between (default: right) */
  align?: "left" | "center" | "right" | "space-between";
}

export const FormActions: React.FC<FormActionsProps> = ({
  children,
  align = "right",
}) => {
  const justifyContent = {
    left: "flex-start",
    center: "center",
    right: "flex-end",
    "space-between": "space-between",
  }[align];

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent,
        gap: 2,
        mt: 3,
        pt: 2,
        borderTop: "1px solid",
        borderColor: "divider",
      }}
    >
      {children}
    </Box>
  );
};

/**
 * FormError - Display form-level error message
 */
interface FormErrorProps {
  /** Error message */
  message?: string | null;
}

export const FormError: React.FC<FormErrorProps> = ({ message }) => {
  if (!message) return null;

  return (
    <Box
      sx={{
        p: 2,
        mb: 2,
        bgcolor: "error.light",
        color: "error.contrastText",
        borderRadius: 1,
      }}
    >
      <Typography variant="body2">{message}</Typography>
    </Box>
  );
};

export default ModalFormLayout;
