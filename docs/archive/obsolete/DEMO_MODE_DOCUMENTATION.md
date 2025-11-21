# Demo Mode Documentation

## Overview

The TRITIQ BOS Demo Mode provides a comprehensive way for users to experience all system features using realistic sample data without affecting any real business data. This documentation covers the implementation, user experience, and QA testing procedures.

## Features

### 1. Demo Mode Access Points

#### Login Page Demo Button
- **Location**: Login page (`/login`)
- **Appearance**: Prominent "Try Demo Mode" button with play icon
- **Function**: Opens the Demo Mode selection dialog

#### Users Page Demo Button  
- **Location**: User Management page (`/admin/users`)
- **Appearance**: "Try Demo Mode" button in the page header
- **Function**: Opens the Demo Mode selection dialog for admin users

### 2. User Type Selection Flow

When clicking any Demo button, users are presented with a choice:

#### Current User Path
- **Selection**: "I have an existing account and want to explore demo features"
- **Flow**: 
  1. User selects "Current User"
  2. Dialog closes and redirects to normal login page
  3. User logs in with existing credentials
  4. System automatically activates demo mode after successful login
  5. User is redirected to `/demo` page with full demo experience

#### New User Path
- **Selection**: "I'm new and want to try the system with a temporary demo account"
- **Flow**:
  1. User selects "New User"
  2. Form appears requesting:
     - Full Name
     - Email Address
     - Phone Number
     - Company Name
  3. System sends demo OTP to provided email
  4. User enters 6-digit OTP code
  5. Temporary demo session is created (valid until logout/browser close)
  6. User is redirected to `/demo` page with full demo experience

### 3. Demo Mode Features

#### Sample Data Coverage
- **Master Data**: Vendors, customers, products with realistic entries
- **Financial Data**: Purchase vouchers, sales vouchers, payment records
- **Analytics**: Customer analytics, sales analytics, service reports
- **Service CRM**: Service requests, work orders, technician assignments
- **Manufacturing**: Production orders, job cards, inventory movements
- **Transport**: Delivery management, vehicle tracking
- **HR Module**: Employee records, attendance, payroll (sample data)

#### Feature Accessibility
- **All Modules**: Every module and sub-module is accessible in demo mode
- **Mega Menu**: Complete navigation menu with all features enabled
- **Reports**: All report types available with sample data
- **Analytics Dashboards**: Full analytics with demo metrics
- **Admin Functions**: User management, settings, audit logs (with sample data)

#### Data Safety
- **Read-Only Operations**: All demo interactions use sample data
- **No Database Writes**: No real data is created, modified, or deleted
- **Isolated Environment**: Demo mode completely separated from production data
- **Clear Indicators**: Visual indicators throughout the interface show demo mode status

### 4. Demo Mode UI Indicators

#### Global Demo Alert
- **Location**: Top of every page in demo mode
- **Content**: 
  - "🎭 Demo Mode Active" header
  - Explanation that this is sample data
  - Toggle switch to enable/disable demo mode
  - Exit Demo button

#### Temporary User Alert (New Users Only)
- **Additional Warning**: Shows for users who created temporary accounts
- **Content**: Explains the temporary nature of the account and session limitations

#### Page-Level Indicators
- **Demo Labels**: Sample data tables and forms show demo indicators
- **Sample Data Watermarks**: Charts and reports include "Sample Data" labels
- **Feature Descriptions**: Each demo section includes explanations

### 5. Session Management

#### Current Users
- **Session Type**: Normal user session with demo mode flag
- **Duration**: Until user manually exits demo mode
- **Exit Behavior**: Returns to normal dashboard/system view
- **Data Persistence**: User's real account and preferences remain intact

#### Temporary Users (New Users)
- **Session Type**: Temporary demo session
- **Duration**: Until logout or browser close
- **Exit Behavior**: Clears session and redirects to login page
- **Data Persistence**: No permanent user account created

## Implementation Details

### Technical Components

#### Frontend Components
- `DemoModeDialog.tsx`: Main dialog for user type selection and new user flow
- `login.tsx`: Enhanced with demo button and demo mode handling
- `admin/users/index.tsx`: Enhanced with demo button for admin users
- `demo.tsx`: Main demo page with enhanced temporary user support

#### State Management
- `localStorage.demoMode`: Flag indicating demo mode is active
- `localStorage.isDemoTempUser`: Flag for temporary demo users
- `localStorage.pendingDemoMode`: Flag for current users entering demo after login

#### Navigation Flow
```
Demo Button Click
    ↓
User Type Selection Dialog
    ↓                    ↓
Current User         New User
    ↓                    ↓
Normal Login       Demo Form + OTP
    ↓                    ↓
Demo Mode          Temp Demo Session
    ↓                    ↓
/demo page         /demo page
```

### Data Architecture

