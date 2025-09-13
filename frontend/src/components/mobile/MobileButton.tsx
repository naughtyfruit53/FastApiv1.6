import React, { ReactNode } from 'react';
import { Button, ButtonProps, CircularProgress } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileButtonProps extends Omit<ButtonProps, 'size'> {
  children: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
  touchFriendly?: boolean;
}

const MobileButton: React.FC<MobileButtonProps> = ({
  children,
  loading = false,
  fullWidth = false,
  touchFriendly = true,
  disabled,
  sx = {},
  ...props
}) => {
  const { isMobile } = useMobileDetection();

  const mobileStyles = isMobile && touchFriendly ? {
    minHeight: 48,
    fontSize: '1rem',
    fontWeight: 500,
    borderRadius: 2,
    padding: '12px 24px',
    transition: 'all 0.2s ease',
    '&:active': {
      transform: 'translateY(1px)',
    },
    '&:disabled': {
      transform: 'none',
    },
    ...sx,
  } : sx;

  return (
    <Button
      {...props}
      disabled={disabled || loading}
      fullWidth={fullWidth}
      size={isMobile ? 'large' : 'medium'}
      sx={mobileStyles}
      startIcon={loading ? <CircularProgress size={16} color="inherit" /> : props.startIcon}
    >
      {children}
    </Button>
  );
};

export default MobileButton;