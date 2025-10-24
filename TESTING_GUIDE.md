# Voucher System Testing Guide

## Overview
This guide outlines comprehensive testing procedures for the date-based voucher numbering system with conflict detection.

## Backend API Testing

### 1. Voucher Number Generation Tests

Test each endpoint's `/next-number` endpoint with different dates:

```bash
# Test current date (no date parameter)
curl -X GET "http://localhost:8000/api/v1/payment-vouchers/next-number"

# Test specific date (monthly reset)
curl -X GET "http://localhost:8000/api/v1/payment-vouchers/next-number?voucher_date=2024-01-15"

# Test different month (should restart sequence if monthly reset)
curl -X GET "http://localhost:8000/api/v1/payment-vouchers/next-number?voucher_date=2024-02-15"

# Test different quarter (should restart if quarterly reset)
curl -X GET "http/localhost:8000/api/v1/payment-vouchers/next-number?voucher_date=2024-04-15"

# Test different year (should restart for new fiscal year)
curl -X GET "http://localhost:8000/api/v1/payment-vouchers/next-number?voucher_date=2025-04-15"
```

Expected results:
- Same period should increment sequence: 00001, 00002, 00003...
- New period should restart: 00001
- Format should match: PREFIX/YEAR/PERIOD/SEQUENCE

### 2. Backdated Conflict Detection Tests

```bash
# Create a voucher with current date
curl -X POST "http://localhost:8000/api/v1/payment-vouchers/" \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-10-24", ...}'

# Check for conflict with earlier date
curl -X GET "http://localhost:8000/api/v1/payment-vouchers/check-backdated-conflict?voucher_date=2024-10-20"
```

Expected response when conflict exists:
```json
{
  "has_conflict": true,
  "later_voucher_count": 1,
  "suggested_date": "2024-10-24",
  "period": "ANNUAL"  // or "OCT" for monthly, "Q4" for quarterly
}
```

Expected response when no conflict:
```json
{
  "has_conflict": false,
  "later_voucher_count": 0,
  "suggested_date": "2024-10-20",
  "period": "ANNUAL"
}
```

### 3. Create Voucher Tests

Test voucher creation with various dates:

```bash
# Create with current date
POST /api/v1/payment-vouchers/
{
  "date": "2024-10-24",
  "entity_id": 1,
  "entity_type": "Vendor",
  "amount": 1000.00,
  ...
}

# Create with backdated date
POST /api/v1/payment-vouchers/
{
  "date": "2024-10-01",
  "entity_id": 1,
  "entity_type": "Vendor",
  "amount": 1000.00,
  ...
}

# Create with future date
POST /api/v1/payment-vouchers/
{
  "date": "2024-11-15",
  "entity_id": 1,
  "entity_type": "Vendor",
  "amount": 1000.00,
  ...
}
```

Verify:
- Voucher number matches the date's period
- Sequence is correct for that period
- No duplicate voucher numbers

## Frontend Testing

### 1. Date Field Interaction Tests

For each voucher form:

**Test Case 1: Date Change Triggers Number Update**
- Open create form
- Enter a date
- Verify voucher number updates automatically
- Change date to different month
- Verify voucher number changes appropriately

**Test Case 2: Backdated Entry Shows Conflict Modal**
- Create a voucher with today's date
- Open new create form
- Enter a date from last week
- Verify conflict modal appears
- Check modal shows correct information:
  - Number of conflicting vouchers
  - Suggested date
  - Period information

**Test Case 3: Conflict Modal Actions**
- Trigger conflict modal
- Click "Use Suggested Date"
  - Verify date changes to suggested
  - Verify modal closes
  - Verify voucher number updates
- Trigger conflict again
- Click "Proceed Anyway"
  - Verify modal closes
  - Verify original date kept
  - Verify can save voucher
- Trigger conflict again
- Click "Cancel & Review"
  - Verify modal closes
  - Verify date field cleared/reverted

### 2. Edit Mode Tests

**Test Case 4: Edit Existing Voucher**
- Open existing voucher in edit mode
- Verify date field shows existing date
- Verify voucher number is read-only
- Change other fields
- Verify saving works without number change

**Test Case 5: Edit Date in Existing Voucher**
- Open existing voucher in edit mode
- Change the date
- Verify voucher number updates (if applicable)
- Verify conflict detection still works

### 3. Organization Settings Tests

Test with different organization voucher settings:

**Test Case 6: Monthly Reset Period**
- Set organization to monthly reset
- Create voucher in January: Should get JAN in number
- Create voucher in February: Should get FEB and restart sequence
- Verify format: PREFIX/YEAR/MONTH/SEQUENCE

**Test Case 7: Quarterly Reset Period**
- Set organization to quarterly reset
- Create voucher in Jan: Should get Q1
- Create voucher in April: Should get Q2 and restart
- Verify format: PREFIX/YEAR/QUARTER/SEQUENCE

**Test Case 8: Annual Reset Period**
- Set organization to annual reset
- Create vouchers in different months
- Verify all use same sequence
- Verify format: PREFIX/YEAR/SEQUENCE

