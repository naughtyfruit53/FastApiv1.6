
# SnappyMail Integration Documentation

## Overview
The application now includes SnappyMail email client integration that allows users to configure and access their email settings.

## Components

### 1. Database Model (`app/models/system_models.py`)
- **SnappyMailConfig**: Stores email configuration per user
- Fields: user_id, email, imap_host, imap_port, smtp_host, smtp_port, use_ssl, password

### 2. API Endpoint (`app/api/v1/mail.py`)
- **GET `/api/v1/mail/config/{user_id}`**: Retrieves SnappyMail configuration
- Authentication required (user must be owner or org_admin)
- Returns configuration without sensitive password field

### 3. Frontend Service (`frontend/src/services/emailService.ts`)
- **getSnappyMailConfig(userId)**: Fetches configuration from API
- **getSnappyMailUrl(userId)**: Constructs SnappyMail URL or returns fallback

### 4. Environment Variables
Required configuration in `.env`:
```
# SnappyMail Configuration
SNAPPYMAIL_IMAP_HOST=imap.gmail.com
SNAPPYMAIL_IMAP_PORT=993
SNAPPYMAIL_SMTP_HOST=smtp.gmail.com
SNAPPYMAIL_SMTP_PORT=587
SNAPPYMAIL_IMAP_SSL=true
SMTP_PASSWORD=your-email-password

# Frontend fallback
NEXT_PUBLIC_SNAPPYMAIL_URL=http://localhost:8888
```

### 5. Database Migration
- Migration file: `migrations/versions/19362ee21e5b_add_snappymail_config.py`
- Creates `snappymail_configs` table with proper indexes and constraints

## Setup Instructions

### 1. Environment Configuration
1. Copy the SnappyMail configuration variables to your `.env` file
2. Update the SMTP_PASSWORD with your email app password
3. Adjust IMAP/SMTP hosts for your email provider if not using Gmail

### 2. Database Setup
1. Run database migrations: `alembic upgrade head`
2. The `snappymail_configs` table will be created automatically

### 3. Seed Configuration (Optional)
1. Update `scripts/seed_snappymail_config.py` with the correct user email
2. Run: `python scripts/seed_snappymail_config.py`
3. This creates a test SnappyMail configuration for the specified user

### 4. Testing
1. Start the FastAPI server
2. Test the endpoint: `GET /api/v1/mail/config/{user_id}`
3. Verify frontend can fetch configuration

## Usage

### Backend Usage
```python
from app.models.system_models import SnappyMailConfig
from app.core.database import get_db

# Query user's SnappyMail config
config = db.query(SnappyMailConfig).filter(
    SnappyMailConfig.user_id == user_id
).first()
```

### Frontend Usage
```typescript
import { getSnappyMailConfig, getSnappyMailUrl } from '../services/emailService';

// Get configuration
const config = await getSnappyMailConfig(userId);

// Get SnappyMail URL
const url = await getSnappyMailUrl(userId);
```

## Error Handling
- **404**: No SnappyMail config found for user
- **403**: Insufficient permissions (not user owner or org_admin)
- **Failed to fetch email config**: Configuration not found, using fallback URL

## Security Notes
- Email passwords are stored encrypted in the database
- API endpoint excludes password field from responses
- Access restricted to user owner or organization admin only
