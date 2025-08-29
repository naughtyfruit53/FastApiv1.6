# Company-Scoped Data Architecture Implementation

## Overview

This implementation adds comprehensive company-level data scoping to the FastAPI application, enabling true multi-company support within organizations. All business data (tasks, customers, vendors, products) can now be isolated and scoped to specific companies while maintaining backwards compatibility.

## Key Features

### 🏢 Multi-Company Data Isolation
- **Tasks & Projects**: Company-specific task management
- **Customers**: Company-scoped customer data
- **Vendors**: Company-scoped vendor management  
- **Products**: Company-specific product catalogs
- **Cross-Model Consistency**: All related data maintains company relationships

### 🔐 Enhanced Access Control
- **User-Company Assignments**: Users can belong to multiple companies
- **Company Admin Roles**: Special admin rights within company scope
- **Permission Enforcement**: RBAC integration with company-level permissions
- **Automatic Access Validation**: All endpoints validate company access

### 🎯 Smart Company Assignment
- **Single Company Auto-Assignment**: Users with access to one company get automatic assignment
- **Multi-Company Validation**: Users with multiple companies must specify company_id
- **Organization-Level Fallback**: Support for organization-wide data (company_id=NULL)
- **Backwards Compatibility**: Existing organization-level data remains accessible

## Database Schema Changes

### Models Updated

#### Task Management
```python
# Task model
class Task(Base):
    # ... existing fields ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # NEW
    
    # Relationships
    company = relationship("Company", back_populates="tasks")  # NEW

# TaskProject model  
class TaskProject(Base):
    # ... existing fields ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # NEW
    
    # Relationships
    company = relationship("Company", back_populates="task_projects")  # NEW
```

#### Business Entities
```python
# Customer model
class Customer(Base):
    # ... existing fields ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # NEW
    
    # Relationships
    company = relationship("Company", back_populates="customers")  # NEW

# Vendor model
class Vendor(Base):
    # ... existing fields ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)  
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # NEW
    
    # Relationships
    company = relationship("Company", back_populates="vendors")  # NEW

# Product model
class Product(Base):
    # ... existing fields ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # NEW
    
    # Relationships
    company = relationship("Company", back_populates="products")  # NEW
```

#### Company Model Extensions
```python
class Company(Base):
    # ... existing fields ...
    
    # NEW: Business entity relationships
    tasks = relationship("Task", back_populates="company")
    task_projects = relationship("TaskProject", back_populates="company")
    vendors = relationship("Vendor", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    products = relationship("Product", back_populates="company")
```

## API Enhancements

### Task Management API

#### Enhanced Endpoints
```python
# Create task with company scoping
POST /api/v1/tasks/
{
    "title": "Company Task",
    "description": "Task for specific company",
    "company_id": 1  # Optional - auto-assigned if user has single company
}

# List tasks with company filtering  
GET /api/v1/tasks/?company_id=1
GET /api/v1/tasks/  # Shows tasks from all user's accessible companies

# Dashboard with company scoping
GET /api/v1/tasks/dashboard?company_id=1
```

#### Smart Company Assignment Logic
```python
# In create task endpoint
if task_data.company_id:
    # Validate user has access to specified company
    rbac.enforce_company_access(user_id, company_id, "task_create")
else:
    # Auto-assign for single-company users
    user_companies = rbac.get_user_companies(user_id)
    if len(user_companies) == 1:
        task_data.company_id = user_companies[0]
    elif len(user_companies) > 1:
        raise HTTPException(400, "company_id required for multi-company users")
```

### Customer Management API

#### Company-Scoped Customer Operations
```python
# Create customer with company validation
POST /api/v1/customers/
{
    "name": "Company Customer",
    "company_id": 1  # Optional - auto-assigned if applicable
}

# List customers with company filtering
GET /api/v1/customers/?company_id=1
GET /api/v1/customers/  # Shows customers from accessible companies
```

## RBAC Integration

### Company Permission Methods
```python
# Existing RBAC service methods for company scoping
rbac = RBACService(db)

# Check company access
rbac.user_has_company_access(user_id, company_id)

# Check company admin status  
rbac.user_is_company_admin(user_id, company_id)

# Get user's accessible companies
user_companies = rbac.get_user_companies(user_id)

# Enforce company access with permission
rbac.enforce_company_access(user_id, company_id, "permission_name")
```

### API Access Patterns
```python
# Pattern used in all company-scoped endpoints
def get_data_with_company_scoping(company_id, current_user, db):
    rbac = RBACService(db)
    user_companies = rbac.get_user_companies(current_user.id)
    
    if company_id is not None:
        # Specific company requested - validate access
        if company_id not in user_companies:
            raise HTTPException(403, "Company access denied")
        # Filter by specific company
        query = query.filter(Model.company_id == company_id)
    elif user_companies:
        # Show data from all accessible companies + org-level
        query = query.filter(or_(
            Model.company_id.in_(user_companies),
            Model.company_id.is_(None)
        ))
    else:
        # No company access - only org-level data
        query = query.filter(Model.company_id.is_(None))
```

