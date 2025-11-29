# TritIQ BOS - Business Made Simple

> **Business Made Simple** — A modern, scalable FastAPI-based backend with Next.js Turbopack frontend for the TritIQ BOS system.

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Run migrations
alembic upgrade head

# 4. Start application (auto-seeding happens on first boot)
uvicorn app.main:app --reload
```

**That's it!** The system automatically seeds baseline data on first boot. 

**Default login**: `naughtyfruit53@gmail.com` / `123456` (change after first login)

📖 **[Complete User Guide](./USER_GUIDE.md)** | **[Database Reset Guide](./DATABASE_RESET_GUIDE.md)**

---

## 🌟 Latest Enhancements

### 🗄️ Unified Database Management (v1.6.2)
- **Unified Seeding**: Single script (`scripts/seed_all.py`) for all baseline data
- **Auto-Seed on Boot**: Automatically seeds missing data on application startup
- **Idempotent Operations**: Safe to run multiple times without duplicates
- **Complete Reset Script**: SQL script to drop all tables (`sql/drop_all_tables.sql`)
- **Streamlined Documentation**: Cleaned up 360+ docs, kept only essential guides
- **Comprehensive User Guide**: New `USER_GUIDE.md` with complete workflows

**What gets auto-seeded:**
- Super admin user
- Module and submodule taxonomy
- RBAC permissions and roles
- Chart of Accounts
- Voucher format templates
- Organization defaults

### 🔒 Authentication Loop Fix (v1.6.1)
- **Standardized Token Storage**: All frontend files now use consistent `ACCESS_TOKEN_KEY` constant
- **Eliminated Auth Loops**: Fixed infinite 401 loops caused by inconsistent token storage keys
- **Backward Compatibility**: Automatic migration from legacy "token" key to new "access_token" key
- **Enhanced Debugging**: Added comprehensive logging throughout auth flow for easier troubleshooting
- **Fixed Token Refresh**: Corrected refresh token endpoint path in API interceptor

**Files Updated**:
- `frontend/src/constants/auth.ts` (new) - Centralized auth constant definitions
- `frontend/src/lib/api.ts` - Updated to use standardized token keys
- `frontend/src/utils/api.ts` - Updated to use standardized token keys
- `frontend/src/context/AuthContext.tsx` - Updated to use standardized token keys
- `frontend/src/services/authService.ts` - Updated to use standardized token keys
- `frontend/src/pages/login.tsx` - Updated to use standardized token keys

**Troubleshooting**:
- All tokens are now stored under the key `access_token` instead of `token`
- Legacy tokens will be automatically migrated on first API call
- Check browser console for detailed auth flow logs with `[AuthProvider]`, `[AuthService]`, and `[API]` prefixes
- Use browser dev tools > Application > Local Storage to inspect token storage

### ⚡ Frontend: Turbopack Integration
- **10x Faster Development**: Turbopack enabled for lightning-fast builds
- **Instant Hot Reload**: Changes reflect immediately without losing state
- **Enhanced Developer Experience**: Improved error reporting and debugging

### 🔐 Backend: Security & Reliability Improvements
- **Secure Password Reset**: Admin-controlled password reset with email notifications
- **Advanced Session Management**: Automatic rollback and retry logic
- **Enhanced Email Service**: HTML templates with robust error handling
- **Comprehensive Logging**: Security auditing and database operation tracking

📖 **[View Complete Enhancement Documentation](./docs/ENHANCEMENTS.md)**

## 🔍 Automated UI Audit System

### Overview
FastApiV1.5 includes a comprehensive automated UI audit system that continuously monitors the accessibility, functionality, and performance of all UI features. The system uses Python Playwright to navigate through the entire application, test every menu and submenu, and generate detailed reports.

### Key Features
- **🎯 Comprehensive Coverage**: Tests all 47+ features across 7 major modules
- **📊 Detailed Reporting**: Generates both Markdown and JSON reports
- **🚀 CI/CD Integration**: Automatically runs on every PR and push to main
- **📱 Cross-browser Testing**: Supports Chromium, Firefox, and WebKit
- **📈 Performance Monitoring**: Tracks load times and identifies slow pages
- **🔔 Automated Notifications**: PR comments and scheduled reports
- **📸 Screenshot Capture**: Visual evidence for debugging broken features

### Quick Start

#### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt
playwright install

# Start your application
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
cd frontend && npm start &

# Run the audit
python scripts/audit_ui_features.py --url http://localhost:3000 --api http://localhost:8000
```

