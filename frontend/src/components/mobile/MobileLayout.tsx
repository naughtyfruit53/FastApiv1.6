import React, { ReactNode, useState } from 'react';
import { Box } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { useAuth } from '../../context/AuthContext';
import MobileHeader from './MobileHeader';
import MobileBottomNav from './MobileBottomNav';
import MobileDrawerNavigation from './MobileDrawerNavigation';

interface MobileLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  onBack?: () => void;
  rightActions?: ReactNode;
  showBackButton?: boolean;
  showMenuButton?: boolean;
  showSearchButton?: boolean;
  showHomeButton?: boolean;
  showBottomNav?: boolean;
  headerElevation?: number;
  className?: string;
}

const MobileLayout: React.FC<MobileLayoutProps> = ({
  children,
  title = 'FastAPI v1.6',
  subtitle,
  onBack,
  rightActions,
  showBackButton = false,
  showMenuButton = true,
  showSearchButton = true,
  showHomeButton = false,
  showBottomNav = true,
  headerElevation = 1,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();
  const { user, logout } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);

  if (!isMobile) {
    return <>{children}</>;
  }

  const handleMenuToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
  };

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
        onMenuToggle={handleMenuToggle}
        rightActions={rightActions}
        showBackButton={showBackButton}
        showMenuButton={showMenuButton}
        showSearchButton={showSearchButton}
        showHomeButton={showHomeButton}
        elevation={headerElevation}
        user={user}
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

      {/* Enhanced Mobile Drawer Navigation */}
      <MobileDrawerNavigation
        open={drawerOpen}
        onClose={handleDrawerClose}
        user={user}
        onLogout={logout}
      />
    </Box>
  );
};

export default MobileLayout;