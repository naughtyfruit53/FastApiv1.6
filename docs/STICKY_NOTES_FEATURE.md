# Sticky Notes Feature Documentation

## Overview

The sticky notes feature allows users to create, edit, and manage personal notes directly on their dashboard. This feature provides a convenient way for users to keep track of important information, reminders, and quick notes.

## Features

### User Experience
- **Dashboard Integration**: Sticky notes panel appears at the top of the dashboard
- **Visual Appeal**: Each note appears as a colored card with shadow effects
- **Interactive**: Users can create, edit, save, and delete notes with intuitive UI
- **Customizable**: Six color themes available (yellow, blue, green, pink, purple, orange)
- **Responsive**: Works seamlessly across desktop and mobile devices
- **Collapsible**: Panel can be expanded/collapsed to save space

### User Control
- **Settings Toggle**: Organization users can enable/disable sticky notes via Settings page
- **Personal Scope**: Notes are user-specific and private
- **Persistent Storage**: Notes are saved in the database and persist across sessions

## API Endpoints

### Sticky Notes Management
- `GET /api/v1/sticky-notes/` - Retrieve user's sticky notes
- `POST /api/v1/sticky-notes/` - Create a new sticky note
- `GET /api/v1/sticky-notes/{id}` - Get specific sticky note
- `PUT /api/v1/sticky-notes/{id}` - Update sticky note
- `DELETE /api/v1/sticky-notes/{id}` - Delete sticky note (soft delete)

### User Settings
- `GET /api/v1/sticky-notes/settings/user-settings` - Get user preferences
- `PUT /api/v1/sticky-notes/settings/user-settings` - Update user preferences

## Database Schema

### sticky_notes Table
```sql
CREATE TABLE sticky_notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    color VARCHAR(20) NOT NULL DEFAULT 'yellow',
    position JSON,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### users Table Addition
- Added `user_settings` JSON field to store user preferences including `sticky_notes_enabled`

## Frontend Components

### StickyNotesPanel
- Main container component for the sticky notes section
- Handles CRUD operations and state management
- Provides create note dialog and error handling
- Responsive horizontal scrolling for multiple notes

### StickyNote
- Individual note component with rich functionality
- Inline editing with save/cancel options
- Color picker for theme customization
- Delete confirmation dialog
- Hover effects and animations

### UserPreferences
- Settings component for user preferences
- Toggle switch for enabling/disabling sticky notes
- Real-time feedback for setting changes

## Technical Implementation

### Backend (FastAPI)
- **Models**: SQLAlchemy models with proper relationships
- **Schemas**: Pydantic models for request/response validation
- **Security**: Organization-scoped access with user isolation
- **Performance**: Indexed queries for efficient data retrieval

### Frontend (Next.js + TypeScript)
- **State Management**: Custom hook `useStickyNotes` for centralized state
- **API Layer**: Service class with proper error handling
- **UI Framework**: Material-UI components with custom styling
- **TypeScript**: Full type safety across all components

### Database
- **Multi-tenancy**: Organization-scoped data isolation
- **Indexing**: Proper indexes for user_id and organization_id
- **Soft Delete**: Notes marked as inactive instead of hard deletion
- **JSON Storage**: Flexible user settings storage

## Usage

### For Users
1. Navigate to the dashboard
2. If sticky notes are enabled, see the panel at the top
3. Click "Add Note" to create a new note
4. Fill in title and content, choose a color
5. Edit notes by clicking the menu icon and selecting "Edit"
6. Change colors using the color picker
7. Delete notes with confirmation dialog

### For Administrators
1. Go to Settings page
2. Find "User Preferences" section
3. Toggle "Enable Sticky Notes" to show/hide the feature
4. Changes take effect immediately

## Color Themes
- **Yellow**: Default sunny note color
- **Blue**: Professional and calming
- **Green**: Natural and fresh
- **Pink**: Warm and friendly
- **Purple**: Creative and unique
- **Orange**: Energetic and vibrant

## Security Considerations
- User notes are isolated by organization and user ID
- No cross-user access to notes
- Soft delete preserves data for potential recovery
- Standard authentication and authorization applied

## Future Enhancements
- Drag and drop positioning
- Note categories and tags
- Search functionality within notes
- Note sharing capabilities
- Rich text formatting
- Due dates and reminders
- Note templates