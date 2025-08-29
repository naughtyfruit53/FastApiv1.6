// frontend/src/components/StickyNotes/StickyNote.tsx

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  TextField,
  IconButton,
  Box,
  Menu,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import {
  Edit,
  Delete,
  Save,
  Cancel,
  MoreVert,
  Palette
} from '@mui/icons-material';

interface StickyNoteProps {
  id: number;
  title: string;
  content: string;
  color: string;
  created_at: string;
  onUpdate: (id: number, data: { title?: string; content?: string; color?: string }) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

const COLORS = [
  { name: 'yellow', color: '#fff59d', border: '#fff176' },
  { name: 'blue', color: '#81d4fa', border: '#4fc3f7' },
  { name: 'green', color: '#a5d6a7', border: '#81c784' },
  { name: 'pink', color: '#f8bbd9', border: '#f48fb1' },
  { name: 'purple', color: '#ce93d8', border: '#ba68c8' },
  { name: 'orange', color: '#ffcc80', border: '#ffb74d' }
];

const StickyNote: React.FC<StickyNoteProps> = ({
  id,
  title,
  content,
  color,
  created_at,
  onUpdate,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);
  const [editContent, setEditContent] = useState(content);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [colorMenuAnchor, setColorMenuAnchor] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const colorConfig = COLORS.find(c => c.name === color) || COLORS[0];

  const handleEdit = () => {
    setIsEditing(true);
    setAnchorEl(null);
  };

  const handleSave = async () => {
    if (!editTitle.trim() || !editContent.trim()) {
      return;
    }

    setLoading(true);
    try {
      await onUpdate(id, {
        title: editTitle.trim(),
        content: editContent.trim()
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating note:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(title);
    setEditContent(content);
    setIsEditing(false);
  };

  const handleColorChange = async (newColor: string) => {
    setLoading(true);
    try {
      await onUpdate(id, { color: newColor });
      setColorMenuAnchor(null);
    } catch (error) {
      console.error('Error updating note color:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(id);
      setDeleteDialogOpen(false);
    } catch (error) {
      console.error('Error deleting note:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      <Card
        sx={{
          width: 280,
          minHeight: 200,
          backgroundColor: colorConfig.color,
          border: `2px solid ${colorConfig.border}`,
          borderRadius: 2,
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: '0 6px 16px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)'
          }
        }}
      >
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            {isEditing ? (
              <TextField
                fullWidth
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                variant="standard"
                placeholder="Note title..."
                InputProps={{
                  disableUnderline: true,
                  sx: {
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    backgroundColor: 'rgba(255,255,255,0.3)',
                    borderRadius: 1,
                    px: 1,
                    py: 0.5
                  }
                }}
                autoFocus
              />
            ) : (
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'rgba(0,0,0,0.8)' }}>
                {title}
              </Typography>
            )}
            
            {!isEditing && (
              <IconButton
                size="small"
                onClick={(e) => setAnchorEl(e.currentTarget)}
                sx={{ color: 'rgba(0,0,0,0.6)' }}
              >
                <MoreVert fontSize="small" />
              </IconButton>
            )}
          </Box>

          {isEditing ? (
            <TextField
              fullWidth
              multiline
              rows={4}
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              variant="outlined"
              placeholder="Write your note content here..."
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255,255,255,0.3)',
                  '& fieldset': {
                    border: 'none'
                  }
                }
              }}
            />
          ) : (
            <Typography variant="body2" sx={{ color: 'rgba(0,0,0,0.7)', whiteSpace: 'pre-wrap' }}>
              {content}
            </Typography>
          )}
        </CardContent>

        <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
          <Chip
            label={formatDate(created_at)}
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.4)',
              color: 'rgba(0,0,0,0.6)',
              fontSize: '0.7rem'
            }}
          />

          {isEditing && (
            <Box>
              <IconButton
                size="small"
                onClick={handleCancel}
                disabled={loading}
                sx={{ color: 'rgba(0,0,0,0.6)', mr: 1 }}
              >
                <Cancel fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                onClick={handleSave}
                disabled={loading || !editTitle.trim() || !editContent.trim()}
                sx={{ color: 'green' }}
              >
                <Save fontSize="small" />
              </IconButton>
            </Box>
          )}
        </CardActions>
      </Card>

      {/* Options Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={handleEdit}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={(e) => setColorMenuAnchor(e.currentTarget)}>
          <Palette fontSize="small" sx={{ mr: 1 }} />
          Change Color
        </MenuItem>
        <MenuItem onClick={() => { setDeleteDialogOpen(true); setAnchorEl(null); }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

      {/* Color Menu */}
      <Menu
        anchorEl={colorMenuAnchor}
        open={Boolean(colorMenuAnchor)}
        onClose={() => setColorMenuAnchor(null)}
      >
        {COLORS.map((colorOption) => (
          <MenuItem
            key={colorOption.name}
            onClick={() => handleColorChange(colorOption.name)}
            sx={{ minWidth: 120 }}
          >
            <Box
              sx={{
                width: 20,
                height: 20,
                backgroundColor: colorOption.color,
                border: `2px solid ${colorOption.border}`,
                borderRadius: 1,
                mr: 1
              }}
            />
            {colorOption.name.charAt(0).toUpperCase() + colorOption.name.slice(1)}
          </MenuItem>
        ))}
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Note</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" disabled={loading}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default StickyNote;