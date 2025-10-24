// frontend/src/components/ChatbotNavigator.tsx

/**
 * Chatbot Navigator Component (Requirement 3)
 * Floating bottom-right assistant that can:
 * - Open pages
 * - Fill forms
 * - Add vendors
 * - Repeat purchase orders
 * - List low-stock items
 * - And more
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Fab,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  Chip,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as BotIcon
} from '@mui/icons-material';
import { useRouter } from 'next/router';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  actions?: ChatAction[];
}

interface ChatAction {
  type: 'navigate' | 'execute';
  label: string;
  data: any;
}

const ChatbotNavigator: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Send welcome message with enhanced capabilities
      addBotMessage(
        "👋 Hello! I'm your AI business assistant. I can help you with:\n\n" +
        "🎯 **Business Advice**: Get recommendations on inventory, cash flow, and sales\n" +
        "📝 **Voucher Creation**: Create invoices, orders, and other documents\n" +
        "🎪 **Lead Management**: Track prospects and opportunities\n" +
        "💰 **Tax & GST**: Information on rates, filing, and compliance\n" +
        "🧭 **Navigation**: Quick access to any page\n\n" +
        "Try asking me:\n" +
        '• "Give me business advice"\n' +
        '• "Create a sales order"\n' +
        '• "What are GST rates?"\n' +
        '• "Show low stock items"\n\n' +
        "What would you like to do?"
      );
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addBotMessage = (text: string, actions?: ChatAction[]) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'bot',
      timestamp: new Date(),
      actions
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const addUserMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    addUserMessage(userMessage);
    setInputText('');
    setIsProcessing(true);

    try {
      // Process the message
      const response = await processUserMessage(userMessage);
      setIsProcessing(false);
      
      if (response.actions && response.actions.length > 0) {
        addBotMessage(response.message, response.actions);
      } else {
        addBotMessage(response.message);
      }
    } catch (error) {
      setIsProcessing(false);
      addBotMessage("I'm sorry, I encountered an error. Please try again.");
    }
  };

  const processUserMessage = async (message: string): Promise<{ message: string; actions?: ChatAction[] }> => {
    // Try to use backend API first
    try {
      const response = await fetch('/api/v1/chatbot/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          message: data.message,
          actions: data.actions,
        };
      }
    } catch (error) {
      console.warn('Backend chatbot unavailable, using fallback logic', error);
    }

    // Fallback to client-side processing if backend fails
    const lowerMsg = message.toLowerCase();

    // Navigate commands
    if (lowerMsg.includes('open') || lowerMsg.includes('go to') || lowerMsg.includes('navigate')) {
      if (lowerMsg.includes('vendor')) {
        return {
          message: "I can take you to the Vendors page.",
          actions: [{
            type: 'navigate',
            label: 'Go to Vendors',
            data: { path: '/vendors' }
          }]
        };
      } else if (lowerMsg.includes('customer')) {
        return {
          message: "I can take you to the Customers page.",
          actions: [{
            type: 'navigate',
            label: 'Go to Customers',
            data: { path: '/customers' }
          }]
        };
      } else if (lowerMsg.includes('purchase order') || lowerMsg.includes('po')) {
        return {
          message: "I can take you to the Purchase Orders page.",
          actions: [{
            type: 'navigate',
            label: 'Go to Purchase Orders',
            data: { path: '/vouchers/purchase-orders' }
          }]
        };
      } else if (lowerMsg.includes('product') || lowerMsg.includes('inventory')) {
        return {
          message: "I can take you to the Products page.",
          actions: [{
            type: 'navigate',
            label: 'Go to Products',
            data: { path: '/products' }
          }]
        };
      }
    }

    // Create/add commands
    if (lowerMsg.includes('add') || lowerMsg.includes('create') || lowerMsg.includes('new')) {
      if (lowerMsg.includes('vendor')) {
        return {
          message: "I can help you create a new vendor. Would you like to go to the vendor creation page?",
          actions: [{
            type: 'navigate',
            label: 'Create Vendor',
            data: { path: '/vendors?action=create' }
          }]
        };
      } else if (lowerMsg.includes('customer')) {
        return {
          message: "I can help you create a new customer.",
          actions: [{
            type: 'navigate',
            label: 'Create Customer',
            data: { path: '/customers?action=create' }
          }]
        };
      } else if (lowerMsg.includes('product')) {
        return {
          message: "I can help you create a new product.",
          actions: [{
            type: 'navigate',
            label: 'Create Product',
            data: { path: '/products?action=create' }
          }]
        };
      }
    }

    // Low stock items
    if (lowerMsg.includes('low stock') || lowerMsg.includes('low-stock') || lowerMsg.includes('inventory alert')) {
      return {
        message: "I can show you items with low stock levels.",
        actions: [{
          type: 'navigate',
          label: 'View Low Stock Items',
          data: { path: '/inventory?filter=low-stock' }
        }]
      };
    }

    // Repeat PO
    if (lowerMsg.includes('repeat') && (lowerMsg.includes('po') || lowerMsg.includes('purchase order'))) {
      return {
        message: "I can help you repeat a previous purchase order. Please go to the Purchase Orders page to select the order to repeat.",
        actions: [{
          type: 'navigate',
          label: 'Go to Purchase Orders',
          data: { path: '/vouchers/purchase-orders' }
        }]
      };
    }

    // Reports
    if (lowerMsg.includes('report')) {
      return {
        message: "I can help you with reports. What type of report would you like?",
        actions: [
          {
            type: 'navigate',
            label: 'Sales Report',
            data: { path: '/reports/sales' }
          },
          {
            type: 'navigate',
            label: 'Purchase Report',
            data: { path: '/reports/purchase' }
          },
          {
            type: 'navigate',
            label: 'Inventory Report',
            data: { path: '/reports/inventory' }
          }
        ]
      };
    }

    // Default response
    return {
      message: "I'm not sure I understand. Try asking me to:\n" +
        "• Open a page (e.g., 'open vendors')\n" +
        "• Add something (e.g., 'add new vendor')\n" +
        "• View low stock items\n" +
        "• Repeat a purchase order\n" +
        "• Generate a report"
    };
  };

  const handleActionClick = (action: ChatAction) => {
    if (action.type === 'navigate') {
      router.push(action.data.path);
      addBotMessage(`Navigating to ${action.label}...`);
      // Optionally close chatbot after navigation
      setTimeout(() => setIsOpen(false), 1000);
    } else if (action.type === 'execute') {
      addBotMessage(`Executing ${action.label}...`);
      // Execute specific action
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <Fab
          color="primary"
          aria-label="chatbot"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1300
          }}
          onClick={() => setIsOpen(true)}
        >
          <ChatIcon />
        </Fab>
      )}

      {/* Chat Window */}
      {isOpen && (
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            width: 400,
            height: 600,
            zIndex: 1300,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              bgcolor: 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <BotIcon />
              <Typography variant="h6">ERP Assistant</Typography>
            </Box>
            <IconButton
              size="small"
              onClick={() => setIsOpen(false)}
              sx={{ color: 'white' }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Messages */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: 2,
              bgcolor: 'grey.50'
            }}
          >
            <List>
              {messages.map((message) => (
                <ListItem
                  key={message.id}
                  sx={{
                    flexDirection: 'column',
                    alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 1
                  }}
                >
                  <Paper
                    sx={{
                      p: 1.5,
                      maxWidth: '80%',
                      bgcolor: message.sender === 'user' ? 'primary.main' : 'white',
                      color: message.sender === 'user' ? 'white' : 'text.primary'
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.text}
                    </Typography>
                  </Paper>
                  
                  {/* Action buttons */}
                  {message.actions && message.actions.length > 0 && (
                    <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {message.actions.map((action, index) => (
                        <Chip
                          key={index}
                          label={action.label}
                          onClick={() => handleActionClick(action)}
                          color="primary"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  )}
                </ListItem>
              ))}
              
              {isProcessing && (
                <ListItem sx={{ justifyContent: 'center' }}>
                  <CircularProgress size={20} />
                </ListItem>
              )}
              
              <div ref={messagesEndRef} />
            </List>
          </Box>

          <Divider />

          {/* Input */}
          <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Type your message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={isProcessing}
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isProcessing}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      )}
    </>
  );
};

export default ChatbotNavigator;
