import React, { ReactNode } from 'react';
import { Box, Typography, Container } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import MobileLayout from './MobileLayout';
import { useMobileNav } from '../../context/MobileNavContext';

export interface MobileDashboardLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  onBack?: () => void;
  onMenuToggle?: () => void;
  showBackButton?: boolean;
  showBottomNav?: boolean;
  className?: string;
}

const MobileDashboardLayout: React.FC<MobileDashboardLayoutProps> = ({
  title,
  subtitle,
  children,
  actions,
  onBack,
  onMenuToggle,
  showBackButton = false,
  showBottomNav = true,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();

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
  const effectiveToggle = onMenuToggle || contextToggle;

  return (
    <MobileLayout
      title={title}
      subtitle={subtitle}
      onBack={onBack}
      onMenuToggle={effectiveToggle}
      rightActions={actions}
      showBackButton={showBackButton}
      showBottomNav={showBottomNav}
      className={className}
    >
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