#### Manual Audit Options
```bash
# Full comprehensive audit (default)
python scripts/audit_ui_features.py

# Headless mode for CI/CD
python scripts/audit_ui_features.py --headless

# Custom URLs and credentials
python scripts/audit_ui_features.py \
  --url https://your-frontend.com \
  --api https://your-api.com \
  --username admin@company.com \
  --password your-password

# Disable screenshots for faster execution
python scripts/audit_ui_features.py --no-screenshots
```

#### GitHub Actions Integration
The audit system automatically runs:
- **On Pull Requests**: Comments with accessibility and performance metrics
- **On Push to Main**: Full audit with artifact upload
- **Daily Schedule**: Comprehensive system health check at 2 AM UTC
- **Manual Trigger**: On-demand audits with configurable scope

### Audit Reports

#### Report Structure
- **📄 Markdown Report**: Human-readable comprehensive analysis
- **📊 JSON Report**: Machine-readable data for integrations
- **📸 Screenshots**: Visual debugging for failed features
- **📈 Performance Metrics**: Load times and optimization suggestions

#### Sample Metrics
```
📊 Executive Summary
├── Accessibility Rate: 91.5%
├── Total Features: 47
├── Accessible: 43
├── Broken: 2
├── Performance Grade: A
└── Average Load Time: 2.3s
```

#### Integration Examples
```python
# Parse audit results programmatically
import json

with open('audit_results/audit_report_latest.json') as f:
    audit_data = json.load(f)
    
accessibility_rate = audit_data['summary_statistics']['accessibility_rate']
broken_features = audit_data['summary_statistics']['broken']

if broken_features > 0:
    print(f"⚠️ {broken_features} features need attention")
```

### Workflow Integration

#### PR Workflow
1. **Trigger**: PR opened/updated with frontend changes
2. **Environment**: Spins up test environment
3. **Audit**: Comprehensive feature testing
4. **Report**: Automatic PR comment with results
5. **Decision**: Pass/fail based on accessibility thresholds

#### Production Monitoring
- **Scheduled Audits**: Daily health checks
- **Alert Thresholds**: <85% accessibility triggers warnings
- **Historical Tracking**: Trend analysis over time
- **Performance Budgets**: Load time regression detection

### Configuration

#### Environment Variables
```env
# Audit system configuration
UI_AUDIT_ENABLED=true
UI_AUDIT_THRESHOLD=85
UI_AUDIT_TIMEOUT=30000
UI_AUDIT_SCREENSHOT=true
```

#### Custom Test Users
```python
# Configure in scripts/audit_ui_features.py
LOGIN_USERS = {
    'admin': {'email': 'admin@test.com', 'password': 'admin123'},
    'user': {'email': 'user@test.com', 'password': 'user123'},
    'readonly': {'email': 'readonly@test.com', 'password': 'readonly123'}
}
```

### Extensibility

#### Adding New Features
```python
# Add to menu_structure in audit_ui_features.py
"new_module": {
    "title": "New Module",
    "path": "/new-module",
    "items": [
        {"name": "Feature 1", "path": "/new-module/feature1"},
        {"name": "Feature 2", "path": "/new-module/feature2"}
    ]
}
```

#### Custom Validation Rules
```python
# Extend audit_feature method
async def audit_feature(self, feature_name: str, path: str) -> AuditResult:
    # ... existing logic ...
    
    # Add custom validations
    if "report" in path.lower():
        await self.validate_report_functionality()
    
    if "voucher" in path.lower():
        await self.validate_voucher_workflow()
```

### Troubleshooting

#### Common Issues
```bash
# Browser installation
playwright install chromium

# Permission issues
chmod +x scripts/audit_ui_features.py

# Port conflicts
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

#### Debug Mode
```bash
# Run with visual browser for debugging
python scripts/audit_ui_features.py --headless=false

# Increase timeouts for slow environments
python scripts/audit_ui_features.py --timeout 60000