## Migration Strategy

### Database Migration
```sql
-- Add company_id columns to all relevant tables
ALTER TABLE tasks ADD COLUMN company_id INTEGER REFERENCES companies(id);
ALTER TABLE task_projects ADD COLUMN company_id INTEGER REFERENCES companies(id);
ALTER TABLE customers ADD COLUMN company_id INTEGER REFERENCES companies(id);
ALTER TABLE vendors ADD COLUMN company_id INTEGER REFERENCES companies(id);
ALTER TABLE products ADD COLUMN company_id INTEGER REFERENCES companies(id);

-- Create indexes for performance
CREATE INDEX idx_task_company ON tasks(company_id);
CREATE INDEX idx_customer_company ON customers(company_id);
-- ... etc for all tables
```

### Data Migration Logic
```sql
-- Auto-assign existing records to companies for single-company organizations
UPDATE tasks 
SET company_id = (
    SELECT MIN(id) FROM companies 
    WHERE organization_id = tasks.organization_id
)
WHERE organization_id IN (
    SELECT organization_id FROM companies 
    GROUP BY organization_id HAVING COUNT(*) = 1
);
```

### Backwards Compatibility
- **Existing Data**: All existing records remain accessible at organization level
- **Single Company Orgs**: Records automatically assigned to the company
- **Multi-Company Orgs**: Records remain organization-level (company_id=NULL) until manually assigned
- **API Compatibility**: All existing endpoints continue to work

## Usage Examples

### Frontend Integration
```javascript
// Get user's companies for company selector
const companies = await api.get('/companies/');

// Create task with company context
const task = await api.post('/tasks/', {
    title: 'New Task',
    company_id: selectedCompanyId
});

// Filter data by company
const tasks = await api.get(`/tasks/?company_id=${companyId}`);
const customers = await api.get(`/customers/?company_id=${companyId}`);
```

### Backend Service Integration
```python
# In any service that needs company scoping
class TaskService:
    def get_user_tasks(self, user_id: int, company_id: Optional[int] = None):
        rbac = RBACService(self.db)
        
        # Get accessible companies
        user_companies = rbac.get_user_companies(user_id)
        
        # Build query with company filtering
        if company_id:
            rbac.enforce_company_access(user_id, company_id)
            return self.db.query(Task).filter(Task.company_id == company_id)
        else:
            return self.db.query(Task).filter(
                or_(
                    Task.company_id.in_(user_companies),
                    Task.company_id.is_(None)
                )
            )
```

## Security Considerations

### Access Control
- ✅ **Company Validation**: All operations validate user's company access
- ✅ **Permission Enforcement**: RBAC permissions enforced at company level  
- ✅ **Data Isolation**: Users cannot access unauthorized company data
- ✅ **Audit Trails**: All operations include company context in logs

### Performance
- ✅ **Database Indexes**: All company_id fields are indexed
- ✅ **Query Optimization**: Efficient filtering by user's accessible companies
- ✅ **Minimal Overhead**: Company checks use existing RBAC infrastructure

## Testing

### Test Coverage
```python
# Example test scenarios implemented
def test_company_scoping():
    # User with single company - auto assignment
    # User with multiple companies - requires company_id
    # User cannot access unauthorized company data
    # Company admin can access company-specific data
    # Organization admin can access all company data
```

## Benefits

### For Organizations
- **Multi-Company Support**: Single instance supports multiple business entities
- **Data Isolation**: Complete separation between company data
- **Flexible User Assignment**: Users can work across multiple companies
- **Scalable Architecture**: Easy to add new companies without data migration

### For Developers  
- **Consistent Patterns**: Same company scoping logic across all models
- **RBAC Integration**: Leverages existing permission system
- **Backwards Compatible**: No breaking changes to existing functionality
- **Well-Documented**: Clear patterns for adding company scoping to new models

### For Users
- **Simplified Interface**: Automatic company assignment when applicable
- **Multi-Company Workflow**: Seamless switching between company contexts  
- **Secure Access**: Cannot accidentally access wrong company data
- **Flexible Permissions**: Company-specific admin roles

## Next Steps

1. **Additional Models**: Apply company scoping to remaining business models
2. **Frontend Updates**: Update UI components to support company selection
3. **Reporting**: Enhance reports to support company-level filtering
4. **API Documentation**: Update OpenAPI specs with company_id parameters
5. **Performance Monitoring**: Monitor query performance with new indexes

This implementation provides a solid foundation for true multi-company architecture while maintaining simplicity and backwards compatibility.