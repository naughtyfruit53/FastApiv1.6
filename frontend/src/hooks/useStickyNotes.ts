// frontend/src/hooks/useStickyNotes.ts
import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  stickyNotesService,
  StickyNote,
  UserSettings,
} from "../services/stickyNotesService";
export const useStickyNotes = (): any => {
  const { user } = useAuth();
  const [notes, setNotes] = useState<StickyNote[]>([]);
  const [userSettings, setUserSettings] = useState<UserSettings>({
    sticky_notes_enabled: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fetchUserSettings = async () => {
    try {
      const settings = await stickyNotesService.getUserSettings();
      setUserSettings(settings);
    } catch (err) {
      console.error("Error fetching user settings:", err);
      // Use disabled settings if fetch fails to prevent unauthorized fetches
      setUserSettings({ sticky_notes_enabled: false });
    }
  };
  const fetchNotes = async () => {
    try {
      setLoading(true);
      const notesData = await stickyNotesService.getNotes();
      setNotes(notesData);
      setError(null);
    } catch (err) {
      console.error("Error fetching notes:", err);
      setError("Failed to load sticky notes");
    } finally {
      setLoading(false);
    }
  };
  const toggleStickyNotes = async (enabled: boolean) => {
    try {
      const updatedSettings = await stickyNotesService.updateUserSettings({
        sticky_notes_enabled: enabled,
      });
      setUserSettings(updatedSettings);
      return updatedSettings;
    } catch (err) {
      console.error("Error updating user settings:", err);
      throw err;
    }
  };
  useEffect(() => {
    if (user) {
      fetchUserSettings();
    } else {
      setUserSettings({ sticky_notes_enabled: false });
    }
  }, [user]);
  useEffect(() => {
    if (userSettings.sticky_notes_enabled && user) {
      fetchNotes();
    }
  }, [userSettings.sticky_notes_enabled, user]);
  return {
    notes,
    userSettings,
    loading,
    error,
    fetchNotes,
    toggleStickyNotes,
    refreshSettings: fetchUserSettings,
  };
};
export default useStickyNotes;
