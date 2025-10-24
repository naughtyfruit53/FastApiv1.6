# Automated Test Suite Documentation

## Voucher Numbering and Conflict Detection Tests

This document describes the automated test suite for the voucher date-based numbering and conflict detection feature.

### Test File Location
**Recommended**: `tests/test_voucher_numbering.py`

Note: The actual test file is created but may be gitignored. Reference this documentation for implementation.

---

## Test Implementation

### Dependencies
```python
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
```

### Test Classes

#### 1. TestVoucherNumberGeneration

Tests voucher number generation with various dates and scenarios.

**Test Cases:**

- `test_generate_number_current_date()`
  - **Purpose**: Verify number generation with current date
  - **Expected**: Returns valid voucher number containing current year
  - **Endpoint**: `GET /api/v1/payment-vouchers/next-number?voucher_date={date}`

- `test_generate_number_without_date()`
  - **Purpose**: Test default behavior when date not specified
  - **Expected**: Returns voucher number using current date
  - **Endpoint**: `GET /api/v1/payment-vouchers/next-number`

- `test_generate_number_backdated()`
  - **Purpose**: Verify backdated voucher number generation
  - **Expected**: Returns valid number for past date
  - **Endpoint**: `GET /api/v1/payment-vouchers/next-number?voucher_date={past_date}`

- `test_sequential_numbers_same_date()`
  - **Purpose**: Ensure sequential numbering for same date
  - **Expected**: Second call returns incremented number
  - **Workflow**: 
    1. Get number for date X
    2. Create voucher with that number
    3. Get number again for date X
    4. Verify increment

---

#### 2. TestBackdatedConflictDetection

Tests conflict detection when creating backdated vouchers.

**Test Cases:**

- `test_no_conflict_when_latest()`
  - **Purpose**: Verify no conflict for future dates
  - **Expected**: `has_conflict: false`, `later_voucher_count: 0`
  - **Endpoint**: `GET /api/v1/payment-vouchers/check-backdated-conflict?voucher_date={future_date}`

- `test_conflict_when_backdated()`
  - **Purpose**: Detect conflicts for backdated entries
  - **Setup**: Create voucher with current date
  - **Test**: Check conflict for past date
  - **Expected**: `has_conflict: true`, `later_voucher_count >= 1`

- `test_conflict_includes_suggested_date()`
  - **Purpose**: Verify suggested date is provided
  - **Expected**: Response includes valid `suggested_date` field
  - **Validation**: Suggested date >= current date

---

#### 3. TestVoucherCreation

Tests end-to-end voucher creation with numbering.

**Test Cases:**

- `test_create_with_current_date()`
  - **Purpose**: Create voucher with current date
  - **Expected**: Success with auto-generated voucher number
  - **Endpoint**: `POST /api/v1/payment-vouchers/`

- `test_create_with_backdated_entry()`
  - **Purpose**: Create backdated voucher
  - **Expected**: Success despite being backdated
  - **Note**: Warning should be shown in UI (not enforced by API)

---

#### 4. TestMultipleVoucherTypes

Tests conflict detection across different voucher types.

**Test Cases:**

- `test_payment_voucher_conflicts()`
  - Tests payment voucher specific endpoints

- `test_receipt_voucher_conflicts()`
  - Tests receipt voucher specific endpoints

- `test_journal_voucher_conflicts()`
  - Tests journal voucher endpoints (with chart_account_id)

- `_test_voucher_type_conflict()` (Helper)
  - Reusable test logic for any voucher type
  - Parameters: client, auth_headers, endpoint, extra_data

---

## Running the Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio httpx
```

### Execute Tests
```bash
# Run all voucher numbering tests
pytest tests/test_voucher_numbering.py -v

# Run specific test class
pytest tests/test_voucher_numbering.py::TestVoucherNumberGeneration -v

# Run specific test
pytest tests/test_voucher_numbering.py::TestBackdatedConflictDetection::test_conflict_when_backdated -v

# Run with coverage
pytest tests/test_voucher_numbering.py --cov=app.services.voucher_service --cov-report=html
```

---

## Test Fixtures

### auth_headers
```python
@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Get authentication headers for API requests"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### client
```python
@pytest.fixture
async def client():
    """Create async HTTP client for testing"""
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

---

## Coverage Goals

- **API Endpoints**: 100% coverage of numbering and conflict endpoints
- **Business Logic**: All VoucherNumberService methods tested
- **Error Scenarios**: Network errors, invalid dates, missing data
- **Edge Cases**: Month boundaries, year boundaries, concurrent requests

---

## Integration with CI/CD

### GitHub Actions Workflow
```yaml
name: Test Voucher Numbering

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: pytest tests/test_voucher_numbering.py -v
```

---

## Expected Test Results

All tests should pass with the following characteristics:

- **Execution Time**: < 10 seconds for full suite
- **Coverage**: > 90% for voucher numbering service
- **Reliability**: 100% pass rate (no flaky tests)
- **Isolation**: Tests don't depend on each other

---

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Ensure test user exists in database
   - Verify credentials in fixture

2. **Database State**
   - Use database transactions with rollback
   - Or use test database that's cleared between runs

3. **Async Issues**
   - Ensure pytest-asyncio is installed
   - Mark tests with `@pytest.mark.asyncio`

4. **Import Errors**
   - Verify PYTHONPATH includes project root
   - Check all dependencies are installed

---

## Future Enhancements

1. **Performance Tests**
   - Load testing with concurrent requests
   - Stress testing with high volume

2. **Security Tests**
   - SQL injection attempts
   - XSS in voucher numbers
   - Cross-organization data access

3. **Edge Case Tests**
   - Leap year boundaries
   - Fiscal year changes
   - Time zone handling

4. **Mock Tests**
   - Test with mocked database
   - Faster execution for unit tests

---

## Maintenance

- **Update Frequency**: After any changes to voucher numbering logic
- **Review Schedule**: Monthly
- **Owner**: QA Team
- **Last Updated**: 2025-10-24

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- API Documentation: `API_DOCUMENTATION.md`
- QA Report: `docs/QA_REPORT.md`
