# AI Implementation Guide - TRITIQ BOS System

## Table of Contents
1. [Overview](#overview)
2. [AI Features Inventory](#ai-features-inventory)
3. [Configuration & Setup](#configuration--setup)
4. [AI Features Documentation](#ai-features-documentation)
5. [Frontend Integration](#frontend-integration)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)
9. [Performance Optimization](#performance-optimization)
10. [FAQ](#faq)

---

## Overview

The TRITIQ BOS system includes comprehensive AI and machine learning capabilities to enhance business intelligence, automation, and user experience. This guide provides detailed information on configuring, implementing, and troubleshooting all AI features.

### Key AI Capabilities
- **AI Chatbot & Virtual Assistant**: Context-aware conversational AI for user assistance
- **Intent Classification**: Automatic detection of user intentions and entity extraction
- **Business Intelligence Advisor**: AI-powered recommendations for business optimization
- **Predictive Analytics**: ML-based forecasting and trend analysis
- **AI-Powered PDF Extraction**: Automatic data extraction from documents
- **Streaming Analytics**: Real-time data processing and insights
- **AutoML**: Automated machine learning model training and deployment
- **Explainability Tools**: Understand AI decision-making processes

---

## AI Features Inventory

### Backend AI Services

#### 1. AI Chatbot Service
**Location**: `app/api/v1/chatbot.py`, `app/services/ai_service.py`

**Status**: ✅ Fully Implemented

**Features**:
- Multi-turn conversation support
- Context-aware responses
- Integration with ERP modules
- Conversation history tracking
- Quick suggestions based on context

**Endpoints**:
- `POST /api/v1/chatbot/chat` - Send message to chatbot
- `GET /api/v1/chatbot/conversations` - List user conversations
- `GET /api/v1/chatbot/conversation/{id}` - Get conversation details
- `DELETE /api/v1/chatbot/conversation/{id}` - Delete conversation

#### 2. Intent Classification & Entity Extraction
**Location**: `app/api/v1/ai.py`, `app/services/ai_service.py`

**Status**: ✅ Fully Implemented

**Features**:
- NLP-based intent detection
- Entity extraction (dates, amounts, products, etc.)
- Multi-language support
- Confidence scoring

**Endpoints**:
- `POST /api/v1/ai/intent/classify` - Classify user intent
- `GET /api/v1/ai/intent/patterns` - Get available intent patterns

#### 3. Business Intelligence Advisor
**Location**: `app/api/v1/ai.py`, `app/services/ai_service.py`

**Status**: ✅ Fully Implemented

**Features**:
- Inventory optimization recommendations
- Cash flow analysis
- Sales performance insights
- Customer retention strategies

**Endpoints**:
- `POST /api/v1/ai/advice` - Get business advice
- `POST /api/v1/ai/advice/batch` - Get multiple recommendations

#### 4. AI Analytics
**Location**: `app/api/v1/ai_analytics.py`, `app/services/ai_analytics_service.py`

**Status**: ✅ Fully Implemented

**Features**:
- Predictive analytics (sales, inventory, customer churn)
- Anomaly detection
- Trend analysis
- Forecasting models

**Endpoints**:
- `POST /api/v1/ai-analytics/predict/sales` - Predict future sales
- `POST /api/v1/ai-analytics/predict/inventory` - Predict inventory needs
- `POST /api/v1/ai-analytics/predict/churn` - Predict customer churn
- `POST /api/v1/ai-analytics/detect-anomalies` - Detect anomalies in data
- `POST /api/v1/ai-analytics/analyze-trends` - Analyze trends

#### 5. Streaming Analytics
**Location**: `app/api/v1/streaming_analytics.py`

**Status**: ✅ Fully Implemented

**Features**:
- Real-time data processing
- Live dashboards
- Event stream analysis
- WebSocket support for live updates

**Endpoints**:
- `GET /api/v1/streaming/dashboard` - Get real-time dashboard data
- `WS /api/v1/streaming/ws` - WebSocket for live updates

#### 6. AutoML
**Location**: `app/api/v1/ai_analytics.py`

**Status**: ✅ Fully Implemented

**Features**:
- Automated model training
- Model selection and tuning
- Feature engineering
- Model deployment

**Endpoints**:
- `POST /api/v1/ai-analytics/automl/train` - Train AutoML model
- `GET /api/v1/ai-analytics/automl/models` - List trained models
- `POST /api/v1/ai-analytics/automl/predict` - Make predictions

#### 7. Explainability
**Location**: `app/api/v1/explainability.py`

**Status**: ✅ Fully Implemented

**Features**:
- SHAP (SHapley Additive exPlanations) values
- Feature importance analysis
- Decision tree visualization
- Model interpretability

**Endpoints**:
- `POST /api/v1/explainability/explain` - Explain model predictions
- `POST /api/v1/explainability/feature-importance` - Get feature importance

#### 8. AI-Powered PDF Extraction
**Location**: `app/api/v1/pdf_generation.py`

**Status**: ✅ Implemented (OCR and template-based extraction)

**Features**:
- Extract structured data from PDFs
- Invoice data extraction
- Receipt parsing
- Document classification

**Endpoints**:
- `POST /api/v1/pdf/extract` - Extract data from PDF

#### 9. Website Agent
**Location**: `app/api/v1/website_agent.py`

**Status**: ✅ Fully Implemented

**Features**:
- AI-powered web scraping
- Content extraction
- Data normalization
- Automated lead generation

**Endpoints**:
- `POST /api/v1/website-agent/scrape` - Scrape website data
- `POST /api/v1/website-agent/extract-leads` - Extract leads from website

#### 10. Email AI Service
**Location**: `app/services/email_ai_service.py`

**Status**: ✅ Fully Implemented

**Features**:
- Email categorization
- Smart reply suggestions
- Priority detection
- Sentiment analysis

---

## Configuration & Setup

### Prerequisites

1. **Python 3.9+** installed
2. **PostgreSQL** database
3. **Redis** (optional, for caching)
4. **OpenAI API Key** (for GPT-powered features)

### Step 1: Environment Variables

Copy `.env.example` to `.env` and configure the following AI-related variables:

```bash
# AI & Machine Learning Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORG_ID=your-openai-org-id  # Optional
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# AI Feature Toggles
ENABLE_AI_CHATBOT=true
ENABLE_AI_ANALYTICS=true
ENABLE_AI_PDF_EXTRACTION=true
ENABLE_AI_BUSINESS_ADVISOR=true
ENABLE_AI_INTENT_CLASSIFICATION=true
ENABLE_STREAMING_ANALYTICS=false
ENABLE_AUTOML=false
ENABLE_AI_EXPLAINABILITY=false

# AI Service Configuration
AI_SERVICE_TIMEOUT=30
AI_CACHE_TTL=3600
AI_RATE_LIMIT=60
```

### Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key and add it to your `.env` file as `OPENAI_API_KEY`

### Step 3: Install Dependencies

```bash
# Backend dependencies
pip install openai tiktoken scikit-learn pandas numpy

# Optional: For advanced ML features
pip install tensorflow torch transformers shap
```

### Step 4: Initialize AI Services

The AI services are automatically initialized when the application starts if the feature flags are enabled.

### Step 5: Verify Setup

Test the AI services:

```bash
# Start the backend
cd /path/to/FastApiv1.6
uvicorn app.main:app --reload

# Test AI endpoints
curl -X POST http://localhost:8000/api/v1/ai/intent/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "What are my sales for last month?"}'
```

---

## AI Features Documentation

### 1. AI Chatbot

#### Overview
The AI Chatbot provides context-aware assistance to users, helping them navigate the ERP system, answer questions, and perform tasks.

#### Usage

**Frontend Access**:
- Navigate to **AI & Analytics** → **AI Chatbot** in the main menu
- Or use the floating chatbot widget (available on all pages)

**API Usage**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chatbot/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "Show me top selling products",
        "conversation_id": None  # Optional: for multi-turn conversations
    }
)
```

**Response**:
```json
{
  "message": "Here are your top selling products:\n1. Product A - 150 units\n2. Product B - 120 units\n3. Product C - 95 units",
  "conversation_id": "uuid-here",
  "suggestions": ["Show sales by month", "View product details"],
  "confidence": 0.95
}
```

#### Configuration
- **Model**: Configure in `.env` as `OPENAI_MODEL` (default: `gpt-3.5-turbo`)
- **Temperature**: Control randomness with `OPENAI_TEMPERATURE` (0.0-2.0)
- **Max Tokens**: Limit response length with `OPENAI_MAX_TOKENS`

---

### 2. Intent Classification

#### Overview
Automatically classifies user queries into predefined intents and extracts relevant entities.

#### Supported Intents
- `sales_inquiry` - Questions about sales data
- `inventory_check` - Stock level queries
- `customer_info` - Customer-related questions
- `financial_query` - Finance and accounting questions
- `order_status` - Order tracking queries
- `product_search` - Product information requests

#### Usage

**API Example**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai/intent/classify",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "What are my sales for last month?"}
)
```

**Response**:
```json
{
  "intent": "sales_inquiry",
  "confidence": 0.95,
  "entities": {
    "time_period": "last_month",
    "metric": "sales"
  }
}
```

---

### 3. Business Intelligence Advisor

#### Overview
Provides AI-powered recommendations for business optimization across multiple categories.

#### Categories
- **Inventory**: Stock optimization, reorder suggestions
- **Cash Flow**: Cash management insights
- **Sales**: Sales performance improvements
- **Customer Retention**: Churn prevention strategies

#### Usage

**API Example**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai/advice",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "category": "inventory",
        "context": {
            "low_stock_items": 5,
            "overstock_items": 3
        }
    }
)
```

**Response**:
```json
{
  "category": "inventory",
  "recommendations": [
    {
      "title": "Reorder Low Stock Items",
      "description": "5 items are below minimum stock level",
      "priority": "high",
      "action": "review_and_reorder"
    },
    {
      "title": "Reduce Overstock",
      "description": "3 items have excess inventory",
      "priority": "medium",
      "action": "promote_or_discount"
    }
  ]
}
```

---

### 4. Predictive Analytics

#### Overview
ML-based forecasting and prediction capabilities for sales, inventory, and customer behavior.

#### Features

**Sales Forecasting**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-analytics/predict/sales",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "product_id": 123,
        "forecast_days": 30
    }
)
```

**Inventory Prediction**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-analytics/predict/inventory",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "product_id": 123,
        "horizon_days": 30
    }
)
```

**Customer Churn Prediction**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-analytics/predict/churn",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "customer_id": 456
    }
)
```

---

### 5. Streaming Analytics

#### Overview
Real-time data processing and live dashboard updates via WebSocket.

#### Usage

**Frontend Implementation**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/streaming/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Live update:', data);
  // Update dashboard
};
```

**Configuration**:
- Enable in `.env`: `ENABLE_STREAMING_ANALYTICS=true`
- Requires Redis for pub/sub functionality

---

### 6. AutoML

#### Overview
Automated machine learning for training custom models without manual ML expertise.

#### Usage

**Train Model**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-analytics/automl/train",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "dataset": "sales_data",
        "target_column": "revenue",
        "problem_type": "regression",
        "max_trials": 10
    }
)
```

