import React from 'react';
import { Box, Typography, Container } from '@mui/material';

export interface DashboardLayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  className?: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  title,
  subtitle,
  children,
  actions,
  maxWidth = 'lg',
  className = ''
}) => {
  return (
    <Box className={`modern-dashboard ${className}`}>
      <Container maxWidth={maxWidth} className="modern-dashboard-container">
        <Box className="modern-dashboard-header">
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'flex-start',
            flexWrap: 'wrap',
            gap: 2
          }}>
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
            {actions && (
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                {actions}
              </Box>
            )}
          </Box>
        </Box>
        
        <Box sx={{ minHeight: '60vh' }}>
          {children}
        </Box>
      </Container>
    </Box>
  );
};

export default DashboardLayout;