# CRM, AI & Chatbot Integration Guide

## Overview

This document provides a comprehensive guide to the CRM system improvements, AI analytics capabilities, and chatbot integration features in the TritiQ ERP system.

## Table of Contents

1. [CRM Module Enhancements](#crm-module-enhancements)
2. [AI Chatbot Implementation](#ai-chatbot-implementation)
3. [Service Module Chatbot](#service-module-chatbot)
4. [Lead Ownership & RBAC](#lead-ownership--rbac)
5. [Commission Tracking](#commission-tracking)
6. [Future Enhancements](#future-enhancements)

---

## CRM Module Enhancements

### Customer Analytics

#### Fixed Issues
- **Voucher Date Error**: Fixed backend API endpoint to use `SalesVoucher.date` instead of non-existent `voucher_date` field
- **Navigation**: Customer analytics now accessible from multiple entry points:
  - Sales Dashboard
  - Customer Database
  - Direct URL navigation

#### Features
- Total customer count with trend analysis
- Active customers tracking
- Revenue analytics with period comparison
- Customer lifetime value calculation
- Satisfaction score tracking
- Customer segmentation analysis
- Top customers by revenue

#### API Endpoints
```python
GET /api/v1/crm/customer-analytics?period_start=YYYY-MM-DD&period_end=YYYY-MM-DD
```

**Response:**
```json
{
  "total_customers": 1245,
  "active_customers": 987,
  "new_customers": 45,
  "churned_customers": 23,
  "total_revenue": 15500000,
  "average_lifetime_value": 125000,
  "average_satisfaction_score": 4.2,
  "customers_by_segment": {
    "Enterprise": 45,
    "Mid-Market": 187,
    "Small Business": 456,
    "Startup": 557
  },
  "top_customers": [
    {"id": 1, "name": "TechCorp", "revenue": 2500000}
  ],
  "period_start": "2024-01-01",
  "period_end": "2024-12-31"
}
```

### Customer Management

#### UX Improvements
- **Add Customer Modal**: Streamlined customer creation with inline modal instead of navigation
- **GST Auto-fill**: Support for GST number validation and auto-population
- **Address Auto-complete**: Pincode-based address lookup
- **Real-time Validation**: Form validation with helpful error messages

#### Empty States
- Implemented proper empty states for:
  - Contacts (when no contacts exist)
  - Accounts (when no accounts exist)
  - Customers (with helpful CTAs)

### Currency Standardization

All CRM modules now support organization-specific currency with **Indian Rupee (₹)** as default:
- Customer analytics displays
- Commission tracking  
- Sales reports
- Account management
- Opportunity values

**Implementation:**
```typescript
import { formatCurrency, getCurrencySymbol } from "../../utils/currencyUtils";

// Usage with default INR
formatCurrency(125000) // Returns "₹1,25,000.00"

// Usage with custom currency
formatCurrency(125000, "USD", "en-US") // Returns "$125,000.00"

// Get currency symbol
getCurrencySymbol("INR") // Returns "₹"
getCurrencySymbol("USD") // Returns "$"
```

---

## Lead Ownership & RBAC

### Overview

The CRM system now implements role-based lead ownership filtering to ensure users only see leads they have permission to view.

### Features

#### Ownership Filtering

**Regular Users (No Admin Access):**
- See only leads assigned to them (`assigned_to_id == user.id`)
- See leads they created (`created_by_id == user.id`)
- Cannot view other users' leads

**Managers/Admins (With Admin Access):**
- See all leads in the organization
- Have permissions: `crm_lead_manage_all`, `crm_admin`, or `is_company_admin`
- Can view owner names for all leads

#### Owner Name Display

For users with admin access, lead lists now include:
- **assigned_to_name**: Name of the user the lead is assigned to
- **created_by_name**: Name of the user who created the lead

**Schema Update:**
```python
class Lead(LeadInDB):
    # Additional fields for display (populated from joins)
    assigned_to_name: Optional[str] = Field(None, description="Name of assigned user")
    created_by_name: Optional[str] = Field(None, description="Name of user who created lead")
```

#### Permission Checks

The backend automatically applies ownership filtering in the `/api/v1/crm/leads` endpoint:

```python
# Check if user has admin/manager permissions
has_admin_access = (
    "crm_lead_manage_all" in user_permissions or 
    "crm_admin" in user_permissions or
    current_user.is_company_admin
)

# If user doesn't have admin access, filter to owned leads
if not has_admin_access:
    stmt = stmt.where(
        or_(
            Lead.assigned_to_id == current_user.id,
            Lead.created_by_id == current_user.id
        )
    )
```

### API Usage

**Get Leads (Automatically Filtered):**
```http
GET /api/v1/crm/leads?skip=0&limit=100
Authorization: Bearer {token}
X-Organization-ID: {org_id}
```

**Response (Admin User):**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "assigned_to_id": 42,
    "assigned_to_name": "Jane Smith",
    "created_by_id": 15,
    "created_by_name": "Mike Johnson",
    "status": "qualified",
    ...
  }
]
```

**Response (Regular User - Only Their Leads):**
```json
[
  {
    "id": 5,
    "first_name": "Alice",
    "last_name": "Brown",
    "email": "alice@example.com",
    "assigned_to_id": 15,
    "assigned_to_name": null,  // Not populated for regular users
    "created_by_id": 15,
    "created_by_name": null,
    "status": "new",
    ...
  }
]
```

### Frontend Integration

The frontend automatically receives filtered leads based on user permissions. No additional filtering needed in UI code:

```typescript
// Leads are automatically filtered by backend
const leads = await crmService.getLeads();

// Display owner names if available (only for admins)
{lead.assigned_to_name && (
  <Chip 
    label={`Assigned to: ${lead.assigned_to_name}`} 
    size="small" 
  />
)}
```

---

## AI Chatbot Implementation

### App Navigation Chatbot

The AI chatbot provides intelligent navigation assistance and task automation throughout the application.

#### Core Features

1. **Natural Language Navigation**
   - "Show me customers"
   - "Open sales dashboard"
   - "Navigate to inventory"

2. **Business Advice**
   - Inventory management recommendations
   - Cash flow optimization tips
   - Sales strategy guidance
   - Tax compliance advice

3. **Task Assistance**
   - Create vouchers with guided input
   - Generate leads from conversations
   - Schedule follow-ups
   - Quick data lookups

4. **Contextual Help**
   - Module-specific guidance
   - Feature explanations
   - Workflow assistance
   - Best practices

#### API Integration

**Endpoint:**
```python
POST /api/v1/chatbot/process
```

**Request:**
```json
{
  "message": "How do I create a sales invoice?",
  "context": {
    "current_page": "/sales/dashboard",
    "user_role": "sales_manager"
  }
}
```

**Response:**
```json
{
  "message": "To create a sales invoice:\n1. Navigate to Vouchers > Sales Vouchers\n2. Click 'Create New Invoice'\n3. Select customer and products\n4. Review and save",
  "actions": [
    {
      "type": "navigate",
      "label": "Go to Sales Vouchers",
      "data": {"path": "/vouchers/sales"}
    }
  ],
  "intent": "create_sales_invoice",
  "confidence": 0.95,
  "suggestions": [
    "How do I add items to an invoice?",
    "What are the tax settings for invoices?"
  ]
}
```

#### Implementation Guidelines

**Frontend Integration:**
```typescript
// pages/ai-chatbot/index.tsx
import { useState } from 'react';
import { chatbotService } from '@/services/chatbotService';

function AIChatbot() {
  const [message, setMessage] = useState('');
  const [responses, setResponses] = useState([]);

  const sendMessage = async () => {
    const response = await chatbotService.sendMessage({
      message,
      context: {
        current_page: window.location.pathname,
        user_role: currentUser.role
      }
    });
    
    setResponses([...responses, response]);
  };

  // Handle action buttons from chatbot
  const handleAction = (action) => {
    if (action.type === 'navigate') {
      router.push(action.data.path);
    } else if (action.type === 'execute') {
      // Execute specific actions
    }
  };

  return (
    // Chatbot UI implementation
  );
}
```

**Backend Service:**
```python
# app/api/v1/chatbot.py
class ChatbotService:
    async def process_message(self, message: str, context: dict):
        # Intent classification
        intent = await self.classify_intent(message)
        
        # Generate response based on intent
        if intent == 'navigation':
            return await self.handle_navigation(message, context)
        elif intent == 'business_advice':
            return await self.provide_advice(message, context)
        elif intent == 'task_automation':
            return await self.automate_task(message, context)
        
        # Default response
        return await self.general_response(message)
```

---

## Service Module Chatbot

### Customer Website Integration

Enable customers to integrate a chatbot on their website that connects to their TritiQ service module.

#### Features

1. **Customer Support**
   - Answer product questions
   - Provide service status
   - Schedule appointments
   - Escalate to human agents

2. **Lead Generation**
   - Capture visitor information
   - Qualify leads automatically
   - Create opportunities in CRM
   - Schedule sales calls

3. **Service Requests**
   - Submit tickets
   - Track existing requests
   - Update contact information
   - Access knowledge base

#### Integration Methods

**1. JavaScript Embed Code**
```html
<!-- Customer Website Integration -->
<script>
  (function() {
    window.TritiQChatbot = {
      apiKey: 'YOUR_API_KEY',
      orgId: 'YOUR_ORG_ID',
      theme: 'light', // or 'dark'
      position: 'bottom-right'
    };
    
    var script = document.createElement('script');
    script.src = 'https://your-erp-domain.com/chatbot-widget.js';
    script.async = true;
    document.head.appendChild(script);
  })();
</script>
```

**2. React Component**
```typescript
import { TritiQChatWidget } from '@tritiq/chatbot-widget';

function MyWebsite() {
  return (
    <div>
      {/* Your website content */}
      <TritiQChatWidget
        apiKey="YOUR_API_KEY"
        orgId="YOUR_ORG_ID"
        theme="light"
      />
    </div>
  );
}
```

**3. WordPress Plugin**
```php
// TritiQ Chatbot WordPress Plugin
// Easy configuration through WordPress admin panel
```

#### Backend API for Customer Chatbot

```python
# app/api/v1/chatbot/public.py
@router.post("/public/chat")
async def handle_public_chat(
    message: str,
    session_id: str,
    api_key: str,
    db: AsyncSession = Depends(get_db)
):
    # Validate API key and get organization
    org = await validate_chatbot_api_key(api_key, db)
    
    # Process message with organization context
    response = await process_customer_message(
        message=message,
        session_id=session_id,
        org_id=org.id,
        db=db
    )
    
    return response
```

#### Configuration Panel

Location: `/service/chatbot-settings`

**Settings:**
- Enable/Disable chatbot
- Generate API keys
- Customize branding (colors, logo)
- Configure greeting message
- Set business hours
- Define escalation rules
- Knowledge base management

---

## Lead Ownership & RBAC

### Requirements

**Role-based Lead Visibility:**
1. **Sales Executives**: See only their assigned leads
2. **Sales Managers**: See all leads with owner information
3. **Management**: See all leads with analytics
4. **Org Admins**: Full access to all leads

### Backend Implementation

```python
# app/api/v1/crm.py
@router.get("/leads", response_model=List[LeadSchema])
async def get_leads(
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    # Base query
    stmt = select(Lead).where(Lead.organization_id == org_id)
    
    # Apply RBAC filters
    if current_user.role == "sales_executive":
        # Executives see only their leads
        stmt = stmt.where(Lead.assigned_to_id == current_user.id)
    elif current_user.role in ["sales_manager", "management", "org_admin"]:
        # Managers and above see all leads
        # Include owner information in response
        stmt = stmt.options(joinedload(Lead.assigned_to))
    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view leads"
        )
    
    result = await db.execute(stmt)
    leads = result.scalars().all()
    
    return leads
```

### Frontend Implementation

```typescript
// pages/sales/leads.tsx
interface Lead {
  id: number;
  lead_number: string;
  first_name: string;
  last_name: string;
  // ... other fields
  assigned_to?: {
    id: number;
    name: string;
    email: string;
  };
  can_edit: boolean;
  can_delete: boolean;
}

// Display owner for managers
{currentUser.role !== 'sales_executive' && (
  <TableCell>
    <Chip
      label={lead.assigned_to?.name || 'Unassigned'}
      size="small"
      variant="outlined"
    />
  </TableCell>
)}
```

---

## Commission Tracking

### Enhanced Features

#### New Fields
1. **Person Name** (Required): Name of the sales person/partner
2. **Person Type** (Required): 
   - Internal (Employee)
   - External (Partner/Agent)

#### Currency
All commission amounts displayed in **₹ (Indian Rupee)**

### Data Model

```python
# app/models/crm_models.py
class Commission(Base):
    __tablename__ = "commissions"
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    sales_person_id = Column(Integer, ForeignKey("users.id"))
    sales_person_name = Column(String, nullable=False)
    person_type = Column(Enum("internal", "external"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))
    commission_type = Column(String)  # percentage, fixed_amount, tiered, bonus
    commission_rate = Column(Float)
    commission_amount = Column(Float)
    base_amount = Column(Float, nullable=False)
    commission_date = Column(Date, nullable=False)
    payment_status = Column(String)  # pending, paid, approved, rejected
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### API Endpoints (To Be Implemented)

```python
# app/api/v1/crm.py

@router.get("/commissions")
async def get_commissions(
    skip: int = 0,
    limit: int = 100,
    person_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get commissions with filtering"""
    pass

@router.post("/commissions")
async def create_commission(
    commission_data: CommissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Create new commission record"""
    pass

@router.put("/commissions/{commission_id}")
async def update_commission(
    commission_id: int,
    commission_data: CommissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Update commission record"""
    pass
```

---

## Future Enhancements

### Planned Features

1. **Advanced AI Analytics**
   - Predictive sales forecasting
   - Customer churn prediction
   - Automated lead scoring
   - Revenue optimization suggestions

2. **Chatbot Enhancements**
   - Multi-language support
   - Voice interface
   - Video chat escalation
   - AI-powered sentiment analysis

3. **CRM Advanced Features**
   - Email campaign integration
   - Social media lead tracking
   - Advanced workflow automation
   - Custom dashboards

4. **Integration Capabilities**
   - WhatsApp Business API
   - Telegram Bot
   - Slack integration
   - Microsoft Teams connector

### Development Roadmap

**Phase 1 (Current)**
- ✅ Customer analytics fixes
- ✅ Currency standardization
- ✅ Commission tracking enhancements
- 🔄 Lead ownership RBAC
- 🔄 Basic chatbot implementation

**Phase 2 (Q2 2025)**
- AI analytics dashboard
- Service chatbot activation
- Advanced lead scoring
- Email campaign integration

**Phase 3 (Q3 2025)**
- Multi-channel chatbot
- Predictive analytics
- Advanced automation
- Third-party integrations

**Phase 4 (Q4 2025)**
- AI-powered website builder
- Advanced customization
- Enterprise features
- Global expansion capabilities

---

## Support & Documentation

For additional support:
- **Technical Documentation**: `/docs/API_DOCUMENTATION.md`
- **User Guide**: `/docs/CRM_USAGE_GUIDE.md`
- **API Reference**: `/api/docs` (Swagger UI)
- **Support Email**: support@tritiq.com

---

*Last Updated: December 2024*
*Version: 1.6*
