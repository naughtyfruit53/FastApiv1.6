import React, { ReactNode } from 'react';
import { Box } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import MobileLayout from './MobileLayout';

interface MobileFormLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  onBack?: () => void;
  onSubmit?: () => void;
  rightActions?: ReactNode;
  showBackButton?: boolean;
  showBottomNav?: boolean;
  className?: string;
}

const MobileFormLayout: React.FC<MobileFormLayoutProps> = ({
  title,
  subtitle,
  children,
  onBack,
  rightActions,
  showBackButton = true,
  showBottomNav = false,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();

  if (!isMobile) {
    // On desktop, just render children without mobile layout
    return <Box className={className}>{children}</Box>;
  }

  return (
    <MobileLayout
      title={title}
      subtitle={subtitle}
      onBack={onBack}
      rightActions={rightActions}
      showBackButton={showBackButton}
      showBottomNav={showBottomNav}
      showMenuButton={false}
      className={className}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          '& .MuiTextField-root': {
            '& .MuiInputBase-root': {
              minHeight: 48,
            },
            '& .MuiInputBase-input': {
              fontSize: '1rem',
            },
          },
          '& .MuiButton-root': {
            minHeight: 48,
            fontSize: '1rem',
          },
        }}
      >
        {children}
      </Box>
    </MobileLayout>
  );
};

export default MobileFormLayout;