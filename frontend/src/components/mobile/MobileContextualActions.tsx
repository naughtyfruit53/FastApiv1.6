import React, { useState } from 'react';
import {
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Backdrop,
  Box,
  Typography,
  Zoom
} from '@mui/material';
import {
  Add,
  Edit,
  Share,
  Download,
  FilterList,
  Refresh,
  MoreVert,
  Close,
  Search,
  Upload,
  Delete,
  Visibility,
  Phone,
  Email,
  Event,
  Bookmark
} from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

export interface ContextualAction {
  icon: React.ReactElement;
  name: string;
  onClick: () => void;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  disabled?: boolean;
  badge?: string;
}

interface MobileContextualActionsProps {
  actions: ContextualAction[];
  primaryAction?: ContextualAction;
  position?: {
    bottom?: number;
    right?: number;
    left?: number;
    top?: number;
  };
  size?: 'small' | 'medium' | 'large';
  direction?: 'up' | 'down' | 'left' | 'right';
  hidden?: boolean;
}

const MobileContextualActions: React.FC<MobileContextualActionsProps> = ({
  actions = [],
  primaryAction,
  position = { bottom: 80, right: 16 },
  size = 'medium',
  direction = 'up',
  hidden = false
}) => {
  const [open, setOpen] = useState(false);
  const { isMobile } = useMobileDetection();

  // Early return after all hooks
  if (!isMobile || hidden || actions.length === 0) {
    return null;
  }

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleActionClick = (action: ContextualAction) => {
    action.onClick();
    handleClose();
  };

  // If there's only one action and it's the primary action, show a simple FAB
  if (actions.length === 1 && primaryAction) {
    return (
      <Zoom in timeout={300}>
        <Fab
          color={primaryAction.color || 'primary'}
          size={size}
          onClick={primaryAction.onClick}
          disabled={primaryAction.disabled}
          sx={{
            position: 'fixed',
            ...position,
            zIndex: 1050,
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
            '&:hover': {
              transform: 'scale(1.1)',
            },
            transition: 'transform 0.2s ease-in-out',
          }}
        >
          {primaryAction.icon}
        </Fab>
      </Zoom>
    );
  }

  // Multiple actions - use SpeedDial
  return (
    <>
      <Backdrop
        open={open}
        onClick={handleClose}
        sx={{
          zIndex: 1040,
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          cursor: 'pointer'
        }}
      />
      <SpeedDial
        ariaLabel="Contextual Actions"
        sx={{
          position: 'fixed',
          ...position,
          zIndex: 1050,
          '& .MuiFab-primary': {
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
            '&:hover': {
              transform: 'scale(1.05)',
            },
            transition: 'transform 0.2s ease-in-out',
          }
        }}
        icon={<SpeedDialIcon icon={primaryAction?.icon || <MoreVert />} openIcon={<Close />} />}
        onClose={handleClose}
        onOpen={handleOpen}
        open={open}
        direction={direction}
        FabProps={{
          size: size,
          color: primaryAction?.color || 'primary',
        }}
      >
        {actions.map((action, index) => (
          <SpeedDialAction
            key={index}
            icon={action.icon}
            tooltipTitle={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2">{action.name}</Typography>
                {action.badge && (
                  <Typography
                    variant="caption"
                    sx={{
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      px: 1,
                      py: 0.25,
                      borderRadius: 1,
                      fontSize: '0.7rem'
                    }}
                  >
                    {action.badge}
                  </Typography>
                )}
              </Box>
            }
            tooltipOpen
            onClick={() => handleActionClick(action)}
            FabProps={{
              size: 'small',
              color: action.color || 'default',
              disabled: action.disabled,
              sx: {
                backgroundColor: action.disabled 
                  ? 'action.disabled' 
                  : action.color 
                  ? `${action.color}.main` 
                  : 'background.paper',
                color: action.disabled 
                  ? 'action.disabled' 
                  : action.color 
                  ? `${action.color}.contrastText` 
                  : 'text.primary',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  transform: 'scale(1.1)',
                  boxShadow: '0 6px 16px rgba(0, 0, 0, 0.15)',
                },
                transition: 'all 0.2s ease-in-out',
              }
            }}
            sx={{
              '& .MuiSpeedDialAction-staticTooltipLabel': {
                backgroundColor: 'background.paper',
                color: 'text.primary',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                borderRadius: 2,
                fontSize: '0.875rem',
                fontWeight: 500,
                whiteSpace: 'nowrap',
                maxWidth: '200px',
              }
            }}
          />
        ))}
      </SpeedDial>
    </>
  );
};

