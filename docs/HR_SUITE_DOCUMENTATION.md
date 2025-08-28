# HR, Payroll, Recruitment & Talent Management Suite

This document provides comprehensive documentation for the HR, Payroll, Recruitment, and Talent Management modules implemented in the FastAPI ERP system.

## Overview

The HR suite provides a complete Human Capital Management solution with the following core modules:

- **HR Core**: Employee management, attendance, leaves, performance reviews
- **Payroll**: Salary structures, payslip generation, tax calculations, loan management
- **Recruitment**: Job postings, candidate pipeline, interview management, offer processing
- **Talent**: Skills matrix, training programs, learning paths, performance development

## Features Implemented

### HR Core Module

#### Employee Management
- **Employee Profiles**: Complete employee information with personal, professional, and contact details
- **Employee Lifecycle**: Onboarding, confirmation, resignation, and offboarding workflows
- **Organizational Hierarchy**: Reporting structure and departmental organization
- **Document Management**: Storage and tracking of employee documents

#### Attendance Management
- **Time Tracking**: Check-in/check-out with location tracking
- **Attendance Status**: Present, absent, half-day, late, on-leave tracking
- **Overtime Calculation**: Automatic overtime hours calculation
- **Approval Workflow**: Manager approval for attendance corrections

#### Leave Management
- **Leave Types**: Configurable leave categories (Annual, Sick, Maternity, etc.)
- **Leave Policies**: Allocation, carry-forward, and cash conversion rules
- **Application Workflow**: Employee application with manager approval
- **Leave Calendar**: Visual representation of team leave schedules

#### Performance Management
- **Review Cycles**: Annual, quarterly, and custom review periods
- **Rating System**: Multi-dimensional performance evaluation
- **Goal Setting**: Objective setting and tracking
- **360-degree Feedback**: Employee, manager, and peer assessments

### Payroll Module

#### Salary Structure Management
- **Salary Components**: Basic salary, allowances, and deductions
- **Salary Revisions**: Historical tracking of salary changes
- **Approval Workflow**: Manager and HR approval for salary structures
- **Effective Dating**: Time-bound salary structures

#### Payroll Processing
- **Payroll Periods**: Monthly, bi-weekly, or custom pay periods
- **Bulk Processing**: Generate payslips for multiple employees
- **Attendance Integration**: Automatic attendance-based calculations
- **Tax Calculations**: Integrated tax slab calculations

#### Payslip Management
- **Automated Generation**: Bulk payslip creation with templates
- **PDF Generation**: Professional payslip documents
- **Email Distribution**: Automatic payslip delivery
- **Employee Self-Service**: Employee access to payslips

#### Loan Management
- **Loan Types**: Salary advance, personal loans, emergency loans
- **Loan Tracking**: Outstanding amount and repayment schedules
- **Payroll Integration**: Automatic deduction from salary
- **Approval Workflow**: Manager and HR loan approvals

### Recruitment Module

#### Job Management
- **Job Postings**: Detailed job descriptions with requirements
- **Job Distribution**: Multi-platform job posting
- **Application Tracking**: Centralized application management
- **Position Management**: Open positions and hiring requirements

#### Candidate Management
- **Candidate Profiles**: Comprehensive candidate information
- **Resume Parsing**: Automatic extraction of candidate details
- **Candidate Pipeline**: Stage-wise candidate progression
- **Communication Tracking**: Interview and communication history

#### Interview Management
- **Interview Scheduling**: Calendar integration and scheduling
- **Interview Types**: Technical, HR, behavioral, group interviews
- **Feedback Collection**: Structured interview evaluation
- **Interviewer Assignment**: Multiple interviewer coordination

#### Offer Management
- **Offer Generation**: Automated offer letter creation
- **Negotiation Tracking**: Offer revision and negotiation history
- **Approval Workflow**: Management approval for offers
- **Onboarding Integration**: Seamless transition to employee onboarding

