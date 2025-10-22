// frontend/src/pages/dashboard/CustomDashboard.tsx
/**
 * Customizable Dashboard with Widget System
 * Supports drag-and-drop widgets and user preferences
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Fab,
} from '@mui/material';
import {
  Add,
  Settings,
  Save,
  RestartAlt,
  DashboardCustomize,
  Assessment,
  ShowChart,
  TableChart,
  CalendarMonth,
} from '@mui/icons-material';
import DashboardWidget, { WidgetConfig } from '../../components/DashboardWidget';
import { useAuth } from '../../context/AuthContext';

interface WidgetTemplate {
  id: string;
  title: string;
  type: 'chart' | 'metric' | 'table' | 'list' | 'custom';
  icon: React.ReactNode;
  defaultSize: { width: number; height: number };
  description: string;
}

const CustomDashboard: React.FC = () => {
  const { user } = useAuth();
  const [widgets, setWidgets] = useState<WidgetConfig[]>([]);
  const [isEditMode, setIsEditMode] = useState(false);
  const [addWidgetDialogOpen, setAddWidgetDialogOpen] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const widgetTemplates: WidgetTemplate[] = [
    {
      id: 'sales-chart',
      title: 'Sales Overview',
      type: 'chart',
      icon: <ShowChart />,
      defaultSize: { width: 400, height: 300 },
      description: 'View sales trends and performance metrics',
    },
    {
      id: 'revenue-metric',
      title: 'Revenue Metrics',
      type: 'metric',
      icon: <Assessment />,
      defaultSize: { width: 300, height: 200 },
      description: 'Track key revenue indicators',
    },
    {
      id: 'recent-orders',
      title: 'Recent Orders',
      type: 'table',
      icon: <TableChart />,
      defaultSize: { width: 500, height: 400 },
      description: 'View recent customer orders',
    },
    {
      id: 'tasks-list',
      title: 'My Tasks',
      type: 'list',
      icon: <CalendarMonth />,
      defaultSize: { width: 350, height: 350 },
      description: 'Manage your daily tasks',
    },
    {
      id: 'customer-analytics',
      title: 'Customer Analytics',
      type: 'chart',
      icon: <Assessment />,
      defaultSize: { width: 450, height: 350 },
      description: 'Analyze customer behavior and trends',
    },
  ];

  useEffect(() => {
    loadDashboardConfig();
  }, []);

  const loadDashboardConfig = () => {
    // Load saved dashboard configuration from localStorage
    const savedConfig = localStorage.getItem(`dashboard-config-${user?.id}`);
    if (savedConfig) {
      try {
        setWidgets(JSON.parse(savedConfig));
      } catch (error) {
        console.error('Failed to load dashboard config:', error);
        loadDefaultWidgets();
      }
    } else {
      loadDefaultWidgets();
    }
  };

  const loadDefaultWidgets = () => {
    // Load default widgets
    const defaultWidgets: WidgetConfig[] = [
      {
        id: 'widget-1',
        title: 'Sales Overview',
        type: 'chart',
        position: { x: 0, y: 0 },
        size: { width: 400, height: 300 },
      },
      {
        id: 'widget-2',
        title: 'Revenue Metrics',
        type: 'metric',
        position: { x: 420, y: 0 },
        size: { width: 300, height: 200 },
      },
    ];
    setWidgets(defaultWidgets);
  };

  const saveDashboardConfig = () => {
    try {
      localStorage.setItem(`dashboard-config-${user?.id}`, JSON.stringify(widgets));
      setAlert({ type: 'success', message: 'Dashboard layout saved successfully' });
      setIsEditMode(false);
    } catch (error) {
      setAlert({ type: 'error', message: 'Failed to save dashboard layout' });
    }
  };

  const handleAddWidget = (template: WidgetTemplate) => {
    const newWidget: WidgetConfig = {
      id: `widget-${Date.now()}`,
      title: template.title,
      type: template.type,
      position: { x: 0, y: widgets.length * 100 },
      size: template.defaultSize,
    };
    setWidgets([...widgets, newWidget]);
    setAddWidgetDialogOpen(false);
    setAlert({ type: 'success', message: 'Widget added successfully' });
  };

  const handleRemoveWidget = (widgetId: string) => {
    setWidgets(widgets.filter((w) => w.id !== widgetId));
    setAlert({ type: 'info', message: 'Widget removed' });
  };

  const handleWidgetPositionChange = (widgetId: string, position: { x: number; y: number }) => {
    setWidgets(widgets.map((w) => (w.id === widgetId ? { ...w, position } : w)));
  };

  const handleResetLayout = () => {
    if (confirm('Are you sure you want to reset to the default layout?')) {
      loadDefaultWidgets();
      setAlert({ type: 'info', message: 'Layout reset to defaults' });
    }
  };

  const renderWidgetContent = (widget: WidgetConfig) => {
    // Placeholder content for different widget types
    switch (widget.type) {
      case 'chart':
        return (
          <Box sx={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Typography color="text.secondary">Chart Widget - {widget.title}</Typography>
          </Box>
        );
      case 'metric':
        return (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Typography variant="h3" color="primary">
              $42,500
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Revenue
            </Typography>
          </Box>
        );
      case 'table':
        return (
          <Box>
            <Typography variant="body2" color="text.secondary">
              Recent data will be displayed here
            </Typography>
          </Box>
        );
      case 'list':
        return (
          <List dense>
            <ListItem>
              <ListItemText primary="Sample task 1" secondary="Due today" />
            </ListItem>
            <ListItem>
              <ListItemText primary="Sample task 2" secondary="Due tomorrow" />
            </ListItem>
          </List>
        );
      default:
        return <Typography>Custom widget content</Typography>;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            My Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Customize your dashboard with widgets
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {isEditMode ? (
            <>
              <Button
                variant="outlined"
                startIcon={<RestartAlt />}
                onClick={handleResetLayout}
              >
                Reset
              </Button>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={saveDashboardConfig}
              >
                Save Layout
              </Button>
            </>
          ) : (
            <Button
              variant="contained"
              startIcon={<Settings />}
              onClick={() => setIsEditMode(true)}
            >
              Edit Dashboard
            </Button>
          )}
        </Box>
      </Box>

      {/* Alerts */}
      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 3 }}>
          {alert.message}
        </Alert>
      )}

      {/* Edit Mode Info */}
      {isEditMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <strong>Edit Mode:</strong> Drag widgets to reposition them. Click the menu on each widget to configure or remove it.
        </Alert>
      )}

      {/* Dashboard Grid */}
      <Box
        sx={{
          position: 'relative',
          minHeight: 600,
          border: isEditMode ? '2px dashed' : 'none',
          borderColor: 'primary.main',
          borderRadius: 1,
          p: 2,
        }}
      >
        {widgets.map((widget) => (
          <DashboardWidget
            key={widget.id}
            config={widget}
            onRemove={isEditMode ? handleRemoveWidget : undefined}
            onPositionChange={isEditMode ? handleWidgetPositionChange : undefined}
            isDraggable={isEditMode}
            isEditable={isEditMode}
          >
            {renderWidgetContent(widget)}
          </DashboardWidget>
        ))}

        {widgets.length === 0 && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: 400,
            }}
          >
            <DashboardCustomize sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No widgets added yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Click the button below to add your first widget
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setAddWidgetDialogOpen(true)}
            >
              Add Widget
            </Button>
          </Box>
        )}
      </Box>

      {/* Add Widget FAB */}
      {isEditMode && widgets.length > 0 && (
        <Fab
          color="primary"
          aria-label="add widget"
          sx={{ position: 'fixed', bottom: 32, right: 32 }}
          onClick={() => setAddWidgetDialogOpen(true)}
        >
          <Add />
        </Fab>
      )}

      {/* Add Widget Dialog */}
      <Dialog
        open={addWidgetDialogOpen}
        onClose={() => setAddWidgetDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Widget</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a widget to add to your dashboard
          </Typography>
          <List>
            {widgetTemplates.map((template) => (
              <ListItem
                key={template.id}
                button
                onClick={() => handleAddWidget(template)}
              >
                <ListItemIcon>{template.icon}</ListItemIcon>
                <ListItemText
                  primary={template.title}
                  secondary={template.description}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddWidgetDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CustomDashboard;
