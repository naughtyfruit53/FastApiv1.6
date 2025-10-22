# Chatbot Widget Embedding Guide

## Overview

The TritIQ AI Chatbot Widget can be embedded in customer websites to provide intelligent assistance. This guide covers how to integrate the chatbot widget into various types of applications.

## Table of Contents

1. [Quick Start](#quick-start)
2. [React/Next.js Integration](#reactnextjs-integration)
3. [Standalone JavaScript Integration](#standalone-javascript-integration)
4. [Configuration Options](#configuration-options)
5. [Customization](#customization)
6. [API Integration](#api-integration)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Node.js 18+ (for React integration)
- Access to TritIQ API endpoint
- Valid authentication token

---

## React/Next.js Integration

### 1. Install Dependencies

If using as a component in your React/Next.js application:

```bash
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled axios
```

### 2. Copy ChatbotWidget Component

Copy the following files to your project:
- `frontend/src/components/ChatbotWidget.tsx`
- `frontend/src/services/aiService.ts`

### 3. Import and Use

```tsx
// pages/_app.tsx or layout.tsx
import ChatbotWidget from '../components/ChatbotWidget';

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <ChatbotWidget 
        position="bottom-right"
        primaryColor="#1976d2"
        onNavigate={(path) => {
          // Handle navigation
          window.location.href = path;
        }}
      />
    </>
  );
}

export default MyApp;
```

### 4. Configure API Endpoint

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://your-tritiq-api.com
```

---

## Standalone JavaScript Integration

### 1. Create Embed Script

Create a standalone bundle using Webpack/Rollup:

**webpack.config.js:**
```javascript
module.exports = {
  entry: './src/chatbot-standalone.tsx',
  output: {
    filename: 'tritiq-chatbot.js',
    library: 'TritIQChatbot',
    libraryTarget: 'umd'
  },
  // ... other config
};
```

### 2. Embed in HTML

Add to your website's HTML:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Your Website</title>
</head>
<body>
  <!-- Your website content -->
  
  <!-- TritIQ Chatbot Widget -->
  <div id="tritiq-chatbot-container"></div>
  
  <!-- Load chatbot script -->
  <script src="https://your-cdn.com/tritiq-chatbot.js"></script>
  <script>
    // Initialize chatbot
    TritIQChatbot.init({
      container: 'tritiq-chatbot-container',
      apiUrl: 'https://your-tritiq-api.com',
      position: 'bottom-right',
      primaryColor: '#1976d2',
      enableSuggestions: true,
      showInsights: true
    });
  </script>
</body>
</html>
```

### 3. Using CDN

```html
<!-- Load dependencies from CDN -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />

<!-- Load TritIQ Chatbot -->
<script src="https://cdn.tritiq.com/chatbot/v1/tritiq-chatbot.min.js"></script>
<script>
  TritIQChatbot.init({
    apiUrl: 'https://api.tritiq.com',
    apiKey: 'your-api-key',
    primaryColor: '#2196f3'
  });
</script>
```

---

## Configuration Options

### ChatbotWidget Props

```typescript
interface ChatbotWidgetProps {
  // Position of the chatbot
  position?: 'bottom-right' | 'bottom-left';
  
  // Primary color for branding
  primaryColor?: string;
  
  // API URL endpoint
  apiUrl?: string;
  
  // Custom navigation handler
  onNavigate?: (path: string) => void;
  
  // Enable/disable suggestions
  enableSuggestions?: boolean;
  
  // Show business insights
  showInsights?: boolean;
  
  // Custom greeting message
  greetingMessage?: string;
  
  // Custom placeholder text
  placeholderText?: string;
  
  // Enable/disable sound
  enableSound?: boolean;
  
  // Auto-open on page load
  autoOpen?: boolean;
  
  // Delay before auto-open (ms)
  autoOpenDelay?: number;
}
```

### Default Configuration

```typescript
const defaultConfig: ChatbotWidgetProps = {
  position: 'bottom-right',
  primaryColor: '#1976d2',
  enableSuggestions: true,
  showInsights: true,
  placeholderText: 'Type your message...',
  enableSound: false,
  autoOpen: false,
  autoOpenDelay: 3000
};
```

---

## Customization

### Custom Styling

#### Using CSS Variables

```css
:root {
  --chatbot-primary-color: #1976d2;
  --chatbot-text-color: #333;
  --chatbot-bg-color: #f5f5f5;
  --chatbot-border-radius: 8px;
  --chatbot-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

#### Custom CSS

```css
/* Customize chatbot container */
.tritiq-chatbot-container {
  font-family: 'Arial', sans-serif;
}

/* Customize message bubbles */
.tritiq-chatbot-message-user {
  background-color: #007bff;
  color: white;
}

.tritiq-chatbot-message-bot {
  background-color: #f0f0f0;
  color: #333;
}

/* Customize action buttons */
.tritiq-chatbot-action-button {
  background-color: transparent;
  border: 1px solid #1976d2;
  color: #1976d2;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.tritiq-chatbot-action-button:hover {
  background-color: #1976d2;
  color: white;
}
```

### Custom Branding

```tsx
<ChatbotWidget 
  position="bottom-right"
  primaryColor="#FF5722"  // Your brand color
  greetingMessage="Welcome to YourCompany! How can I help?"
  placeholderText="Ask me anything..."
/>
```

---

## API Integration

### Authentication

The chatbot requires authentication to access the API.

#### Using API Key

```typescript
import aiService from '@/services/aiService';

// Set API key in localStorage
localStorage.setItem('access_token', 'your-api-key');

// Now all API calls will include the token
const response = await aiService.processChatMessage({
  message: "Hello"
});
```

#### Using OAuth

```typescript
// After OAuth login
const token = await loginWithOAuth();
localStorage.setItem('access_token', token);
```

### Custom API Endpoints

If you need to use custom endpoints:

```typescript
// Modify aiService.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class AIService {
  private getHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }
  
  // Custom endpoint
  async customEndpoint(data: any): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/custom/endpoint`,
      data,
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}
```

---

## Troubleshooting

### Common Issues

#### 1. Chatbot Not Appearing

**Problem:** Chatbot widget doesn't show up on the page.

**Solutions:**
- Check if component is properly imported
- Verify z-index is high enough (should be > 1000)
- Check browser console for errors
- Ensure dependencies are installed

```tsx
// Check z-index
<ChatbotWidget 
  style={{ zIndex: 9999 }}
/>
```

#### 2. API Connection Errors

**Problem:** "Failed to fetch" or "Network error" in console.

**Solutions:**
- Verify API URL is correct
- Check if token is valid
- Ensure CORS is configured on backend
- Test API endpoint with curl/Postman

```bash
# Test API endpoint
curl -X POST https://your-api.com/api/v1/chatbot/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"message":"hello"}'
```

#### 3. Styling Issues

**Problem:** Chatbot looks broken or unstyled.

**Solutions:**
- Ensure Material-UI is properly installed
- Check if fonts are loading
- Verify CSS is not being overridden

```bash
# Install dependencies
npm install @mui/material @mui/icons-material
```

#### 4. Messages Not Sending

**Problem:** Messages don't send or get stuck.

**Solutions:**
- Check network tab in DevTools
- Verify API response format
- Check for JavaScript errors
- Ensure message is not empty

#### 5. Navigation Not Working

**Problem:** Action buttons don't navigate.

**Solutions:**
- Implement `onNavigate` handler
- Use React Router or Next.js router
- Check if paths are correct

```tsx
<ChatbotWidget 
  onNavigate={(path) => {
    // Using React Router
    history.push(path);
    
    // Or using Next.js
    router.push(path);
    
    // Or using window.location
    window.location.href = path;
  }}
/>
```

### Debug Mode

Enable debug mode to see detailed logs:

```typescript
// In aiService.ts
const DEBUG = true;

if (DEBUG) {
  console.log('[AIService] Request:', request);
  console.log('[AIService] Response:', response);
}
```

### Contact Support

If issues persist:
- Email: support@tritiq.com
- Documentation: https://docs.tritiq.com
- GitHub Issues: https://github.com/tritiq/erp/issues

---

## Performance Optimization

### Lazy Loading

Load chatbot only when needed:

```tsx
import dynamic from 'next/dynamic';

const ChatbotWidget = dynamic(
  () => import('../components/ChatbotWidget'),
  { ssr: false }
);
```

### Code Splitting

Split chatbot into separate bundle:

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      cacheGroups: {
        chatbot: {
          test: /[\\/]components[\\/]ChatbotWidget/,
          name: 'chatbot',
          chunks: 'all'
        }
      }
    }
  }
};
```

### Caching

Cache chatbot responses:

```typescript
const cache = new Map<string, ChatResponse>();

async function getCachedResponse(message: string): Promise<ChatResponse> {
  if (cache.has(message)) {
    return cache.get(message)!;
  }
  
  const response = await aiService.processChatMessage({ message });
  cache.set(message, response);
  return response;
}
```

---

## Advanced Features

### Custom Intents

Add custom intent handlers:

```typescript
// Custom intent handler
const handleCustomIntent = (intent: string, message: string) => {
  switch (intent) {
    case 'book_appointment':
      return {
        message: 'I can help you book an appointment.',
        actions: [
          { type: 'navigate', label: 'Book Now', data: { path: '/appointments' } }
        ]
      };
    default:
      return null;
  }
};
```

### Multi-language Support

Add language detection and translation:

```typescript
// Detect language
const detectLanguage = (message: string): string => {
  // Use language detection library
  return 'en';
};

// Translate response
const translateResponse = (response: string, targetLang: string): string => {
  // Use translation API
  return response;
};
```

### Voice Input

Add speech recognition:

```typescript
// Enable voice input
const startVoiceInput = () => {
  const recognition = new webkitSpeechRecognition();
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInputText(transcript);
  };
  recognition.start();
};
```

---

## Security Best Practices

1. **Never expose API keys in client-side code**
   ```typescript
   // ❌ Bad
   const API_KEY = 'sk-1234567890';
   
   // ✅ Good
   const API_KEY = process.env.NEXT_PUBLIC_API_KEY;
   ```

2. **Use HTTPS in production**
   ```typescript
   const API_URL = process.env.NODE_ENV === 'production'
     ? 'https://api.tritiq.com'
     : 'http://localhost:8000';
   ```

3. **Validate user input**
   ```typescript
   const sanitizeInput = (input: string): string => {
     return input.trim().slice(0, 1000); // Limit length
   };
   ```

4. **Rate limiting**
   ```typescript
   let requestCount = 0;
   const MAX_REQUESTS = 10;
   
   const checkRateLimit = (): boolean => {
     if (requestCount >= MAX_REQUESTS) {
       return false;
     }
     requestCount++;
     return true;
   };
   ```

---

## Examples

### E-commerce Website

```tsx
<ChatbotWidget 
  position="bottom-right"
  primaryColor="#FF6B6B"
  greetingMessage="Welcome to our store! How can I help you find products today?"
  onNavigate={(path) => {
    // Custom navigation for e-commerce
    if (path.includes('/products')) {
      router.push(path);
    } else {
      window.location.href = path;
    }
  }}
/>
```

### SaaS Application

```tsx
<ChatbotWidget 
  position="bottom-left"
  primaryColor="#4CAF50"
  enableSuggestions={true}
  showInsights={true}
  greetingMessage="Need help? I'm here to assist you!"
/>
```

### Corporate Website

```tsx
<ChatbotWidget 
  position="bottom-right"
  primaryColor="#1565C0"
  placeholderText="Ask about our services..."
  autoOpen={true}
  autoOpenDelay={5000}
/>
```

---

## License

Copyright © 2025 TritIQ. All rights reserved.

For licensing inquiries, contact: licensing@tritiq.com