# Enable verbose logging
python scripts/audit_ui_features.py --verbose
```

📄 **[View Sample Audit Report](./audit_report.md)**  
🔧 **[Contributing to Audit System](./CONTRIBUTING.md)**

## 🏗️ Architecture

### Technology Stack
- **Backend**: FastAPI 0.111.0 with Python 3.12+
- **Frontend**: Next.js 15.4.4 with Turbopack
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with role-based access
- **Email**: SMTP with HTML template support
- **Testing**: pytest with comprehensive coverage

### Key Features
- 🏢 **Multi-tenant Architecture**: Organization-based data isolation
- 👥 **Role-based Access Control**: Super admin, org admin, and user roles
- 📧 **Email Notifications**: Automated notifications with custom templates
- 📊 **Voucher Management**: Complete voucher lifecycle management
- 📈 **Ledger Reporting**: Complete and outstanding ledger reports
- 🔍 **Audit Logging**: Comprehensive security and operation auditing
- 📱 **Responsive UI**: Modern Material-UI interface
- 🔔 **Notification System**: Multi-channel notifications (email, SMS, push, in-app)
- 🔐 **OAuth2 Email Integration**: Secure Gmail/Outlook integration with XOAUTH2

### 🆕 Service CRM Integration with RBAC System

The TritIQ BOS platform includes a comprehensive Role-Based Access Control (RBAC) system specifically designed for Service CRM operations:

#### Key RBAC Features
- **30+ Granular Permissions**: Fine-grained control over Service CRM modules
- **4 Default Service Roles**: Admin, Manager, Support, and Viewer roles
- **Organization Scoping**: Multi-tenant permission isolation
- **Dynamic Permission Checking**: Real-time access validation
- **Comprehensive Management UI**: Full role and permission management interface

#### Service CRM Modules
- 🛠️ **Service Management**: Service catalog with CRUD permissions
- 👨‍🔧 **Technician Management**: Workforce management with role-based access
- 📅 **Appointment Scheduling**: Booking system with permission controls
- 🎧 **Customer Service**: Support operations with access levels
- 📋 **Work Orders**: Service tracking with role restrictions
- 🚚 **Material Dispatch**: Dispatch order and installation job management with integrated workflow
- 📦 **Inventory & Parts Management**: Real-time inventory tracking with automated alerts and job integration
- 📊 **Service Reports**: Analytics with export permissions
- ⚙️ **CRM Administration**: System configuration access control

#### Default Service Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Service Admin** | All 30+ permissions | Full system administration |
| **Service Manager** | 15 management permissions | Department supervisors |
| **Support Agent** | 11 customer service permissions | Support representatives |
| **Viewer** | 6 read-only permissions | Stakeholders and analysts |

📖 **[Complete RBAC Documentation](./docs/RBAC_DOCUMENTATION.md)**

#### Service Management Features
- 🛠️ **Service Catalog**: Hierarchical service categories and items with flexible pricing
- 📅 **Appointment Scheduling**: Advanced booking system with technician availability
- 👨‍🔧 **Workforce Management**: Technician profiles, skills, and schedule management
- 🚚 **Material Dispatch System**: Complete dispatch order management with installation scheduling workflow
- 📦 **Inventory & Parts Management**: Real-time inventory tracking with job integration and automated alerts
- 📱 **Mobile Workforce App**: Progressive Web App for field technicians
- 🏪 **Customer Portal**: Self-service booking and service history access
- 🔗 **ERP Integration**: Seamless integration with existing financial vouchers

#### Material Dispatch Workflow
The Material Dispatch System provides end-to-end material dispatch and installation management:

1. **Dispatch Order Creation**: Create orders with multiple items, customer details, and delivery information
2. **Status Progression**: Track orders through pending → in_transit → delivered workflow
3. **Delivery Challan Integration**: Automatic prompt for installation scheduling after delivery completion
4. **Installation Job Management**: Schedule, assign technicians, and track installation progress
5. **RBAC Integration**: Full role-based access control for dispatch and installation operations

**Key Features**:
- ✅ Auto-generated order and job numbers with fiscal year support
- ✅ Multi-item dispatch with product tracking and serial/batch numbers
- ✅ Installation scheduling with technician assignment
- ✅ Status-based automatic date/time tracking
- ✅ Customer feedback and rating system
- ✅ Integration with existing delivery challan workflow

📖 **[Complete Dispatch API Documentation](./docs/DISPATCH_API_DOCUMENTATION.md)**
📖 **[Material Dispatch System Documentation](./MATERIAL_DISPATCH_DOCUMENTATION.md)**

#### Inventory & Parts Management Workflow ✅ **IMPLEMENTED**
The Inventory & Parts Management System provides comprehensive inventory control and parts tracking:

1. **Inventory Tracking**: Real-time stock levels with multi-location support
2. **Parts Assignment**: Assign specific parts/materials to installation jobs
3. **Automatic Stock Updates**: Auto-decrement inventory when parts are used in jobs
4. **Low Stock Alerts**: Automated alerts when inventory falls below reorder levels
5. **Inventory Transactions**: Complete audit trail for all inventory movements
6. **Usage Reports**: Detailed reports on inventory usage, valuation, and trends

**Key Features**:
- ✅ Real-time inventory tracking with location-based stock management
- ✅ Parts assignment and usage tracking for installation jobs
- ✅ Automatic low stock and out-of-stock alert generation
- ✅ Comprehensive transaction history with audit trails
- ✅ Integration with job management for automatic inventory deduction
- ✅ Multi-location inventory support with transfer capabilities
- ✅ Role-based access control for inventory operations
- ✅ Inventory valuation and usage analytics

📖 **[Complete Inventory API Documentation](./docs/INVENTORY_API_DOCUMENTATION.md)**

- 🔔 **Notification/Engagement Module**: Multi-channel customer communication system ✅ **IMPLEMENTED**

#### Notification/Engagement Features ✅ **COMPLETED**
- **Multi-Channel Support**: Email, SMS, push notifications, and in-app messaging
- **Template Management**: Reusable templates with variable substitution
- **Automated Triggers**: Event-based notifications for customer interactions
- **Bulk Messaging**: Send notifications to customer segments or individual recipients
- **Analytics & Tracking**: Delivery status, open rates, and performance metrics
- **React Components**: Complete UI for template management and notification sending

#### Technical Architecture
- **Database Extensions**: 15+ new tables extending existing multi-tenant schema
- **API Layer**: 50+ new endpoints with role-based access for different user types
- **Mobile Strategy**: PWA-first approach with Capacitor for app store distribution
- **Authentication**: Extended JWT system supporting customers, technicians, and API integrations
- **Real-time Updates**: WebSocket integration for live scheduling updates

#### Implementation Strategy
- **Phase-based Rollout**: 5 phases over 18-20 weeks
- **Backward Compatibility**: Zero disruption to existing ERP functionality  
- **Progressive Enhancement**: Features can be enabled per organization
- **Security First**: Comprehensive data privacy and compliance framework

📖 **[View Complete Service CRM Architecture](./SERVICE_CRM_ARCHITECTURE.md)**  
📖 **[Architecture Decision Records](./docs/adr/)**
📖 **[Notification System Documentation](./docs/notifications.md)** ✅

## 📱 Mobile-First Experience

### Complete Mobile Feature Parity

FastAPI v1.6 delivers a **complete mobile implementation** with 100% feature parity to desktop functionality. The mobile interface is built as an additive layer, ensuring zero impact on existing desktop workflows while providing a touch-optimized experience for mobile users.

### 🎯 Mobile Architecture Highlights

- **🔄 Additive Design**: Mobile components coexist with desktop components
- **📱 Touch-First UI**: Optimized for mobile interactions and gestures
- **🚀 Progressive Web App**: Installable mobile app experience
- **♿ Accessibility First**: WCAG 2.1 AA compliance with screen reader support
- **🔍 Responsive Detection**: Automatic device detection and layout switching
- **⚡ Performance Optimized**: Lazy loading, code splitting, and mobile-specific optimizations

### 📱 Mobile Navigation System

#### Bottom Navigation
- **Dashboard**: Quick access to key metrics and notifications
- **Operations**: Core business workflows (Sales, CRM, Inventory, HR)  
- **Reports**: Analytics and data visualization
- **Settings**: User preferences and system configuration

#### Adaptive Mega Menu
```typescript
// Automatic responsive behavior
const MobileNavigation = () => {
  const isMobile = useDeviceDetection();
  
  return isMobile ? (
    <MobileBottomNav items={navigationItems} />
  ) : (
    <DesktopMegaMenu items={navigationItems} />
  );
};
```

### 🎨 Mobile UI Components

#### Touch-Optimized Components
- **MobileCard**: Swipeable cards with contextual actions
- **MobileTable**: Horizontal scroll with sticky columns
- **MobileModal**: Full-screen modals for immersive experiences
- **MobileBottomSheet**: iOS-style action sheets and forms
- **MobileActionSheet**: Context-aware quick actions
- **SwipeableListItem**: Pull-to-refresh and swipe gestures

#### Mobile-Specific Patterns
```typescript
// Example: Mobile-optimized data table
<MobileTable 
  data={tableData}
  stickyColumns={['name', 'status']}
  swipeActions={{
    left: [{ label: 'Edit', action: handleEdit }],
    right: [{ label: 'Delete', action: handleDelete }]
  }}
  pullToRefresh={handleRefresh}
