import React, { ReactNode } from 'react';
import { Drawer, Box, Typography } from '@mui/material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileDrawerProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children?: ReactNode;
  width?: number;
  anchor?: 'left' | 'right' | 'top' | 'bottom';
}

const MobileDrawer: React.FC<MobileDrawerProps> = ({
  open,
  onClose,
  title,
  children,
  width = 280,
  anchor = 'left',
}) => {
  const { isMobile } = useMobileDetection();

  if (!isMobile) return null;

  return (
    <Drawer
      anchor={anchor}
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: width,
          backgroundColor: 'background.paper',
        }
      }}
      ModalProps={{
        keepMounted: true, // Better performance on mobile
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100%',
        overflow: 'hidden'
      }}>
        {title && (
          <Box sx={{ 
            padding: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'primary.main',
            color: 'primary.contrastText'
          }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {title}
            </Typography>
          </Box>
        )}

        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {children}
        </Box>
      </Box>
    </Drawer>
  );
};

export default MobileDrawer;