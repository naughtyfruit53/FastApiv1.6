import React, { ReactNode, useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, useTheme } from '@mui/material';
import { ArrowBack, Menu as MenuIcon, Search, Home } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { useRouter } from 'next/router';
import MobileGlobalSearch from './MobileGlobalSearch';

interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  onMenuToggle?: () => void;
  rightActions?: ReactNode;
  showBackButton?: boolean;
  showMenuButton?: boolean;
  showSearchButton?: boolean;
  showHomeButton?: boolean;
  elevation?: number;
  user?: any;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({
  title,
  subtitle,
  onBack,
  onMenuToggle,
  rightActions,
  showBackButton = false,
  showMenuButton = true,
  showSearchButton = true,
  showHomeButton = false,
  elevation = 1,
  user,
}) => {
  const theme = useTheme();
  const { isMobile } = useMobileDetection();
  const router = useRouter();
  const [searchOpen, setSearchOpen] = useState(false);

  if (!isMobile) return null;

  const handleHomeClick = () => {
    router.push('/mobile/dashboard');
  };

  const handleSearchOpen = () => {
    setSearchOpen(true);
  };

  const handleSearchClose = () => {
    setSearchOpen(false);
  };

  return (
    <>
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

          {showHomeButton && !showBackButton && (
            <IconButton
              edge="start"
              onClick={handleHomeClick}
              sx={{
                marginRight: 1,
                minWidth: 44,
                minHeight: 44,
                backgroundColor: 'primary.light',
                color: 'primary.contrastText',
                '&:hover': {
                  backgroundColor: 'primary.main',
                }
              }}
            >
              <Home />
            </IconButton>
          )}

          {showMenuButton && !showBackButton && !showHomeButton && (
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

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {showSearchButton && (
              <IconButton
                onClick={handleSearchOpen}
                sx={{
                  minWidth: 44,
                  minHeight: 44,
                }}
              >
                <Search />
              </IconButton>
            )}
            {rightActions}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Global Search Dialog */}
      <MobileGlobalSearch
        open={searchOpen}
        onClose={handleSearchClose}
        user={user}
      />
    </>
  );
};

export default MobileHeader;