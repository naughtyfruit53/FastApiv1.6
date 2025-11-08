# Paid User Guide - FastAPI v1.6

**Version**: 1.6  
**Last Updated**: October 29, 2025  
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Subscription Plans](#subscription-plans)
3. [Feature Access by Plan](#feature-access-by-plan)
4. [Permission System](#permission-system)
5. [Module Licensing](#module-licensing)
6. [User Management](#user-management)
7. [Getting Started](#getting-started)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Overview

FastAPI v1.6 implements a comprehensive Role-Based Access Control (RBAC) system with tenant isolation and module-based licensing. This guide explains how permissions and feature access work for paid users.

### Key Concepts

- **Organization**: Your company's isolated environment
- **Module**: A functional area (e.g., Manufacturing, CRM, Finance)
- **Permission**: Granular access rights (e.g., "create_product", "view_reports")
- **Role**: A collection of permissions (e.g., "Admin", "Manager", "User")
- **License**: Subscription that enables specific modules

---

## Subscription Plans

### Free Plan

**Price**: $0/month  
**Users**: Up to 3  
**Modules**: None  
**Features**:
- Basic user management
- Organization setup
- Limited API access

### Starter Plan

**Price**: $49/month  
**Users**: Up to 10  
**Modules**: Choose 2  
**Features**:
- Full RBAC system
- Basic reporting
- Email support
- Standard API limits

### Professional Plan

**Price**: $199/month  
**Users**: Up to 50  
**Modules**: Choose 5  
**Features**:
- All Starter features
- Advanced analytics
- Custom reports
- Priority support
- Extended API limits

### Enterprise Plan

**Price**: Custom  
**Users**: Unlimited  
**Modules**: All modules  
**Features**:
- All Professional features
- Dedicated support
- Custom integrations
- SLA guarantees
- Unlimited API access
- White-label options

---

## Feature Access by Plan

### Core Features (All Plans)

✅ **Authentication & Security**
- User login/logout
- Password management
- Two-factor authentication (OTP)
- Session management

✅ **Basic Organization Management**
- Organization profile
- User invitations
- Basic settings

### Module Access by Plan

| Module | Free | Starter | Professional | Enterprise |
|--------|------|---------|--------------|------------|
| Manufacturing | ❌ | 🔄 | 🔄 | ✅ |
| CRM | ❌ | 🔄 | 🔄 | ✅ |
| Finance & Accounting | ❌ | 🔄 | 🔄 | ✅ |
| HR & Payroll | ❌ | 🔄 | 🔄 | ✅ |
| Inventory Management | ❌ | 🔄 | 🔄 | ✅ |
| Service Desk | ❌ | 🔄 | 🔄 | ✅ |
| Project Management | ❌ | 🔄 | 🔄 | ✅ |
| Analytics & Reporting | ❌ | Basic | Advanced | ✅ |
| AI & ML Features | ❌ | ❌ | Limited | ✅ |
| Integration APIs | Limited | Standard | Extended | ✅ |

🔄 = Available based on selected modules in subscription

### Feature Comparison

#### Manufacturing Module

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Bill of Materials (BOM) | ✅ | ✅ | ✅ |
| Production Orders | ✅ | ✅ | ✅ |
| Quality Control | ❌ | ✅ | ✅ |
| Job Work | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |

#### CRM Module

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Lead Management | ✅ | ✅ | ✅ |
| Contact Management | ✅ | ✅ | ✅ |
| Opportunity Tracking | ✅ | ✅ | ✅ |
| Email Integration | ❌ | ✅ | ✅ |
| AI Lead Scoring | ❌ | ❌ | ✅ |
| Custom Workflows | ❌ | ✅ | ✅ |

#### Finance Module

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Chart of Accounts | ✅ | ✅ | ✅ |
| Voucher Management | ✅ | ✅ | ✅ |
| Basic Reports | ✅ | ✅ | ✅ |
| Advanced Reports | ❌ | ✅ | ✅ |
| Financial Forecasting | ❌ | ❌ | ✅ |
| Multi-currency | ❌ | ✅ | ✅ |

---

## Permission System

### Default Roles

#### Super Admin
- **Access**: Full system access
- **Permissions**: All permissions across all modules
- **Can**:
  - Manage organization settings
  - Create/delete users
  - Assign roles and permissions
  - Access all data
  - Reset data
  - Manage billing

#### Admin
- **Access**: Full access within organization
- **Permissions**: All permissions for licensed modules
- **Can**:
  - Manage users (within org)
  - Configure module settings
  - Access all module data
  - Generate reports
  - Cannot: Manage billing, delete organization

#### Manager
- **Access**: Read/write access to assigned modules
- **Permissions**: Create, read, update for licensed modules
- **Can**:
  - Create and edit records
  - View all data in assigned modules
  - Generate standard reports
  - Cannot: Delete records, manage users

#### User
- **Access**: Read-only or limited write access
- **Permissions**: Read permissions, limited create/update
- **Can**:
  - View assigned data
  - Create own records
  - Update own records
  - Cannot: Delete, access others' data, manage settings

### Permission Granularity

Permissions follow the pattern: `{module}:{action}`

**Actions**:
- `read` - View data
- `create` - Create new records
- `update` - Modify existing records
- `delete` - Remove records
- `export` - Export data
- `import` - Import data

**Examples**:
- `manufacturing:read` - View manufacturing data
- `crm:create` - Create CRM records (leads, contacts)
- `finance:update` - Edit financial records
- `reports:export` - Export reports
- `user:delete` - Delete users (admin only)

### Custom Roles

Enterprise plan users can create custom roles with specific permission combinations.

**Example**: "Sales Manager" role
- Permissions:
  - `crm:read`, `crm:create`, `crm:update`
  - `customer:read`, `customer:create`
  - `reports:read`, `reports:export`
  - `order:read`, `order:create`

---

## Module Licensing

### How Module Licensing Works

1. **Purchase Subscription**: Select plan and modules
2. **Module Activation**: Modules are enabled for your organization
3. **User Assignment**: Assign users to modules via roles
4. **Feature Access**: Users can access module features based on permissions

### Checking Module Status

**Frontend**: Navigation menu shows only enabled modules  
**API**: `/api/v1/organizations/{org_id}/modules` endpoint

**Example Response**:
```json
{
  "organization_id": 123,
  "modules": [
    {
      "module_code": "manufacturing",
      "enabled": true,
      "license_expires": "2025-12-31"
    },
    {
      "module_code": "crm",
      "enabled": true,
      "license_expires": "2025-12-31"
    }
  ]
}
```

### Module Upgrade Path

**Starter → Professional**:
1. Additional 3 modules available
2. Advanced features unlocked
3. Existing data preserved
4. No downtime

**Professional → Enterprise**:
1. All modules unlocked
2. AI/ML features enabled
3. Custom integrations available
4. Dedicated support team assigned

---

## User Management

### Adding Users

**Admin or Super Admin Only**

1. Navigate to Settings → Users
2. Click "Invite User"
3. Enter email address
4. Select role
5. Assign modules
6. Send invitation

**API**: `POST /api/v1/organizations/users`
```json
{
  "email": "newuser@company.com",
  "full_name": "John Doe",
  "role": "manager",
  "modules": ["manufacturing", "crm"]
}
```

### Managing Permissions

**Assigning Permissions**:
1. Go to Settings → Users
2. Select user
3. Click "Edit Permissions"
4. Select role or custom permissions
5. Save changes

**Best Practices**:
- Use predefined roles when possible
- Grant minimum necessary permissions (least privilege)
- Review permissions quarterly
- Audit permission changes via audit logs

### User Limits by Plan

| Plan | User Limit | Additional Users |
|------|------------|------------------|
| Free | 3 | Not available |
| Starter | 10 | $5/user/month |
| Professional | 50 | $4/user/month |
| Enterprise | Unlimited | Included |

---

## Getting Started

### New Organization Setup

**Step 1: Initial Login**
- Use invitation email link
- Set password (must be changed on first login)
- Complete organization profile

**Step 2: Configure Organization**
- Add company details
- Upload logo
- Set timezone and currency
- Configure tax settings

**Step 3: Activate Modules**
- Select plan
- Choose modules (based on plan)
- Enter payment information
- Activate license

**Step 4: Invite Team Members**
- Add users
- Assign roles
- Send invitations
- Track acceptance

**Step 5: Import Data** (Optional)
- Use migration tools
- Import from Excel
- Connect integrations (Tally, Zoho)
- Validate imported data

### Quick Start Checklist

- [ ] Complete organization profile
- [ ] Activate required modules
- [ ] Create user accounts
- [ ] Assign roles and permissions
- [ ] Configure module settings
- [ ] Import initial data
- [ ] Test key workflows
- [ ] Train team members

---

## Common Workflows

### Workflow 1: Creating a Sales Order (CRM + Finance)

**Required Permissions**: `crm:create`, `order:create`

1. Navigate to CRM → Sales Orders
2. Click "New Order"
3. Select customer (creates lead if new)
4. Add products/services
5. Set pricing and terms
6. Generate quote (PDF)
7. Convert to invoice
8. Record payment

**Notes**:
- Requires CRM and Finance modules
- Auto-generates vouchers
- Integrates with inventory if enabled

### Workflow 2: Manufacturing Process

**Required Permissions**: `manufacturing:create`, `manufacturing:update`

1. Create Bill of Materials (BOM)
2. Generate Production Order
3. Issue materials from inventory
4. Track production stages
5. Quality control checks
6. Receive finished goods
7. Update inventory

**Notes**:
- Requires Manufacturing module
- Optional Inventory module for auto-updates
- QC requires Professional plan or higher

### Workflow 3: Hiring Process (HR Module)

**Required Permissions**: `hr:create`, `hr:update`

1. Create job posting
2. Review applications
3. Schedule interviews
4. Make offer
5. Onboard employee
6. Set up payroll
7. Assign permissions

**Notes**:
- Requires HR module
- Integrates with user management
- Payroll setup requires Finance module

---

## Troubleshooting

### Common Issues

#### "Access Denied" or 403 Error

**Cause**: Insufficient permissions  
**Solution**:
1. Check your role assignment
2. Verify module is licensed
3. Contact admin to update permissions
4. Ensure organization has active subscription

#### Module Not Visible in Navigation

**Cause**: Module not licensed or permissions missing  
**Solution**:
1. Check subscription plan includes module
2. Verify module is activated: Settings → Modules
3. Check user has permissions for module
4. Try logging out and back in

#### Cannot Create/Edit Records

**Cause**: Missing create/update permissions  
**Solution**:
1. Verify role has required permissions
2. Check if record belongs to your organization
3. Ensure no workflow approval required
4. Contact admin for permission update

#### Data Not Showing (Empty Lists)

**Cause**: Tenant isolation - seeing only your org's data  
**Solution**:
- **Expected behavior**: Each organization sees only their data
- Verify data was created in your organization
- Check filters are not too restrictive
- Super admins can see all orgs (if needed)

### Permission Debugging

**Check Your Permissions**:
1. Go to Settings → My Profile
2. View "My Permissions" section
3. Review assigned roles
4. Check module access

**Audit Logs**:
- View permission changes: Settings → Audit Logs
- Filter by action type: "PERMISSION_CHANGE"
- Review who made changes and when

### Getting Help

**Support Channels**:

**Free Plan**:
- Community forum
- Documentation

**Starter Plan**:
- Email support (24-48 hour response)
- Documentation
- Community forum

**Professional Plan**:
- Email support (12-24 hour response)
- Priority ticket system
- Phone support (business hours)
- Documentation

**Enterprise Plan**:
- Dedicated account manager
- 24/7 phone and email support
- 4-hour SLA for critical issues
- Custom training sessions
- On-site support (if needed)

---

## Appendix

### Permission Matrix

See `RBAC_COMPREHENSIVE_GUIDE.md` for complete permission matrix.

### API Rate Limits

| Plan | Requests/Hour | Burst |
|------|---------------|-------|
| Free | 100 | 10 |
| Starter | 1,000 | 50 |
| Professional | 10,000 | 200 |
| Enterprise | Unlimited | Unlimited |

### Data Storage Limits

| Plan | Storage | File Upload Size |
|------|---------|------------------|
| Free | 1 GB | 5 MB |
| Starter | 25 GB | 25 MB |
| Professional | 250 GB | 100 MB |
| Enterprise | Unlimited | 500 MB |

### Billing FAQ

**Q: Can I change my plan?**  
A: Yes, upgrade/downgrade anytime. Changes take effect at next billing cycle.

**Q: What happens if I exceed user limits?**  
A: System will prompt to upgrade or remove users. Grace period of 7 days.

**Q: Can I change my selected modules?**  
A: Yes, Starter and Professional plans can swap modules monthly. Enterprise has all modules.

**Q: Is there a free trial?**  
A: Yes, 14-day free trial of Professional plan with all modules.

**Q: What payment methods are accepted?**  
A: Credit card, PayPal, bank transfer (Enterprise only), and invoice (Enterprise only).

---

**Document Version**: 1.0  
**Last Updated**: October 29, 2025  
**For Questions**: support@fastapiv16.com