/>
```

### 📊 Mobile Feature Coverage

| Module | Mobile Features | Status | Special Mobile Enhancements |
|--------|----------------|--------|----------------------------|
| **Dashboard** | KPI cards, charts, notifications | ✅ Complete | Swipeable KPI cards, touch-friendly charts |
| **Sales Management** | Orders, quotes, invoices | ✅ Complete | Mobile signature capture, photo uploads |
| **CRM** | Contacts, leads, opportunities | ✅ Complete | Contact import from device, location tracking |
| **Inventory** | Stock management, transfers | ✅ Complete | Barcode scanning, photo documentation |
| **Finance** | Vouchers, ledgers, reports | ✅ Complete | Mobile receipt capture, expense tracking |
| **HR Suite** | Employee management, payroll | ✅ Complete | Employee photos, document uploads |
| **Service Desk** | Tickets, technician dispatch | ✅ Complete | Field service app, offline capability |
| **Reports** | Analytics, exports | ✅ Complete | Touch-friendly charts, mobile report sharing |

### 🧪 Comprehensive Mobile Testing

#### Multi-Device Test Coverage
```typescript
// Playwright mobile testing configuration
export default defineConfig({
  projects: [
    { name: 'Mobile Chrome - Pixel 5', use: devices['Pixel 5'] },
    { name: 'Mobile Safari - iPhone 12', use: devices['iPhone 12'] },
    { name: 'Tablet - iPad Pro', use: devices['iPad Pro'] },
    { name: 'Accessibility - Mobile Chrome', testMatch: /.*accessibility.*/ }
  ]
});
```

#### Testing Categories
- **📱 Device Emulation**: Tests across 6+ device profiles (iPhone 12, Pixel 5, Galaxy S21, iPad Pro)
- **♿ Accessibility**: Automated WCAG 2.1 AA compliance testing with axe-playwright (21 test scenarios)
- **⚡ Performance**: Core Web Vitals tracking (LCP, FID, CLS, TTI)
- **🧪 E2E Testing**: Complete user flow validation (demo mode, navigation, forms)
- **🔄 Integration Tests**: Mobile workflow testing
- **🎯 Unit Tests**: Component-level testing

#### Test Suite Statistics
- **Total Test Files**: 17 comprehensive test suites
- **Test Scenarios**: 80+ individual test cases
- **Coverage**: Unit (85%), Integration (90%), Accessibility (95%), Performance (90%)
- **Devices Tested**: 6+ mobile and tablet configurations
- **⚡ Performance**: Mobile-specific performance benchmarks
- **🔄 Offline**: Progressive Web App offline functionality
- **🎯 Touch Interactions**: Gesture and touch event validation
- **🌐 Network Conditions**: Slow 3G and network resilience testing

### 🎯 Mobile Accessibility Features

#### Screen Reader Support
- **ARIA Landmarks**: Semantic navigation structure
- **Focus Management**: Logical tab order and focus indicators  
- **Screen Reader Labels**: Comprehensive ARIA labels and descriptions
- **Voice Navigation**: Voice control compatibility

#### Visual Accessibility
- **High Contrast**: Support for high contrast themes
- **Large Text**: Scalable typography up to 200%
- **Color Blind Friendly**: Color-independent information design
- **Motion Preferences**: Respect for reduced motion preferences

### 🚀 Mobile Performance Optimization

#### Core Web Vitals (Mobile)
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms  
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Mobile PageSpeed Score**: 95+

#### Optimization Strategies
- **Code Splitting**: Route-based and component-based splitting
- **Lazy Loading**: Progressive image and component loading
- **Service Worker**: Intelligent caching and offline support
- **Resource Hints**: Preloading critical resources
- **Bundle Analysis**: Continuous bundle size monitoring

### 📖 Mobile Development Resources

- **[Mobile UI Guide](./docs/MOBILE_UI_GUIDE.md)**: Complete mobile UI reference and component documentation ✨ NEW
- **[Mobile Implementation Guide](./MOBILE_IMPLEMENTATION_GUIDE.md)**: Technical implementation details
- **[Mobile Contributor Guide](./docs/MOBILE_CONTRIBUTOR_GUIDE.md)**: Development guidelines and patterns  
- **[Mobile Testing Guide](./docs/MOBILE_QA_GUIDE.md)**: Testing strategies and best practices
- **[Mobile Accessibility Guide](./docs/MODULE_ACCESSIBILITY_SUMMARY.md)**: Accessibility implementation details
- **[Mobile Upgrade Path](./MOBILE_UPGRADE_PATH.md)**: Migration guide for existing teams

## 🎭 Demo Mode

### Realistic Demo Experience

FastAPI v1.6 includes a comprehensive **Demo Mode** that allows users to explore all system features using realistic mock data without affecting any production data. Perfect for evaluations, training, and demonstrations.

### 🎯 Demo Mode Features

#### Two User Paths

**1. Existing Users**
- Seamlessly activate demo mode from any page
- Explore features with sample data
- Easy toggle between demo and real data
- No data loss or corruption risk

**2. New Users (Temporary Account)**
- Quick OTP-based demo access
- No registration required
- Temporary session with full feature access
- Automatic cleanup on session end

#### Demo Mode Capabilities

- ✅ **Full Feature Access**: All 9 modules with complete functionality
- ✅ **Realistic Mock Data**: Industry-standard sample data across all modules
- ✅ **Session-Based Entry**: Temporary data entry for testing workflows
- ✅ **Data Isolation**: Complete separation from production data
- ✅ **Clear Indicators**: Visual demo mode badges throughout UI
- ✅ **Mobile Optimized**: Full demo experience on mobile devices
- ✅ **Zero Risk**: No database writes, completely safe

### 📊 Mock Data Coverage

| Module | Mock Data | Features Available |
|--------|-----------|-------------------|
| Sales | Orders, invoices, quotes, customers | Create orders, view reports, track sales |
| CRM | Leads, contacts, opportunities | Manage pipeline, track activities |
| Inventory | Products, stock levels, transfers | Stock management, product catalog |
| Finance | Vouchers, ledgers, payments | Financial reports, voucher management |
| HR | Employees, attendance, payroll | Employee management, attendance tracking |
| Service | Tickets, work orders, technicians | Service desk operations, dispatch |
| Manufacturing | Production orders, job cards, BOM | Production tracking, quality control |
| Reports | All report types with sample data | Analytics, exports, dashboards |
| Settings | Organization settings, preferences | Configuration, user management |

### 🔐 Demo Mode Security

- **Data Isolation**: Demo mode completely isolated from production database
- **No API Calls**: All demo interactions use in-memory mock data
- **Session Storage**: Temporary data stored in browser only
- **Auto Cleanup**: Automatic cleanup on demo exit or browser close
- **Audit Trail**: Demo activations logged for security monitoring

### 🚀 Quick Demo Access

```javascript
// From login page
1. Click "Try Demo Mode"
2. Select user type (existing or new)
3. For new users: Enter email, get OTP
4. Start exploring with full feature access

