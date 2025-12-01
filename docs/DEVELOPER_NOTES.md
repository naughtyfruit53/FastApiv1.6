# Developer Notes

Developer documentation for TritIQ Business Suite API contracts, HR data model, and testing instructions.

---

## Table of Contents

1. [API Contracts & DTO Standards](#api-contracts--dto-standards)
2. [HR Data Model (Phase 2)](#hr-data-model-phase-2)
3. [Test Instructions](#test-instructions)
4. [Feature Flags](#feature-flags)
5. [Export Contract Formats](#export-contract-formats)

---

## API Contracts & DTO Standards

### General Conventions

All API endpoints follow these conventions:

| Convention | Standard |
|------------|----------|
| **URL Format** | `/api/v1/{module}/{resource}` |
| **Request Body** | JSON with snake_case keys |
| **Response Body** | JSON with snake_case keys |
| **Date Format** | ISO 8601 (`YYYY-MM-DD`) |
| **DateTime Format** | ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SSZ`) |
| **Time Format** | ISO 8601 (`HH:MM:SS`) |
| **Decimal Precision** | 2 decimal places for currency, configurable for others |
| **Pagination** | `skip` (offset) and `limit` query parameters |

### Authentication

All endpoints (except auth/demo) require JWT bearer token:

```http
Authorization: Bearer <jwt_token>
```

### Standard Response Formats

**Success Response:**
```json
{
  "id": 123,
  "field": "value",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**List Response:**
```json
[
  { "id": 1, "field": "value" },
  { "id": 2, "field": "value" }
]
```

**Error Response:**
```json
{
  "detail": "Error message describing the issue"
}
```

### Pydantic Schema Patterns

**Create Schema:** Fields required for creation
```python
class DepartmentCreate(BaseModel):
    name: str = Field(..., description="Department name")
    code: str = Field(..., description="Unique code")
    is_active: bool = Field(default=True)
```

**Update Schema:** All fields optional
```python
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
```

**Response Schema:** Full object with computed fields
```python
class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
```

### Multi-tenant Scoping

All data is scoped by `organization_id`. The enforcement module automatically:
1. Extracts `organization_id` from JWT claims
2. Filters queries to organization scope
3. Validates access permissions via RBAC

---

## HR Data Model (Phase 2)

### Core Entities

```
┌─────────────────────────────────────────────────────────────────┐
│                       HR Core Models                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Department  │────▶│   Position   │     │  Work Shift  │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Employee Profile                         │      │
│  │  - Personal info, documents, banking                  │      │
│  │  - Employment status, dates                           │      │
│  └──────────────────────────────────────────────────────┘      │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐        │
│  │ Attendance │      │   Leave    │      │ Performance│        │
│  │  Records   │      │Applications│      │  Reviews   │        │
│  └────────────┘      └────────────┘      └────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2 Extended Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    HR Phase 2 Models                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────┐           │
│  │  Attendance Policy   │   │    Leave Balance     │           │
│  │  - Accrual rules     │   │  - Per employee/type │           │
│  │  - Overtime calc     │   │  - Year tracking     │           │
│  │  - Late thresholds   │   │  - Carry forward     │           │
│  └──────────────────────┘   └──────────────────────┘           │
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────┐           │
│  │     Timesheet        │   │   Payroll Arrear     │           │
│  │  - Weekly/monthly    │   │  - Salary revisions  │           │
│  │  - Project hours     │   │  - Bonus/allowances  │           │
│  │  - Approval flow     │   │  - Retro adjustments │           │
│  └──────────────────────┘   └──────────────────────┘           │
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────┐           │
│  │ Statutory Deduction  │   │  Payroll Approval    │           │
│  │  - PF, ESI, TDS      │   │  - Multi-level       │           │
│  │  - Slab-based calc   │   │  - Role-based        │           │
│  └──────────────────────┘   └──────────────────────┘           │
│                                                                 │
│  ┌──────────────────────┐                                      │
│  │ Bank Payment Export  │                                      │
│  │  - NEFT/RTGS files   │                                      │
│  │  - Bank-specific     │                                      │
│  └──────────────────────┘                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 4 Scaffolding Models (Feature-flagged)

```
┌─────────────────────────────────────────────────────────────────┐
│                Phase 4 Scaffolding (Feature-flagged)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────┐           │
│  │ HR Analytics Snapshot│   │   Position Budget    │           │
│  │  - Headcount metrics │   │  - Fiscal year plan  │           │
│  │  - Attrition rates   │   │  - Budget vs actual  │           │
│  │  - Payroll costs     │   │  - Variance tracking │           │
│  └──────────────────────┘   └──────────────────────┘           │
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────┐           │
│  │  Employee Transfer   │   │ Integration Adapter  │           │
│  │  - Dept/location     │   │  - SSO/IdP hooks     │           │
│  │  - Promotion history │   │  - Payroll providers │           │
│  │  - Salary changes    │   │  - Hardware APIs     │           │
│  └──────────────────────┘   └──────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Database Relationships

```sql
-- Department self-referencing hierarchy
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    parent_id INTEGER REFERENCES departments(id),
    manager_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL,
    UNIQUE(organization_id, code)
);

-- Employee profile extends user
CREATE TABLE employee_profiles (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    employee_code VARCHAR(50) NOT NULL,
    reporting_manager_id INTEGER REFERENCES users(id),
    UNIQUE(organization_id, employee_code)
);

-- Attendance record per employee per day
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    employee_id INTEGER NOT NULL REFERENCES employee_profiles(id),
    attendance_date DATE NOT NULL,
    UNIQUE(organization_id, employee_id, attendance_date)
);
```

---

## Test Instructions

### Running Smoke Tests

```bash
# Run all smoke tests
pytest tests/test_smoke.py -v

# Run specific test class
pytest tests/test_smoke.py::TestHRSmoke -v

# Run with coverage
pytest tests/test_smoke.py --cov=app --cov-report=html
```

### Smoke Test Categories

| Test Class | Coverage |
|------------|----------|
| `TestAuthenticationSmoke` | Auth, password reset, demo endpoints |
| `TestVoucherSmoke` | Voucher module imports |
| `TestHRSmoke` | HR models and schemas |
| `TestAISmoke` | AI and chatbot endpoints |
| `TestPhase4ScaffoldingSmoke` | Phase 4 feature-flagged models |
| `TestPayrollSmoke` | Payroll models and schemas |
| `TestLinkageValidation` | Frontend-backend linkage script |

### Running Linkage Validation

```bash
# Run linkage validation script
python scripts/validate_linkages.py

# Output includes:
# - Validation score (0-100)
# - Errors (missing critical linkages)
# - Warnings (potential gaps)
# - JSON report at docs/linkage_validation_report.json
```

### API Testing with httpx

```python
import httpx

# Login and get token
async with httpx.AsyncClient(base_url="http://localhost:8000/api/v1") as client:
    # Login
    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    
    # Use authenticated endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/hr/employees", headers=headers)
    employees = response.json()
```

---

## Feature Flags

### Environment Variables

```bash
# Phase 4 features (disabled by default)
ENABLE_HR_ANALYTICS=false
ENABLE_POSITION_BUDGETING=false
ENABLE_EMPLOYEE_TRANSFERS=false
ENABLE_INTEGRATION_ADAPTERS=false

# Extended routers
ENABLE_EXTENDED_ROUTERS=false
ENABLE_AI_ANALYTICS=false
```

### Feature Flag Check Pattern

```python
import os

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature flag is enabled."""
    env_var = f"ENABLE_{feature_name.upper()}"
    return os.getenv(env_var, "false").lower() == "true"

# Usage in endpoint
@router.get("/analytics/snapshots")
async def get_analytics(
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    if not is_feature_enabled("hr_analytics"):
        raise HTTPException(status_code=403, detail="Feature not enabled")
    # ... endpoint logic
```

### Database Model Feature Flags

Phase 4 models include `is_feature_enabled` column:
```python
class HRAnalyticsSnapshot(Base):
    # ... fields
    is_feature_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
```

---

## Export Contract Formats

### CSV Export Format

```csv
employee_code,employee_name,department,gross_pay,deductions,net_pay,pay_date
EMP001,John Doe,Engineering,75000.00,15000.00,60000.00,2024-01-31
EMP002,Jane Smith,Marketing,65000.00,13000.00,52000.00,2024-01-31
```

### JSON Export Format

```json
{
  "export_date": "2024-01-31T10:00:00Z",
  "period": "January 2024",
  "records": [
    {
      "employee_code": "EMP001",
      "employee_name": "John Doe",
      "department": "Engineering",
      "gross_pay": 75000.00,
      "deductions": 15000.00,
      "net_pay": 60000.00,
      "pay_date": "2024-01-31"
    }
  ],
  "summary": {
    "total_employees": 1,
    "total_gross": 75000.00,
    "total_deductions": 15000.00,
    "total_net": 60000.00
  }
}
```

### Export API Request Schema

```python
class PayrollExportRequest(BaseModel):
    payroll_period_id: int
    export_format: ExportFormat  # csv, json, xlsx
    include_components: bool = True
    include_deductions: bool = True
    department_ids: Optional[List[int]] = None

class ExportFormat(BaseModel):
    format: str = "csv"  # csv, json, xlsx
    include_headers: bool = True
    date_format: str = "%Y-%m-%d"
    decimal_places: int = 2
```

### Bank Payment Export Formats

**NEFT/RTGS Format:**
```
NEFT|{beneficiary_name}|{account_number}|{ifsc}|{amount}|{narration}
```

**Generic CSV:**
```csv
beneficiary_name,account_number,bank_name,ifsc_code,amount,payment_date
John Doe,1234567890,HDFC Bank,HDFC0001234,60000.00,2024-01-31
```

---

## Integration Adapter Contracts

### SSO/IdP Adapter Configuration

```json
{
  "adapter_type": "sso",
  "provider": "azure_ad",
  "config": {
    "client_id": "<azure_client_id>",
    "client_secret": "<azure_client_secret>",
    "tenant_id": "<azure_tenant_id>",
    "auth_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
    "token_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
    "scopes": ["openid", "profile", "email"]
  }
}
```

### Payroll Provider Adapter Configuration

```json
{
  "adapter_type": "payroll_provider",
  "provider": "adp",
  "config": {
    "api_key": "<adp_api_key>",
    "api_url": "https://api.adp.com/v1",
    "company_id": "<company_identifier>",
    "sync_frequency": "daily"
  }
}
```

### Attendance Hardware Adapter Configuration

```json
{
  "adapter_type": "attendance_hardware",
  "provider": "zkteco",
  "config": {
    "device_ip": "192.168.1.100",
    "port": 4370,
    "api_key": "<device_api_key>",
    "sync_method": "push"  // push, pull
  }
}
```

---

**Last Updated:** 2025-12-01  
**Version:** 1.6.0-PRA
