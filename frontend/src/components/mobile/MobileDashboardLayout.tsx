import React, { ReactNode } from 'react';
import { Box, Typography, Container } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { useMobileRouting } from '../../hooks/mobile/useMobileRouting';
import MobileLayout from './MobileLayout';
import NavigationBreadcrumbs from './NavigationBreadcrumbs';
import { useMobileNav } from '../../context/MobileNavContext';

export interface MobileDashboardLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  rightActions?: ReactNode; // For header actions
  onBack?: () => void;
  showBackButton?: boolean;
  showBottomNav?: boolean;
  showBreadcrumbs?: boolean;
  showHomeButton?: boolean;
  className?: string;
}

const MobileDashboardLayout: React.FC<MobileDashboardLayoutProps> = ({
  title,
  subtitle,
  children,
  actions, // Legacy support
  rightActions, // New header actions
  onBack,
  showBackButton = false,
  showBottomNav = true,
  showBreadcrumbs = true,
  showHomeButton = false,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();
  const { getBreadcrumbs, canGoBack, goBack } = useMobileRouting();

  // On desktop, use regular layout
  if (!isMobile) {
    return (
      <Box
        className={`modern-dashboard ${className}`}
        sx={{
          opacity: 0,
          animation: 'fadeInUp 0.6s ease-out forwards',
          '@keyframes fadeInUp': {
            from: {
              opacity: 0,
              transform: 'translateY(30px)',
            },
            to: {
              opacity: 1,
              transform: 'translateY(0)',
            },
          },
        }}
      >
        <Container maxWidth="lg" className="modern-dashboard-container">
          <Box
            className="modern-dashboard-header"
            sx={{
              mb: 4,
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: '-16px',
                left: 0,
                width: '60px',
                height: '3px',
                background:
                  'linear-gradient(90deg, var(--primary-500), var(--primary-100))',
                borderRadius: '2px',
              },
            }}
          >
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                flexWrap: 'wrap',
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
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                {actions}
              </Box>
            </Box>
          </Box>
          <Box
            sx={{
              minHeight: '60vh',
              position: 'relative',
              overflow: 'visible',
              '& > *': {
                opacity: 0,
                animation: 'fadeInUp 0.8s ease-out 0.2s forwards',
              },
            }}
          >
            {children}
          </Box>
        </Container>
      </Box>
    );
  }

  // Mobile layout
  const { onMenuToggle: contextToggle } = useMobileNav();
  const breadcrumbs = getBreadcrumbs();
  
  const handleBackAction = onBack || (canGoBack() ? goBack : undefined);

  return (
    <MobileLayout
      title={title}
      subtitle={subtitle}
      onBack={handleBackAction}
      rightActions={rightActions || actions} // Support both prop names
      showBackButton={showBackButton || (canGoBack() && !showHomeButton)}
      showHomeButton={showHomeButton}
      showBottomNav={showBottomNav}
      className={className}
    >
      {/* Breadcrumbs for navigation context */}
      {showBreadcrumbs && breadcrumbs.length > 1 && (
        <NavigationBreadcrumbs
          items={breadcrumbs}
          showBackButton={false} // Header already has back button
          showHomeButton={false} // Header already has home button
          maxItems={2} // Keep it simple on mobile
        />
      )}
      
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          '& > *': {
            opacity: 0,
            animation: 'mobileSlideIn 0.5s ease-out forwards',
          },
          '& > *:nth-of-type(1)': { animationDelay: '0.1s' },
          '& > *:nth-of-type(2)': { animationDelay: '0.2s' },
          '& > *:nth-of-type(3)': { animationDelay: '0.3s' },
          '& > *:nth-of-type(4)': { animationDelay: '0.4s' },
          '& > *:nth-of-type(5)': { animationDelay: '0.5s' },
          '@keyframes mobileSlideIn': {
            from: {
              opacity: 0,
              transform: 'translateY(20px)',
            },
            to: {
              opacity: 1,
              transform: 'translateY(0)',
            },
          },
        }}
      >
        {children}
      </Box>
    </MobileLayout>
  );
};

export default MobileDashboardLayout;