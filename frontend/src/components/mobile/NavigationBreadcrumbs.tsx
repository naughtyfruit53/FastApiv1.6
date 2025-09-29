import React from 'react';
import { 
  Box, 
  Breadcrumbs, 
  Link, 
  Typography, 
  IconButton,
  Chip
} from '@mui/material';
import { 
  NavigateNext, 
  Home, 
  ArrowBack
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactElement;
  current?: boolean;
}

interface NavigationBreadcrumbsProps {
  items: BreadcrumbItem[];
  showBackButton?: boolean;
  showHomeButton?: boolean;
  onBack?: () => void;
  maxItems?: number;
}

const NavigationBreadcrumbs: React.FC<NavigationBreadcrumbsProps> = ({
  items,
  showBackButton = true,
  showHomeButton = false,
  onBack,
  maxItems = 3
}) => {
  const router = useRouter();
  const { isMobile } = useMobileDetection();

  // Early return after all hooks
  if (!isMobile) {
    return null;
  }

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  const handleNavigate = (path: string) => {
    if (path) {
      router.push(path);
    }
  };

  // Truncate breadcrumbs for mobile display
  const displayItems = items.length > maxItems 
    ? [items[0], { label: '...', path: undefined }, ...items.slice(-2)]
    : items;

  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: 1,
      px: 2,
      py: 1,
      backgroundColor: 'background.paper',
      borderBottom: '1px solid',
      borderColor: 'divider',
      minHeight: 48
    }}>
      {/* Back Button */}
      {showBackButton && (
        <IconButton
          size="small"
          onClick={handleBack}
          sx={{
            mr: 1,
            backgroundColor: 'action.hover',
            '&:hover': {
              backgroundColor: 'action.selected',
            }
          }}
        >
          <ArrowBack />
        </IconButton>
      )}

      {/* Home Button */}
      {showHomeButton && (
        <IconButton
          size="small"
          onClick={() => handleNavigate('/mobile/dashboard')}
          sx={{
            mr: 1,
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

      {/* Breadcrumb Navigation */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Breadcrumbs
          separator={<NavigateNext fontSize="small" />}
          maxItems={maxItems}
          sx={{
            '& .MuiBreadcrumbs-li': {
              display: 'flex',
              alignItems: 'center',
            },
            '& .MuiBreadcrumbs-separator': {
              margin: '0 4px',
              color: 'text.secondary',
            }
          }}
        >
          {displayItems.map((item, index) => {
            const isLast = index === displayItems.length - 1;
            const isEllipsis = item.label === '...';
            
            if (isEllipsis) {
              return (
                <Typography
                  key={index}
                  variant="body2"
                  color="text.secondary"
                  sx={{ 
                    fontWeight: 500,
                    fontSize: '0.875rem'
                  }}
                >
                  ...
                </Typography>
              );
            }

            if (isLast || !item.path) {
              return (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {item.icon}
                  <Typography
                    variant="body2"
                    color={isLast ? 'text.primary' : 'text.secondary'}
                    sx={{ 
                      fontWeight: isLast ? 600 : 400,
                      fontSize: '0.875rem',
                      textOverflow: 'ellipsis',
                      overflow: 'hidden',
                      whiteSpace: 'nowrap',
                      maxWidth: '120px'
                    }}
                  >
                    {item.label}
                  </Typography>
                  {isLast && item.current && (
                    <Chip
                      label="Current"
                      size="small"
                      color="primary"
                      variant="outlined"
                      sx={{ 
                        fontSize: '0.6rem', 
                        height: 18,
                        ml: 0.5
                      }}
                    />
                  )}
                </Box>
              );
            }

            return (
              <Link
                key={index}
                underline="hover"
                color="inherit"
                onClick={() => handleNavigate(item.path!)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  cursor: 'pointer',
                  color: 'text.secondary',
                  '&:hover': {
                    color: 'primary.main',
                  }
                }}
              >
                {item.icon}
                <Typography
                  variant="body2"
                  sx={{ 
                    fontSize: '0.875rem',
                    textOverflow: 'ellipsis',
                    overflow: 'hidden',
                    whiteSpace: 'nowrap',
                    maxWidth: '100px'
                  }}
                >
                  {item.label}
                </Typography>
              </Link>
            );
          })}
        </Breadcrumbs>
      </Box>
    </Box>
  );
};

export default NavigationBreadcrumbs;