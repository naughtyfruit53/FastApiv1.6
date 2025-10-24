# AI Features Guide - Tritiq ERP System

## Overview
This guide provides a comprehensive overview of all AI-powered features in the Tritiq ERP system, including backend implementation status, frontend availability, usage instructions, and troubleshooting tips.

---

## Table of Contents
1. [AI Chatbot & Intent Classification](#1-ai-chatbot--intent-classification)
2. [AI Analytics & ML Models](#2-ai-analytics--ml-models)
3. [AI Agents](#3-ai-agents)
4. [Explainability & AutoML](#4-explainability--automl)
5. [Streaming Analytics](#5-streaming-analytics)
6. [Business Intelligence Advisor](#6-business-intelligence-advisor)
7. [AI-Powered PDF Extraction](#7-ai-powered-pdf-extraction)
8. [Website Agent AI](#8-website-agent-ai)
9. [Service Desk AI](#9-service-desk-ai)
10. [Customer Analytics AI](#10-customer-analytics-ai)
11. [Configuration & Setup](#configuration--setup)
12. [Troubleshooting](#troubleshooting)

---

## 1. AI Chatbot & Intent Classification

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/chatbot.py`, `app/api/v1/ai.py`)
- **Frontend**: ✅ Available (CRM AI Chatbot interface)
- **Models**: `app/models/ai_agents.py`, `app/services/ai_service.py`

### Features
- **Intent Classification**: Automatically classifies user queries into categories (inventory, sales, customer, finance, etc.)
- **Entity Extraction**: Extracts key entities (dates, amounts, product names) from user messages
- **Conversational AI**: Maintains conversation context for multi-turn interactions
- **Business Advice**: Provides recommendations based on query intent

### API Endpoints

#### Classify Intent
```http
POST /api/v1/ai/intent/classify
Content-Type: application/json

{
  "message": "What are my sales for last month?"
}

Response:
{
  "intent": "sales_inquiry",
  "confidence": 0.95,
  "entities": {
    "time_period": "last_month"
  }
}
```

#### Get Business Advice
```http
POST /api/v1/ai/business-advice
Content-Type: application/json

{
  "category": "inventory",
  "context": {
    "low_stock_items": 5
  }
}

Response:
{
  "category": "inventory",
  "recommendations": [
    {
      "title": "Reorder Low Stock Items",
      "description": "5 items are below minimum stock level",
      "priority": "high"
    }
  ]
}
```

#### Chat Endpoint
```http
POST /api/v1/chatbot/chat
Content-Type: application/json

{
  "message": "Show me top selling products",
  "conversation_id": "optional-uuid"
}
```

### Frontend Access
1. Navigate to **CRM** → **AI Chatbot** in the main menu
2. Type your query in the chat interface
3. The AI will classify intent and provide relevant information
4. Supports follow-up questions with context awareness

### Configuration
Set environment variables:
```bash
# Optional: Use OpenAI for enhanced NLP (requires API key)
OPENAI_API_KEY=your_api_key_here
USE_OPENAI_CHATBOT=true

# Or use local NLP models (default)
USE_LOCAL_NLP=true
```

---

## 2. AI Analytics & ML Models

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/ai_analytics.py`, `app/api/v1/ml_analytics.py`)
- **Frontend**: ⚠️ Partially Available (Analytics Hub)
- **Models**: `app/models/ai_analytics_models.py`

### Features
- **Predictive Analytics**: Sales forecasting, demand prediction, churn prediction
- **Time Series Analysis**: Trend detection, seasonality analysis
- **Anomaly Detection**: Identifies unusual patterns in data
- **Customer Segmentation**: ML-based customer clustering
- **AutoML**: Automated model selection and training

### API Endpoints

#### Train ML Model
```http
POST /api/v1/ai-analytics/train
Content-Type: application/json

{
  "model_type": "sales_forecast",
  "data_source": "sales_vouchers",
  "parameters": {
    "forecast_period": 30,
    "features": ["season", "day_of_week", "promotions"]
  }
}
```

#### Get Predictions
```http
GET /api/v1/ai-analytics/predict?model_id=123&input_data=...
```

#### Get Model Insights
```http
GET /api/v1/ai-analytics/models/{model_id}/insights
```

### Available Models

1. **Sales Forecasting**
   - Predicts future sales based on historical data
   - Considers seasonality, trends, and external factors
   
2. **Demand Prediction**
   - Forecasts product demand for inventory planning
   - Uses time series and regression algorithms

3. **Customer Churn Prediction**
   - Identifies customers likely to churn
   - Provides risk scores and retention recommendations

4. **Anomaly Detection**
   - Detects unusual transactions or patterns
   - Flags potential fraud or errors

### Frontend Access
1. Navigate to **Analytics** → **AI Analytics Hub**
2. Select the type of analysis you want to perform
3. Configure parameters (date range, features, etc.)
4. Click "Train Model" or "Get Predictions"
5. View results in interactive charts and tables

### Pending Frontend Implementation
- [ ] Custom model configuration UI
- [ ] Model performance comparison dashboard
- [ ] A/B testing interface for models
- [ ] Automated retraining scheduler

---

## 3. AI Agents

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/ai_agents.py`)
- **Frontend**: ❌ Not Yet Implemented
- **Models**: `app/models/ai_agents.py`

### Features
- **Agent Management**: Create, configure, and manage AI agents
- **Agent Capabilities**: Define what each agent can do
- **Agent Interactions**: Track all interactions with agents
- **Multi-agent Orchestration**: Coordinate multiple agents for complex tasks

### API Endpoints

#### Create AI Agent
```http
POST /api/v1/ai-agents
Content-Type: application/json

{
  "name": "Inventory Assistant",
  "description": "Helps manage inventory levels and reordering",
  "agent_type": "inventory_management",
  "capabilities": ["check_stock", "create_po", "analyze_demand"],
  "config": {
    "auto_reorder_threshold": 10,
    "preferred_vendors": [1, 2, 3]
  }
}
```

#### List AI Agents
```http
GET /api/v1/ai-agents
```

#### Interact with Agent
```http
POST /api/v1/ai-agents/{agent_id}/interact
Content-Type: application/json

{
  "message": "Check stock for product ID 123",
  "context": {}
}
```

### Agent Types
1. **Inventory Management Agent**: Stock monitoring, reorder suggestions
2. **Customer Service Agent**: Handle customer queries, ticket creation
3. **Sales Agent**: Lead qualification, opportunity identification
4. **Finance Agent**: Payment reminders, expense categorization

### Frontend Implementation Needed
To implement the frontend for AI Agents:

1. **Create Agents Management Page** (`frontend/src/pages/ai-agents/index.tsx`)
   ```typescript
   // List all agents, create new agents, configure existing ones
   ```

2. **Agent Configuration Modal**
   - Configure agent capabilities
   - Set thresholds and rules
   - Define triggers and actions

3. **Agent Interaction Interface**
   - Chat-like interface for agent interactions
   - Display agent responses and actions
   - Track interaction history

4. **Agent Performance Dashboard**
   - Show agent metrics (tasks completed, success rate)
   - Display cost/benefit analysis
   - Track agent improvements over time

---

## 4. Explainability & AutoML

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/explainability.py`)
- **Frontend**: ⚠️ Partially Available
- **Services**: `app/services/explainability_service.py`

### Features
- **Model Explainability**: SHAP values, feature importance
- **AutoML**: Automated model selection, hyperparameter tuning
- **Model Comparison**: Compare multiple models on same dataset
- **Feature Engineering**: Automatic feature generation

### API Endpoints

#### Get Model Explanation
```http
GET /api/v1/explainability/model/{model_id}/explain
```

#### Feature Importance
```http
GET /api/v1/explainability/model/{model_id}/feature-importance
```

#### AutoML Train
```http
POST /api/v1/explainability/automl/train
Content-Type: application/json

{
  "problem_type": "classification",
  "target": "customer_churn",
  "features": ["purchase_frequency", "avg_order_value", "last_purchase_days"],
  "test_size": 0.2
}
```

### Frontend Access
1. Navigate to **Analytics** → **Explainability**
2. Select a trained model
3. View feature importance charts
4. Explore SHAP value explanations
5. Compare model performance metrics

---

## 5. Streaming Analytics

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/streaming_analytics.py`)
- **Frontend**: ⚠️ Partially Available
- **Real-time**: WebSocket support for live updates

### Features
- **Real-time Dashboards**: Live sales, inventory, and customer metrics
- **Event Streaming**: Process events as they happen
- **Real-time Alerts**: Instant notifications for important events
- **Live Reporting**: Up-to-the-second reports

### API Endpoints

#### Get Real-time Metrics
```http
GET /api/v1/streaming-analytics/realtime/sales
GET /api/v1/streaming-analytics/realtime/inventory
GET /api/v1/streaming-analytics/realtime/customers
```

#### Subscribe to Events (WebSocket)
```javascript
const ws = new WebSocket('ws://your-domain/ws/streaming-analytics');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

### Frontend Access
1. Navigate to **Dashboard** → **Real-time Analytics**
2. View live metrics updating automatically
3. Configure alert thresholds
4. Export real-time data snapshots

---

## 6. Business Intelligence Advisor

### Status
- **Backend**: ✅ Fully Implemented (Part of `ai.py`)
- **Frontend**: ⚠️ Accessible via Chatbot
- **Service**: `app/services/ai_service.BusinessAdvisor`

### Features
- **Inventory Advice**: Stock optimization recommendations
- **Cash Flow Advice**: Improve cash flow management
- **Sales Strategy**: Increase sales effectiveness
- **Customer Retention**: Reduce churn

### Usage
Ask the AI Chatbot business-related questions:
- "How can I improve my cash flow?"
- "What inventory should I reorder?"
- "Which customers are at risk of churning?"
- "How can I increase sales?"

---

## 7. AI-Powered PDF Extraction

### Status
- **Backend**: ✅ Fully Implemented
- **Frontend**: ⚠️ Partially Available (Upload interface exists)
- **Documentation**: `AI_PDF_EXTRACTION_GUIDE.md`

### Supported Services
1. **Mindee API** (Recommended): 250 docs/month free
2. **Google Document AI**: 1000 pages/month free
3. **PDF.co**: 100 requests/month free

### Features
- **Invoice Extraction**: Automatically extract vendor, amounts, line items
- **Receipt Processing**: Parse receipt data
- **Business Document OCR**: Extract text from any business document

### Configuration
```bash
# Mindee (Recommended)
MINDEE_API_KEY=your_api_key
USE_AI_EXTRACTION=true

# Google Document AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_DOCUMENT_AI_KEY=your_project_id
```

### API Endpoints
```http
POST /api/v1/pdf/extract
Content-Type: multipart/form-data

file: <pdf_file>
```

### Frontend Usage
1. Navigate to any voucher creation page (Purchase, Sales, etc.)
2. Look for "Upload PDF" or "AI Extract" button
3. Upload invoice/receipt PDF
4. System automatically fills form fields
5. Review and adjust extracted data
6. Save voucher

---

## 8. Website Agent AI

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/website_agent.py`)
- **Frontend**: ✅ Available
- **Models**: `app/models/website_agent.py`

### Features
- **Chatbot for Websites**: Embed AI chatbot on your website
- **Lead Capture**: Automatically capture visitor information
- **FAQ Handling**: Answer common questions automatically
- **Integration**: Webhook support for third-party tools

### API Endpoints

#### Create Website Agent
```http
POST /api/v1/website-agent
Content-Type: application/json

{
  "name": "Support Bot",
  "website_url": "https://example.com",
  "greeting_message": "Hello! How can I help you today?",
  "chatbot_enabled": true,
  "lead_capture_enabled": true
}
```

#### Get Embed Code
```http
GET /api/v1/website-agent/{agent_id}/embed-code
```

### Frontend Access
1. Navigate to **Settings** → **Website Agent**
2. Create a new website agent
3. Configure greeting, FAQ, and behavior
4. Copy embed code
5. Paste on your website

---

## 9. Service Desk AI

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/service_desk.py`)
- **Frontend**: ✅ Available
- **Integration**: Chatbot integration for service desk

### Features
- **Ticket Auto-categorization**: AI classifies support tickets
- **Smart Routing**: Route tickets to correct team/person
- **Response Suggestions**: AI suggests responses for agents
- **Sentiment Analysis**: Detect customer sentiment

### API Endpoints

#### Create Chatbot Conversation
```http
POST /api/v1/service-desk/chatbot/conversations
```

#### Add Chatbot Message
```http
POST /api/v1/service-desk/chatbot/conversations/{conversation_id}/messages
Content-Type: application/json

{
  "message": "I need help with my order",
  "sender_type": "customer"
}
```

### Frontend Access
1. Navigate to **Service Desk** → **Tickets**
2. AI automatically categorizes new tickets
3. View suggested responses in ticket view
4. Sentiment indicator shows customer mood

---

## 10. Customer Analytics AI

### Status
- **Backend**: ✅ Fully Implemented (`app/api/v1/customer_analytics.py`)
- **Frontend**: ✅ Available
- **Models**: ML-based customer segmentation

### Features
- **Customer Segmentation**: RFM analysis, behavioral clustering
- **Churn Prediction**: Identify at-risk customers
- **Lifetime Value**: Predict customer LTV
- **Recommendation Engine**: Product recommendations for customers

### API Endpoints

#### Get Customer Segments
```http
GET /api/v1/customer-analytics/segments
```

#### Get Customer Insights
```http
GET /api/v1/customer-analytics/customers/{customer_id}/insights
```

#### Get Recommendations
```http
GET /api/v1/customer-analytics/customers/{customer_id}/recommendations
```

### Frontend Access
1. Navigate to **CRM** → **Customer Analytics**
2. View customer segments (Champions, At Risk, etc.)
3. See individual customer insights
4. Get AI-powered recommendations

---

## Configuration & Setup

### Environment Variables

```bash
# AI Services
USE_AI_FEATURES=true
OPENAI_API_KEY=your_openai_key  # Optional for enhanced AI
USE_LOCAL_NLP=true  # Use local models if no OpenAI key

# PDF Extraction
USE_AI_EXTRACTION=true
MINDEE_API_KEY=your_mindee_key

# Analytics
ENABLE_ML_ANALYTICS=true
AUTO_TRAIN_MODELS=false  # Set to true for automatic retraining

# Chatbot
CHATBOT_ENABLED=true
CHATBOT_RESPONSE_TIME_LIMIT=30  # seconds
```

### Database Migrations
Ensure all AI-related tables are created:
```bash
alembic upgrade head
```

### Installing Dependencies
```bash
pip install -r requirements.txt
# Includes: scikit-learn, pandas, numpy, transformers, etc.
```

---

## Troubleshooting

### Issue: AI Features Not Working
**Solution**: 
1. Check `USE_AI_FEATURES=true` in environment
2. Verify database migrations are up to date
3. Check API logs for errors: `tail -f logs/app.log`

### Issue: PDF Extraction Fails
**Solution**:
1. Verify API key is set correctly
2. Check API quota (free tier limits)
3. Ensure PDF is valid and not corrupted
4. Try different AI service (Mindee vs Google)

### Issue: Chatbot Gives Generic Responses
**Solution**:
1. Train custom intents in `app/services/ai_service.py`
2. Add more training data for intent classification
3. Use OpenAI integration for better responses

### Issue: ML Models Not Training
**Solution**:
1. Check sufficient data exists (min 100 records recommended)
2. Verify features are numeric or properly encoded
3. Check for missing values in training data
4. Review model training logs

### Issue: Real-time Analytics Not Updating
**Solution**:
1. Check WebSocket connection is established
2. Verify firewall allows WebSocket traffic
3. Check backend streaming service is running
4. Review browser console for errors

---

## API Authentication

All AI endpoints require authentication. Include JWT token in header:
```http
Authorization: Bearer <your_jwt_token>
```

Get token by logging in:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

---

## Performance Considerations

1. **Model Training**: Can take 1-5 minutes depending on data size
2. **Real-time Analytics**: Updates every 5-10 seconds (configurable)
3. **Chatbot Response**: Typically < 1 second
4. **PDF Extraction**: 2-5 seconds per document

---

## Future Enhancements

Planned AI features:
- [ ] Voice-to-text for mobile app
- [ ] Image recognition for product identification
- [ ] Advanced NLP for email parsing
- [ ] Predictive maintenance for manufacturing
- [ ] Dynamic pricing recommendations
- [ ] Automated report generation

---

## Support

For AI feature support:
- Email: support@tritiqerp.com
- Documentation: https://docs.tritiqerp.com/ai-features
- API Reference: https://api.tritiqerp.com/docs

---

## Appendix: AI Models Used

| Feature | Model Type | Library | Accuracy |
|---------|-----------|---------|----------|
| Intent Classification | Naive Bayes / BERT | scikit-learn / transformers | 90-95% |
| Sales Forecasting | ARIMA / Prophet | statsmodels / fbprophet | 85-90% |
| Customer Segmentation | K-Means / DBSCAN | scikit-learn | N/A |
| Churn Prediction | Random Forest | scikit-learn | 80-85% |
| Anomaly Detection | Isolation Forest | scikit-learn | 75-80% |
| Text Classification | TF-IDF + SVM | scikit-learn | 85-90% |

---

**Last Updated**: October 2025  
**Version**: 1.6  
**Maintainer**: Tritiq ERP Team
