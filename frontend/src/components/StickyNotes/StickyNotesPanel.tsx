// frontend/src/components/StickyNotes/StickyNotesPanel.tsx

import React, { useState, useEffect } from 'react';
import Draggable from 'react-draggable';
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
  ExpandMore
} from '@mui/icons-material';
import StickyNote from './StickyNote';
import { useAuth } from '../../context/AuthContext';
import { stickyNotesService } from '../../services/stickyNotesService';
import { useStickyNotes } from '../../hooks/useStickyNotes';

interface StickyNoteData {
  id: number;
  title: string;
  content: string;
  color: string;
  created_at: string;
  updated_at?: string;
}

const COLORS = [
  { name: 'yellow', label: 'Yellow' },
  { name: 'blue', label: 'Blue' },
  { name: 'green', label: 'Green' },
  { name: 'pink', label: 'Pink' },
  { name: 'purple', label: 'Purple' },
  { name: 'orange', label: 'Orange' }
];

const StickyNotesPanel: React.FC = () => {
  const { user } = useAuth();
  const { userSettings } = useStickyNotes();
  const [notes, setNotes] = useState<StickyNoteData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newNote, setNewNote] = useState({
    title: '',
    content: '',
    color: 'yellow'
  });
  const [expanded, setExpanded] = useState(false);
  const [creating, setCreating] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const savedPosition = localStorage.getItem('stickyNotesPosition');
    if (savedPosition) {
      setPosition(JSON.parse(savedPosition));
    } else {
      // Position next to title: right-aligned, y aligned with title (assume header 64px, title margin 16px)
      setPosition({
        x: window.innerWidth - 320, // Panel width 300 + margin 20
        y: 80 // Approximate title position
      });
    }

    // Update on resize to keep right-aligned
    const handleResize = () => {
      setPosition(prev => ({
        ...prev,
        x: window.innerWidth - 320
      }));
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleDragStop = (e: any, data: any) => {
    const newPosition = { x: data.x, y: data.y };
    setPosition(newPosition);
    localStorage.setItem('stickyNotesPosition', JSON.stringify(newPosition));
  };

  useEffect(() => {
    if (userSettings.sticky_notes_enabled) {
      fetchNotes();
    }
  }, [userSettings.sticky_notes_enabled]);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const data = await stickyNotesService.getNotes();
      setNotes(data);
      setError(null);
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
      const createdNote = await stickyNotesService.createNote(newNote);
      setNotes(prev => [createdNote, ...prev]);
      setNewNote({ title: '', content: '', color: 'yellow' });
      setCreateDialogOpen(false);
      setError(null);
    } catch (err) {
      console.error('Error creating note:', err);
      setError('Failed to create sticky note');
    } finally {
      setCreating(false);
    }
  };

  const updateNote = async (id: number, updateData: { title?: string; content?: string; color?: string }) => {
    try {
      const updatedNote = await stickyNotesService.updateNote(id, updateData);
      setNotes(prev => prev.map(note => note.id === id ? updatedNote : note));
      setError(null);
    } catch (err) {
      console.error('Error updating note:', err);
      setError('Failed to update sticky note');
      throw err;
    }
  };

  const deleteNote = async (id: number) => {
    try {
      await stickyNotesService.deleteNote(id);
      setNotes(prev => prev.filter(note => note.id !== id));
      setError(null);
    } catch (err) {
      console.error('Error deleting note:', err);
      setError('Failed to delete sticky note');
      throw err;
    }
  };

  if (!userSettings.sticky_notes_enabled && notes.length === 0) {
    return null;
  }

  return (
    <Draggable
      handle=".drag-handle"
      bounds="body"
      position={position}
      onStop={handleDragStop}
      onStart={(e) => {
        console.log('Drag started');
        // Prevent drag if clicking on button or icon
        if ((e.target as HTMLElement).closest('button')) {
          return false;
        }
      }}
    >
      <Paper
        elevation={4}
        sx={{
          position: 'absolute',
          width: 300,
          maxWidth: '90vw',
          zIndex: 1300,
          borderRadius: 2,
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
        }}
      >
        <Box
          className="drag-handle"
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2,
            backgroundColor: 'rgba(255,255,255,0.9)',
            borderBottom: '1px solid rgba(0,0,0,0.1)',
            cursor: 'move',
            userSelect: 'none'
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
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ color: 'text.secondary' }}
            className="no-drag"
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

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
                  No sticky notes yet. Create your first note!
                </Typography>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<Add />}
                  onClick={() => setCreateDialogOpen(true)}
                  sx={{
                    mt: 2,
                    backgroundColor: '#ffa726',
                    '&:hover': { backgroundColor: '#ff9800' }
                  }}
                  className="no-drag"
                >
                  Add Note
                </Button>
              </Box>
            ) : (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                  maxHeight: 400,
                  overflowY: 'auto'
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

        {notes.length > 0 && (
          <Box sx={{ p: 2, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
            <Button
              variant="contained"
              size="small"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{
                width: '100%',
                backgroundColor: '#ffa726',
                '&:hover': { backgroundColor: '#ff9800' }
              }}
              className="no-drag"
            >
              Add Note
            </Button>
          </Box>
        )}

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
    </Draggable>
  );
};

export default StickyNotesPanel;