/**
 * VerticalFormLayout Component
 * Consistent stacked single-column form layout with spacing and validation messages
 */
import React from 'react';
import { Box, Stack, FormHelperText, Typography, Divider } from '@mui/material';

interface VerticalFormLayoutProps {
  children: React.ReactNode;
  spacing?: number;
  maxWidth?: string | number;
  showDividers?: boolean;
}

/**
 * Main container for vertical form layouts
 */
export const VerticalFormLayout: React.FC<VerticalFormLayoutProps> = ({
  children,
  spacing = 3,
  maxWidth,
  showDividers = false,
}) => {
  return (
    <Box sx={{ maxWidth, mx: 'auto', width: '100%' }}>
      <Stack
        spacing={spacing}
        divider={showDividers ? <Divider flexItem /> : undefined}
      >
        {children}
      </Stack>
    </Box>
  );
};

interface FormSectionProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  spacing?: number;
}

/**
 * Form section with optional title and description
 */
export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  spacing = 2,
}) => {
  return (
    <Box>
      {title && (
        <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
          {title}
        </Typography>
      )}
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
      )}
      <Stack spacing={spacing}>{children}</Stack>
    </Box>
  );
};

interface FormFieldProps {
  label?: string;
  required?: boolean;
  error?: string;
  helperText?: string;
  children: React.ReactNode;
}

/**
 * Form field wrapper with label and validation message support
 */
export const FormField: React.FC<FormFieldProps> = ({
  label,
  required,
  error,
  helperText,
  children,
}) => {
  return (
    <Box>
      {label && (
        <Typography
          variant="body2"
          fontWeight="medium"
          sx={{ mb: 0.5 }}
          component="label"
        >
          {label}
          {required && (
            <Box component="span" sx={{ color: 'error.main', ml: 0.5 }}>
              *
            </Box>
          )}
        </Typography>
      )}
      {children}
      {(error || helperText) && (
        <FormHelperText error={!!error}>
          {error || helperText}
        </FormHelperText>
      )}
    </Box>
  );
};

interface FormRowProps {
  children: React.ReactNode;
  gap?: number;
}

/**
 * Horizontal row within vertical form for side-by-side fields
 */
export const FormRow: React.FC<FormRowProps> = ({ children, gap = 2 }) => {
  return (
    <Box sx={{ display: 'flex', gap, flexWrap: 'wrap' }}>
      {React.Children.map(children, (child) => (
        <Box sx={{ flex: 1, minWidth: 0 }}>{child}</Box>
      ))}
    </Box>
  );
};

export default VerticalFormLayout;
