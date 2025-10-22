/**
 * Chatbot Widget Component
 * Can be embedded in customer websites
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Fab,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  Avatar,
  Divider,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import aiService, { ChatMessage, ChatResponse } from '../services/aiService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  actions?: Array<{
    type: string;
    label: string;
    data: any;
  }>;
  suggestions?: string[];
}

interface ChatbotWidgetProps {
  position?: 'bottom-right' | 'bottom-left';
  primaryColor?: string;
  onNavigate?: (path: string) => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  position = 'bottom-right',
  primaryColor = '#1976d2',
  onNavigate
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      loadInitialData();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadInitialData = async () => {
    try {
      const data = await aiService.getChatSuggestions();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }

    addBotMessage(
      "👋 Hi! I'm your AI assistant. I can help you with:\n\n" +
      "• Business advice\n" +
      "• Creating documents\n" +
      "• Navigation\n" +
      "• Reports and analytics\n\n" +
      "What can I help you with today?"
    );
  };

  const addBotMessage = (text: string, actions?: any[], suggestionsList?: string[]) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'bot',
      timestamp: new Date(),
      actions,
      suggestions: suggestionsList
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
    if (!inputText.trim() || isProcessing) return;

    const userMessage = inputText.trim();
    addUserMessage(userMessage);
    setInputText('');
    setIsProcessing(true);

    try {
      const request: ChatMessage = { message: userMessage };
      const response: ChatResponse = await aiService.processChatMessage(request);
      
      addBotMessage(
        response.message,
        response.actions,
        response.suggestions
      );

      if (response.suggestions && response.suggestions.length > 0) {
        setSuggestions(response.suggestions);
      }
      
    } catch (error) {
      console.error('Error processing message:', error);
      addBotMessage("I'm sorry, I encountered an error. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleActionClick = (action: any) => {
    if (action.type === 'navigate' && action.data?.path) {
      if (onNavigate) {
        onNavigate(action.data.path);
      } else if (typeof window !== 'undefined') {
        window.location.href = action.data.path;
      }
      addBotMessage(`Navigating to ${action.label}...`);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
  };

  const positionStyles = position === 'bottom-right' 
    ? { bottom: 24, right: 24 }
    : { bottom: 24, left: 24 };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <Fab
          aria-label="chatbot"
          sx={{
            position: 'fixed',
            ...positionStyles,
            zIndex: 1300,
            bgcolor: primaryColor,
            '&:hover': {
              bgcolor: primaryColor,
              filter: 'brightness(0.9)'
            }
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
            ...positionStyles,
            width: { xs: '90vw', sm: 400 },
            height: { xs: '80vh', sm: 600 },
            maxWidth: '100%',
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
              bgcolor: primaryColor,
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <BotIcon />
              <Typography variant="h6">AI Assistant</Typography>
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
                    mb: 1,
                    p: 0
                  }}
                >
                  <Box sx={{ display: 'flex', gap: 1, maxWidth: '85%' }}>
                    {message.sender === 'bot' && (
                      <Avatar sx={{ bgcolor: primaryColor, width: 28, height: 28 }}>
                        <BotIcon sx={{ fontSize: 16 }} />
                      </Avatar>
                    )}
                    
                    <Box>
                      <Paper
                        sx={{
                          p: 1.5,
                          bgcolor: message.sender === 'user' ? primaryColor : 'white',
                          color: message.sender === 'user' ? 'white' : 'text.primary'
                        }}
                      >
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {message.text}
                        </Typography>
                      </Paper>
                      
                      {/* Action buttons */}
                      {message.actions && message.actions.length > 0 && (
                        <Box sx={{ mt: 0.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {message.actions.map((action, index) => (
                            <Chip
                              key={index}
                              label={action.label}
                              onClick={() => handleActionClick(action)}
                              size="small"
                              sx={{
                                cursor: 'pointer',
                                '&:hover': {
                                  bgcolor: 'grey.200'
                                }
                              }}
                            />
                          ))}
                        </Box>
                      )}
                      
                      {/* Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <Box sx={{ mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Try:
                          </Typography>
                          <Box sx={{ mt: 0.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {message.suggestions.slice(0, 3).map((suggestion, index) => (
                              <Chip
                                key={index}
                                label={suggestion}
                                size="small"
                                onClick={() => handleSuggestionClick(suggestion)}
                                sx={{ cursor: 'pointer', fontSize: '0.7rem' }}
                              />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                    
                    {message.sender === 'user' && (
                      <Avatar sx={{ bgcolor: 'grey.500', width: 28, height: 28 }}>
                        <PersonIcon sx={{ fontSize: 16 }} />
                      </Avatar>
                    )}
                  </Box>
                </ListItem>
              ))}
              
              {isProcessing && (
                <ListItem sx={{ justifyContent: 'center', p: 1 }}>
                  <CircularProgress size={20} />
                </ListItem>
              )}
              
              <div ref={messagesEndRef} />
            </List>
          </Box>

          <Divider />

          {/* Input */}
          <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
            {/* Quick Suggestions */}
            {suggestions.length > 0 && (
              <Box sx={{ mb: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {suggestions.slice(0, 3).map((suggestion, index) => (
                  <Chip
                    key={index}
                    label={suggestion}
                    size="small"
                    onClick={() => handleSuggestionClick(suggestion)}
                    sx={{ cursor: 'pointer', fontSize: '0.7rem' }}
                  />
                ))}
              </Box>
            )}
            
            <Box sx={{ display: 'flex', gap: 1 }}>
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
                size="small"
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      )}
    </>
  );
};

export default ChatbotWidget;