### Talent Development Module

#### Skills Management
- **Skills Matrix**: Comprehensive skills database
- **Skill Assessment**: Employee skill evaluations
- **Skill Gap Analysis**: Identification of training needs
- **Certification Tracking**: Professional certification management

#### Training Management
- **Training Programs**: Course catalog and program management
- **Training Delivery**: Multiple delivery methods (online, classroom, blended)
- **Training Enrollment**: Employee registration and tracking
- **Training Effectiveness**: ROI and effectiveness measurement

#### Learning Paths
- **Career Development**: Structured learning journeys
- **Competency Mapping**: Role-based skill requirements
- **Progress Tracking**: Individual learning progress monitoring
- **Certification Pathways**: Professional certification tracks

## API Endpoints

### HR Core APIs
```
GET    /api/v1/hr/employees              # List employees
POST   /api/v1/hr/employees              # Create employee
GET    /api/v1/hr/employees/{id}         # Get employee details
PUT    /api/v1/hr/employees/{id}         # Update employee
DELETE /api/v1/hr/employees/{id}         # Delete employee

GET    /api/v1/hr/attendance             # List attendance records
POST   /api/v1/hr/attendance             # Create attendance record
PUT    /api/v1/hr/attendance/{id}        # Update attendance record

GET    /api/v1/hr/leave-types            # List leave types
POST   /api/v1/hr/leave-types            # Create leave type
PUT    /api/v1/hr/leave-types/{id}       # Update leave type

GET    /api/v1/hr/leave-applications     # List leave applications
POST   /api/v1/hr/leave-applications     # Create leave application
PUT    /api/v1/hr/leave-applications/{id}/approve  # Approve leave
PUT    /api/v1/hr/leave-applications/{id}/reject   # Reject leave

GET    /api/v1/hr/performance-reviews    # List performance reviews
POST   /api/v1/hr/performance-reviews    # Create performance review
PUT    /api/v1/hr/performance-reviews/{id}  # Update performance review

GET    /api/v1/hr/dashboard              # HR dashboard data
```

### Payroll APIs
```
GET    /api/v1/payroll/salary-structures    # List salary structures
POST   /api/v1/payroll/salary-structures    # Create salary structure
PUT    /api/v1/payroll/salary-structures/{id}  # Update salary structure
PUT    /api/v1/payroll/salary-structures/{id}/approve  # Approve salary structure

GET    /api/v1/payroll/periods              # List payroll periods
POST   /api/v1/payroll/periods              # Create payroll period
PUT    /api/v1/payroll/periods/{id}/process # Process payroll

GET    /api/v1/payroll/payslips             # List payslips
POST   /api/v1/payroll/payslips             # Create payslip
POST   /api/v1/payroll/payslips/bulk-generate  # Bulk generate payslips

GET    /api/v1/payroll/loans                # List employee loans
POST   /api/v1/payroll/loans                # Create loan application
PUT    /api/v1/payroll/loans/{id}/approve   # Approve loan

GET    /api/v1/payroll/settings             # Get payroll settings
PUT    /api/v1/payroll/settings             # Update payroll settings

GET    /api/v1/payroll/dashboard            # Payroll dashboard data
```

## Database Schema

### Core Tables

#### Employee Profiles
- `employee_profiles`: Extended employee information
- `attendance_records`: Daily attendance tracking
- `leave_types`: Leave category configuration
- `leave_applications`: Employee leave requests
- `performance_reviews`: Performance evaluation records

#### Payroll Tables
- `salary_structures`: Employee salary definitions
- `payroll_periods`: Payroll processing periods
- `payslips`: Generated employee payslips
- `tax_slabs`: Income tax configuration
- `employee_loans`: Loan and advance tracking
- `payroll_settings`: Organization payroll configuration

#### Recruitment Tables
- `job_postings`: Job openings and requirements
- `candidates`: Candidate profiles and information
- `job_applications`: Application submissions
- `interviews`: Interview scheduling and feedback
- `job_offers`: Offer management and tracking
- `recruitment_pipelines`: Customizable recruitment stages

