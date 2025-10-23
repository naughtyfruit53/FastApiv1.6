/**
 * AI Help Service
 * 
 * Provides AI-powered contextual help and chatbot functionality
 * for mobile and demo modes.
 */

export interface AIMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  confidence?: number;
  intent?: string;
  suggestions?: string[];
}

export interface AIContext {
  page?: string;
  module?: string;
  userRole?: string;
  isDemoMode?: boolean;
  isMobile?: boolean;
  previousActions?: string[];
}

export interface AIResponse {
  message: string;
  confidence: number;
  intent: string;
  suggestions?: string[];
  relatedTopics?: string[];
  quickActions?: Array<{
    label: string;
    action: string;
  }>;
}

class AIHelpService {
  private apiBaseUrl: string;
  private conversationHistory: AIMessage[] = [];

  constructor() {
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Send a message to the AI chatbot
   */
  async sendMessage(
    message: string,
    context?: AIContext
  ): Promise<AIResponse> {
    try {
      // For now, use a mock response. In production, this would call the backend API
      return this.generateMockResponse(message, context);
    } catch (error) {
      console.error('Error sending message to AI:', error);
      throw error;
    }
  }

  /**
   * Get contextual help based on current page/module
   */
  async getContextualHelp(context: AIContext): Promise<AIResponse> {
    const helpPrompt = this.buildContextualPrompt(context);
    return this.sendMessage(helpPrompt, context);
  }

  /**
   * Get quick help suggestions based on context
   */
  async getQuickSuggestions(context: AIContext): Promise<string[]> {
    const suggestions = this.generateContextualSuggestions(context);
    return suggestions;
  }

  /**
   * Add message to conversation history
   */
  addToHistory(message: AIMessage): void {
    this.conversationHistory.push(message);
    // Keep only last 20 messages to prevent memory issues
    if (this.conversationHistory.length > 20) {
      this.conversationHistory = this.conversationHistory.slice(-20);
    }
  }

  /**
   * Get conversation history
   */
  getHistory(): AIMessage[] {
    return this.conversationHistory;
  }

  /**
   * Clear conversation history
   */
  clearHistory(): void {
    this.conversationHistory = [];
  }

  /**
   * Build contextual prompt based on user context
   */
  private buildContextualPrompt(context: AIContext): string {
    const parts = ['I need help with'];
    
    if (context.module) {
      parts.push(`the ${context.module} module`);
    }
    
    if (context.page) {
      parts.push(`on the ${context.page} page`);
    }
    
    if (context.isDemoMode) {
      parts.push('in demo mode');
    }
    
    if (context.isMobile) {
      parts.push('on mobile');
    }
    
    return parts.join(' ') + '.';
  }

  /**
   * Generate contextual suggestions based on context
   */
  private generateContextualSuggestions(context: AIContext): string[] {
    const suggestions: string[] = [];
    
    if (context.module === 'sales') {
      suggestions.push(
        'How do I create a new sales order?',
        'What is the sales order workflow?',
        'How to view sales reports?'
      );
    } else if (context.module === 'inventory') {
      suggestions.push(
        'How do I add new products?',
        'How to manage stock levels?',
        'What is the inventory transfer process?'
      );
    } else if (context.module === 'finance') {
      suggestions.push(
        'How do I create a voucher?',
        'How to view ledger reports?',
        'What are the payment terms?'
      );
    } else if (context.isDemoMode) {
      suggestions.push(
        'What features can I explore in demo mode?',
        'How do I navigate the system?',
        'What sample data is available?'
      );
    } else {
      suggestions.push(
        'How do I get started?',
        'What are the main features?',
        'Where can I find reports?'
      );
    }
    
    return suggestions;
  }

  /**
   * Generate mock AI response (for development)
   * In production, this would be replaced with actual AI API calls
   */
  private generateMockResponse(message: string, context?: AIContext): AIResponse {
    const lowerMessage = message.toLowerCase();
    
    // Detect intent
    let intent = 'general_help';
    if (lowerMessage.includes('create') || lowerMessage.includes('add')) {
      intent = 'create_action';
    } else if (lowerMessage.includes('view') || lowerMessage.includes('see')) {
      intent = 'view_action';
    } else if (lowerMessage.includes('report')) {
      intent = 'reporting';
    } else if (lowerMessage.includes('demo')) {
      intent = 'demo_help';
    }
    
    // Generate response based on intent and context
    let responseMessage = '';
    const suggestions: string[] = [];
    const quickActions: Array<{ label: string; action: string }> = [];
    
    if (intent === 'create_action') {
      responseMessage = `To create a new item in the ${context?.module || 'system'}, click the "Add New" button at the top right of the page. Fill in the required fields and click "Save" to create the item.`;
      suggestions.push(
        'How do I edit an existing item?',
        'Can I duplicate items?',
        'What fields are required?'
      );
      quickActions.push(
        { label: 'Show me the form', action: 'navigate_to_form' },
        { label: 'View examples', action: 'show_examples' }
      );
    } else if (intent === 'view_action') {
      responseMessage = `You can view items by navigating to the list view. Use the filters and search options to find specific items. Click on any item to see its details.`;
      suggestions.push(
        'How do I filter the list?',
        'Can I export the data?',
        'How to sort items?'
      );
      quickActions.push(
        { label: 'Open list view', action: 'navigate_to_list' },
        { label: 'Show filters', action: 'show_filters' }
      );
    } else if (intent === 'demo_help') {
      responseMessage = `Welcome to demo mode! You can explore all features with sample data. Your actions won't affect real data. Try creating orders, viewing reports, or exploring different modules.`;
      suggestions.push(
        'What sample data is available?',
        'How do I exit demo mode?',
        'Can I share this demo session?'
      );
      quickActions.push(
        { label: 'Tour the features', action: 'start_tour' },
        { label: 'View sample data', action: 'show_samples' }
      );
    } else {
      responseMessage = `I'm here to help! You can ask me about any feature in the system. Try asking specific questions like "How do I create a sales order?" or "Where can I find reports?"`;
      suggestions.push(
        'What can you help me with?',
        'Show me around',
        'What are the main features?'
      );
      quickActions.push(
        { label: 'Take a tour', action: 'start_tour' },
        { label: 'View documentation', action: 'open_docs' }
      );
    }
    
    return {
      message: responseMessage,
      confidence: 0.85,
      intent,
      suggestions,
      quickActions,
      relatedTopics: this.generateRelatedTopics(context)
    };
  }

  /**
   * Generate related help topics
   */
  private generateRelatedTopics(context?: AIContext): string[] {
    if (context?.module === 'sales') {
      return ['Sales Orders', 'Quotations', 'Invoices', 'Customers'];
    } else if (context?.module === 'inventory') {
      return ['Products', 'Stock Management', 'Transfers', 'Adjustments'];
    } else if (context?.module === 'finance') {
      return ['Vouchers', 'Ledgers', 'Reports', 'Payments'];
    }
    return ['Getting Started', 'Navigation', 'Reports', 'Settings'];
  }
}

// Export singleton instance
export const aiHelpService = new AIHelpService();
export default aiHelpService;
