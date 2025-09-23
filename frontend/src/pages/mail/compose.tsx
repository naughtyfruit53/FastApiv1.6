// frontend/src/pages/mail/compose.tsx
import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Toolbar,
  AppBar,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  Send,
  Save,
  AttachFile,
  Close,
  InsertEmoticon,
  AccountBox,
  ExpandMore,
  ExpandLess,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import EmailCompose from "../../components/EmailCompose";

const ComposePage: React.FC = () => {
  const router = useRouter();
  const [open, setOpen] = useState(true);
  const [showTemplates, setShowTemplates] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await fetch('/api/v1/mail/templates');
        if (response.ok) {
          const data = await response.json();
          setTemplates(data);
        }
      } catch (err) {
        console.error('Error fetching templates:', err);
      }
    };
    fetchTemplates();
  }, []);

  const handleClose = () => {
    setOpen(false);
    router.back();
  };

  const handleUseTemplate = (template: any) => {
    // Implement template application logic here
    console.log('Using template:', template);
    setShowTemplates(false);
  };

  return (
    <Dialog open={open} onClose={handleClose} fullScreen>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Compose Email
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={() => console.log('Save draft')}
            sx={{ mr: 1 }}
          >
            Save Draft
          </Button>
          <IconButton onClick={handleClose} sx={{ ml: 1 }}>
            <Close />
          </IconButton>
        </Toolbar>
      </AppBar>
      <DialogContent>
        <EmailCompose open={open} onClose={handleClose} />
      </DialogContent>

      {/* Templates Dialog */}
      <Dialog
        open={showTemplates}
        onClose={() => setShowTemplates(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Choose Email Template</DialogTitle>
        <DialogContent>
          <List>
            {templates.map((template) => (
              <ListItem
                key={template.id}
                button
                onClick={() => handleUseTemplate(template)}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={template.name}
                  secondary={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        Subject: {template.subject_template}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {template.body_text_template?.substring(0, 100)}...
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTemplates(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default ComposePage;