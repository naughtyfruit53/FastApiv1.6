// frontend/src/components/DashboardWidget.tsx
/**
 * Customizable Dashboard Widget Component
 * Supports drag-and-drop, resizing, and user preferences
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Tooltip,
} from '@mui/material';
import {
  MoreVert,
  DragIndicator,
  Refresh,
  Close,
  Settings,
} from '@mui/icons-material';
import Draggable from 'react-draggable';

export interface WidgetConfig {
  id: string;
  title: string;
  type: 'chart' | 'metric' | 'table' | 'list' | 'custom';
  position: { x: number; y: number };
  size: { width: number; height: number };
  refreshInterval?: number;
  settings?: Record<string, any>;
}

interface DashboardWidgetProps {
  config: WidgetConfig;
  children: React.ReactNode;
  onRefresh?: () => void;
  onRemove?: (widgetId: string) => void;
  onConfigure?: (widgetId: string) => void;
  onPositionChange?: (widgetId: string, position: { x: number; y: number }) => void;
  isDraggable?: boolean;
  isEditable?: boolean;
  loading?: boolean;
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({
  config,
  children,
  onRefresh,
  onRemove,
  onConfigure,
  onPositionChange,
  isDraggable = true,
  isEditable = true,
  loading = false,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [position, setPosition] = useState(config.position);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDragStop = (_e: any, data: any) => {
    const newPosition = { x: data.x, y: data.y };
    setPosition(newPosition);
    if (onPositionChange) {
      onPositionChange(config.id, newPosition);
    }
  };

  const widgetActions = (
    <>
      {onRefresh && (
        <Tooltip title="Refresh">
          <IconButton
            size="small"
            onClick={onRefresh}
            disabled={loading}
            sx={{ minWidth: 40, minHeight: 40 }}
          >
            <Refresh sx={{
              animation: loading ? 'spin 1s linear infinite' : 'none',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
              },
            }} />
          </IconButton>
        </Tooltip>
      )}
      {isEditable && (
        <IconButton
          size="small"
          onClick={handleMenuOpen}
          sx={{ minWidth: 40, minHeight: 40 }}
        >
          <MoreVert />
        </IconButton>
      )}
    </>
  );

  const menuItems = (
    <Menu
      anchorEl={anchorEl}
      open={Boolean(anchorEl)}
      onClose={handleMenuClose}
    >
      {onConfigure && (
        <MenuItem
          onClick={() => {
            handleMenuClose();
            onConfigure(config.id);
          }}
        >
          <Settings sx={{ mr: 1 }} fontSize="small" />
          Configure
        </MenuItem>
      )}
      {onRemove && (
        <MenuItem
          onClick={() => {
            handleMenuClose();
            onRemove(config.id);
          }}
        >
          <Close sx={{ mr: 1 }} fontSize="small" />
          Remove
        </MenuItem>
      )}
    </Menu>
  );

  const widgetContent = (
    <Card
      sx={{
        width: config.size.width,
        height: config.size.height,
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 3,
        '&:hover': {
          boxShadow: 6,
        },
      }}
    >
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isDraggable && (
              <DragIndicator
                sx={{ cursor: 'move', color: 'text.secondary' }}
              />
            )}
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              {config.title}
            </Typography>
          </Box>
        }
        action={widgetActions}
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ flexGrow: 1, overflow: 'auto', pt: 0 }}>
        {loading ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            <Typography color="text.secondary">Loading...</Typography>
          </Box>
        ) : (
          children
        )}
      </CardContent>
      {menuItems}
    </Card>
  );

  if (isDraggable) {
    return (
      <Draggable
        position={position}
        onStop={handleDragStop}
        handle=".MuiCardHeader-root"
        bounds="parent"
      >
        <div style={{ position: 'absolute' }}>
          {widgetContent}
        </div>
      </Draggable>
    );
  }

  return widgetContent;
};

export default DashboardWidget;