// Predefined action sets for common use cases
export const createStandardActions = {
  // Common CRUD actions
  crud: (handlers: {
    onCreate?: () => void;
    onEdit?: () => void;
    onDelete?: () => void;
    onView?: () => void;
  }): ContextualAction[] => [
    ...(handlers.onCreate ? [{
      icon: <Add />,
      name: 'Create New',
      onClick: handlers.onCreate,
      color: 'primary' as const
    }] : []),
    ...(handlers.onEdit ? [{
      icon: <Edit />,
      name: 'Edit',
      onClick: handlers.onEdit,
      color: 'secondary' as const
    }] : []),
    ...(handlers.onView ? [{
      icon: <Visibility />,
      name: 'View Details',
      onClick: handlers.onView,
      color: 'info' as const
    }] : []),
    ...(handlers.onDelete ? [{
      icon: <Delete />,
      name: 'Delete',
      onClick: handlers.onDelete,
      color: 'error' as const
    }] : [])
  ],

  // Data management actions
  dataManagement: (handlers: {
    onRefresh?: () => void;
    onFilter?: () => void;
    onSearch?: () => void;
    onExport?: () => void;
    onImport?: () => void;
  }): ContextualAction[] => [
    ...(handlers.onRefresh ? [{
      icon: <Refresh />,
      name: 'Refresh',
      onClick: handlers.onRefresh,
      color: 'primary' as const
    }] : []),
    ...(handlers.onFilter ? [{
      icon: <FilterList />,
      name: 'Filter',
      onClick: handlers.onFilter,
      color: 'secondary' as const
    }] : []),
    ...(handlers.onSearch ? [{
      icon: <Search />,
      name: 'Search',
      onClick: handlers.onSearch,
      color: 'info' as const
    }] : []),
    ...(handlers.onExport ? [{
      icon: <Download />,
      name: 'Export',
      onClick: handlers.onExport,
      color: 'success' as const
    }] : []),
    ...(handlers.onImport ? [{
      icon: <Upload />,
      name: 'Import',
      onClick: handlers.onImport,
      color: 'warning' as const
    }] : [])
  ],

  // Communication actions
  communication: (handlers: {
    onCall?: () => void;
    onEmail?: () => void;
    onShare?: () => void;
    onSchedule?: () => void;
  }): ContextualAction[] => [
    ...(handlers.onCall ? [{
      icon: <Phone />,
      name: 'Call',
      onClick: handlers.onCall,
      color: 'success' as const
    }] : []),
    ...(handlers.onEmail ? [{
      icon: <Email />,
      name: 'Email',
      onClick: handlers.onEmail,
      color: 'primary' as const
    }] : []),
    ...(handlers.onShare ? [{
      icon: <Share />,
      name: 'Share',
      onClick: handlers.onShare,
      color: 'info' as const
    }] : []),
    ...(handlers.onSchedule ? [{
      icon: <Event />,
      name: 'Schedule',
      onClick: handlers.onSchedule,
      color: 'secondary' as const
    }] : [])
  ],

  // Sales specific actions
  sales: (handlers: {
    onAddLead?: () => void;
    onFollowUp?: () => void;
    onConvert?: () => void;
    onQuote?: () => void;
  }): ContextualAction[] => [
    ...(handlers.onAddLead ? [{
      icon: <Add />,
      name: 'Add Lead',
      onClick: handlers.onAddLead,
      color: 'primary' as const
    }] : []),
    ...(handlers.onFollowUp ? [{
      icon: <Event />,
      name: 'Follow Up',
      onClick: handlers.onFollowUp,
      color: 'warning' as const
    }] : []),
    ...(handlers.onConvert ? [{
      icon: <Bookmark />,
      name: 'Convert',
      onClick: handlers.onConvert,
      color: 'success' as const
    }] : []),
    ...(handlers.onQuote ? [{
      icon: <Edit />,
      name: 'Create Quote',
      onClick: handlers.onQuote,
      color: 'secondary' as const
    }] : [])
  ]
};

export default MobileContextualActions;