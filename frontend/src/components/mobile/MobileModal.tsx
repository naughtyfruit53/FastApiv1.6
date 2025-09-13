import React, { ReactNode } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  Slide,
  useTheme,
} from '@mui/material';
import { TransitionProps } from '@mui/material/transitions';
import { Close } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

interface MobileModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  actions?: ReactNode;
  fullScreen?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  showCloseButton?: boolean;
  closeOnBackdrop?: boolean;
  className?: string;
}

const MobileModal: React.FC<MobileModalProps> = ({
  open,
  onClose,
  title,
  children,
  actions,
  fullScreen,
  maxWidth = 'sm',
  showCloseButton = true,
  closeOnBackdrop = true,
  className = '',
}) => {
  const theme = useTheme();
  const { isMobile } = useMobileDetection();

  // Force full screen on mobile for better UX
  const shouldBeFullScreen = isMobile || fullScreen;

  const handleBackdropClick = (event: React.MouseEvent) => {
    if (!closeOnBackdrop) {
      event.stopPropagation();
      return;
    }
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={closeOnBackdrop ? onClose : undefined}
      fullScreen={shouldBeFullScreen}
      maxWidth={shouldBeFullScreen ? false : maxWidth}
      fullWidth={!shouldBeFullScreen}
      TransitionComponent={isMobile ? Transition : undefined}
      className={`mobile-modal ${className}`}
      PaperProps={{
        sx: {
          ...(isMobile && {
            margin: 0,
            borderRadius: shouldBeFullScreen ? 0 : '12px 12px 0 0',
            maxHeight: shouldBeFullScreen ? '100vh' : '90vh',
            ...(shouldBeFullScreen && {
              width: '100vw',
              height: '100vh',
            }),
          }),
        },
      }}
      onClick={closeOnBackdrop ? handleBackdropClick : undefined}
    >
      {title && (
        <DialogTitle
          sx={{
            padding: isMobile ? 2 : 3,
            paddingBottom: isMobile ? 1 : 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            position: 'relative',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontSize: isMobile ? '1.25rem' : '1.5rem',
                fontWeight: 600,
                lineHeight: 1.2,
              }}
            >
              {title}
            </Typography>
            {showCloseButton && (
              <IconButton
                onClick={onClose}
                sx={{
                  position: 'absolute',
                  right: isMobile ? 8 : 16,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  minWidth: 44,
                  minHeight: 44,
                }}
              >
                <Close />
              </IconButton>
            )}
          </Box>
        </DialogTitle>
      )}

      <DialogContent
        sx={{
          padding: isMobile ? 2 : 3,
          paddingTop: title ? (isMobile ? 2 : 3) : (isMobile ? 2 : 3),
          paddingBottom: actions ? (isMobile ? 1 : 2) : (isMobile ? 2 : 3),
          overflow: 'auto',
          WebkitOverflowScrolling: 'touch',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </DialogContent>

      {actions && (
        <DialogActions
          sx={{
            padding: isMobile ? 2 : 3,
            paddingTop: isMobile ? 1 : 2,
            borderTop: '1px solid',
            borderColor: 'divider',
            gap: isMobile ? 1 : 2,
            flexDirection: isMobile ? 'column' : 'row',
            '& > button': {
              ...(isMobile && {
                width: '100%',
                minHeight: 48,
              }),
            },
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default MobileModal;