## Integration Testing

### Scenario 1: Complete Workflow
1. Create initial voucher with current date
2. Create backdated voucher (last month)
   - Verify conflict modal appears
   - Use suggested date
   - Verify voucher created with current date
3. Create future-dated voucher (next month)
   - Verify no conflict
   - Verify appropriate sequence number
4. List all vouchers
   - Verify correct ordering
   - Verify all numbers are unique

### Scenario 2: Multi-User Concurrent Creation
1. User A opens create form with date X
2. User B opens create form with date X
3. User A saves voucher
4. User B tries to save
   - Should get next sequence number
   - Should not conflict

### Scenario 3: Period Transition
1. Create vouchers near end of period (e.g., Oct 31)
2. Create voucher at start of new period (Nov 1)
3. Verify sequence resets appropriately
4. Create backdated voucher for previous period
   - Verify conflict detection works
   - Verify suggested date is end of previous period

## Manual Testing Checklist

For each of the 17 voucher types, verify:

### Payment Voucher
- [ ] Next-number endpoint works
- [ ] Conflict check endpoint works
- [ ] Date change updates number
- [ ] Conflict modal appears for backdated entries
- [ ] All modal actions work
- [ ] Create saves correctly
- [ ] Edit works correctly

### Receipt Voucher
- [ ] Next-number endpoint works
- [ ] Conflict check endpoint works
- [ ] Date change updates number
- [ ] Conflict modal appears for backdated entries
- [ ] All modal actions work
- [ ] Create saves correctly
- [ ] Edit works correctly

*[Repeat for all 17 voucher types]*

## Automated Test Suite

### Backend Unit Tests
Create tests in `/tests/test_voucher_numbering.py`:

```python
import pytest
from datetime import datetime, timedelta

def test_voucher_number_generation_current_date():
    """Test voucher number generation with current date"""
    # Create voucher with today's date
    # Verify number format matches expected pattern
    pass

def test_voucher_number_generation_backdated():
    """Test voucher number generation with backdated entry"""
    # Create voucher with past date
    # Verify number uses that date's period
    pass

def test_conflict_detection_with_existing_vouchers():
    """Test conflict detection when later vouchers exist"""
    # Create voucher with current date
    # Check conflict for earlier date
    # Verify has_conflict is True
    pass

def test_no_conflict_when_latest():
    """Test no conflict when date is latest"""
    # Create voucher with date X
    # Check conflict for date X+1
    # Verify has_conflict is False
    pass

def test_monthly_period_reset():
    """Test voucher numbering with monthly reset"""
    # Set org to monthly reset
    # Create vouchers in different months
    # Verify sequence resets each month
    pass

def test_quarterly_period_reset():
    """Test voucher numbering with quarterly reset"""
    # Set org to quarterly reset
    # Create vouchers in different quarters
    # Verify sequence resets each quarter
    pass

def test_annual_period_reset():
    """Test voucher numbering with annual reset"""
    # Set org to annual reset
    # Create vouchers in different months
    # Verify continuous sequence
    pass
```

### Frontend Integration Tests
Create tests using Playwright or Cypress:

```javascript
describe('Voucher Date-Based Numbering', () => {
  it('should update voucher number when date changes', async () => {
    // Navigate to payment voucher create
    // Enter date
    // Verify voucher number field updates
  });

  it('should show conflict modal for backdated entry', async () => {
    // Create voucher with current date
    // Open new create form
    // Enter past date
    // Verify modal appears
  });

  it('should update date when using suggested date', async () => {
    // Trigger conflict modal
    // Click "Use Suggested Date"
    // Verify date field updated
    // Verify modal closed
  });
});
```

## Performance Testing

### Load Tests
- Create 1000 vouchers with sequential dates
- Measure time to generate each number
- Verify no performance degradation
- Check database query count

### Concurrency Tests
- Simulate 10 concurrent users creating vouchers
- Verify no duplicate numbers
- Verify all conflict checks work correctly

## Regression Testing

Ensure existing functionality still works:
- [ ] Voucher creation without date still works
- [ ] Existing vouchers display correctly
- [ ] Voucher search/filter works
- [ ] Voucher PDF generation works
- [ ] Voucher email sending works
- [ ] Voucher deletion works
- [ ] Voucher status updates work

## Security Testing

- [ ] Verify user can only access their organization's vouchers
- [ ] Verify conflict check doesn't leak other org data
- [ ] Verify SQL injection protection in date parameter
- [ ] Verify XSS protection in conflict modal
- [ ] Verify proper authentication required for all endpoints

## Browser Compatibility

Test frontend in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Android)

## Error Handling

Test error scenarios:
- [ ] Invalid date format
- [ ] Network errors during API calls
- [ ] API timeout
- [ ] Missing required fields
- [ ] Unauthorized access
- [ ] Database connection failure

## QA Sign-off Criteria

Before marking complete:
- [ ] All backend endpoints tested and working
- [ ] All frontend forms tested and working
- [ ] All automated tests passing
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Documentation complete
- [ ] User acceptance testing passed
