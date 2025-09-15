import React, { ReactNode } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, useTheme } from '@mui/material';
import { ArrowBack, Menu as MenuIcon } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  onMenuToggle?: () => void;
  rightActions?: ReactNode;
  showBackButton?: boolean;
  showMenuButton?: boolean;
  elevation?: number;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({
  title,
  subtitle,
  onBack,
  onMenuToggle,
  rightActions,
  showBackButton = false,
  showMenuButton = true,
  elevation = 1,
}) => {
  const theme = useTheme();
  const { isMobile } = useMobileDetection();

  if (!isMobile) return null;

  return (
    <AppBar 
      position="sticky" 
      elevation={elevation}
      sx={{
        backgroundColor: 'background.paper',
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar
        sx={{
          minHeight: '56px !important',
          paddingLeft: theme.spacing(1),
          paddingRight: theme.spacing(1),
        }}
      >
        {showBackButton && onBack && (
          <IconButton
            edge="start"
            onClick={onBack}
            sx={{
              marginRight: 1,
              minWidth: 44,
              minHeight: 44,
            }}
          >
            <ArrowBack />
          </IconButton>
        )}

        {showMenuButton && !showBackButton && (
          <IconButton
            edge="start"
            onClick={onMenuToggle}
            sx={{
              marginRight: 1,
              minWidth: 44,
              minHeight: 44,
            }}
          >
            <MenuIcon />
          </IconButton>
        )}

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            variant="h6"
            noWrap
            sx={{
              fontSize: '1.125rem',
              fontWeight: 600,
              lineHeight: 1.2,
            }}
          >
            {title}
          </Typography>
          {subtitle && (
            <Typography
              variant="body2"
              noWrap
              sx={{
                fontSize: '0.875rem',
                color: 'text.secondary',
                lineHeight: 1,
                marginTop: 0.25,
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>

        {rightActions && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {rightActions}
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default MobileHeader;