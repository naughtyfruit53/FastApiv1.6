// frontend/src/services/stickyNotesService.ts

import api from '../lib/api';

export interface StickyNote {
  id: number;
  title: string;
  content: string;
  color: string;
  created_at: string;
  updated_at?: string;
}

export interface StickyNoteCreate {
  title: string;
  content: string;
  color: string;
}

export interface StickyNoteUpdate {
  title?: string;
  content?: string;
  color?: string;
}

export interface UserSettings {
  sticky_notes_enabled: boolean;
}

export interface UserSettingsUpdate {
  sticky_notes_enabled?: boolean;
}

class StickyNotesService {
  private baseUrl = '/sticky_notes';

  async getNotes(): Promise<StickyNote[]> {
    try {
      const response = await api.get<StickyNote[]>(this.baseUrl);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch sticky notes:', error);
      throw error;
    }
  }

  async createNote(noteData: StickyNoteCreate): Promise<StickyNote> {
    try {
      const response = await api.post<StickyNote>(this.baseUrl, noteData);
      return response.data;
    } catch (error) {
      console.error('Failed to create sticky note:', error);
      throw error;
    }
  }

  async updateNote(id: number, updateData: StickyNoteUpdate): Promise<StickyNote> {
    try {
      const response = await api.put<StickyNote>(`${this.baseUrl}/${id}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Failed to update sticky note:', error);
      throw error;
    }
  }

  async deleteNote(id: number): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${id}`);
    } catch (error) {
      console.error('Failed to delete sticky note:', error);
      throw error;
    }
  }

  async getUserSettings(): Promise<UserSettings> {
    try {
      const response = await api.get<UserSettings>(`${this.baseUrl}/settings/user-settings`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user settings:', error);
      throw error;
    }
  }

  async updateUserSettings(settings: UserSettingsUpdate): Promise<UserSettings> {
    try {
      const response = await api.put<UserSettings>(`${this.baseUrl}/settings/user-settings`, settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update user settings:', error);
      throw error;
    }
  }
}

export const stickyNotesService = new StickyNotesService();