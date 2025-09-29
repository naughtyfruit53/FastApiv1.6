import React, { useState, useRef, ReactNode } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { Refresh } from '@mui/icons-material';

interface MobilePullToRefreshProps {
  children: ReactNode;
  onRefresh: () => Promise<void>;
  isRefreshing?: boolean;
  refreshThreshold?: number;
  enabled?: boolean;
}

const MobilePullToRefresh: React.FC<MobilePullToRefreshProps> = ({
  children,
  onRefresh,
  isRefreshing = false,
  refreshThreshold = 80,
  enabled = true,
}) => {
  const [pullDistance, setPullDistance] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isTriggered, setIsTriggered] = useState(false);
  const startY = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!enabled || isRefreshing) return;
    
    const scrollTop = containerRef.current?.scrollTop || 0;
    if (scrollTop > 0) return; // Only allow pull-to-refresh at the top
    
    startY.current = e.touches[0].clientY;
    setIsDragging(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || !enabled || isRefreshing) return;
    
    const currentY = e.touches[0].clientY;
    const distance = currentY - startY.current;
    
    if (distance > 0) {
      e.preventDefault(); // Prevent scrolling
      const adjustedDistance = Math.min(distance * 0.5, refreshThreshold * 1.5);
      setPullDistance(adjustedDistance);
      setIsTriggered(adjustedDistance >= refreshThreshold);
    }
  };

  const handleTouchEnd = async () => {
    if (!isDragging || !enabled) return;
    
    setIsDragging(false);
    
    if (isTriggered && pullDistance >= refreshThreshold) {
      try {
        await onRefresh();
      } catch (error) {
        console.error('Refresh failed:', error);
      }
    }
    
    setPullDistance(0);
    setIsTriggered(false);
  };

  const getRefreshIndicatorOpacity = () => {
    if (isRefreshing) return 1;
    return Math.min(pullDistance / refreshThreshold, 1);
  };

  const getRefreshIndicatorTransform = () => {
    if (isRefreshing) return 'translateY(0) scale(1)';
    const scale = Math.min(pullDistance / refreshThreshold, 1);
    return `translateY(${Math.max(pullDistance - 40, 0)}px) scale(${scale})`;
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        height: '100%',
        overflow: 'auto',
        '-webkit-overflow-scrolling': 'touch',
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Pull-to-refresh indicator */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: getRefreshIndicatorOpacity(),
          transform: getRefreshIndicatorTransform(),
          transition: isRefreshing || !isDragging ? 'all 0.3s ease' : 'none',
          py: 1,
          px: 2,
          bgcolor: 'background.paper',
          borderRadius: 4,
          boxShadow: 1,
          minWidth: 120,
        }}
      >
        {isRefreshing ? (
          <>
            <CircularProgress size={24} sx={{ mb: 0.5 }} />
            <Typography variant="caption" color="text.secondary">
              Refreshing...
            </Typography>
          </>
        ) : (
          <>
            <Refresh
              sx={{
                mb: 0.5,
                transform: isTriggered ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s ease',
                color: isTriggered ? 'primary.main' : 'text.secondary',
              }}
            />
            <Typography
              variant="caption"
              color={isTriggered ? 'primary.main' : 'text.secondary'}
            >
              {isTriggered ? 'Release to refresh' : 'Pull to refresh'}
            </Typography>
          </>
        )}
      </Box>

      {/* Content with dynamic padding for refresh indicator */}
      <Box
        sx={{
          paddingTop: pullDistance > 0 ? `${Math.min(pullDistance, 60)}px` : 0,
          transition: !isDragging ? 'padding-top 0.3s ease' : 'none',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default MobilePullToRefresh;