#### Talent Development Tables
- `skill_categories`: Skills organization structure
- `skills`: Skills master data
- `employee_skills`: Employee skill assessments
- `training_programs`: Training course catalog
- `training_sessions`: Scheduled training sessions
- `training_enrollments`: Employee training registrations
- `learning_paths`: Structured learning journeys
- `employee_learning_paths`: Individual learning progress

## Setup Instructions

### 1. Database Migration
```bash
# Generate migration for HR models
alembic revision --autogenerate -m "Add HR, Payroll, Recruitment and Talent models"

# Apply migration
alembic upgrade head
```

### 2. Sample Data Creation
```bash
# Run the sample data seeder
python seed_hr_data.py
```

### 3. Frontend Setup
The HR frontend components are located in:
- `/frontend/src/pages/hr/dashboard.tsx` - HR Dashboard
- `/frontend/src/pages/hr/employees.tsx` - Employee Management
- Additional pages can be created following the same pattern

### 4. API Integration
Update your main FastAPI application to include the HR routes:
```python
from app.api.v1.hr import router as hr_router
from app.api.v1.payroll import router as payroll_router

app.include_router(hr_router, prefix="/api/v1")
app.include_router(payroll_router, prefix="/api/v1")
```

## Configuration

### Payroll Settings
Configure organization-specific payroll settings:
- Pay frequency (monthly, bi-weekly, weekly)
- Working days and hours
- PF rates and ceilings
- Professional tax settings
- HRA percentages
- Overtime multipliers

### Leave Policies
Configure leave types with:
- Annual allocation
- Carry forward rules
- Cash conversion policies
- Approval requirements
- Advance notice periods

### Performance Review Cycles
Set up review cycles with:
- Review frequency
- Rating scales
- Review templates
- Approval workflows

## Security Considerations

### Role-Based Access Control (RBAC)
- **HR Admin**: Full access to all HR functions
- **HR Manager**: Access to team-specific HR functions
- **Employee**: Self-service access to personal information
- **Manager**: Access to direct reports' information

### Data Privacy
- Personal information encryption
- Audit trails for all data changes
- Secure document storage
- GDPR compliance features

### Multi-tenant Security
- Organization-level data isolation
- Row-level security policies
- Encrypted sensitive data fields

## Reporting and Analytics

### HR Reports
- Employee demographics
- Attendance trends
- Leave utilization
- Performance analytics
- Turnover analysis

### Payroll Reports
- Payroll summaries
- Tax reports
- Cost center analysis
- Compliance reports

### Recruitment Analytics
- Time-to-hire metrics
- Source effectiveness
- Interview conversion rates
- Offer acceptance rates

## Integration Points

### CRM Integration
- Customer service employee assignments
- Sales team performance tracking
- Customer interaction history

### ERP Integration
- Cost center allocations
- Project resource assignments
- Financial reporting integration

### Third-party Integrations
- Email systems for notifications
- Calendar systems for scheduling
- Document management systems
- Biometric attendance systems

## Future Enhancements

### Phase 2 Features
- Advanced analytics and AI insights
- Mobile application for employees
- Workflow automation engine
- Document management system
- Employee self-service portal
- Manager dashboard
- Compliance management
- Benefits administration

### Integration Roadmap
- Single Sign-On (SSO) integration
- Active Directory integration
- Third-party payroll systems
- Government compliance systems
- Learning Management Systems (LMS)

## Support and Maintenance

### Troubleshooting
Common issues and solutions are documented in the support guide.

### Updates
Regular updates include:
- Security patches
- Feature enhancements
- Bug fixes
- Performance improvements

### Backup and Recovery
- Automated daily backups
- Point-in-time recovery
- Disaster recovery procedures

---

For technical support or feature requests, please contact the development team or raise an issue in the project repository.