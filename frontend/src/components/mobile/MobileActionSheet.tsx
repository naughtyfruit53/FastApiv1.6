import React, { ReactNode } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileActionSheetAction {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  destructive?: boolean;
  disabled?: boolean;
}

interface MobileActionSheetProps {
  open: boolean;
  onClose: () => void;
  actions: MobileActionSheetAction[];
  title?: string;
  cancelLabel?: string;
}

const MobileActionSheet: React.FC<MobileActionSheetProps> = ({
  open,
  onClose,
  actions,
  title,
  cancelLabel = 'Cancel',
}) => {
  const { isMobile } = useMobileDetection();

  if (!isMobile || !open) return null;

  return (
    <>
      {/* Backdrop */}
      <Box
        onClick={onClose}
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 1300,
          opacity: open ? 1 : 0,
          transition: 'opacity 0.3s ease',
        }}
      />

      {/* Action Sheet */}
      <Paper
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          borderRadius: '12px 12px 0 0',
          zIndex: 1301,
          transform: open ? 'translateY(0)' : 'translateY(100%)',
          transition: 'transform 0.3s ease',
          boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.15)',
          overflow: 'hidden',
        }}
      >
        <Box sx={{ padding: 2 }}>
          {/* Handle */}
          <Box
            sx={{
              width: 36,
              height: 4,
              backgroundColor: 'divider',
              borderRadius: 2,
              margin: '0 auto 16px',
            }}
          />

          {/* Title */}
          {title && (
            <Box sx={{ textAlign: 'center', marginBottom: 2 }}>
              <Typography variant="h6" color="text.secondary">
                {title}
              </Typography>
            </Box>
          )}

          {/* Actions */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {actions.map((action, index) => (
              <Box
                key={index}
                onClick={() => {
                  if (!action.disabled) {
                    action.onClick();
                    onClose();
                  }
                }}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: 2,
                  borderRadius: 2,
                  cursor: action.disabled ? 'not-allowed' : 'pointer',
                  opacity: action.disabled ? 0.5 : 1,
                  backgroundColor: 'transparent',
                  '&:active': !action.disabled ? {
                    backgroundColor: 'action.hover',
                  } : {},
                  transition: 'background-color 0.2s ease',
                }}
              >
                {action.icon && (
                  <Box sx={{ marginRight: 2, color: action.destructive ? 'error.main' : 'text.primary' }}>
                    {action.icon}
                  </Box>
                )}
                <Typography
                  variant="body1"
                  sx={{
                    color: action.destructive ? 'error.main' : 'text.primary',
                    fontWeight: 500,
                  }}
                >
                  {action.label}
                </Typography>
              </Box>
            ))}

            {/* Cancel Button */}
            <Box
              onClick={onClose}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 2,
                marginTop: 1,
                borderRadius: 2,
                backgroundColor: 'action.hover',
                cursor: 'pointer',
                '&:active': {
                  backgroundColor: 'action.selected',
                },
                transition: 'background-color 0.2s ease',
              }}
            >
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {cancelLabel}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Paper>
    </>
  );
};

export default MobileActionSheet;