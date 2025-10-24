/**
 * AI Chatbot Component
 * 
 * Provides an interactive AI-powered chatbot for contextual help
 * in mobile and demo modes.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Fade,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { aiHelpService, AIMessage, AIContext } from './aiHelpService';

interface AIChatbotProps {
  open: boolean;
  onClose: () => void;
  context?: AIContext;
  position?: 'bottom-right' | 'bottom-left' | 'center';
  variant?: 'compact' | 'full';
}

export const AIChatbot: React.FC<AIChatbotProps> = ({
  open,
  onClose,
  context,
  position = 'bottom-right',
  variant = 'compact',
}) => {
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load initial suggestions on mount
  useEffect(() => {
    if (open && context) {
      loadSuggestions();
    }
  }, [open, context]);

  const loadSuggestions = async () => {
    try {
      const sug = await aiHelpService.getQuickSuggestions(context || {});
      setSuggestions(sug);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleSendMessage = async (message?: string) => {
    const messageText = message || inputValue.trim();
    if (!messageText) return;

    // Add user message
    const userMessage: AIMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    aiHelpService.addToHistory(userMessage);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get AI response
      const response = await aiHelpService.sendMessage(messageText, context);
      
      // Add AI message
      const aiMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        confidence: response.confidence,
        intent: response.intent,
        suggestions: response.suggestions,
      };
      setMessages(prev => [...prev, aiMessage]);
      aiHelpService.addToHistory(aiMessage);
      
      // Update suggestions
      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const getPositionStyles = () => {
    const base = {
      position: 'fixed' as const,
      zIndex: 1300,
    };

    if (position === 'bottom-right') {
      return {
        ...base,
        bottom: 24,
        right: 24,
      };
    } else if (position === 'bottom-left') {
      return {
        ...base,
        bottom: 24,
        left: 24,
      };
    } else {
      return {
        ...base,
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
      };
    }
  };

  if (!open) return null;

  return (
    <Fade in={open}>
      <Paper
        elevation={8}
        sx={{
          ...getPositionStyles(),
          width: variant === 'compact' ? 380 : 480,
          maxHeight: variant === 'compact' ? 500 : 600,
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BotIcon />
            <Typography variant="h6">AI Assistant</Typography>
          </Box>
          <IconButton
            size="small"
            onClick={onClose}
            sx={{ color: 'primary.contrastText' }}
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
            bgcolor: 'background.default',
          }}
        >
          {messages.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <BotIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Hello! I'm your AI assistant.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask me anything or click a suggestion below.
              </Typography>
            </Box>
          )}

          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                mb: 2,
                display: 'flex',
                gap: 1,
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                }}
              >
                {message.role === 'user' ? <PersonIcon sx={{ fontSize: 18 }} /> : <BotIcon sx={{ fontSize: 18 }} />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 1.5,
                  maxWidth: '75%',
                  bgcolor: message.role === 'user' ? 'primary.light' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <Typography variant="body2">{message.content}</Typography>
                {message.confidence && (
                  <Typography variant="caption" sx={{ mt: 0.5, opacity: 0.7, display: 'block' }}>
                    Confidence: {(message.confidence * 100).toFixed(0)}%
                  </Typography>
                )}
              </Paper>
            </Box>
          ))}

          {isLoading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                <BotIcon sx={{ fontSize: 18 }} />
              </Avatar>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <CircularProgress size={8} />
                <CircularProgress size={8} />
                <CircularProgress size={8} />
              </Box>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <Box
            sx={{
              px: 2,
              py: 1,
              borderTop: 1,
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Suggested questions:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <Chip
                  key={index}
                  label={suggestion}
                  size="small"
                  onClick={() => handleSuggestionClick(suggestion)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Input */}
        <Box
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            display: 'flex',
            gap: 1,
          }}
        >
          <TextField
            fullWidth
            size="small"
            placeholder="Ask me anything..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={isLoading}
          />
          <IconButton
            color="primary"
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Fade>
  );
};

export default AIChatbot;
