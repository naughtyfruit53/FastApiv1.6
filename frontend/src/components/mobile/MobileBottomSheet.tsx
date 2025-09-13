import React, { ReactNode, useState, useEffect, useRef } from 'react';
import { Box, Paper, Typography, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileBottomSheetProps {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  height?: 'auto' | 'half' | 'full' | number;
  showHandle?: boolean;
  showCloseButton?: boolean;
  dismissible?: boolean;
  backdrop?: boolean;
  snapPoints?: number[];
  initialSnap?: number;
  onSnapChange?: (snapIndex: number) => void;
}

const MobileBottomSheet: React.FC<MobileBottomSheetProps> = ({
  open,
  onClose,
  children,
  title,
  height = 'auto',
  showHandle = true,
  showCloseButton = false,
  dismissible = true,
  backdrop = true,
  snapPoints = [],
  initialSnap = 0,
  onSnapChange,
}) => {
  const { isMobile } = useMobileDetection();
  const [currentSnap, setCurrentSnap] = useState(initialSnap);
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [currentY, setCurrentY] = useState(0);
  const sheetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && snapPoints.length > 0) {
      setCurrentSnap(initialSnap);
    }
  }, [open, initialSnap, snapPoints]);

  const getSheetHeight = () => {
    if (snapPoints.length > 0) {
      return `${snapPoints[currentSnap]}%`;
    }
    
    switch (height) {
      case 'full':
        return '100%';
      case 'half':
        return '50%';
      case 'auto':
        return 'auto';
      default:
        return typeof height === 'number' ? `${height}px` : height;
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (!dismissible || snapPoints.length === 0) return;
    
    setIsDragging(true);
    setStartY(e.touches[0].clientY);
    setCurrentY(e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || snapPoints.length === 0) return;
    
    const y = e.touches[0].clientY;
    const deltaY = y - startY;
    setCurrentY(y);

    // Only allow downward dragging for closing
    if (deltaY > 0) {
      e.preventDefault();
    }
  };

  const handleTouchEnd = () => {
    if (!isDragging || snapPoints.length === 0) {
      setIsDragging(false);
      return;
    }

    const deltaY = currentY - startY;
    const threshold = 50;

    if (deltaY > threshold) {
      // Snap to next lower point or close
      if (currentSnap < snapPoints.length - 1) {
        const newSnap = currentSnap + 1;
        setCurrentSnap(newSnap);
        onSnapChange?.(newSnap);
      } else {
        onClose();
      }
    } else if (deltaY < -threshold) {
      // Snap to next higher point
      if (currentSnap > 0) {
        const newSnap = currentSnap - 1;
        setCurrentSnap(newSnap);
        onSnapChange?.(newSnap);
      }
    }

    setIsDragging(false);
  };

  const handleBackdropClick = () => {
    if (dismissible) {
      onClose();
    }
  };

  if (!isMobile || !open) return null;

  return (
    <>
      {/* Backdrop */}
      {backdrop && (
        <Box
          onClick={handleBackdropClick}
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1300,
            opacity: open ? 1 : 0,
            transition: 'opacity 0.3s ease',
          }}
        />
      )}

      {/* Bottom Sheet */}
      <Paper
        ref={sheetRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          height: getSheetHeight(),
          borderRadius: '16px 16px 0 0',
          zIndex: 1301,
          transform: open ? 'translateY(0)' : 'translateY(100%)',
          transition: isDragging ? 'none' : 'transform 0.3s ease',
          boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          maxHeight: '95vh',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            padding: '16px 20px 8px',
            borderBottom: title || showCloseButton ? '1px solid' : 'none',
            borderColor: 'divider',
            flexShrink: 0,
          }}
        >
          {/* Handle */}
          {showHandle && (
            <Box
              sx={{
                width: 36,
                height: 4,
                backgroundColor: 'divider',
                borderRadius: 2,
                margin: '0 auto 12px',
                cursor: dismissible ? 'grab' : 'default',
                '&:active': {
                  cursor: dismissible ? 'grabbing' : 'default',
                },
              }}
            />
          )}

          {/* Title and Close Button */}
          {(title || showCloseButton) && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: title ? 1 : 0,
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {title || ''}
              </Typography>
              {showCloseButton && (
                <IconButton
                  onClick={onClose}
                  size="small"
                  sx={{
                    marginLeft: 'auto',
                  }}
                >
                  <CloseIcon />
                </IconButton>
              )}
            </Box>
          )}
        </Box>

        {/* Content */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            padding: 2,
            '-webkit-overflow-scrolling': 'touch',
          }}
        >
          {children}
        </Box>

        {/* Snap Indicator */}
        {snapPoints.length > 1 && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              padding: 1,
              gap: 0.5,
            }}
          >
            {snapPoints.map((_, index) => (
              <Box
                key={index}
                sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  backgroundColor: index === currentSnap ? 'primary.main' : 'divider',
                  transition: 'background-color 0.2s ease',
                }}
              />
            ))}
          </Box>
        )}
      </Paper>
    </>
  );
};

export default MobileBottomSheet;