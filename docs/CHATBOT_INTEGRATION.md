# Service Module Chatbot Integration Guide

## Overview

The TritiQ ERP system includes a powerful AI chatbot that can be integrated into customer websites to provide real-time support, lead generation, and service ticket creation capabilities.

## Table of Contents

1. [Features](#features)
2. [Integration Methods](#integration-methods)
3. [Website Integration Script](#website-integration-script)
4. [Configuration Options](#configuration-options)
5. [API Endpoints](#api-endpoints)
6. [Customization](#customization)
7. [Security](#security)

---

## Features

### Core Capabilities

- **Business Advice**: Get recommendations on inventory, cash flow, and sales strategies
- **Navigation Assistance**: Quick navigation to any module or feature
- **Voucher Creation**: Create invoices, orders, and other vouchers through natural language
- **Lead Management**: Create and track leads from chat interactions
- **Tax Queries**: GST guidance and tax-related queries
- **Analytics Insights**: Access to sales, customer, and financial analytics

### Service Module Features

- **Ticket Creation**: Customers can create service tickets directly through chat
- **Ticket Status**: Check status of existing service requests
- **Knowledge Base**: Access to common issues and solutions
- **SLA Tracking**: View SLA compliance and expected resolution times

---

## Integration Methods

### Method 1: Direct Script Injection (Recommended)

Add the following script to your website's HTML, just before the closing `</body>` tag:

```html
<!-- TritiQ ERP Chatbot Integration -->
<script>
  (function() {
    var config = {
      apiUrl: 'https://your-erp-domain.com/api/v1',
      organizationId: 'YOUR_ORG_ID',
      apiKey: 'YOUR_API_KEY',
      theme: {
        primaryColor: '#1976d2',
        headerText: 'Chat with us',
        position: 'bottom-right', // or 'bottom-left'
        welcomeMessage: 'Hi! How can I help you today?'
      }
    };
    
    var script = document.createElement('script');
    script.src = 'https://your-erp-domain.com/static/chatbot-widget.js';
    script.async = true;
    script.onload = function() {
      TritiQChatbot.init(config);
    };
    document.body.appendChild(script);
    
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://your-erp-domain.com/static/chatbot-widget.css';
    document.head.appendChild(link);
  })();
</script>
```

### Method 2: NPM Package (For React/Vue/Angular)

```bash
npm install @tritiq/chatbot-widget
```

Then in your application:

```javascript
import { TritiQChatbot } from '@tritiq/chatbot-widget';
import '@tritiq/chatbot-widget/dist/styles.css';

TritiQChatbot.init({
  apiUrl: 'https://your-erp-domain.com/api/v1',
  organizationId: 'YOUR_ORG_ID',
  apiKey: 'YOUR_API_KEY',
  theme: {
    primaryColor: '#1976d2',
    headerText: 'Chat with us',
    position: 'bottom-right'
  }
});
```

### Method 3: iframe Embedding

```html
<iframe 
  src="https://your-erp-domain.com/chatbot/widget?org=YOUR_ORG_ID&key=YOUR_API_KEY"
  width="400" 
  height="600"
  frameborder="0"
  style="position: fixed; bottom: 20px; right: 20px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>
```

---

## Website Integration Script

### Complete Integration Example

Save this as `chatbot-integration.js`:

```javascript
/**
 * TritiQ ERP Chatbot Widget Integration
 * Version: 1.0.0
 */

class TritiQChatbotWidget {
  constructor(config) {
    this.config = {
      apiUrl: config.apiUrl || 'https://api.tritiq.com/api/v1',
      organizationId: config.organizationId,
      apiKey: config.apiKey,
      theme: {
        primaryColor: config.theme?.primaryColor || '#1976d2',
        headerText: config.theme?.headerText || 'Support Chat',
        position: config.theme?.position || 'bottom-right',
        welcomeMessage: config.theme?.welcomeMessage || 'Hello! How can I assist you?',
        ...config.theme
      },
      features: {
        ticketCreation: config.features?.ticketCreation !== false,
        leadCapture: config.features?.leadCapture !== false,
        knowledgeBase: config.features?.knowledgeBase !== false,
        ...config.features
      }
    };
    
    this.isOpen = false;
    this.messages = [];
    this.sessionId = this.generateSessionId();
    
    this.init();
  }
  
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  init() {
    this.createWidget();
    this.attachEventListeners();
    this.loadWelcomeMessage();
  }
  
  createWidget() {
    const position = this.config.theme.position;
    const positionStyles = position === 'bottom-left' 
      ? 'left: 20px; bottom: 20px;' 
      : 'right: 20px; bottom: 20px;';
    
    const widgetHTML = `
      <div id="tritiq-chatbot-container" style="position: fixed; ${positionStyles} z-index: 9999;">
        <!-- Chat Button -->
        <button id="tritiq-chat-toggle" style="
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: ${this.config.theme.primaryColor};
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s;
        ">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
          </svg>
        </button>
        
        <!-- Chat Window -->
        <div id="tritiq-chat-window" style="
          display: none;
          position: absolute;
          bottom: 70px;
          ${position === 'bottom-left' ? 'left: 0;' : 'right: 0;'}
          width: 380px;
          height: 600px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.2);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        ">
          <!-- Header -->
          <div style="
            background: ${this.config.theme.primaryColor};
            color: white;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
          ">
            <span style="font-weight: 600; font-size: 16px;">${this.config.theme.headerText}</span>
            <button id="tritiq-chat-close" style="
              background: transparent;
              border: none;
              color: white;
              cursor: pointer;
              font-size: 24px;
              padding: 0;
              width: 24px;
              height: 24px;
            ">&times;</button>
          </div>
          
          <!-- Messages -->
          <div id="tritiq-chat-messages" style="
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f5f5f5;
          "></div>
          
          <!-- Input -->
          <div style="
            padding: 16px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 8px;
          ">
            <input 
              id="tritiq-chat-input" 
              type="text" 
              placeholder="Type your message..."
              style="
                flex: 1;
                padding: 10px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
                outline: none;
                font-size: 14px;
              "
            />
            <button id="tritiq-chat-send" style="
              background: ${this.config.theme.primaryColor};
              color: white;
              border: none;
              border-radius: 50%;
              width: 40px;
              height: 40px;
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
            ">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', widgetHTML);
  }
  
  attachEventListeners() {
    const toggleBtn = document.getElementById('tritiq-chat-toggle');
    const closeBtn = document.getElementById('tritiq-chat-close');
    const sendBtn = document.getElementById('tritiq-chat-send');
    const input = document.getElementById('tritiq-chat-input');
    
    toggleBtn.addEventListener('click', () => this.toggleChat());
    closeBtn.addEventListener('click', () => this.toggleChat());
    sendBtn.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
  }
  
  toggleChat() {
    this.isOpen = !this.isOpen;
    const window = document.getElementById('tritiq-chat-window');
    window.style.display = this.isOpen ? 'flex' : 'none';
  }
  
  loadWelcomeMessage() {
    this.addMessage({
      text: this.config.theme.welcomeMessage,
      isBot: true
    });
  }
  
  addMessage(message) {
    const messagesContainer = document.getElementById('tritiq-chat-messages');
    const messageEl = document.createElement('div');
    messageEl.style.cssText = `
      margin-bottom: 12px;
      display: flex;
      ${message.isBot ? 'justify-content: flex-start;' : 'justify-content: flex-end;'}
    `;
    
    messageEl.innerHTML = `
      <div style="
        background: ${message.isBot ? 'white' : this.config.theme.primaryColor};
        color: ${message.isBot ? '#333' : 'white'};
        padding: 10px 14px;
        border-radius: 16px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
      ">
        ${message.text}
      </div>
    `;
    
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  async sendMessage() {
    const input = document.getElementById('tritiq-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    this.addMessage({ text: message, isBot: false });
    input.value = '';
    
    // Show typing indicator
    this.showTypingIndicator();
    
    try {
      // Call API
      const response = await fetch(`${this.config.apiUrl}/chatbot/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.config.apiKey,
          'X-Organization-ID': this.config.organizationId
        },
        body: JSON.stringify({
          message: message,
          context: {
            sessionId: this.sessionId,
            source: 'website',
            timestamp: new Date().toISOString()
          }
        })
      });
      
      const data = await response.json();
      
      // Hide typing indicator
      this.hideTypingIndicator();
      
      // Add bot response
      this.addMessage({ text: data.message, isBot: true });
      
      // Handle actions if present
      if (data.actions && data.actions.length > 0) {
        this.showActions(data.actions);
      }
      
    } catch (error) {
      this.hideTypingIndicator();
      this.addMessage({ 
        text: 'Sorry, I encountered an error. Please try again.', 
        isBot: true 
      });
      console.error('Chatbot error:', error);
    }
  }
  
  showTypingIndicator() {
    const messagesContainer = document.getElementById('tritiq-chat-messages');
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.style.cssText = 'margin-bottom: 12px;';
    indicator.innerHTML = `
      <div style="
        background: white;
        padding: 10px 14px;
        border-radius: 16px;
        display: inline-block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
      ">
        <span style="animation: blink 1.4s infinite;">●</span>
        <span style="animation: blink 1.4s infinite 0.2s;">●</span>
        <span style="animation: blink 1.4s infinite 0.4s;">●</span>
      </div>
    `;
    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
  }
  
  showActions(actions) {
    const messagesContainer = document.getElementById('tritiq-chat-messages');
    const actionsEl = document.createElement('div');
    actionsEl.style.cssText = 'margin-bottom: 12px;';
    
    const actionButtons = actions.map(action => `
      <button onclick="TritiQChatbot.handleAction('${action.type}', '${JSON.stringify(action.data).replace(/"/g, '&quot;')}')" style="
        background: white;
        border: 1px solid ${this.config.theme.primaryColor};
        color: ${this.config.theme.primaryColor};
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        cursor: pointer;
        font-size: 13px;
      ">
        ${action.label}
      </button>
    `).join('');
    
    actionsEl.innerHTML = `<div style="display: flex; flex-wrap: wrap;">${actionButtons}</div>`;
    messagesContainer.appendChild(actionsEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  handleAction(type, dataStr) {
    const data = JSON.parse(dataStr.replace(/&quot;/g, '"'));
    
    if (type === 'navigate' && data.path) {
      // Open in new window or redirect
      window.open(this.config.apiUrl.replace('/api/v1', '') + data.path, '_blank');
    } else if (type === 'create_ticket') {
      // Handle ticket creation
      this.addMessage({ 
        text: 'I\'ll help you create a ticket. Please provide more details.', 
        isBot: true 
      });
    }
  }
}

// Global initialization function
window.TritiQChatbot = {
  init: function(config) {
    if (!config.organizationId || !config.apiKey) {
      console.error('TritiQ Chatbot: organizationId and apiKey are required');
      return;
    }
    
    new TritiQChatbotWidget(config);
  }
};

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
  @keyframes blink {
    0%, 50%, 100% { opacity: 0.3; }
    25%, 75% { opacity: 1; }
  }
`;
document.head.appendChild(style);
```

---

## Configuration Options

### Required Configuration

| Option | Type | Description |
|--------|------|-------------|
| `apiUrl` | string | Base URL of your ERP API |
| `organizationId` | string | Your organization ID |
| `apiKey` | string | API key for authentication |

### Theme Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `primaryColor` | string | `#1976d2` | Primary brand color |
| `headerText` | string | `'Support Chat'` | Header title |
| `position` | string | `'bottom-right'` | Widget position |
| `welcomeMessage` | string | `'Hello! How can I assist you?'` | Initial message |

### Features Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ticketCreation` | boolean | `true` | Enable ticket creation |
| `leadCapture` | boolean | `true` | Enable lead capture |
| `knowledgeBase` | boolean | `true` | Enable knowledge base |

---

## API Endpoints

### Process Message

```http
POST /api/v1/chatbot/process
Content-Type: application/json
X-API-Key: YOUR_API_KEY
X-Organization-ID: YOUR_ORG_ID

{
  "message": "I need help with inventory",
  "context": {
    "sessionId": "session_123",
    "source": "website"
  }
}
```

**Response:**

```json
{
  "message": "I can help you with inventory. What would you like to know?",
  "intent": "inventory_help",
  "confidence": 0.95,
  "actions": [
    {
      "type": "navigate",
      "label": "View Inventory",
      "data": { "path": "/inventory" }
    }
  ],
  "suggestions": ["Show low stock items", "View stock reports"]
}
```

---

## Customization

### Custom Styling

Add your own CSS to override default styles:

```css
#tritiq-chatbot-container {
  font-family: 'Your Font', sans-serif !important;
}

#tritiq-chat-window {
  border-radius: 20px !important;
}
```

### Custom Intents

Configure custom business-specific intents:

```javascript
TritiQChatbot.init({
  // ... other config
  customIntents: [
    {
      keywords: ['warranty', 'guarantee'],
      response: 'Our products come with a 2-year warranty...',
      actions: [
        { type: 'navigate', label: 'Warranty Policy', data: { path: '/warranty' } }
      ]
    }
  ]
});
```

---

## Security

### Best Practices

1. **Use HTTPS**: Always serve the chatbot over HTTPS
2. **Rotate API Keys**: Regularly rotate your API keys
3. **Rate Limiting**: Implement rate limiting on your API
4. **Input Sanitization**: All user inputs are sanitized on the backend
5. **CORS Configuration**: Properly configure CORS for your domain

### API Key Management

```javascript
// Store API key securely, never expose in client code
// Use environment variables or secure storage
const config = {
  apiKey: process.env.TRITIQ_API_KEY,
  // ...
};
```

---

## Support

For technical support or questions:
- Documentation: https://docs.tritiq.com
- Email: support@tritiq.com
- GitHub Issues: https://github.com/tritiq/erp/issues

---

## License

Copyright © 2024 TritiQ. All rights reserved.
