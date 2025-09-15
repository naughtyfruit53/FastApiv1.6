import React, { ReactNode } from 'react';
import { Box } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import MobileHeader from './MobileHeader';
import MobileBottomNav from './MobileBottomNav';

interface MobileLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  onBack?: () => void;
  onMenuToggle?: () => void;
  rightActions?: ReactNode;
  showBackButton?: boolean;
  showMenuButton?: boolean;
  showBottomNav?: boolean;
  headerElevation?: number;
  className?: string;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({
  children,
  title = 'FastAPI v1.6',
  subtitle,
  onBack,
  onMenuToggle,
  rightActions,
  showBackButton = false,
  showMenuButton = true,
  showBottomNav = true,
  headerElevation = 1,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();

  if (!isMobile) {
    return <>{children}</>;
  }

  return (
    <Box
      className={`mobile-layout ${className}`}
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.default',
        overflow: 'hidden',
      }}
    >
      <MobileHeader
        title={title}
        subtitle={subtitle}
        onBack={onBack}
        onMenuToggle={onMenuToggle}
        rightActions={rightActions}
        showBackButton={showBackButton}
        showMenuButton={showMenuButton}
        elevation={headerElevation}
      />

      <Box
        className="mobile-content"
        sx={{
          flex: 1,
          padding: 2,
          paddingBottom: showBottomNav ? 'calc(9 * 8px + max(env(safe-area-inset-bottom), constant(safe-area-inset-bottom)))' : 2,  // Updated for safe area (9 theme spacing = 72px + inset)
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
        }}
      >
        {children}
      </Box>

      {showBottomNav && <MobileBottomNav />}
    </Box>
  );
};

export default MobileLayout;