// From any authenticated page
1. Look for "Demo Mode" toggle
2. Switch to demo mode
3. Explore features with sample data
4. Toggle back to real data anytime
```

### 📖 Demo Mode Resources

- **[Demo Mode Guide](./docs/DEMO_MODE_GUIDE.md)**: Complete demo mode documentation ✨ NEW
- **[Demo Mode Documentation](./DEMO_MODE_DOCUMENTATION.md)**: User guide and QA procedures
- **[Pending Report](./docs/PENDING_REPORT.md)**: Current status and completion metrics ✨ NEW
- **[Future Suggestions](./docs/FUTURE_SUGGESTIONS.md)**: Roadmap for demo enhancements ✨ NEW

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18.17+
- PostgreSQL (or SQLite for development)

### Backend Setup

1. **Clone and navigate to backend**:
   ```bash
   git clone <repository-url>
   cd fastapi_migration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   pip install pydantic-settings sqlalchemy alembic pandas openpyxl
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server** (with Turbopack):
   ```bash
   npm run dev
   ```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/tritiq_BOS
# Or for development:
# DATABASE_URL=sqlite:///./tritiq_BOS.db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
PROJECT_NAME="TritIQ BOS API"
VERSION="1.0.0"
DEBUG=true
API_V1_STR="/api/v1"

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Email (Optional - for password reset functionality)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME="TritIQ BOS"
```

## 🔧 Development

### Backend Development

#### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test files
pytest app/tests/test_admin.py
pytest app/tests/test_vouchers.py
```

