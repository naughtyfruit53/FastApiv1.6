# AI Help & Chatbot Integration Guide

## Overview

The TritIQ Business Suite includes an integrated AI-powered help system that provides contextual assistance, intelligent Q&A, and guided support for mobile and demo modes.

## Features

### 1. Contextual Help
- **Smart Context Detection**: Automatically detects the current page, module, and user activity
- **Relevant Suggestions**: Provides suggestions based on user context
- **Quick Actions**: Suggests next steps and common workflows
- **Related Topics**: Links to related help content

### 2. AI Chatbot
- **Natural Language Processing**: Understands questions in natural language
- **Intent Recognition**: Identifies user intent and provides relevant answers
- **Conversation History**: Maintains conversation context for follow-up questions
- **Confidence Scoring**: Shows confidence level for AI responses

### 3. Mobile Optimization
- **Touch-Friendly Interface**: Optimized for mobile interactions
- **Compact Mode**: Space-efficient design for small screens
- **Quick Access**: Always available through floating action button
- **Offline Graceful Degradation**: Basic help available offline

### 4. Demo Mode Integration
- **Demo-Specific Help**: Tailored guidance for demo mode features
- **Feature Tours**: Step-by-step walkthroughs of system capabilities
- **Sample Data Explanation**: Context about mock data and its usage
- **Exploration Guidance**: Helps users discover features

## Architecture

### Frontend Components

#### AIChatbot Component
Located: `frontend/src/ai/AIChatbot.tsx`

A React component that provides the chatbot UI.

**Props:**
```typescript
interface AIChatbotProps {
  open: boolean;              // Controls visibility
  onClose: () => void;        // Close handler
  context?: AIContext;        // Current context
  position?: 'bottom-right' | 'bottom-left' | 'center';
  variant?: 'compact' | 'full';
}
```

**Usage:**
```tsx
import { AIChatbot } from '@/ai/AIChatbot';

<AIChatbot
  open={chatOpen}
  onClose={() => setChatOpen(false)}
  context={{
    page: 'sales',
    module: 'orders',
    isDemoMode: true,
    isMobile: true
  }}
  position="bottom-right"
  variant="compact"
/>
```

#### AI Help Service
Located: `frontend/src/ai/aiHelpService.ts`

Service for AI interactions and help content.

**Key Methods:**
```typescript
// Send message to AI
await aiHelpService.sendMessage(message, context);

// Get contextual help
await aiHelpService.getContextualHelp(context);

// Get quick suggestions
await aiHelpService.getQuickSuggestions(context);

// Manage conversation history
aiHelpService.getHistory();
aiHelpService.clearHistory();
```

### Context Detection

The AI help system automatically detects:

1. **Page Context**: Current page URL and title
2. **Module Context**: Active business module (sales, inventory, etc.)
3. **User Role**: User's role and permissions
4. **Demo Mode**: Whether in demo or production mode
5. **Device Type**: Mobile, tablet, or desktop
6. **Previous Actions**: Recent user interactions

### Response Generation

AI responses include:

```typescript
interface AIResponse {
  message: string;           // Main response text
  confidence: number;        // Confidence score (0-1)
  intent: string;           // Detected user intent
  suggestions?: string[];    // Follow-up suggestions
  relatedTopics?: string[];  // Related help topics
  quickActions?: Array<{     // Suggested actions
    label: string;
    action: string;
  }>;
}
```

## Integration Guide

### Adding AI Help to a Page

1. **Import the chatbot:**
```tsx
import { AIChatbot } from '@/ai/AIChatbot';
import { useState } from 'react';
```

2. **Add state management:**
```tsx
const [chatOpen, setChatOpen] = useState(false);
```

3. **Define context:**
```tsx
const context = {
  page: 'sales-orders',
  module: 'sales',
  isDemoMode: demoMode,
  isMobile: isMobileView,
};
```

4. **Add help button:**
```tsx
<IconButton
  onClick={() => setChatOpen(true)}
  aria-label="Open AI help"
>
  <HelpIcon />
</IconButton>
```

5. **Add chatbot component:**
```tsx
<AIChatbot
  open={chatOpen}
  onClose={() => setChatOpen(false)}
  context={context}
/>
```

### Mobile Implementation

For mobile pages, use compact variant:

```tsx
<AIChatbot
  open={chatOpen}
  onClose={() => setChatOpen(false)}
  context={context}
  position="bottom-right"
  variant="compact"
/>
```

Add a floating action button:

