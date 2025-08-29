// frontend/src/components/StickyNotes/StickyNotesPanel.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
  Collapse,
  IconButton,
  Paper
} from '@mui/material';
import {
  Add,
  StickyNote2,
  ExpandLess,
  ExpandMore,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import StickyNote from './StickyNote';
import { useAuth } from '../../context/AuthContext';

interface StickyNoteData {
  id: number;
  title: string;
  content: string;
  color: string;
  created_at: string;
  updated_at?: string;
}

interface StickyNotesPanelProps {
  stickyNotesEnabled: boolean;
}

const COLORS = [
  { name: 'yellow', label: 'Yellow' },
  { name: 'blue', label: 'Blue' },
  { name: 'green', label: 'Green' },
  { name: 'pink', label: 'Pink' },
  { name: 'purple', label: 'Purple' },
  { name: 'orange', label: 'Orange' }
];

const StickyNotesPanel: React.FC<StickyNotesPanelProps> = ({ stickyNotesEnabled }) => {
  const { user } = useAuth();
  const [notes, setNotes] = useState<StickyNoteData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newNote, setNewNote] = useState({
    title: '',
    content: '',
    color: 'yellow'
  });
  const [expanded, setExpanded] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (stickyNotesEnabled) {
      fetchNotes();
    }
  }, [stickyNotesEnabled]);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/sticky-notes/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNotes(data);
        setError(null);
      } else {
        throw new Error('Failed to fetch sticky notes');
      }
    } catch (err) {
      console.error('Error fetching notes:', err);
      setError('Failed to load sticky notes');
    } finally {
      setLoading(false);
    }
  };

  const createNote = async () => {
    if (!newNote.title.trim() || !newNote.content.trim()) {
      return;
    }

    try {
      setCreating(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/sticky-notes/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newNote)
      });

      if (response.ok) {
        const createdNote = await response.json();
        setNotes(prev => [createdNote, ...prev]);
        setNewNote({ title: '', content: '', color: 'yellow' });
        setCreateDialogOpen(false);
        setError(null);
      } else {
        throw new Error('Failed to create sticky note');
      }
    } catch (err) {
      console.error('Error creating note:', err);
      setError('Failed to create sticky note');
    } finally {
      setCreating(false);
    }
  };

  const updateNote = async (id: number, updateData: { title?: string; content?: string; color?: string }) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/sticky-notes/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedNote = await response.json();
        setNotes(prev => prev.map(note => note.id === id ? updatedNote : note));
        setError(null);
      } else {
        throw new Error('Failed to update sticky note');
      }
    } catch (err) {
      console.error('Error updating note:', err);
      setError('Failed to update sticky note');
      throw err;
    }
  };

  const deleteNote = async (id: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/sticky-notes/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setNotes(prev => prev.filter(note => note.id !== id));
        setError(null);
      } else {
        throw new Error('Failed to delete sticky note');
      }
    } catch (err) {
      console.error('Error deleting note:', err);
      setError('Failed to delete sticky note');
      throw err;
    }
  };

  if (!stickyNotesEnabled) {
    return null;
  }

  return (
    <Paper
      elevation={2}
      sx={{
        mb: 3,
        borderRadius: 2,
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          backgroundColor: 'rgba(255,255,255,0.9)',
          borderBottom: '1px solid rgba(0,0,0,0.1)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <StickyNote2 sx={{ color: '#ffa726', mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Sticky Notes
          </Typography>
          <Typography variant="body2" sx={{ ml: 1, color: 'text.secondary' }}>
            ({notes.length})
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            variant="contained"
            size="small"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{
              mr: 1,
              backgroundColor: '#ffa726',
              '&:hover': { backgroundColor: '#ff9800' }
            }}
          >
            Add Note
          </Button>
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ color: 'text.secondary' }}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </Box>

      {/* Content */}
      <Collapse in={expanded}>
        <Box sx={{ p: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={40} />
            </Box>
          ) : notes.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <StickyNote2 sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body1" color="text.secondary">
                No sticky notes yet. Create your first note to get started!
              </Typography>
            </Box>
          ) : (
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                overflowX: 'auto',
                pb: 1,
                '&::-webkit-scrollbar': {
                  height: 8
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  borderRadius: 4
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: 'rgba(0,0,0,0.3)',
                  borderRadius: 4
                }
              }}
            >
              {notes.map((note) => (
                <StickyNote
                  key={note.id}
                  id={note.id}
                  title={note.title}
                  content={note.content}
                  color={note.color}
                  created_at={note.created_at}
                  onUpdate={updateNote}
                  onDelete={deleteNote}
                />
              ))}
            </Box>
          )}
        </Box>
      </Collapse>

      {/* Create Note Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Sticky Note</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            value={newNote.title}
            onChange={(e) => setNewNote(prev => ({ ...prev, title: e.target.value }))}
            margin="normal"
            variant="outlined"
          />
          <TextField
            fullWidth
            label="Content"
            value={newNote.content}
            onChange={(e) => setNewNote(prev => ({ ...prev, content: e.target.value }))}
            margin="normal"
            variant="outlined"
            multiline
            rows={4}
          />
          <TextField
            fullWidth
            label="Color"
            value={newNote.color}
            onChange={(e) => setNewNote(prev => ({ ...prev, color: e.target.value }))}
            margin="normal"
            variant="outlined"
            select
          >
            {COLORS.map((color) => (
              <MenuItem key={color.name} value={color.name}>
                {color.label}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={createNote}
            variant="contained"
            disabled={creating || !newNote.title.trim() || !newNote.content.trim()}
          >
            {creating ? <CircularProgress size={20} /> : 'Create Note'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default StickyNotesPanel;