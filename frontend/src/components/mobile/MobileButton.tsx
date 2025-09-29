import React, { ReactNode, useRef, useEffect } from 'react';
import { Button, ButtonProps, CircularProgress, Box } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileButtonProps extends Omit<ButtonProps, 'size'> {
  children: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
  touchFriendly?: boolean;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  announceStateChanges?: boolean;
  focusOnMount?: boolean;
  hapticFeedback?: boolean;
}

const MobileButton: React.FC<MobileButtonProps> = ({
  children,
  loading = false,
  fullWidth = false,
  touchFriendly = true,
  disabled,
  sx = {},
  accessibilityLabel,
  accessibilityHint,
  announceStateChanges = false,
  focusOnMount = false,
  hapticFeedback = true,
  onClick,
  onFocus,
  onBlur,
  ...props
}) => {
  const { isMobile } = useMobileDetection();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [isPressed, setIsPressed] = React.useState(false);
  const [hasFocus, setHasFocus] = React.useState(false);

  // Focus management
  useEffect(() => {
    if (focusOnMount && buttonRef.current) {
      buttonRef.current.focus();
    }
  }, [focusOnMount]);

  // Enhanced mobile styles with accessibility improvements
  const mobileStyles = isMobile && touchFriendly ? {
    minHeight: 48, // WCAG minimum touch target size
    minWidth: 48,
    fontSize: '1rem',
    fontWeight: 500,
    borderRadius: 2,
    padding: '12px 24px',
    transition: 'all 0.2s ease',
    
    // Enhanced focus indicators for accessibility
    '&:focus': {
      outline: '3px solid',
      outlineColor: 'primary.main',
      outlineOffset: '2px',
      zIndex: 1,
    },
    
    // High contrast mode support
    '@media (prefers-contrast: high)': {
      border: '2px solid',
      '&:focus': {
        outline: '4px solid',
        outlineColor: 'text.primary',
      },
    },
    
    // Reduced motion support
    '@media (prefers-reduced-motion: reduce)': {
      transition: 'none',
      '&:active': {
        transform: 'none',
      },
    },
    
    // Touch feedback
    '&:active': {
      transform: isPressed ? 'translateY(1px)' : 'none',
      transition: 'transform 0.1s ease',
    },
    
    '&:disabled': {
      transform: 'none',
      opacity: 0.6,
    },
    
    // Better color contrast
    '&:hover:not(:disabled)': {
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
    },
    
    ...sx,
  } : {
    // Enhanced focus for desktop
    '&:focus': {
      outline: '2px solid',
      outlineColor: 'primary.main',
      outlineOffset: '2px',
    },
    '@media (prefers-contrast: high)': {
      border: '1px solid',
      '&:focus': {
        outline: '3px solid',
        outlineColor: 'text.primary',
      },
    },
    ...sx,
  };

  const handleTouchStart = () => {
    setIsPressed(true);
    
    // Haptic feedback for supported devices
    if (hapticFeedback && 'vibrate' in navigator) {
      navigator.vibrate(10);
    }
  };

  const handleTouchEnd = () => {
    setIsPressed(false);
  };

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    // Announce state changes for screen readers
    if (announceStateChanges) {
      const announcement = loading ? 'Loading' : 'Action completed';
      // This would integrate with a screen reader announcement system
      console.log('Screen reader announcement:', announcement);
    }

    if (onClick) {
      onClick(event);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (onClick) {
        onClick(event as any);
      }
    }
  };

  const handleFocus = (event: React.FocusEvent<HTMLButtonElement>) => {
    setHasFocus(true);
    if (onFocus) {
      onFocus(event);
    }
  };

  const handleBlur = (event: React.FocusEvent<HTMLButtonElement>) => {
    setHasFocus(false);
    if (onBlur) {
      onBlur(event);
    }
  };

  // Compute accessible label
  const computedAriaLabel = accessibilityLabel || 
    (typeof children === 'string' ? children : 'Button');

  const ariaDescribedBy = accessibilityHint ? `${computedAriaLabel}-hint` : undefined;

  return (
    <Box sx={{ position: 'relative', display: fullWidth ? 'block' : 'inline-block' }}>
      <Button
        {...props}
        ref={buttonRef}
        disabled={disabled || loading}
        fullWidth={fullWidth}
        size={isMobile ? 'large' : 'medium'}
        sx={mobileStyles}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleTouchStart}
        onMouseUp={handleTouchEnd}
        startIcon={loading ? (
          <CircularProgress 
            size={16} 
            color="inherit" 
            aria-label="Loading"
          />
        ) : props.startIcon}
        aria-label={computedAriaLabel}
        aria-describedby={ariaDescribedBy}
        aria-pressed={isPressed ? 'true' : undefined}
        aria-busy={loading || undefined}
        role="button"
        tabIndex={disabled ? -1 : 0}
      >
        {children}
      </Button>
      
      {/* Hidden hint text for screen readers */}
      {accessibilityHint && (
        <Box
          id={`${computedAriaLabel}-hint`}
          sx={{
            position: 'absolute',
            width: '1px',
            height: '1px',
            padding: 0,
            margin: '-1px',
            overflow: 'hidden',
            clip: 'rect(0,0,0,0)',
            whiteSpace: 'nowrap',
            border: 0,
          }}
        >
          {accessibilityHint}
        </Box>
      )}
      
      {/* Loading announcement for screen readers */}
      {loading && announceStateChanges && (
        <Box
          role="status"
          aria-live="polite"
          sx={{
            position: 'absolute',
            width: '1px',
            height: '1px',
            padding: 0,
            margin: '-1px',
            overflow: 'hidden',
            clip: 'rect(0,0,0,0)',
            whiteSpace: 'nowrap',
            border: 0,
          }}
        >
          Loading, please wait
        </Box>
      )}
    </Box>
  );
};

export default MobileButton;