```tsx
<Fab
  color="primary"
  aria-label="AI Help"
  sx={{
    position: 'fixed',
    bottom: 16,
    right: 16,
    zIndex: 1000,
  }}
  onClick={() => setChatOpen(true)}
>
  <SmartToyIcon />
</Fab>
```

### Demo Mode Integration

Enable demo-specific help:

```tsx
const context = {
  page: currentPage,
  module: currentModule,
  isDemoMode: true,  // Enable demo mode features
  previousActions: userActions,
};
```

Demo mode provides:
- Feature discovery tips
- Sample data explanations
- Guided tours
- Common workflows

## Customization

### Custom Prompts

Add custom help prompts for specific modules:

```typescript
const customPrompts = {
  'sales-orders': 'How do I create a sales order?',
  'inventory': 'How do I manage stock levels?',
  'reports': 'What reports are available?',
};
```

### Custom Responses

Extend AI service for domain-specific responses:

```typescript
// In aiHelpService.ts
private generateCustomResponse(message: string, context: AIContext): AIResponse {
  // Add your custom logic here
  if (context.module === 'custom-module') {
    return {
      message: 'Custom help for your module',
      confidence: 1.0,
      intent: 'custom',
      suggestions: ['Custom suggestion 1', 'Custom suggestion 2']
    };
  }
  return this.generateMockResponse(message, context);
}
```

### Styling

Customize chatbot appearance:

```tsx
<AIChatbot
  open={chatOpen}
  onClose={() => setChatOpen(false)}
  context={context}
  sx={{
    '& .MuiPaper-root': {
      borderRadius: 4,
      boxShadow: 6,
    },
  }}
/>
```

## Best Practices

### 1. Context Awareness
Always provide rich context for better AI responses:
```typescript
const context = {
  page: router.pathname,
  module: getCurrentModule(),
  userRole: user.role,
  isDemoMode: isDemoActive,
  isMobile: window.innerWidth < 768,
  previousActions: getRecentActions(),
};
```

### 2. Error Handling
Handle AI service errors gracefully:
```typescript
try {
  const response = await aiHelpService.sendMessage(message, context);
  // Handle response
} catch (error) {
  console.error('AI help error:', error);
  // Show fallback help
}
```

### 3. Performance
- Lazy load chatbot component
- Debounce user input
- Cache common responses
- Minimize context data

### 4. Accessibility
- Ensure keyboard navigation
- Add ARIA labels
- Support screen readers
- Provide text alternatives

## Testing

### Unit Tests

Test AI service methods:
```typescript
describe('AIHelpService', () => {
  it('should generate response with context', async () => {
    const response = await aiHelpService.sendMessage(
      'How do I create an order?',
      { module: 'sales', isDemoMode: true }
    );
    expect(response.intent).toBe('create_action');
    expect(response.confidence).toBeGreaterThan(0.8);
  });
});
```

### Integration Tests

Test chatbot component:
```typescript
describe('AIChatbot', () => {
  it('should open and close', () => {
    render(<AIChatbot open={true} onClose={mockClose} />);
    fireEvent.click(screen.getByLabelText('Close'));
    expect(mockClose).toHaveBeenCalled();
  });
});
```

## Troubleshooting

### Common Issues

**Chatbot not opening:**
- Check `open` prop is true
- Verify z-index is sufficient
- Check for console errors

**No responses:**
- Verify AI service is initialized
- Check network connectivity
- Review context data format

**Poor response quality:**
- Provide more context
- Use specific questions
- Check intent detection

### Debug Mode

Enable debug logging:
```typescript
// In aiHelpService.ts
console.log('AI Context:', context);
console.log('AI Response:', response);
```

## Future Enhancements

### Planned Features
1. **Backend AI Integration**: Connect to actual AI/ML models
2. **Multi-language Support**: Internationalization
3. **Voice Input**: Speech-to-text for queries
4. **Advanced Analytics**: Track help effectiveness
5. **Personalization**: Learn from user interactions
6. **Proactive Help**: Suggest help before users ask
7. **Integration with Documentation**: Link to detailed docs

### Roadmap
- Q1 2025: Backend AI service integration
- Q2 2025: Multi-language support
- Q3 2025: Voice input and advanced features
- Q4 2025: Personalization and analytics

## Support

For questions or issues:
1. Check this documentation
2. Review code examples
3. Contact development team
4. Submit feature requests

## Version History

- **v1.0.0** (2025-10-23): Initial implementation
  - AI chatbot component
  - Context-aware help
  - Mobile optimization
  - Demo mode integration
