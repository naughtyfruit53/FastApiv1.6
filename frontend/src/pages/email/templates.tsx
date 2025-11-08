'use client';

/**
 * Email Templates Page
 * Manage email templates for quick composition
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FileCopy as FileCopyIcon,
} from '@mui/icons-material';
import { ProtectedPage } from '../../components/ProtectedPage';

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  category?: string;
}

const EmailTemplates: React.FC = () => {
  const [templates, setTemplates] = useState<EmailTemplate[]>([
    {
      id: 1,
      name: 'Welcome Email',
      subject: 'Welcome to our service!',
      body: 'Dear {{name}},\n\nThank you for joining us...',
      category: 'Onboarding',
    },
    {
      id: 2,
      name: 'Follow-up',
      subject: 'Following up on our conversation',
      body: 'Hi {{name}},\n\nI wanted to follow up...',
      category: 'Sales',
    },
  ]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);

  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    setDialogOpen(true);
  };

  const handleEditTemplate = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setDialogOpen(true);
  };

  const handleDeleteTemplate = (id: number) => {
    setTemplates(templates.filter(t => t.id !== id));
  };

  const handleSaveTemplate = () => {
    // TODO: Implement save logic
    setDialogOpen(false);
  };

  return (
    <ProtectedPage moduleKey="email" action="read">
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Email Templates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateTemplate}
        >
          Create Template
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        Create reusable email templates with variables like {'{{name}}'} and {'{{email}}'} for quick composition.
      </Alert>

      {templates.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            No Templates Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Create your first email template to save time when composing emails
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateTemplate}
            sx={{ mt: 2 }}
          >
            Create Your First Template
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid item xs={12} md={6} lg={4} key={template.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {template.name}
                  </Typography>
                  {template.category && (
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                      Category: {template.category}
                    </Typography>
                  )}
                  <Typography variant="body2" color="text.primary" gutterBottom>
                    <strong>Subject:</strong> {template.subject}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mt: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {template.body}
                  </Typography>
                </CardContent>
                <CardActions>
                  <IconButton
                    size="small"
                    onClick={() => handleEditTemplate(template)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteTemplate(template.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                  <IconButton size="small" color="default">
                    <FileCopyIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Template Editor Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTemplate ? 'Edit Template' : 'Create Template'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Template Name"
            fullWidth
            variant="outlined"
            defaultValue={editingTemplate?.name || ''}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Category (Optional)"
            fullWidth
            variant="outlined"
            defaultValue={editingTemplate?.category || ''}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Subject"
            fullWidth
            variant="outlined"
            defaultValue={editingTemplate?.subject || ''}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Email Body"
            fullWidth
            multiline
            rows={8}
            variant="outlined"
            defaultValue={editingTemplate?.body || ''}
            helperText="Use {{variable}} for dynamic content (e.g., {{name}}, {{email}})"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveTemplate} variant="contained">
            Save Template
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </ProtectedPage>
  );
};

export default EmailTemplates;