**Make Predictions**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/ai-analytics/automl/predict",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model_id": "model-uuid",
        "features": {
            "month": 12,
            "region": "North",
            "product_category": "Electronics"
        }
    }
)
```

---

### 7. AI Explainability

#### Overview
Understand how AI models make decisions using SHAP values and feature importance.

#### Usage

**Explain Prediction**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/explainability/explain",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model_id": "model-uuid",
        "instance": {
            "feature1": 100,
            "feature2": 50
        }
    }
)
```

**Get Feature Importance**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/explainability/feature-importance",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model_id": "model-uuid"
    }
)
```

---

## Frontend Integration

### Accessing AI Features

#### Menu Navigation
All AI features are accessible from the **AI & Analytics** section in the main menu:

1. **AI Chatbot** - `/ai-chatbot`
2. **Advanced Analytics** - `/analytics/advanced-analytics`
3. **Streaming Dashboard** - `/analytics/streaming-dashboard`
4. **AutoML** - `/analytics/automl`
5. **A/B Testing** - `/analytics/ab-testing`

#### Chatbot Widget
The floating chatbot widget is available on all pages:
- Click the chatbot icon in the bottom-right corner
- Type your question
- Get instant AI-powered responses

### Example: Using AI Chatbot Component

```typescript
import { AIChatbot } from '@/ai/AIChatbot';

