// frontend/src/components/StickyNotes/StickyNotesPanel.tsx
import React, { useState, useEffect } from 'react';
import {
declare function fetchNotes(...args: any[]): any;
  Box,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Typography // Added import
} from '@mui/material';
import {PushPin, PushPinOutlined} from '@mui/icons-material';
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
  position?: { x: number; y: number };
  pinned?: boolean;
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
const  = useAuth();
  const { userSettings } = useStickyNotes();
  const [notes, setNotes] = useState<StickyNoteData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [popupOpen, setPopupOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newNote, setNewNote] = useState({
    title: '',
    content: '',
    color: 'yellow',
    position: { x: window.innerWidth - 300, y: 100 },
    pinned: false
  });
  const [creating, setCreating] = useState(false);
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
      setNewNote({ title: '', content: '', color: 'yellow', position: { x: window.innerWidth - 300, y: 100 }, pinned: false });
      setCreateDialogOpen(false);
      setError(null);
    } catch (err) {
      console.error('Error creating note:', err);
      setError('Failed to create sticky note');
    } finally {
      setCreating(false);
    }
  };
  const updateNote = async (id: number, updateData: { title?: string; content?: string; color?: string; position?: { x: number; y: number }; pinned?: boolean }) => {
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
  const togglePin = (note: StickyNoteData) => {
    updateNote(note.id, { pinned: !note.pinned });
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
  // Always show icon, regardless of settings, but disable functionality if not enabled
  return (
    <>
      <Box
        className="sticky-notes-icon"
        sx={{
          position: 'fixed',
          bottom: 'var(--space-4)',
          right: 'var(--space-4)',
          width: '1in',
          height: '1in',
          zIndex: 1500,
          opacity: 0.2,
          '&:hover': {
            opacity: 1,
          },
          cursor: 'pointer'
        }}
        onClick={() => {
          if (!userSettings.sticky_notes_enabled) {
            setError('Sticky notes feature is disabled. Please enable in settings.');
            return;
          }
          setPopupOpen(true);
        }}
      >
        <svg width="100%" height="100%" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <rect x="0" y="0" width="100" height="100" fill="yellow" rx="10" ry="10" />
          <polygon points="100,50 100,100 50,100" fill="#4b5563" />
          <polygon points="100,60 100,100 60,100" fill="#b45309" />
        </svg>
      </Box>
      {/* Pinned notes - rendered separately at top right */}
      {notes.filter(note => note.pinned).map((note) => (
        <Box
          key={note.id}
          sx={{
            position: 'fixed',
            top: 'var(--space-4)',
            right: 'var(--space-4)',
            zIndex: 1400,
            opacity: 0.9,
            '&:hover': { opacity: 1 }
          }}
        >
          <StickyNote
            id={note.id}
            title={note.title}
            content={note.content}
            color={note.color}
            created_at={note.created_at}
            position={{ x: 0, y: 0 }} // Fixed position
            pinned={note.pinned}
            onUpdate={updateNote}
            onDelete={deleteNote}
          />
        </Box>
      ))}
      {/* Unpinned notes - draggable as before */}
      {notes.filter(note => !note.pinned).map((note) => (
        <StickyNote
          key={note.id}
          id={note.id}
          title={note.title}
          content={note.content}
          color={note.color}
          created_at={note.created_at}
          position={note.position}
          pinned={note.pinned}
          onUpdate={updateNote}
          onDelete={deleteNote}
        />
      ))}
      {/* Popup dialog for notes list */}
      <Dialog
        open={popupOpen}
        onClose={() => setPopupOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Sticky Notes</DialogTitle>
        <DialogContent>
          {loading ? (
            <CircularProgress />
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : notes.length === 0 ? (
            <Typography>No notes yet. Add one!</Typography>
          ) : (
            <List>
              {notes.map((note) => (
                <ListItem key={note.id}>
                  <ListItemText primary={note.title} secondary={note.content} />
                  <ListItemSecondaryAction>
                    <IconButton onClick={() => togglePin(note)}>
                      {note.pinned ? <PushPin /> : <PushPinOutlined />}
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(true)} variant="contained">Add Note</Button>
          <Button onClick={() => setPopupOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      {/* Create note dialog */}
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
      {error && (
        <Alert severity="error" sx={{ position: 'fixed', top: 'var(--space-4)', right: 'var(--space-4)', zIndex: 1600 }}>
          {error}
        </Alert>
      )}
    </>
  );
};
export default StickyNotesPanel;