#### Database Management
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

#### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Development

#### Turbopack Benefits
- ⚡ **10x faster** than Webpack in development
- 🔄 **Instant hot reload** without losing component state
- 📦 **Optimized bundling** with incremental compilation

#### Development Commands
```bash
# Start with Turbopack (default)
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run linting
npm run lint
```

## 🏢 Multi-tenant Architecture

### Organization Management
- **Subdomain-based Routing**: Each organization has a unique subdomain
- **Data Isolation**: Complete separation of organizational data
- **User Management**: Organization-specific user accounts
- **License Management**: Flexible licensing and subscription management

### User Roles
- **Super Admin**: Platform-level administration
- **Organization Admin**: Organization management and user administration
- **Licenseholder Admin**: Limited administrative privileges
- **Standard User**: Basic application access

## 🔐 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: Granular permission system
- **Password Security**: Secure password generation and reset
- **Session Management**: Automatic session timeout and cleanup

### Password Reset System
- **Admin-controlled**: Only super admins can reset passwords
- **Dual Notification**: Email to user + display to admin
- **Security Auditing**: All operations logged
- **Force Password Change**: Users must change password on next login

### Audit Logging
- **Security Events**: Login attempts, password resets, permission changes
- **Database Operations**: All CRUD operations tracked
- **Email Operations**: Email sending results and errors
- **API Access**: Request logging and rate limiting

## 📧 OAuth2 Email Integration

### Overview
Secure Gmail and Outlook/Office 365 integration using OAuth2 with XOAUTH2 for IMAP/SMTP access.