function MyPage() {
  const [chatbotOpen, setChatbotOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setChatbotOpen(true)}>
        Open AI Assistant
      </button>
      
      <AIChatbot
        open={chatbotOpen}
        onClose={() => setChatbotOpen(false)}
        context={{
          page: 'sales-dashboard',
          module: 'sales'
        }}
      />
    </div>
  );
}
```

---

## API Reference

### Authentication
All AI endpoints require authentication via JWT token:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### Common Response Format

**Success Response**:
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

### Rate Limiting
- Default: 60 requests per minute per user
- Configure with `AI_RATE_LIMIT` in `.env`
- Returns `429 Too Many Requests` when exceeded

---

## Troubleshooting

### Common Issues

#### 1. AI Features Not Available

**Symptom**: AI endpoints return 404 or features are disabled

**Solution**:
- Check `.env` file for AI feature flags
- Ensure `ENABLE_AI_CHATBOT=true` and other relevant flags are set
- Restart the backend server after changing `.env`

#### 2. OpenAI API Errors

**Symptom**: Chatbot returns errors like "Invalid API key"

**Solution**:
- Verify `OPENAI_API_KEY` is correctly set in `.env`
- Check API key is active on OpenAI platform
- Ensure you have sufficient credits in your OpenAI account
- Check OpenAI service status: https://status.openai.com

#### 3. Slow AI Responses

**Symptom**: AI requests take too long to complete

**Solution**:
- Reduce `OPENAI_MAX_TOKENS` to limit response size
- Enable Redis caching with `REDIS_URL`
- Increase `AI_SERVICE_TIMEOUT` if needed
- Consider using `gpt-3.5-turbo` instead of `gpt-4` for faster responses

#### 4. Rate Limit Exceeded

**Symptom**: "Too many requests" errors

**Solution**:
- Increase `AI_RATE_LIMIT` in `.env`
- Implement request queuing on frontend
- Use caching to reduce redundant requests

#### 5. Memory Issues with ML Models

**Symptom**: Server crashes or runs out of memory

**Solution**:
- Disable unused AI features (AutoML, Explainability)
- Increase server memory allocation
- Use model compression techniques
- Implement lazy loading for ML models

---

## Security Best Practices

### 1. API Key Management
- **Never commit** `.env` file to version control
- Use environment-specific `.env` files
- Rotate API keys regularly
- Use separate keys for development and production

### 2. Data Privacy
- **PII Protection**: Ensure sensitive data is encrypted before sending to AI services
- **Data Retention**: Configure how long AI conversations and predictions are stored
- **GDPR Compliance**: Implement data deletion requests for AI-generated data

### 3. Access Control
- Implement role-based access control (RBAC) for AI features
- Restrict expensive AI operations to authorized users
- Log all AI API usage for audit trails

### 4. Rate Limiting
- Implement both user-level and IP-level rate limiting
- Set different limits for different AI features based on cost
- Monitor API usage to detect abuse

### 5. Input Validation
- Sanitize all user inputs before sending to AI services
- Implement input length limits
- Validate data types and formats
- Prevent prompt injection attacks

### 6. Error Handling
- Never expose API keys or internal errors to users
- Log errors securely on server-side
- Provide generic error messages to users
- Implement fallback mechanisms for AI failures

---

## Performance Optimization

### 1. Caching
```python
# Enable Redis caching
REDIS_URL=redis://localhost:6379
AI_CACHE_TTL=3600  # 1 hour
```

**Benefits**:
- Reduce redundant AI API calls
- Faster response times for repeated queries
- Lower API costs

### 2. Request Batching
Group multiple AI requests into a single API call when possible:

```python
# Instead of multiple single requests
response = requests.post(
    "http://localhost:8000/api/v1/ai/advice/batch",
    json={
        "requests": [
            {"category": "inventory", "context": {...}},
            {"category": "sales", "context": {...}}
        ]
    }
)
```

### 3. Asynchronous Processing
For expensive operations, use background tasks:

```python
# FastAPI background task
@router.post("/ai/train-model")
async def train_model(background_tasks: BackgroundTasks):
    background_tasks.add_task(train_ml_model, params)
    return {"message": "Training started"}
