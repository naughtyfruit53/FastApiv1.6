import React, { ReactNode, useState, useRef } from 'react';
import { Box, Menu, MenuItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface ContextualAction {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  destructive?: boolean;
  divider?: boolean;
}

interface MobileContextualMenuProps {
  children: ReactNode;
  actions: ContextualAction[];
  disabled?: boolean;
  longPressDelay?: number;
  hapticFeedback?: boolean;
}

const MobileContextualMenu: React.FC<MobileContextualMenuProps> = ({
  children,
  actions,
  disabled = false,
  longPressDelay = 500,
  hapticFeedback = true,
}) => {
  const { isMobile } = useMobileDetection();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const longPressTimer = useRef<NodeJS.Timeout>();
  const pressStartTime = useRef<number>(0);
  const hasMoved = useRef(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const triggerHapticFeedback = () => {
    if (hapticFeedback && 'vibrate' in navigator) {
      navigator.vibrate(50);
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled || !isMobile) return;

    hasMoved.current = false;
    pressStartTime.current = Date.now();
    
    longPressTimer.current = setTimeout(() => {
      if (!hasMoved.current) {
        triggerHapticFeedback();
        setAnchorEl(elementRef.current);
        setMenuOpen(true);
        e.preventDefault();
      }
    }, longPressDelay);
  };

  const handleTouchMove = () => {
    hasMoved.current = true;
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }
  };

  const handleTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    if (!isMobile && !disabled) {
      e.preventDefault();
      setAnchorEl(e.currentTarget as HTMLElement);
      setMenuOpen(true);
    }
  };

  const handleMenuClose = () => {
    setMenuOpen(false);
    setAnchorEl(null);
  };

  const handleActionClick = (action: ContextualAction) => {
    if (!action.disabled) {
      action.onClick();
      handleMenuClose();
    }
  };

  return (
    <>
      <Box
        ref={elementRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onContextMenu={handleContextMenu}
        sx={{
          cursor: disabled ? 'default' : 'pointer',
          userSelect: 'none',
          WebkitUserSelect: 'none',
          WebkitTouchCallout: 'none',
          position: 'relative',
          '&:active': isMobile && !disabled ? {
            transform: 'scale(0.98)',
            transition: 'transform 0.1s ease',
          } : {},
        }}
      >
        {children}
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'center',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'center',
          horizontal: 'center',
        }}
        PaperProps={{
          sx: {
            minWidth: 200,
            maxWidth: 300,
            borderRadius: 2,
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
            border: '1px solid',
            borderColor: 'divider',
          },
        }}
        MenuListProps={{
          sx: {
            padding: 1,
          },
        }}
      >
        {actions.map((action, index) => (
          <React.Fragment key={index}>
            <MenuItem
              onClick={() => handleActionClick(action)}
              disabled={action.disabled}
              sx={{
                borderRadius: 1,
                margin: '2px 0',
                padding: '12px 16px',
                minHeight: 48,
                color: action.destructive ? 'error.main' : 'text.primary',
                '&:hover': {
                  backgroundColor: action.destructive ? 'error.lighter' : 'action.hover',
                },
                '&.Mui-disabled': {
                  opacity: 0.5,
                },
              }}
            >
              {action.icon && (
                <ListItemIcon
                  sx={{
                    color: action.destructive ? 'error.main' : 'inherit',
                    minWidth: 36,
                  }}
                >
                  {action.icon}
                </ListItemIcon>
              )}
              <ListItemText
                primary={action.label}
                primaryTypographyProps={{
                  fontWeight: 500,
                  fontSize: '0.95rem',
                }}
              />
            </MenuItem>
            {action.divider && index < actions.length - 1 && (
              <Divider sx={{ margin: '4px 0' }} />
            )}
          </React.Fragment>
        ))}
      </Menu>
    </>
  );
};

export default MobileContextualMenu;