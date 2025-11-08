# API Client Guide

## Overview

The FastAPI v1.6 application uses a centralized API client configuration to prevent common issues like URL duplication, inconsistent error handling, and token management problems.

## Centralized Configuration

### Using the Config Module

All API URLs should be retrieved from the centralized configuration:

```typescript
import { getApiUrl, getApiBaseUrl } from '../utils/config';

// Get full API URL (includes /api/v1)
const apiUrl = getApiUrl(); // Returns: http://localhost:8000/api/v1

// Get base URL (without /api/v1)
const baseUrl = getApiBaseUrl(); // Returns: http://localhost:8000
```

### Why Centralized Configuration?

**Problem:** Before centralization, services defined their own API URLs, leading to:
- Duplicated `/api/v1/api/v1/...` in URLs
- Inconsistent base URL handling
- Hard-to-maintain scattered configurations

**Solution:** Single source of truth in `utils/config.ts`:
- Automatically removes trailing slashes
- Prevents accidental `/api/v1` duplication
- Environment variable support with sensible defaults

## API Client Usage

### Standard Client

Use the centralized API client for most operations:

```typescript
import { apiClient } from '../services/api/client';

// GET request
const response = await apiClient.get('/users');

// POST request
const response = await apiClient.post('/users', userData);

// PUT request
const response = await apiClient.put(`/users/${id}`, userData);

// DELETE request
const response = await apiClient.delete(`/users/${id}`);

// File upload
const response = await apiClient.uploadFile('/upload', file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});

// File download
await apiClient.downloadFile('/files/123', 'document.pdf');
```

### Features

#### 1. Automatic Token Management
- Automatically attaches Bearer token from localStorage
- Validates JWT format (must have 3 parts: header.payload.signature)
- Refreshes expired tokens automatically

#### 2. Retry Logic
- Automatically retries on network errors
- Exponential backoff for transient failures
- Configurable retry count (default: 3 attempts)

#### 3. Enhanced Error Handling
- User-friendly error messages for 401, 403, 404 errors
- Automatic token refresh on 401
- Structured error responses with context

#### 4. Request/Response Logging
- Development mode logging for debugging
- Timestamps and request details
- Error context preservation

## Error Handling

### 401 Unauthorized
When a 401 error occurs:
1. Client attempts to refresh the access token using refresh token
2. If refresh succeeds, retries the original request
3. If refresh fails, clears tokens and redirects to login

```typescript
// Handled automatically - no code needed
const response = await apiClient.get('/protected-resource');
```

### 403 Forbidden (Permission Denied)
Provides clear error messages indicating:
- The required permission
- The module that was accessed
- User-friendly explanation

```typescript
try {
  await apiClient.post('/admin/users', userData);
} catch (error) {
  // Error message includes permission details
  console.error(error.message); // "You don't have permission..."
}
```

### 404 Not Found
Enhanced to detect access denials disguised as 404s:
```typescript
try {
  await apiClient.get('/resource/123');
} catch (error) {
  // Will indicate if it's an access issue
  console.error(error.message);
}
```

### Network Errors
User-friendly messages for connection issues:
```typescript
try {
  await apiClient.get('/api/endpoint');
} catch (error) {
  // "Failed to establish a secure connection..."
}
```

## Creating New Services

When creating a new service, follow this pattern:

```typescript
import { getApiUrl } from '../utils/config';
import axios from 'axios';

// DO THIS ✓
const API_BASE_URL = getApiUrl();

// Then use it directly without appending /api/v1
export async function fetchData() {
  const response = await axios.get(`${API_BASE_URL}/my-endpoint`);
  return response.data;
}

// DON'T DO THIS ✗
const API_BASE_URL = 'http://localhost:8000';
const response = await axios.get(`${API_BASE_URL}/api/v1/my-endpoint`);
```

## Best Practices

### 1. Always Use Centralized Config
```typescript
// ✓ Good
import { getApiUrl } from '../utils/config';
const API_URL = getApiUrl();

// ✗ Bad
const API_URL = process.env.NEXT_PUBLIC_API_URL + '/api/v1';
```

### 2. Use the API Client
```typescript
// ✓ Good - uses all built-in features
import { apiClient } from '../services/api/client';
await apiClient.get('/users');

// ✗ Bad - manual token handling, no retry, poor errors
import axios from 'axios';
await axios.get('/api/v1/users', {
  headers: { Authorization: `Bearer ${token}` }
});
```

### 3. Handle Errors Gracefully
```typescript
// ✓ Good
try {
  const data = await apiClient.get('/data');
  return data;
} catch (error) {
  // Error already has user-friendly message
  showNotification(error.message);
  return null;
}
```

### 4. Use Proper TypeScript Types
```typescript
interface User {
  id: number;
  name: string;
}

const response = await apiClient.get<User[]>('/users');
// response.data is typed as User[]
```

## Configuration Options

### Environment Variables

Set in `.env.local`:
```bash
# API base URL (without /api/v1)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The config module will automatically append `/api/v1` when needed.

### Feature Flags

Additional configuration options in `utils/config.ts`:
```typescript
export const config = {
  apiUrl: getApiBaseUrl(),
  apiUrlWithPath: getApiUrl(),
  features: {
    // Feature flags...
  }
};
```

## Troubleshooting

### Issue: Getting `/api/v1/api/v1/` in URLs

**Cause:** Manually appending `/api/v1` when using `getApiUrl()`

**Solution:** Use `getApiUrl()` directly without appending path
```typescript
// ✗ Wrong
const url = `${getApiUrl()}/api/v1/users`; // Results in /api/v1/api/v1/users

// ✓ Correct
const url = `${getApiUrl()}/users`; // Results in /api/v1/users
```

### Issue: 401 Errors Not Refreshing Token

**Cause:** Token not in localStorage or invalid format

**Solution:** Ensure token is stored properly
```typescript
localStorage.setItem('access_token', validJWT);
localStorage.setItem('refresh_token', refreshToken);
```

### Issue: CORS Errors

**Cause:** Mismatched base URLs or credentials mode

**Solution:** Check `withCredentials` setting in client config and ensure backend CORS is configured

## Testing

### Unit Tests
```typescript
import { apiClient } from '../services/api/client';

// Mock the client for testing
jest.mock('../services/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  }
}));

// In test
(apiClient.get as jest.Mock).mockResolvedValue({ data: mockData });
```

### Integration Tests
See `frontend/src/services/api/__tests__/client.test.ts` for examples.

## Migration Guide

### Migrating Existing Services

1. Replace hardcoded URLs:
```typescript
// Before
const API_URL = 'http://localhost:8000/api/v1';

// After
import { getApiUrl } from '../utils/config';
const API_URL = getApiUrl();
```

2. Remove duplicate `/api/v1` from endpoints:
```typescript
// Before
axios.get(`${API_URL}/api/v1/users`)

// After
axios.get(`${API_URL}/users`)
```

3. Consider using apiClient instead of raw axios:
```typescript
// Before
const response = await axios.get(`${API_URL}/users`, {
  headers: { Authorization: `Bearer ${token}` }
});

// After
const response = await apiClient.get('/users');
// Token handling is automatic
```

## See Also

- [Module-Menu-Permission Mapping Guide](./MODULE_MENU_PERMISSION_MAPPING.md)
- [Entitlements Implementation](./ENTITLEMENTS_IMPLEMENTATION_SUMMARY.md)
- [RBAC Documentation](./RBAC_COMPREHENSIVE_GUIDE.md)