```

### 4. Model Optimization
- Use quantized models for faster inference
- Implement model caching to avoid reloading
- Use smaller models for less critical features
- Consider edge deployment for low-latency requirements

### 5. Monitoring
Track AI performance metrics:
- Response times
- API call frequency
- Error rates
- Cache hit rates
- Model accuracy over time

---

## FAQ

### Q1: Do I need OpenAI API access to use all AI features?

**A:** Not all features require OpenAI. The chatbot and some NLP features use OpenAI, but predictive analytics, AutoML, and explainability work with local ML models. You can enable/disable features individually.

### Q2: How much does OpenAI API usage cost?

**A:** Costs depend on the model and usage:
- `gpt-3.5-turbo`: ~$0.002 per 1K tokens
- `gpt-4`: ~$0.03 per 1K tokens
Monitor usage at https://platform.openai.com/usage

### Q3: Can I use alternative AI providers instead of OpenAI?

**A:** Yes! The AI service layer is designed to be provider-agnostic. You can implement adapters for:
- Azure OpenAI
- Anthropic Claude
- Google PaLM
- Hugging Face models
- Self-hosted models

### Q4: How do I train custom ML models?

**A:** Use the AutoML feature:
1. Prepare your dataset in CSV format
2. Call `/api/v1/ai-analytics/automl/train` endpoint
3. Specify target column and problem type
4. Monitor training progress
5. Use trained model for predictions

### Q5: Is my data sent to external AI services secure?

**A:** Yes, with proper configuration:
- Data is transmitted over HTTPS
- OpenAI does not use API data to train models (as per their policy)
- Sensitive data should be encrypted before sending
- Consider using Azure OpenAI for compliance requirements

### Q6: Can I disable specific AI features?

**A:** Yes! Use feature flags in `.env`:
```bash
ENABLE_AI_CHATBOT=false
ENABLE_AI_ANALYTICS=false
# etc.
```

### Q7: How do I backup AI models and conversation history?

**A:** 
- ML models are stored in database (backup with regular DB backups)
- Conversation history is in PostgreSQL (include in DB backup)
- Exported models can be saved as files in `uploads/models/`

### Q8: What's the maximum conversation length for the chatbot?

**A:** 
- Token limit: Configured by `OPENAI_MAX_TOKENS` (default: 1000)
- Message history: Last 10 messages included for context
- Adjust in code if more context is needed

---

## Support & Resources

### Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [SHAP Documentation](https://shap.readthedocs.io/)

### Community
- GitHub Issues: Report bugs and request features
- Discord/Slack: Join community discussions
- Stack Overflow: Tag questions with `tritiq-erp`

### Professional Support
Contact support@tritiq.com for:
- Enterprise AI features
- Custom model training
- Performance optimization
- Security audits

---

## Changelog

### Version 1.6.0 (Current)
- ✅ AI Chatbot with GPT-3.5/4 support
- ✅ Intent classification and entity extraction
- ✅ Business intelligence advisor
- ✅ Predictive analytics (sales, inventory, churn)
- ✅ Streaming analytics with WebSocket
- ✅ AutoML capabilities
- ✅ AI explainability with SHAP
- ✅ AI-powered PDF extraction
- ✅ Website agent for data scraping
- ✅ Email AI service

### Roadmap
- 🔄 Multi-language chatbot support
- 🔄 Computer vision for invoice scanning
- 🔄 Voice assistant integration
- 🔄 Advanced recommendation engine
- 🔄 Natural language to SQL queries
- 🔄 Sentiment analysis for customer feedback

---

## License

This AI Implementation Guide is part of the TRITIQ BOS system.
© 2025 Tritiq Technologies. All rights reserved.