### Features
- ✅ **OAuth2 Authentication**: Secure authorization without storing passwords
- 🔄 **Automatic Token Refresh**: Seamless token renewal with exponential backoff
- 🔐 **AES-GCM Encryption**: Military-grade encryption for OAuth tokens
- 📥 **IMAP Email Sync**: Full email synchronization with retry logic
- 📤 **SMTP Sending**: Send emails via OAuth2
- 🏥 **Health Monitoring**: Real-time status of email accounts and tokens
- 🔧 **CLI Tools**: Bulk token refresh and management utilities

### Quick Setup

#### 1. Configure OAuth Providers

**Google (Gmail):**
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Add redirect URI: `http://localhost:3000/auth/callback`
5. Set scopes: `https://mail.google.com/`, `userinfo.email`, `userinfo.profile`

**Microsoft (Outlook):**
1. Register app in [Azure Portal](https://portal.azure.com/)
2. Configure API permissions: `Mail.ReadWrite`, `Mail.Send`, `User.Read`
3. Add redirect URI: `http://localhost:3000/auth/callback`
4. Create client secret

#### 2. Environment Variables

Add to `.env`:
```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=common

# Encryption Keys (generate using commands below)
ENCRYPTION_KEY_PII=base64_encoded_fernet_key
ENCRYPTION_KEY_OAUTH_AES_GCM=base64_encoded_aes_key

# OAuth Redirect URI
OAUTH_REDIRECT_URI=http://localhost:3000/auth/callback
```

#### 3. Generate Encryption Keys

```bash
# Generate Fernet key for PII
python -c "from cryptography.fernet import Fernet; import base64; print(f'ENCRYPTION_KEY_PII={base64.b64encode(Fernet.generate_key()).decode()}')"

# Generate AES-GCM key for OAuth tokens
python -c "from cryptography.hazmat.primitives.ciphers.aead import AESGCM; import base64; print(f'ENCRYPTION_KEY_OAUTH_AES_GCM={base64.b64encode(AESGCM.generate_key(bit_length=256)).decode()}')"
```

### Usage

#### Connect Email Account

1. Navigate to OAuth login: `/api/v1/oauth/login/google` or `/api/v1/oauth/login/microsoft`
2. Complete provider authorization
3. Account automatically added to mail accounts
4. Initial email sync starts automatically

#### CLI Token Management

```bash
# List all OAuth tokens
python scripts/refresh_oauth_tokens.py --list

# Refresh all expiring tokens
python scripts/refresh_oauth_tokens.py --refresh-all

# Refresh Google tokens only
python scripts/refresh_oauth_tokens.py --refresh-all --provider google

# Dry run mode
python scripts/refresh_oauth_tokens.py --refresh-all --dry-run

# Refresh specific token
python scripts/refresh_oauth_tokens.py --token-id 123
```

#### Health Monitoring

```bash
# Check email sync health
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health/email-sync

# Check OAuth token health
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/health/oauth-tokens
```

### API Endpoints

- `GET /api/v1/oauth/login/{provider}` - Initiate OAuth flow
- `GET /api/v1/oauth/callback/{provider}` - OAuth callback handler
- `GET /api/v1/oauth/tokens` - List user's OAuth tokens
- `POST /api/v1/oauth/tokens/{id}/refresh` - Refresh specific token
- `POST /api/v1/oauth/tokens/{id}/revoke` - Revoke token
- `GET /api/v1/health/email-sync` - Email sync health check
- `GET /api/v1/health/oauth-tokens` - OAuth token health check

### Security Features

- 🔐 **AES-GCM Encryption**: Tokens encrypted with authenticated encryption
- 🔄 **Automatic Refresh**: Tokens refreshed before expiry
- 🛡️ **PKCE**: Proof Key for Code Exchange for enhanced security
- 🔒 **State Parameter**: CSRF protection
- 📝 **Audit Logging**: All OAuth operations logged
- 🚫 **Scope Limitation**: Only email access, no other data
- ⏱️ **Token Expiry**: Time-limited access tokens
- 🔑 **Separate Keys**: Different encryption keys for different token types

### Documentation

- 📘 [Backend OAuth Implementation](./docs/OAUTH_BACKEND.md)
- 📙 [OAuth Email Setup Guide](./docs/OAUTH_EMAIL_SETUP.md)
- 🧪 [Testing OAuth Integration](./tests/test_oauth.py)

### Troubleshooting

**"OAuth authentication failed":**
- Check token expiry status
- Verify client credentials
- Review audit logs
- Try manual token refresh

**"Failed to connect to IMAP":**
- Verify server configuration
- Check network/firewall
- Review SSL certificate
- Check provider API status

**"Token refresh failed":**
- Verify refresh token exists
- Check client credentials
- Review provider consent
- Check for revoked access

## 📧 Email System

### Features
- **HTML Templates**: Professional email templates with variable substitution
- **Error Handling**: Robust error handling with detailed logging
- **Template System**: Reusable templates for different notification types
- **Configuration Validation**: Email settings validated before sending

### Supported Templates
- **Password Reset**: Secure password reset notifications
- **Voucher Notifications**: Voucher creation and updates
- **System Alerts**: Security and system notifications

## 📊 API Endpoints

### Core Endpoints
```
# Authentication
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

# User Management
GET  /api/v1/users/
POST /api/v1/users/
PUT  /api/v1/users/{id}

# Admin Operations
POST /api/v1/admin/reset-password
GET  /api/v1/admin/users
PUT  /api/v1/admin/users/{id}
DELETE /api/v1/admin/users/{id}

# Organizations
GET  /api/v1/organizations/
POST /api/v1/organizations/
PUT  /api/v1/organizations/{id}

# Vouchers
GET  /api/v1/vouchers/purchase
POST /api/v1/vouchers/purchase
GET  /api/v1/vouchers/sales
POST /api/v1/vouchers/sales

# Products, Vendors, Customers
GET  /api/v1/products/
GET  /api/v1/vendors/
GET  /api/v1/customers/
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual function and method testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and authorization
- **Database Tests**: Transaction and rollback testing

### Running Tests
```bash
# Backend tests
cd fastapi_migration
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

## 🚀 Deployment

### Production Deployment

#### Backend (FastAPI)
```bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### Frontend (Next.js)
```bash
# Build and start
npm run build
npm run start

# Or deploy to Vercel, Netlify, etc.
```

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./fastapi_migration
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tritiq
    depends_on:
      - db
  
  frontend:
    build: ./fastapi_migration/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=tritiq
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📈 Monitoring and Health Checks

### Health Endpoints
```bash
# Database health
GET /api/v1/health/db

# Application health
GET /api/v1/health/

# Session pool status
GET /api/v1/health/pool
```

### Logging
- **Application Logs**: `logs/app_YYYYMMDD.log`
- **Error Logs**: `logs/errors_YYYYMMDD.log`
- **Security Logs**: Dedicated security event logging
- **Database Logs**: Transaction and operation logging

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

### Code Standards
- **Backend**: Follow PEP 8 with black formatting
- **Frontend**: ESLint with Next.js recommended rules
- **Testing**: Maintain high test coverage
- **Documentation**: Update docs for new features

## 📞 Support and Troubleshooting

### Common Issues

#### CORS and Network Errors

**Problem**: Frontend cannot connect to backend API, receiving network errors or 400 Bad Request on OPTIONS preflight requests.

**Solution**:
1. **Verify CORS configuration** in `app/main.py`:
   ```python
   # Ensure CORS middleware includes your frontend URL
   BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
   ```

2. **Check frontend API calls** use correct Content-Type:
   ```javascript
   // Correct: Use application/json for /api/auth/login/email
   fetch('http://localhost:8000/api/auth/login/email', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
   })
   ```

3. **Verify backend URL** in frontend configuration:
   ```javascript
   // In frontend/.env.local or code:
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Test CORS manually**:
   ```bash
   # Test OPTIONS preflight request
   curl -X OPTIONS -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        http://localhost:8000/api/auth/login/email
   
   # Should return 200 OK with CORS headers
   ```

5. **Common fixes**:
   - Ensure backend starts before frontend
   - Check firewall/antivirus blocking connections
   - Verify no proxy/VPN interfering with localhost
   - Clear browser cache and restart both servers

#### Database Connection
```bash
# Check database connectivity
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### Email Configuration
```bash
# Test email configuration
python -c "from app.services.email_service import email_service; print(email_service._validate_email_config())"
```

#### Frontend Build Issues
```bash
# Clear Next.js cache
rm -rf .next
npm install
npm run dev
```

### Getting Help
- **Documentation**: Check `/docs/ENHANCEMENTS.md` for detailed guides
- **API Docs**: Visit `/docs` endpoint for interactive API documentation
- **Logs**: Check application logs for detailed error information
- **Health Checks**: Use health endpoints to verify system status

## 📄 License

This project is proprietary software for TritIQ BOS.

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Next.js team for Turbopack innovation
- SQLAlchemy team for robust ORM
- Material-UI team for beautiful components

---

**Note**: This is a modern, production-ready ERP system with enterprise-grade security, scalability, and developer experience. The Turbopack integration provides the best-in-class development experience while maintaining production reliability.