#### Sample Data Structure
- **Realistic Volume**: Appropriate number of records for each entity type
- **Relationship Integrity**: Proper foreign key relationships maintained
- **Business Logic**: Sample data follows real business scenarios
- **Variety**: Diverse examples covering common use cases

#### Demo Data Sources
- **Static Mock Data**: Predefined datasets for consistent demo experience
- **Generated Scenarios**: Common business scenarios (sales cycles, inventory management)
- **Industry Examples**: Sample data relevant to various industry verticals

## User Experience Guide

### For Prospective Customers
1. **Easy Access**: No account creation required to try the system
2. **Full Feature Set**: Experience all capabilities without limitations
3. **Realistic Data**: Sample data reflects real business scenarios
4. **Guided Experience**: Clear explanations and context throughout

### For Current Users
1. **Safe Exploration**: Try new features without affecting real data
2. **Training Environment**: Practice using unfamiliar modules
3. **Feature Discovery**: Explore capabilities they haven't used yet
4. **Quick Toggle**: Easy to switch between demo and live data

### For Administrators
1. **User Training**: Create training sessions using demo mode
2. **Feature Demonstration**: Show capabilities to team members
3. **Testing Environment**: Safely test configurations and workflows
4. **Sales Support**: Demonstrate system capabilities to prospects

## QA Testing Procedures

### Test Cases

#### Demo Access Testing
1. **Login Page Demo Button**
   - Verify button appears and is clickable
   - Confirm dialog opens with proper content
   - Test user type selection functionality

2. **Users Page Demo Button**
   - Verify button appears for admin users only
   - Confirm proper role-based access control
   - Test integration with existing user management

#### User Flow Testing
3. **Current User Flow**
   - Test user type selection
   - Verify redirect to login page
   - Confirm demo mode activation after login
   - Validate demo page access

4. **New User Flow**
   - Test form validation and submission
   - Verify OTP sending simulation
   - Test OTP verification (accept any 6-digit code)
   - Confirm temporary session creation

#### Demo Mode Functionality
5. **Demo Environment Testing**
   - Verify all modules are accessible
   - Confirm sample data loads correctly
   - Test that no real data is affected
   - Validate demo mode indicators

6. **Session Management Testing**
   - Test demo mode toggle functionality
   - Verify exit demo behavior for both user types
   - Confirm session cleanup for temporary users
   - Test browser close behavior for temporary users

#### Data Safety Testing
7. **Data Isolation Testing**
   - Confirm demo operations don't affect production data
   - Verify sample data consistency
   - Test that demo changes don't persist
   - Validate proper data source separation

#### UI/UX Testing
8. **Visual Indicators Testing**
   - Verify demo mode alerts appear consistently
   - Test demo mode toggle functionality
   - Confirm temporary user warnings show properly
   - Validate demo indicators throughout interface

### Regression Testing
- **Authentication Flow**: Ensure normal login still works
- **Existing Features**: Verify no impact on current functionality
- **Role-Based Access**: Confirm RBAC still functions correctly
- **Performance**: Validate no performance degradation

### Browser Compatibility
- **Chrome**: Test all demo features
- **Firefox**: Verify compatibility
- **Safari**: Test on macOS/iOS
- **Edge**: Ensure Microsoft compatibility
- **Mobile**: Test responsive design on mobile devices

## Security Considerations

### Data Protection
- **No Real Data Exposure**: Demo mode completely isolated from production
- **Temporary Sessions**: New user sessions automatically expire
- **Local Storage**: Demo flags stored locally, not on server
- **No Persistence**: Temporary demo users don't create database records

### Access Control
- **Role Preservation**: Current users maintain their actual permissions
- **Demo Limitations**: Temporary users have limited, read-only access
- **Session Validation**: Proper session management for all user types
- **Audit Trail**: Demo activities can be logged separately if needed

## Support and Troubleshooting

### Common Issues
1. **Demo Mode Not Activating**: Check localStorage flags and browser console
2. **OTP Not Working**: Verify any 6-digit number should work in demo
3. **Session Expires**: Expected behavior for temporary users
4. **Missing Sample Data**: Check demo data loading and API responses

### Support Procedures
- **User Guidance**: Provide clear instructions for demo mode access
- **Issue Escalation**: Process for handling demo mode problems
- **Feedback Collection**: Gather user feedback on demo experience
- **Continuous Improvement**: Regular updates based on user feedback

## Future Enhancements

### Planned Features
- **Guided Tours**: Interactive tours for specific modules
- **Demo Scenarios**: Pre-built business scenarios users can follow
- **Video Integration**: Embedded tutorial videos within demo mode
- **Progress Tracking**: Track which features users explore in demo

### Analytics
- **Usage Metrics**: Track demo mode usage patterns
- **Feature Popularity**: Identify most-used demo features
- **Conversion Tracking**: Monitor demo-to-signup conversion rates
- **User Feedback**: Collect and analyze demo experience feedback