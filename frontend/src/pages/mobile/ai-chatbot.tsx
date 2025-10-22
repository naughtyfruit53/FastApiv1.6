// frontend/src/pages/mobile/ai-chatbot.tsx
/**
 * Mobile-Optimized AI Chatbot Page
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Paper,
  Avatar,
  Chip,
  List,
  ListItem,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Mic,
  AttachFile,
} from '@mui/icons-material';
import {
  MobileDashboardLayout,
  MobileCard,
} from '../../components/mobile';
import aiAgentService from '../../services/aiAgentService';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  intent?: string;
  confidence?: number;
  suggestions?: string[];
}

const MobileAIChatbot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
      suggestions: ['Sales forecast', 'Customer insights', 'Recent orders'],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await aiAgentService.sendChatbotMessage(inputValue);
      
      setTimeout(() => {
        const botMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: 'bot',
          timestamp: new Date(),
          intent: response.intent,
          confidence: response.confidence,
          suggestions: response.suggestions,
        };
        setMessages((prev) => [...prev, botMessage]);
        setIsTyping(false);
      }, 500);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <MobileDashboardLayout
      title="AI Assistant"
      subtitle="Chat with your AI assistant"
      showBottomNav={true}
    >
      <MobileCard
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 200px)',
          p: 0,
        }}
      >
        {/* Messages Container */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                gap: 1,
              }}
            >
              {message.sender === 'bot' && (
                <Avatar
                  sx={{
                    bgcolor: 'primary.main',
                    width: 36,
                    height: 36,
                  }}
                >
                  <SmartToy sx={{ fontSize: 20 }} />
                </Avatar>
              )}
              <Box
                sx={{
                  maxWidth: '75%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5,
                }}
              >
                <Paper
                  sx={{
                    p: 1.5,
                    bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                    color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                    borderRadius: 2,
                    ...(message.sender === 'user' && {
                      borderBottomRightRadius: 4,
                    }),
                    ...(message.sender === 'bot' && {
                      borderBottomLeftRadius: 4,
                    }),
                  }}
                >
                  <Typography variant="body2">{message.text}</Typography>
                  {message.intent && message.confidence && (
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`${message.intent} (${Math.round(message.confidence * 100)}%)`}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                  )}
                </Paper>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    px: 1,
                    alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  {formatTime(message.timestamp)}
                </Typography>
                {message.suggestions && message.suggestions.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                    {message.suggestions.map((suggestion, index) => (
                      <Chip
                        key={index}
                        label={suggestion}
                        size="small"
                        onClick={() => handleSuggestionClick(suggestion)}
                        sx={{
                          cursor: 'pointer',
                          '&:hover': {
                            bgcolor: 'primary.light',
                          },
                        }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
              {message.sender === 'user' && (
                <Avatar
                  sx={{
                    bgcolor: 'secondary.main',
                    width: 36,
                    height: 36,
                  }}
                >
                  <Person sx={{ fontSize: 20 }} />
                </Avatar>
              )}
            </Box>
          ))}
          
          {isTyping && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Avatar
                sx={{
                  bgcolor: 'primary.main',
                  width: 36,
                  height: 36,
                }}
              >
                <SmartToy sx={{ fontSize: 20 }} />
              </Avatar>
              <Paper
                sx={{
                  p: 1.5,
                  bgcolor: 'grey.100',
                  borderRadius: 2,
                  borderBottomLeftRadius: 4,
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  Typing...
                </Typography>
              </Paper>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Container */}
        <Box
          sx={{
            borderTop: 1,
            borderColor: 'divider',
            p: 2,
            bgcolor: 'background.paper',
          }}
        >
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <IconButton
              size="small"
              sx={{ minWidth: 40, minHeight: 40 }}
            >
              <AttachFile />
            </IconButton>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type a message..."
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
            <IconButton
              size="small"
              sx={{ minWidth: 40, minHeight: 40 }}
            >
              <Mic />
            </IconButton>
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={!inputValue.trim()}
              sx={{
                minWidth: 40,
                minHeight: 40,
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '&:disabled': {
                  bgcolor: 'grey.300',
                },
              }}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileAIChatbot;
