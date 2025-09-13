import React, { ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardActions, Typography } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileCardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  elevation?: number;
  onClick?: () => void;
  className?: string;
}

const MobileCard: React.FC<MobileCardProps> = ({
  title,
  subtitle,
  children,
  actions,
  elevation = 1,
  onClick,
  className = '',
}) => {
  const { isMobile } = useMobileDetection();

  const cardStyles = isMobile ? {
    borderRadius: 3,
    marginBottom: 2,
    '&:active': onClick ? {
      backgroundColor: 'action.hover',
      transform: 'scale(0.98)',
    } : {},
    transition: 'all 0.2s ease',
    cursor: onClick ? 'pointer' : 'default',
  } : {
    borderRadius: 2,
    marginBottom: 3,
    cursor: onClick ? 'pointer' : 'default',
  };

  const contentStyles = isMobile ? {
    padding: 2,
    '&:last-child': {
      paddingBottom: 2,
    },
  } : {};

  const Card_Component = (
    <Card
      elevation={elevation}
      onClick={onClick}
      className={`mobile-card ${className}`}
      sx={cardStyles}
    >
      {(title || subtitle) && (
        <CardHeader
          title={title && (
            <Typography
              variant={isMobile ? 'h6' : 'h6'}
              sx={{
                fontSize: isMobile ? '1.125rem' : '1.25rem',
                fontWeight: 600,
                lineHeight: 1.2,
              }}
            >
              {title}
            </Typography>
          )}
          subheader={subtitle && (
            <Typography
              variant="body2"
              sx={{
                fontSize: isMobile ? '0.875rem' : '0.875rem',
                color: 'text.secondary',
                marginTop: 0.5,
              }}
            >
              {subtitle}
            </Typography>
          )}
          sx={{
            padding: isMobile ? 2 : 3,
            paddingBottom: title || subtitle ? (isMobile ? 1 : 2) : 0,
          }}
        />
      )}

      <CardContent sx={contentStyles}>
        {children}
      </CardContent>

      {actions && (
        <CardActions
          sx={{
            padding: isMobile ? 2 : 3,
            paddingTop: isMobile ? 1 : 2,
            gap: 1,
            justifyContent: 'flex-end',
          }}
        >
          {actions}
        </CardActions>
      )}
    </Card>
  );

  return Card_Component;
};

export default MobileCard;