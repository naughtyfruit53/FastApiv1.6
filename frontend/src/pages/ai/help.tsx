// AI Help & Guidance Page
import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Search as SearchIcon,
  Help as HelpIcon,
  SmartToy as BotIcon,
  MenuBook as GuideIcon,
  VideoLibrary as VideoIcon,
  Article as ArticleIcon,
  ExpandMore as ExpandMoreIcon,
  TipsAndUpdates as TipIcon,
} from '@mui/icons-material';
import { AIChatbot } from '@/ai/AIChatbot';

const AIHelpPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const helpCategories = [
    {
      title: 'Getting Started',
      icon: <GuideIcon />,
      color: '#1976d2',
      topics: [
        'Setting up your account',
        'Understanding the dashboard',
        'Basic navigation',
        'Your first transaction',
      ],
    },
    {
      title: 'AI Features',
      icon: <BotIcon />,
      color: '#9c27b0',
      topics: [
        'Using the AI Chatbot',
        'Predictive Analytics',
        'Business Recommendations',
        'Intent Classification',
      ],
    },
    {
      title: 'Tutorials',
      icon: <VideoIcon />,
      color: '#f44336',
      topics: [
        'Creating invoices',
        'Managing inventory',
        'Processing payments',
        'Generating reports',
      ],
    },
    {
      title: 'FAQs',
      icon: <HelpIcon />,
      color: '#ff9800',
      topics: [
        'Account management',
        'Security & privacy',
        'Troubleshooting',
        'Integration setup',
      ],
    },
  ];

  const faqs = [
    {
      question: 'How do I use the AI Chatbot?',
      answer:
        'Click the chatbot icon in the bottom-right corner of any page, or navigate to AI & Analytics > AI Chatbot. Type your question and get instant AI-powered assistance.',
    },
    {
      question: 'What AI features are available?',
      answer:
        'Our ERP includes AI Chatbot, Predictive Analytics, Business Intelligence Advisor, AutoML, Streaming Analytics, and AI-powered PDF extraction. Each feature is designed to enhance your business intelligence and automation.',
    },
    {
      question: 'How accurate are the AI predictions?',
      answer:
        'Our AI models are trained on historical data and continuously improve over time. Accuracy varies by feature but typically ranges from 85-95% for sales forecasting and 90%+ for intent classification.',
    },
    {
      question: 'Can I customize AI recommendations?',
      answer:
        'Yes! AI recommendations can be fine-tuned based on your business context. Navigate to Settings > AI Configuration to adjust parameters and preferences.',
    },
    {
      question: 'Is my data secure when using AI features?',
      answer:
        'Absolutely. All data is encrypted in transit and at rest. We use OpenAI API with strict privacy policies, and your data is never used to train external models without explicit consent.',
    },
  ];

  const quickTips = [
    'Use the AI Chatbot for quick answers instead of searching through documentation',
    'Enable predictive analytics to get early warnings about inventory shortages',
    'Review AI business recommendations weekly for optimization insights',
    'Use AutoML to create custom prediction models for your specific business needs',
    'Check streaming analytics for real-time business insights',
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          AI Help & Guidance
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Get help with AI features, learn best practices, and find answers to common questions
        </Typography>
      </Box>

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <TextField
          fullWidth
          placeholder="Search for help topics..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          variant="outlined"
        />
      </Paper>

      {/* Quick Tips */}
      <Paper sx={{ p: 3, mb: 4, backgroundColor: '#f5f5f5' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TipIcon sx={{ mr: 1, color: 'warning.main' }} />
          <Typography variant="h6" fontWeight="bold">
            Quick Tips
          </Typography>
        </Box>
        <List dense>
          {quickTips.map((tip, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <Chip label={index + 1} size="small" color="primary" />
              </ListItemIcon>
              <ListItemText primary={tip} />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Help Categories */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {helpCategories.map((category) => (
          <Grid item xs={12} sm={6} md={3} key={category.title}>
            <Card sx={{ height: '100%' }}>
              <CardActionArea sx={{ height: '100%' }}>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      mb: 2,
                      color: category.color,
                    }}
                  >
                    {category.icon}
                    <Typography variant="h6" sx={{ ml: 1 }} fontWeight="bold">
                      {category.title}
                    </Typography>
                  </Box>
                  <List dense>
                    {category.topics.map((topic, index) => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemText
                          primary={topic}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* FAQs */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Frequently Asked Questions
        </Typography>
        <Divider sx={{ my: 2 }} />
        {faqs.map((faq, index) => (
          <Accordion key={index}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="medium">{faq.question}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography color="text.secondary">{faq.answer}</Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      {/* AI Assistant CTA */}
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <BotIcon sx={{ fontSize: 48, mb: 2 }} />
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Need More Help?
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          Chat with our AI assistant for instant, context-aware support
        </Typography>
        <Box
          sx={{
            display: 'inline-block',
            bgcolor: 'white',
            color: 'primary.main',
            px: 3,
            py: 1.5,
            borderRadius: 2,
            cursor: 'pointer',
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.9)',
            },
          }}
          onClick={() => setChatbotOpen(true)}
        >
          <Typography variant="button" fontWeight="bold">
            Open AI Chatbot
          </Typography>
        </Box>
      </Paper>

      {/* AI Chatbot */}
      <AIChatbot
        open={chatbotOpen}
        onClose={() => setChatbotOpen(false)}
        context={{ page: 'ai-help', module: 'help' }}
      />
    </Container>
  );
};

export default AIHelpPage;
