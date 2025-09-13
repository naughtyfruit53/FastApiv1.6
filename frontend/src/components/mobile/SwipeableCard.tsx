import React, { ReactNode, useState, useRef, useCallback } from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface SwipeAction {
  label: string;
  icon?: ReactNode;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'success';
  action: () => void;
}

interface SwipeableCardProps {
  children: ReactNode;
  leftActions?: SwipeAction[];
  rightActions?: SwipeAction[];
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  disabled?: boolean;
  threshold?: number;
  className?: string;
}

const SwipeableCard: React.FC<SwipeableCardProps> = ({
  children,
  leftActions = [],
  rightActions = [],
  onSwipeLeft,
  onSwipeRight,
  disabled = false,
  threshold = 80,
  className,
}) => {
  const { isMobile } = useMobileDetection();
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [swiping, setSwiping] = useState(false);
  const startX = useRef(0);
  const startY = useRef(0);
  const isDragging = useRef(false);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (disabled || !isMobile) return;
    
    startX.current = e.touches[0].clientX;
    startY.current = e.touches[0].clientY;
    setSwiping(true);
  }, [disabled, isMobile]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (disabled || !isMobile || !swiping) return;

    const currentX = e.touches[0].clientX;
    const currentY = e.touches[0].clientY;
    const deltaX = currentX - startX.current;
    const deltaY = currentY - startY.current;

    // Prevent horizontal swipe if vertical movement is dominant
    if (Math.abs(deltaY) > Math.abs(deltaX) && !isDragging.current) {
      return;
    }

    if (Math.abs(deltaX) > 10) {
      isDragging.current = true;
      e.preventDefault();
    }

    // Limit swipe distance
    const maxSwipe = 120;
    const constrainedOffset = Math.max(-maxSwipe, Math.min(maxSwipe, deltaX));
    setSwipeOffset(constrainedOffset);
  }, [disabled, isMobile, swiping]);

  const handleTouchEnd = useCallback(() => {
    if (disabled || !isMobile) return;

    const absOffset = Math.abs(swipeOffset);
    
    if (absOffset > threshold) {
      if (swipeOffset > 0) {
        // Swiped right
        if (leftActions.length > 0 && leftActions[0]) {
          leftActions[0].action();
        } else if (onSwipeRight) {
          onSwipeRight();
        }
      } else {
        // Swiped left
        if (rightActions.length > 0 && rightActions[0]) {
          rightActions[0].action();
        } else if (onSwipeLeft) {
          onSwipeLeft();
        }
      }
    }

    // Reset state
    setSwipeOffset(0);
    setSwiping(false);
    isDragging.current = false;
  }, [disabled, isMobile, swipeOffset, threshold, leftActions, rightActions, onSwipeLeft, onSwipeRight]);

  const getActionColor = (color: SwipeAction['color']) => {
    switch (color) {
      case 'primary': return 'primary.main';
      case 'secondary': return 'secondary.main';
      case 'error': return 'error.main';
      case 'warning': return 'warning.main';
      case 'success': return 'success.main';
      default: return 'primary.main';
    }
  };

  if (!isMobile) {
    return (
      <Card className={className}>
        <CardContent>{children}</CardContent>
      </Card>
    );
  }

  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 2,
      }}
    >
      {/* Left Actions */}
      {leftActions.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: 120,
            display: 'flex',
            transform: `translateX(${Math.min(0, swipeOffset - 120)}px)`,
            transition: swiping ? 'none' : 'transform 0.3s ease',
          }}
        >
          {leftActions.map((action, index) => (
            <Box
              key={index}
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: getActionColor(action.color),
                cursor: 'pointer',
              }}
              onClick={action.action}
            >
              <Box sx={{ textAlign: 'center', color: 'white' }}>
                {action.icon && (
                  <Box sx={{ marginBottom: 0.5 }}>{action.icon}</Box>
                )}
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {action.label}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      )}

      {/* Right Actions */}
      {rightActions.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            right: 0,
            top: 0,
            bottom: 0,
            width: 120,
            display: 'flex',
            transform: `translateX(${Math.max(0, swipeOffset + 120)}px)`,
            transition: swiping ? 'none' : 'transform 0.3s ease',
          }}
        >
          {rightActions.map((action, index) => (
            <Box
              key={index}
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: getActionColor(action.color),
                cursor: 'pointer',
              }}
              onClick={action.action}
            >
              <Box sx={{ textAlign: 'center', color: 'white' }}>
                {action.icon && (
                  <Box sx={{ marginBottom: 0.5 }}>{action.icon}</Box>
                )}
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {action.label}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      )}

      {/* Main Card */}
      <Card
        className={className}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        sx={{
          position: 'relative',
          transform: `translateX(${swipeOffset}px)`,
          transition: swiping ? 'none' : 'transform 0.3s ease',
          zIndex: 1,
          cursor: disabled ? 'default' : 'grab',
          userSelect: 'none',
          '&:active': {
            cursor: disabled ? 'default' : 'grabbing',
          },
        }}
      >
        <CardContent>{children}</CardContent>
      </Card>
    </Box>
  );
};

export default SwipeableCard;