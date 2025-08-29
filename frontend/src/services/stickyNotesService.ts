// frontend/src/services/stickyNotesService.ts

import { apiRequest } from '../utils/api';

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
  private baseUrl = '/api/v1/sticky-notes';

  async getNotes(): Promise<StickyNote[]> {
    return await apiRequest('GET', this.baseUrl);
  }

  async createNote(noteData: StickyNoteCreate): Promise<StickyNote> {
    return await apiRequest('POST', this.baseUrl, noteData);
  }

  async updateNote(id: number, updateData: StickyNoteUpdate): Promise<StickyNote> {
    return await apiRequest('PUT', `${this.baseUrl}/${id}`, updateData);
  }

  async deleteNote(id: number): Promise<void> {
    return await apiRequest('DELETE', `${this.baseUrl}/${id}`);
  }

  async getUserSettings(): Promise<UserSettings> {
    return await apiRequest('GET', `${this.baseUrl}/settings/user-settings`);
  }

  async updateUserSettings(settings: UserSettingsUpdate): Promise<UserSettings> {
    return await apiRequest('PUT', `${this.baseUrl}/settings/user-settings`, settings);
  }
}

export const stickyNotesService = new StickyNotesService();