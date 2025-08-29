import React from 'react';
import { Box, Typography } from '@mui/material';
import { TrendingUp, TrendingDown, Minus } from '@mui/icons-material';

export interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  description?: string;
  trend?: {
    value: number;
    period: string;
    direction: 'up' | 'down' | 'neutral';
  };
  loading?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color = 'primary',
  description,
  trend,
  loading = false,
  size = 'medium',
  className = ''
}) => {
  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      // Format numbers with proper localization
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`;
      } else if (val >= 1000) {
        return `${(val / 1000).toFixed(1)}K`;
      }
      return val.toLocaleString();
    }
    return val;
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    
    switch (trend.direction) {
      case 'up':
        return <TrendingUp sx={{ fontSize: 16 }} />;
      case 'down':
        return <TrendingDown sx={{ fontSize: 16 }} />;
      case 'neutral':
      default:
        return <Minus sx={{ fontSize: 16 }} />;
    }
  };

  const getTrendColor = () => {
    if (!trend) return 'inherit';
    
    switch (trend.direction) {
      case 'up':
        return 'var(--success-600)';
      case 'down':
        return 'var(--error-600)';
      case 'neutral':
      default:
        return 'var(--text-secondary)';
    }
  };

  if (loading) {
    return (
      <Box
        className={`modern-metric-card ${color} ${className}`}
        sx={{
          minHeight: size === 'large' ? 140 : size === 'small' ? 100 : 120,
        }}
      >
        <Box className="metric-card-header">
          <Box className={`metric-card-icon ${color}`}>
            <Box className="modern-skeleton" sx={{ width: 24, height: 24, borderRadius: '4px' }} />
          </Box>
          <Box className="metric-card-content" sx={{ flex: 1 }}>
            <Box className="modern-skeleton" sx={{ height: 16, width: '60%', mb: 1 }} />
            <Box className="modern-skeleton" sx={{ height: 24, width: '80%' }} />
          </Box>
        </Box>
        {description && (
          <Box className="modern-skeleton" sx={{ height: 12, width: '90%', mt: 2 }} />
        )}
      </Box>
    );
  }

  return (
    <Box 
      className={`modern-metric-card ${color} ${className} animate-fade-in-up`}
      sx={{
        minHeight: size === 'large' ? 140 : size === 'small' ? 100 : 120,
      }}
    >
      <Box className="metric-card-header">
        <Box className={`metric-card-icon ${color}`}>
          {React.cloneElement(icon, { sx: { fontSize: 24 } })}
        </Box>
        <Box className="metric-card-content">
          <Typography className="metric-card-title" variant="body2">
            {title}
          </Typography>
          <Typography className="metric-card-value" variant="h4">
            {formatValue(value)}
          </Typography>
        </Box>
      </Box>
      
      {description && (
        <Typography className="metric-card-description" variant="body2">
          {description}
        </Typography>
      )}

      {trend && (
        <Box 
          className={`metric-card-trend ${trend.direction}`}
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            gap: 0.5,
            mt: 1,
            color: getTrendColor()
          }}
        >
          {getTrendIcon()}
          <Typography variant="caption" sx={{ fontWeight: 500 }}>
            {trend.value > 0 ? '+' : ''}{trend.value}% {trend.period}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default MetricCard;