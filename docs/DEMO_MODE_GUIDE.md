# Demo Mode Guide - FastAPI v1.6

## Overview

The Demo Mode feature in FastAPI v1.6 TritIQ Business Suite provides a comprehensive, realistic demonstration environment where users can explore all system features using realistic mock data without affecting any real business data. This guide covers implementation, usage, testing, and best practices for demo mode.

## Table of Contents

- [Architecture](#architecture)
- [User Flows](#user-flows)
- [Mock Data System](#mock-data-system)
- [Session Management](#session-management)
- [Demo Mode Indicators](#demo-mode-indicators)
- [Module Coverage](#module-coverage)
- [Testing](#testing)
- [Implementation Details](#implementation-details)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Architecture

### Design Principles

1. **Zero Production Impact**: Demo mode operates completely isolated from real data
2. **Realistic Experience**: Mock data mirrors real-world scenarios
3. **Session-Based**: Temporary data exists only during user session
4. **Feature Parity**: All features available in demo mode match production
5. **Clear Indicators**: Users always know they're in demo mode
6. **Easy Exit**: Simple, clear path to exit demo mode

### System Architecture

```
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Demo Indicator │  │  Toggle Control │  │
│  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Demo Mode Controller                │
│  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Session Mgr │  │ Mock Data Provider   │ │
│  └─────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│ Session Store│        │  Mock Data   │
│  (Browser)   │        │  Repository  │
└──────────────┘        └──────────────┘
```

## User Flows

### Flow 1: Existing User Demo Mode

**Use Case**: Registered users want to explore demo features

**Steps:**
1. User clicks "Try Demo Mode" button on login page or dashboard
2. System presents demo mode selection dialog
3. User selects "I have an existing account"
4. Dialog closes, user proceeds to login
5. After successful login, system detects `pendingDemoMode` flag
6. System activates demo mode for the session
7. User redirected to `/demo` page
8. Demo mode active with all features using mock data

**Session Details:**
- Session Type: Authenticated user session with demo flag
- Data Storage: LocalStorage with `demoMode=true`
- Duration: Until user manually exits demo mode
- Exit Behavior: Returns to normal authenticated dashboard

### Flow 2: New User Demo Mode (Temporary Account)

**Use Case**: New users want to try the system without registering

**Steps:**
1. User clicks "Try Demo Mode" button on login page
2. System presents demo mode selection dialog
3. User selects "I'm new and want to try"
4. User fills in demo registration form:
   - Full Name
   - Email Address
   - Phone Number
   - Company Name
5. System sends 6-digit OTP to provided email
6. User enters OTP code
7. System validates OTP and creates temporary session
8. User redirected to `/demo` page
9. Demo mode active with temporary account

**Session Details:**
- Session Type: Temporary demo session (not a real user account)
- Data Storage: LocalStorage with `demoMode=true` and `isDemoTempUser=true`
- Duration: Until browser close or manual session end
- Exit Behavior: Clears all temporary data, redirects to login
- Security: No actual database user created, session-only authentication

### Flow 3: Demo Mode from User Management Page

**Use Case**: Admin wants to demonstrate features to stakeholders

**Steps:**
1. Admin navigates to User Management page (`/admin/users`)
2. Admin clicks "Try Demo Mode" button in page header
3. System presents demo mode selection dialog
4. Admin proceeds with either Flow 1 or Flow 2
5. Demo mode activated

## Mock Data System

### Data Categories

#### 1. Master Data

**Vendors**
```javascript
{
  id: 1,
  name: "ABC Suppliers",
  contact: "John Doe",
  email: "contact@abcsuppliers.com",
  phone: "+91-9876543210",
  address: "123 Industrial Area, Mumbai",
  gst: "27AAAAA1234A1Z5",
  status: "active",
  credit_limit: 500000,
  outstanding: 125000
}
```

**Customers**
```javascript
{
  id: 1,
  name: "Tech Solutions Ltd",
  contact: "Jane Smith",
  email: "jane@techsolutions.com",
  phone: "+91-9876543211",
  industry: "IT Services",
  gst: "27BBBBB5678B1Z5",
  credit_days: 30,
  status: "active",
  total_orders: 45,
  lifetime_value: 2500000
}
```

**Products**
```javascript
{
  id: 1,
  code: "PROD-001",
  name: "Industrial Motor 5HP",
  category: "Motors & Drives",
  hsn_code: "85015100",
  unit: "Piece",
  purchase_price: 12500,
  selling_price: 15750,
  stock_quantity: 25,
  reorder_level: 5,
  gst_rate: 18
}
```

#### 2. Transaction Data

**Purchase Vouchers**
```javascript
{
  id: 1,
  voucher_number: "PV-2024-001",
  date: "2024-01-15",
  vendor_id: 1,
  vendor_name: "ABC Suppliers",
  items: [
    {
      product: "Industrial Motor 5HP",
      quantity: 10,
      rate: 12500,
      gst: 18,
      amount: 147500
    }
  ],
  subtotal: 125000,
  gst_amount: 22500,
  total_amount: 147500,
  status: "confirmed",
  payment_status: "partial",
  paid_amount: 100000,
  due_amount: 47500
}
```

**Sales Vouchers**
```javascript
{
  id: 1,
  voucher_number: "SV-2024-001",
  date: "2024-01-15",
  customer_id: 1,
  customer_name: "Tech Solutions Ltd",
  items: [
    {
      product: "Industrial Motor 5HP",
      quantity: 5,
      rate: 15750,
      discount: 5,
      gst: 18,
      amount: 87806.25
    }
  ],
  subtotal: 74812.5,
  discount_amount: 3937.5,
  gst_amount: 13468.75,
  total_amount: 87806.25,
  status: "confirmed",
  payment_status: "paid",
  delivery_status: "delivered"
}
```

#### 3. CRM Data

**Leads**
```javascript
{
  id: 1,
  name: "Global Manufacturing Inc",
  contact: "Robert Johnson",
  email: "robert@globalmanuf.com",
  phone: "+91-9876543212",
  source: "Website",
  status: "qualified",
  priority: "high",
  expected_value: 500000,
  probability: 75,
  next_action: "Schedule demo call",
  assigned_to: "Sales Team",
  created_date: "2024-01-10"
}
```

**Opportunities**
```javascript
{
  id: 1,
  name: "Enterprise ERP Implementation",
  account: "Tech Solutions Ltd",
  value: 1500000,
  stage: "proposal",
  probability: 60,
  close_date: "2024-03-31",
  products: ["ERP License", "Implementation Services", "Training"],
  competitors: ["SAP", "Oracle"],
  next_steps: "Present final proposal",
  owner: "John Sales Manager"
}
```

#### 4. Service CRM Data

**Service Requests**
```javascript
{
  id: 1,
  ticket_number: "SR-2024-001",
  customer: "Tech Solutions Ltd",
  service_type: "Installation",
  priority: "high",
  status: "in_progress",
  assigned_technician: "Mike Tech",
  scheduled_date: "2024-01-20",
  description: "Install new motor at factory unit 3",
  location: "Factory Unit 3, Pune",
  estimated_duration: "4 hours",
  parts_required: ["Installation Kit", "Mounting Brackets"]
}
```

**Work Orders**
```javascript
{
  id: 1,
  work_order_number: "WO-2024-001",
  service_request: "SR-2024-001",
  technician: "Mike Tech",
  status: "scheduled",
  scheduled_date: "2024-01-20",
  start_time: "09:00",
  estimated_hours: 4,
  tasks: [
    "Inspect installation site",
    "Mount motor on base",
    "Connect electrical wiring",
    "Test operation",
    "Customer sign-off"
  ],
  materials: [
    { item: "Installation Kit", quantity: 1, allocated: true }
  ]
}
```

#### 5. Manufacturing Data

**Production Orders**
```javascript
{
  id: 1,
  order_number: "MO-2024-001",
  product: "Custom Assembly Unit",
  quantity: 50,
  status: "in_progress",
  start_date: "2024-01-15",
  expected_completion: "2024-01-30",
  bom_items: [
    { component: "Base Plate", required: 50, allocated: 50 },
    { component: "Motor Assembly", required: 50, allocated: 48 },
    { component: "Control Panel", required: 50, allocated: 50 }
  ],
  completed_quantity: 25,
  progress: 50,
  quality_checks: "Passed"
}
```

**Job Cards**
```javascript
{
  id: 1,
  job_number: "JC-2024-001",
  production_order: "MO-2024-001",
  operation: "Assembly",
  machine: "Assembly Line 1",
  operator: "Worker 1",
  status: "active",
  start_time: "2024-01-15 08:00",
  planned_hours: 4,
  actual_hours: 3.5,
  quantity_completed: 25
}
```

#### 6. HR Data

**Employees**
```javascript
{
  id: 1,
  employee_code: "EMP-001",
  name: "John Doe",
  department: "Sales",
  designation: "Sales Manager",
  email: "john.doe@company.com",
  phone: "+91-9876543213",
  joining_date: "2020-01-15",
  status: "active",
  reporting_to: "Director Sales",
  salary: 75000,
  leave_balance: 12
}
```

**Attendance**
```javascript
{
  id: 1,
  employee_code: "EMP-001",
  date: "2024-01-15",
  check_in: "09:00",
  check_out: "18:00",
  hours_worked: 9,
  status: "present",
  overtime: 0
}
```

#### 7. Analytics Data

**Sales Metrics**
```javascript
{
  period: "January 2024",
  total_revenue: 2500000,
  total_orders: 45,
  average_order_value: 55556,
  new_customers: 8,
  repeat_customers: 15,
  top_products: [
    { product: "Industrial Motor 5HP", revenue: 450000, units: 30 },
    { product: "Control Panel", revenue: 380000, units: 25 }
  ],
  top_customers: [
    { customer: "Tech Solutions Ltd", revenue: 650000 },
    { customer: "Global Corp", revenue: 520000 }
  ]
}
```

### Mock Data Management

**Loading Mock Data**
```typescript
// services/demoDataService.ts
export class DemoDataService {
  private static instance: DemoDataService;
  private mockData: Map<string, any[]>;

  static getInstance() {
    if (!DemoDataService.instance) {
      DemoDataService.instance = new DemoDataService();
    }
    return DemoDataService.instance;
  }

  async loadMockData(module: string) {
    // Load from static JSON files
    const data = await import(`../data/demo/${module}.json`);
    this.mockData.set(module, data.default);
    return data.default;
  }

  getMockData(module: string, filters?: any) {
    const data = this.mockData.get(module) || [];
    if (filters) {
      return this.applyFilters(data, filters);
    }
    return data;
  }
}
```

## Session Management

### Session Storage

**LocalStorage Keys:**
```javascript
{
  "demoMode": "true",                    // Demo mode active flag
  "isDemoTempUser": "true",             // Temporary user flag
  "pendingDemoMode": "true",            // Pending demo activation after login
  "demoSessionData": {                  // Session-specific data
    "email": "user@example.com",
    "companyName": "Demo Company",
    "sessionStart": "2024-01-15T10:00:00Z",
    "lastActivity": "2024-01-15T11:30:00Z"
  },
  "demoTempData": {                     // Temporary user-entered data
    "customOrders": [...],
    "notes": [...],
    "preferences": {...}
  }
}
```

### Session Lifecycle

**Initialization**
```typescript
// Check and initialize demo mode on app load
useEffect(() => {
  const initializeDemoMode = () => {
    const demoMode = localStorage.getItem('demoMode') === 'true';
    const isDemoTempUser = localStorage.getItem('isDemoTempUser') === 'true';
    
    if (demoMode) {
      setIsDemoActive(true);
      setIsTempUser(isDemoTempUser);
      
      // Load demo session data
      const sessionData = JSON.parse(
        localStorage.getItem('demoSessionData') || '{}'
      );
      
      // Update last activity
      sessionData.lastActivity = new Date().toISOString();
      localStorage.setItem('demoSessionData', JSON.stringify(sessionData));
    }
  };
  
  initializeDemoMode();
}, []);
```

**Activity Tracking**
```typescript
// Track user activity to maintain session
const updateLastActivity = () => {
  if (isDemoActive) {
    const sessionData = JSON.parse(
      localStorage.getItem('demoSessionData') || '{}'
    );
    sessionData.lastActivity = new Date().toISOString();
    localStorage.setItem('demoSessionData', JSON.stringify(sessionData));
  }
};

// Update on any user interaction
useEffect(() => {
  const events = ['click', 'keypress', 'scroll', 'touchstart'];
  events.forEach(event => {
    window.addEventListener(event, updateLastActivity);
  });
  
  return () => {
    events.forEach(event => {
      window.removeEventListener(event, updateLastActivity);
    });
  };
}, [isDemoActive]);
```

**Session Termination**
```typescript
const endDemoSession = () => {
  // Clear all demo-related data
  localStorage.removeItem('demoMode');
  localStorage.removeItem('isDemoTempUser');
  localStorage.removeItem('pendingDemoMode');
  localStorage.removeItem('demoSessionData');
  localStorage.removeItem('demoTempData');
  
  // For temporary users, clear auth data too
  if (isTempUser) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('organization_id');
  }
  
  // Redirect appropriately
  if (isTempUser) {
    router.push('/login');
  } else {
    router.push('/dashboard');
  }
};
```

## Demo Mode Indicators

### Global Demo Alert

**Component: DemoModeAlert**
```typescript
<Alert 
  severity="info" 
  sx={{ 
    position: 'sticky', 
    top: 0, 
    zIndex: 1100,
    borderRadius: 0,
    mb: 2
  }}
  action={
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <FormControlLabel
        control={
          <Switch
            checked={demoMode}
            onChange={handleToggleDemo}
            color="primary"
          />
        }
        label="Demo Mode"
      />
      <Button
        color="inherit"
        size="small"
        onClick={handleExitDemo}
        startIcon={<ExitToApp />}
      >
        {isDemoTempUser ? "End Session" : "Exit Demo"}
      </Button>
    </Box>
  }
>
  <Typography variant="h6" component="div">
    🎭 Demo Mode Active {isDemoTempUser && "(Temporary User)"}
  </Typography>
  <Typography variant="body2">
    Viewing sample data. All interactions are simulated.
  </Typography>
</Alert>
```

### Page-Level Indicators

**Data Table Watermark**
```typescript
<Box sx={{ position: 'relative' }}>
  <DataGrid ... />
  {demoMode && (
    <Chip
      label="DEMO DATA"
      size="small"
      sx={{
        position: 'absolute',
        top: 8,
        right: 8,
        opacity: 0.7
      }}
    />
  )}
</Box>
```

**Chart Watermark**
```typescript
<Box sx={{ position: 'relative' }}>
  <Chart ... />
  {demoMode && (
    <Typography
      variant="caption"
      sx={{
        position: 'absolute',
        bottom: 8,
        right: 8,
        opacity: 0.5,
        fontStyle: 'italic'
      }}
    >
      Sample Data
    </Typography>
  )}
</Box>
```

### Mobile Demo Indicators

**Bottom Badge**
```typescript
{demoMode && isMobile && (
  <Chip
    label="🎭 DEMO"
    size="small"
    color="info"
    sx={{
      position: 'fixed',
      bottom: 70, // Above bottom nav
      right: 16,
      zIndex: 1000,
      boxShadow: 2
    }}
  />
)}
```

## Module Coverage

### ✅ Fully Implemented Modules

#### Dashboard
- **Mock Data**: KPI cards, activity feed, charts
- **Features**: All widgets functional with demo data
- **User Entry**: None (read-only)
- **Indicators**: Demo mode alert, chart watermarks

#### Sales Management
- **Mock Data**: Orders, invoices, quotes, customers
- **Features**: Create/view/edit orders (session-based)
- **User Entry**: Session-based order creation
- **Indicators**: Form headers, data table badges

#### CRM
- **Mock Data**: Leads, contacts, opportunities, activities
- **Features**: Lead management, opportunity pipeline
- **User Entry**: Session-based lead/contact creation
- **Indicators**: Demo badges on cards

#### Inventory
- **Mock Data**: Products, stock levels, transfers
- **Features**: Stock viewing, transfer requests
- **User Entry**: Session-based adjustments
- **Indicators**: Stock badges, watermarks

#### Finance
- **Mock Data**: Vouchers, ledgers, payments
- **Features**: Voucher viewing, payment recording
- **User Entry**: Session-based voucher notes
- **Indicators**: Voucher form headers

#### HR
- **Mock Data**: Employees, attendance, leave, payroll
- **Features**: Employee viewing, attendance tracking
- **User Entry**: Session-based leave requests
- **Indicators**: Employee card badges

#### Service Desk
- **Mock Data**: Tickets, work orders, technicians
- **Features**: Ticket viewing, status updates
- **User Entry**: Session-based ticket notes
- **Indicators**: Ticket badges, status indicators

#### Manufacturing
- **Mock Data**: Production orders, job cards, BOM
- **Features**: Order viewing, progress tracking
- **User Entry**: Session-based production notes
- **Indicators**: Production order badges

#### Reports
- **Mock Data**: All report types with sample data
- **Features**: Report viewing, export (sample data)
- **User Entry**: Custom report parameters
- **Indicators**: Report header badges

### Session-Based User Entry

**Implementation Pattern**
```typescript
const handleDemoDataEntry = async (newData: any) => {
  if (!isDemoMode) {
    // Regular API call for real users
    return await api.post('/endpoint', newData);
  }
  
  // For demo mode, store in session
  const tempData = JSON.parse(
    localStorage.getItem('demoTempData') || '{}'
  );
  
  const module = 'orders'; // or relevant module
  if (!tempData[module]) {
    tempData[module] = [];
  }
  
  // Add temporary entry with generated ID
  newData.id = `demo_${Date.now()}`;
  newData._isTemporary = true;
  tempData[module].push(newData);
  
  localStorage.setItem('demoTempData', JSON.stringify(tempData));
  
  // Return mock response
  return { success: true, data: newData };
};
```

**Retrieving Demo Data with Temp Entries**
```typescript
const fetchDemoData = (module: string) => {
  // Get base mock data
  const mockData = DemoDataService.getInstance().getMockData(module);
  
  // Get temporary user entries
  const tempData = JSON.parse(
    localStorage.getItem('demoTempData') || '{}'
  );
  
  const userEntries = tempData[module] || [];
  
  // Merge and return
  return [...mockData, ...userEntries];
};
```

## Testing

### Demo Mode Test Cases

#### 1. Access and Activation
```typescript
describe('Demo Mode Access', () => {
  test('should show demo mode button on login page', async () => {
    const { getByText } = render(<LoginPage />);
    expect(getByText('Try Demo Mode')).toBeInTheDocument();
  });
  
  test('should open demo selection dialog on button click', async () => {
    const { getByText, getByRole } = render(<LoginPage />);
    fireEvent.click(getByText('Try Demo Mode'));
    expect(getByRole('dialog')).toBeInTheDocument();
  });
});
```

#### 2. Session Management
```typescript
describe('Demo Session', () => {
  test('should set demo mode flag in localStorage', () => {
    activateDemoMode();
    expect(localStorage.getItem('demoMode')).toBe('true');
  });
  
  test('should maintain demo session across page navigation', () => {
    activateDemoMode();
    navigateTo('/mobile/dashboard');
    expect(isDemoModeActive()).toBe(true);
  });
  
  test('should clear demo data on session end', () => {
    activateDemoMode();
    endDemoSession();
    expect(localStorage.getItem('demoMode')).toBeNull();
  });
});
```

#### 3. Data Isolation
```typescript
describe('Demo Data Isolation', () => {
  test('should not persist demo data to database', async () => {
    activateDemoMode();
    await createDemoOrder(sampleOrder);
    
    // Verify no API call made
    expect(mockApiPost).not.toHaveBeenCalled();
    
    // Verify data in session storage only
    const tempData = JSON.parse(localStorage.getItem('demoTempData'));
    expect(tempData.orders).toHaveLength(1);
  });
});
```

#### 4. UI Indicators
```typescript
describe('Demo Indicators', () => {
  test('should show demo alert banner', () => {
    activateDemoMode();
    const { getByText } = render(<Dashboard />);
    expect(getByText(/Demo Mode Active/i)).toBeInTheDocument();
  });
  
  test('should show demo badges on data tables', () => {
    activateDemoMode();
    const { getByText } = render(<OrdersList />);
    expect(getByText('DEMO DATA')).toBeInTheDocument();
  });
});
```

### E2E Demo Mode Tests

```typescript
// tests/mobile/integration/demo-mode.spec.ts
import { test, expect, devices } from '@playwright/test';

test.describe('Demo Mode E2E', () => {
  test('Complete new user demo flow on mobile', async ({ page }) => {
    // Configure mobile viewport
    await page.setViewportSize(devices['iPhone 12'].viewport);
    
    // Navigate to login
    await page.goto('/login');
    
    // Click demo button
    await page.click('text=Try Demo Mode');
    
    // Select new user
    await page.click('text=I\'m new and want to try');
    
    // Fill demo registration
    await page.fill('[name="fullName"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="phoneNumber"]', '+1234567890');
    await page.fill('[name="companyName"]', 'Test Company');
    
    // Submit
    await page.click('text=Continue');
    
    // Enter OTP (any 6 digits in demo)
    await page.fill('[name="otp"]', '123456');
    await page.click('text=Verify');
    
    // Should redirect to demo page
    await expect(page).toHaveURL('/demo');
    
    // Should show demo indicator
    await expect(page.locator('text=Demo Mode Active')).toBeVisible();
    
    // Should show temporary user warning
    await expect(page.locator('text=Temporary User')).toBeVisible();
    
    // Test navigation in demo mode
    await page.click('text=Sales');
    await expect(page).toHaveURL(/\/mobile\/sales/);
    
    // Should still show demo indicator
    await expect(page.locator('text=DEMO')).toBeVisible();
    
    // Test session data entry
    await page.click('text=Create Order');
    await page.fill('[name="customerName"]', 'Demo Customer');
    await page.click('text=Save');
    
    // Verify in session storage (not persisted)
    const demoTempData = await page.evaluate(() => {
      return localStorage.getItem('demoTempData');
    });
    expect(demoTempData).toBeTruthy();
    
    // Exit demo
    await page.click('text=End Session');
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
    
    // Demo data should be cleared
    const clearedData = await page.evaluate(() => {
      return localStorage.getItem('demoMode');
    });
    expect(clearedData).toBeNull();
  });
});
```

## Implementation Details

### Key Files

```
frontend/src/
├── components/
│   └── DemoModeDialog.tsx          # Demo mode entry dialog
├── pages/
│   └── demo.tsx                     # Main demo dashboard
├── hooks/
│   └── useDemoMode.ts              # Demo mode state management
├── services/
│   └── demoDataService.ts          # Mock data provider
├── data/
│   └── demo/                        # Mock data JSON files
│       ├── vendors.json
│       ├── customers.json
│       ├── products.json
│       ├── orders.json
│       └── ...
└── utils/
    └── demoHelpers.ts              # Demo utility functions
```

### Custom Hook: useDemoMode

```typescript
// hooks/useDemoMode.ts
export const useDemoMode = () => {
  const [isDemoActive, setIsDemoActive] = useState(false);
  const [isTempUser, setIsTempUser] = useState(false);
  const [sessionData, setSessionData] = useState(null);

  useEffect(() => {
    const demoMode = localStorage.getItem('demoMode') === 'true';
    const tempUser = localStorage.getItem('isDemoTempUser') === 'true';
    
    setIsDemoActive(demoMode);
    setIsTempUser(tempUser);
    
    if (demoMode) {
      const data = JSON.parse(
        localStorage.getItem('demoSessionData') || '{}'
      );
      setSessionData(data);
    }
  }, []);

  const activateDemoMode = (options: DemoModeOptions) => {
    localStorage.setItem('demoMode', 'true');
    if (options.isTempUser) {
      localStorage.setItem('isDemoTempUser', 'true');
    }
    
    const sessionData = {
      email: options.email || '',
      companyName: options.companyName || '',
      sessionStart: new Date().toISOString(),
      lastActivity: new Date().toISOString()
    };
    
    localStorage.setItem('demoSessionData', JSON.stringify(sessionData));
    setIsDemoActive(true);
    setIsTempUser(options.isTempUser || false);
  };

  const deactivateDemoMode = () => {
    localStorage.removeItem('demoMode');
    localStorage.removeItem('isDemoTempUser');
    localStorage.removeItem('demoSessionData');
    localStorage.removeItem('demoTempData');
    
    if (isTempUser) {
      localStorage.removeItem('access_token');
    }
    
    setIsDemoActive(false);
    setIsTempUser(false);
  };

  const saveTempData = (module: string, data: any) => {
    const tempData = JSON.parse(
      localStorage.getItem('demoTempData') || '{}'
    );
    
    if (!tempData[module]) {
      tempData[module] = [];
    }
    
    data.id = `demo_${Date.now()}`;
    data._isTemporary = true;
    tempData[module].push(data);
    
    localStorage.setItem('demoTempData', JSON.stringify(tempData));
  };

  const getTempData = (module: string) => {
    const tempData = JSON.parse(
      localStorage.getItem('demoTempData') || '{}'
    );
    return tempData[module] || [];
  };

  return {
    isDemoActive,
    isTempUser,
    sessionData,
    activateDemoMode,
    deactivateDemoMode,
    saveTempData,
    getTempData
  };
};
```

## Best Practices

### Do's ✅

1. **Always show clear demo indicators** on every page and component
2. **Use realistic mock data** that reflects actual business scenarios
3. **Maintain session data** only in browser storage, never in database
4. **Provide easy exit** from demo mode at all times
5. **Test demo flows** on both desktop and mobile devices
6. **Update mock data regularly** to keep it relevant
7. **Document demo limitations** where applicable
8. **Track demo usage** for analytics (anonymously)

### Don'ts ❌

1. **Never persist demo data** to production database
2. **Don't mix demo and real data** in the UI
3. **Don't require authentication** for temporary demo users (beyond OTP)
4. **Don't make API calls** when in demo mode
5. **Don't cache demo data** beyond session lifetime
6. **Don't expose sensitive** production data in demo mode
7. **Don't make demo mode** the default experience
8. **Don't forget mobile optimization** for demo flows

## Troubleshooting

### Common Issues

**Issue: Demo mode persists after logout**
```typescript
// Solution: Clear demo flags on logout
const handleLogout = () => {
  // Clear auth tokens
  localStorage.removeItem('access_token');
  
  // Clear demo mode
  localStorage.removeItem('demoMode');
  localStorage.removeItem('isDemoTempUser');
  localStorage.removeItem('demoSessionData');
  localStorage.removeItem('demoTempData');
  
  router.push('/login');
};
```

**Issue: Demo data not showing**
```typescript
// Solution: Verify mock data loading
useEffect(() => {
  if (isDemoMode) {
    const loadData = async () => {
      try {
        const data = await DemoDataService.getInstance()
          .loadMockData('orders');
        setOrders(data);
      } catch (error) {
        console.error('Failed to load demo data:', error);
        // Fallback to inline mock data
        setOrders(fallbackDemoData);
      }
    };
    loadData();
  }
}, [isDemoMode]);
```

**Issue: Demo indicators not visible on mobile**
```typescript
// Solution: Ensure proper z-index and positioning
const DemoIndicator = styled(Chip)({
  position: 'fixed',
  bottom: 70, // Above mobile bottom nav
  right: 16,
  zIndex: 1000, // Above most content
  boxShadow: theme.shadows[4],
  [theme.breakpoints.down('sm')]: {
    bottom: 60, // Adjust for mobile
    fontSize: '0.75rem'
  }
});
```

## Security Considerations

### Data Privacy

1. **No PII in Mock Data**: Use fictional names, addresses, contacts
2. **No Real Credentials**: Never use actual passwords or API keys
3. **Anonymous Analytics**: Track demo usage without personal data
4. **Session Isolation**: Each demo session completely isolated

### Access Control

1. **No Database Access**: Demo mode never accesses production database
2. **API Isolation**: Demo API calls intercepted and mocked
3. **Limited Session**: Temporary users have restricted permissions
4. **Audit Trail**: Log demo mode activations for security monitoring

## Analytics & Monitoring

### Tracking Demo Usage

```typescript
// Track demo mode activation
const trackDemoActivation = (userType: 'current' | 'new') => {
  analytics.track('demo_mode_activated', {
    user_type: userType,
    timestamp: new Date().toISOString(),
    device: isMobile ? 'mobile' : 'desktop'
  });
};

// Track demo feature usage
const trackDemoFeature = (feature: string) => {
  if (isDemoMode) {
    analytics.track('demo_feature_used', {
      feature,
      session_duration: getSessionDuration(),
      user_type: isTempUser ? 'temporary' : 'existing'
    });
  }
};
```

### Success Metrics

- Demo mode activation rate
- Average demo session duration
- Features explored in demo mode
- Demo to signup conversion rate
- Mobile vs desktop demo usage
- Exit points in demo flow

## Onboarding & Tutorial System

### Demo Onboarding

TritIQ includes a comprehensive onboarding system that guides new demo users through key features.

#### DemoOnboarding Component

Automatically shows a guided tour to first-time demo users.

**Usage:**
```typescript
import DemoOnboarding from '@/components/DemoOnboarding';

// Add to demo page
<DemoOnboarding onComplete={() => console.log('Tour completed')} />
```

**Features:**
- Auto-starts for first-time users
- Skip and resume capability
- Progress tracking
- Element highlighting
- Step-by-step guidance

**Tour Steps:**
1. Welcome message
2. Dashboard overview
3. Module navigation
4. Mobile features
5. Demo safety reminder
6. Demo mode indicator
7. Getting started guide

**Configuration:**
```typescript
const demoSteps = [
  {
    title: 'Welcome to TritIQ Demo',
    description: 'Explore all features with realistic demo data.',
    image: '/icons/icon-512x512.png',
  },
  {
    title: 'Navigate the Dashboard',
    description: 'Your dashboard provides key metrics overview.',
    target: '[data-tour="dashboard"]',
  },
  // ... more steps
];
```

#### OnboardingTour Component

Reusable tour component for creating custom onboarding flows.

**Usage:**
```typescript
import OnboardingTour from '@/components/OnboardingTour';

const [showTour, setShowTour] = useState(true);

<OnboardingTour
  open={showTour}
  onClose={() => setShowTour(false)}
  onComplete={() => handleTourComplete()}
  steps={customSteps}
/>
```

**Props:**
- `open`: Boolean to control visibility
- `onClose`: Callback when tour is closed
- `onComplete`: Callback when tour is completed
- `steps`: Array of tour steps

**Step Configuration:**
```typescript
interface TourStep {
  title: string;
  description: string;
  target?: string;      // CSS selector for element to highlight
  image?: string;       // Optional image URL
  action?: () => void;  // Optional action to perform
}
```

**Features:**
- Linear progress indicator
- Step navigation (next/back)
- Element spotlight overlay
- Smooth scrolling to elements
- Stepper visualization
- Custom images per step

#### InteractiveTutorial Component

Context-sensitive tutorials for specific features.

**Usage:**
```typescript
import InteractiveTutorial from '@/components/InteractiveTutorial';

<InteractiveTutorial
  featureId="sales-orders"
  steps={salesOrderSteps}
  onComplete={() => markFeatureLearned('sales-orders')}
/>
```

**Features:**
- Contextual help popover
- Persistent help button
- Auto-start on feature entry
- Completion tracking per feature
- Spotlight overlay
- Action suggestions

**Example Tutorial Steps:**
```typescript
const salesOrderSteps = [
  {
    id: 'create-order',
    target: '[data-tutorial="create-order-btn"]',
    title: 'Create New Order',
    content: 'Click here to start creating a new sales order.',
    placement: 'bottom',
    action: 'Try clicking the button to create your first order',
  },
  {
    id: 'order-details',
    target: '[data-tutorial="order-form"]',
    title: 'Order Details',
    content: 'Fill in customer information and order items.',
    placement: 'right',
  },
  // ... more steps
];
```

**Tutorial Lifecycle:**
```typescript
// Check if tutorial completed
const completed = localStorage.getItem('tutorial-completed-sales-orders');

// Mark as completed
localStorage.setItem('tutorial-completed-sales-orders', 'true');

// Reset tutorial
localStorage.removeItem('tutorial-completed-sales-orders');
```

### Onboarding Best Practices

1. **Keep It Short**: 5-7 steps maximum for main tour
2. **Highlight Value**: Focus on key features and benefits
3. **Make It Skippable**: Always provide skip option
4. **Allow Restart**: Include help button to restart tour
5. **Progressive Disclosure**: Introduce features gradually
6. **Mobile Optimized**: Ensure tours work well on mobile
7. **Contextual**: Show tutorials when user needs them
8. **Track Completion**: Monitor which steps users skip

### Tutorial Targeting

Add data attributes to elements for tutorial targeting:

```typescript
// In your components
<Button data-tour="create-order" data-tutorial="create-order-btn">
  Create Order
</Button>

<Box data-tour="dashboard">
  {/* Dashboard content */}
</Box>

<Chip data-tour="demo-badge" label="DEMO MODE" />
```

### Customizing Tours

Create custom tours for different user types:

```typescript
// For temporary users
const tempUserTour = [
  { title: 'Welcome Guest', description: 'Your session will last 1 hour...' },
  // ...
];

// For existing users trying demo
const existingUserTour = [
  { title: 'Welcome to Demo Mode', description: 'All your real data is safe...' },
  // ...
];

// For mobile users
const mobileTour = [
  { title: 'Mobile Features', description: 'Swipe, tap, and gesture controls...' },
  // ...
];
```

## Future Enhancements

See [FUTURE_SUGGESTIONS.md](./FUTURE_SUGGESTIONS.md) for:
- Video walkthroughs
- Demo mode personalization
- Multi-language demo support
- Voice-guided demo
- Advanced analytics
- A/B testing for onboarding flows

## Support Resources

- [Mobile UI Guide](./MOBILE_UI_GUIDE.md)
- [Demo Mode Documentation](../DEMO_MODE_DOCUMENTATION.md)
- [Testing Guide](../MOBILE_QA_GUIDE.md)
- [API Documentation](../API_DOCUMENTATION.md)

## Feedback

We value your feedback on demo mode:
- Report issues: GitHub Issues with [Demo] tag
- Suggest improvements: Pull requests welcome
- Ask questions: Community forum or support@company.com

---

Last Updated: 2025-10-23
Version: 1.6.0
