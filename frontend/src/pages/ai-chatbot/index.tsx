/**
 * AI Chatbot Page
 * Full-featured chatbot interface with business intelligence
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  Avatar,
  Divider,
  Chip,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Button,
  Tabs,
  Tab
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Lightbulb as InsightIcon,
  TrendingUp as TrendingIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import aiService, { ChatMessage, ChatResponse, SmartInsight } from '../../services/aiService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  intent?: string;
  confidence?: number;
  actions?: Array<{
    type: string;
    label: string;
    data: any;
  }>;
  suggestions?: string[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AIChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [insights, setInsights] = useState<SmartInsight[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    // Load initial data
    loadSuggestions();
    loadInsights();
    
    // Send welcome message
    addBotMessage(
      "👋 Hello! I'm your AI business assistant.\n\n" +
      "I can help you with:\n" +
      "🎯 Business advice and recommendations\n" +
      "📝 Creating vouchers and documents\n" +
      "🎪 Lead and customer management\n" +
      "💰 Tax and GST information\n" +
      "🧭 Quick navigation\n" +
      "📊 Business insights and analytics\n\n" +
      "What would you like to do today?"
    );
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const data = await aiService.getChatSuggestions();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const insightsData = await aiService.getSmartInsights();
      setInsights(insightsData.insights);
      
      const recsData = await aiService.getRecommendations();
      setRecommendations(recsData.recommendations);
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };

  const addBotMessage = (
    text: string,
    intent?: string,
    confidence?: number,
    actions?: any[],
    suggestionList?: string[]
  ) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'bot',
      timestamp: new Date(),
      intent,
      confidence,
      actions,
      suggestions: suggestionList
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
      const request: ChatMessage = {
        message: userMessage
      };

      const response: ChatResponse = await aiService.processChatMessage(request);
      
      addBotMessage(
        response.message,
        response.intent,
        response.confidence,
        response.actions,
        response.suggestions
      );
      
      // Update suggestions based on response
      if (response.suggestions && response.suggestions.length > 0) {
        setSuggestions(response.suggestions);
      }
      
    } catch (error) {
      console.error('Error processing message:', error);
      addBotMessage(
        "I'm sorry, I encountered an error processing your request. Please try again."
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
  };

  const handleActionClick = (action: any) => {
    if (action.type === 'navigate' && action.data?.path) {
      router.push(action.data.path);
      addBotMessage(`Navigating to ${action.label}...`);
    } else if (action.type === 'execute') {
      addBotMessage(`Executing ${action.label}...`);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
      case 'urgent':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <BotIcon fontSize="large" color="primary" />
        AI Business Assistant
      </Typography>

      <Grid container spacing={3}>
        {/* Main Chat Area */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ height: 'calc(100vh - 250px)', display: 'flex', flexDirection: 'column' }}>
            {/* Chat Header */}
            <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
              <Typography variant="h6">Chat with AI Assistant</Typography>
              <Typography variant="caption">
                Get instant help with business operations, analytics, and insights
              </Typography>
            </Box>

            {/* Messages Area */}
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
                      mb: 2
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, maxWidth: '85%' }}>
                      {message.sender === 'bot' && (
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                          <BotIcon fontSize="small" />
                        </Avatar>
                      )}
                      
                      <Box>
                        <Paper
                          sx={{
                            p: 2,
                            bgcolor: message.sender === 'user' ? 'primary.main' : 'white',
                            color: message.sender === 'user' ? 'white' : 'text.primary',
                            boxShadow: message.sender === 'user' ? 2 : 1
                          }}
                        >
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {message.text}
                          </Typography>
                          
                          {message.intent && message.confidence && (
                            <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                              <Chip 
                                label={`Intent: ${message.intent}`} 
                                size="small" 
                                color="secondary"
                              />
                              <Chip 
                                label={`Confidence: ${(message.confidence * 100).toFixed(0)}%`} 
                                size="small"
                                color={message.confidence > 0.8 ? 'success' : 'warning'}
                              />
                            </Box>
                          )}
                        </Paper>
                        
                        {/* Action Buttons */}
                        {message.actions && message.actions.length > 0 && (
                          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {message.actions.map((action, index) => (
                              <Button
                                key={index}
                                variant="outlined"
                                size="small"
                                onClick={() => handleActionClick(action)}
                              >
                                {action.label}
                              </Button>
                            ))}
                          </Box>
                        )}
                        
                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Suggested follow-ups:
                            </Typography>
                            <Box sx={{ mt: 0.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {message.suggestions.map((suggestion, index) => (
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
                      </Box>
                      
                      {message.sender === 'user' && (
                        <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                          <PersonIcon fontSize="small" />
                        </Avatar>
                      )}
                    </Box>
                  </ListItem>
                ))}
                
                {isProcessing && (
                  <ListItem sx={{ justifyContent: 'center' }}>
                    <CircularProgress size={24} />
                    <Typography variant="body2" sx={{ ml: 2 }}>
                      Processing your request...
                    </Typography>
                  </ListItem>
                )}
                
                <div ref={messagesEndRef} />
              </List>
            </Box>

            <Divider />

            {/* Input Area */}
            <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
              {/* Quick Suggestions */}
              {suggestions.length > 0 && (
                <Box sx={{ mb: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ width: '100%', mb: 0.5 }}>
                    Quick suggestions:
                  </Typography>
                  {suggestions.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      size="small"
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              )}
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
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
                  multiline
                  maxRows={3}
                />
                <IconButton
                  color="primary"
                  onClick={handleSendMessage}
                  disabled={!inputText.trim() || isProcessing}
                  sx={{ alignSelf: 'flex-end' }}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Sidebar with Insights and Recommendations */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} variant="fullWidth">
              <Tab label="Insights" icon={<InsightIcon />} iconPosition="start" />
              <Tab label="Recommendations" icon={<TrendingIcon />} iconPosition="start" />
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <Typography variant="h6" gutterBottom>
                Smart Insights
              </Typography>
              {insights.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No insights available at the moment.
                </Typography>
              ) : (
                insights.map((insight, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                        <Typography variant="subtitle2" color="primary">
                          {insight.title}
                        </Typography>
                        <Chip 
                          label={insight.priority} 
                          size="small" 
                          color={getPriorityColor(insight.priority)}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {insight.message}
                      </Typography>
                      <Chip label={insight.category} size="small" sx={{ mr: 1 }} />
                      <Button 
                        size="small" 
                        variant="text"
                        onClick={() => handleActionClick({
                          type: 'navigate',
                          label: insight.action_label,
                          data: { action: insight.action }
                        })}
                      >
                        {insight.action_label}
                      </Button>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Typography variant="h6" gutterBottom>
                AI Recommendations
              </Typography>
              {recommendations.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No recommendations available.
                </Typography>
              ) : (
                <List>
                  {recommendations.map((recommendation, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <SpeedIcon color="primary" fontSize="small" />
                          <Typography variant="body2">
                            {recommendation}
                          </Typography>
                        </Box>
                      </ListItem>
                      {index < recommendations.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AIChatbotPage;
