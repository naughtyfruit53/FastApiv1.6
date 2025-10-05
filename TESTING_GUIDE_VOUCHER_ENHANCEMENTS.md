# Testing Guide for Voucher Enhancements

This guide provides test cases for the voucher system enhancements. Due to the gitignore pattern blocking `test_*.py` files, these tests should be integrated into the existing test suite or the pattern should be updated.

## Test Implementation Options

1. **Add to existing test files** in the `/tests` directory
2. **Update `.gitignore`** to allow `tests/test_*.py` specifically
3. **Rename test file** to follow a different convention (e.g., `voucher_enhancements_tests.py`)

## Test Cases

### 1. Voucher Number Generation Tests

#### Test: Voucher number with prefix enabled
```python
async def test_voucher_number_with_prefix():
    """Test voucher number generation with prefix enabled"""
    # Setup: Create org settings with prefix="TEST"
    # Action: Generate voucher number
    # Assert: Should start with "TEST-PO/"
```

#### Test: Voucher number without prefix
```python
async def test_voucher_number_without_prefix():
    """Test voucher number generation without prefix"""
    # Setup: Create org settings with prefix disabled
    # Action: Generate voucher number
    # Assert: Should start with "PO/" (no prefix)
```

#### Test: Quarterly reset period
```python
async def test_voucher_number_quarterly_reset():
    """Test voucher number with quarterly reset"""
    # Setup: Set counter_reset_period to QUARTERLY
    # Action: Generate voucher number
    # Assert: Should include "/Q1/", "/Q2/", "/Q3/", or "/Q4/"
```

#### Test: Monthly reset period
```python
async def test_voucher_number_monthly_reset():
    """Test voucher number with monthly reset"""
    # Setup: Set counter_reset_period to MONTHLY
    # Action: Generate voucher number
    # Assert: Should include month abbreviation (JAN, FEB, etc.)
```

#### Test: Annual reset period (default)
```python
async def test_voucher_number_annual_reset():
    """Test voucher number with annual reset (default)"""
    # Setup: Set counter_reset_period to ANNUALLY
    # Action: Generate voucher number
    # Assert: Should be format "PO/2526/00001"
```

### 2. Email Template Tests

#### Test: Create voucher email template
```python
async def test_create_voucher_email_template():
    """Test creating a voucher email template"""
    # Action: Create VoucherEmailTemplate
    # Assert: Template saved with correct fields
```

#### Test: Unique constraint per org/voucher/entity
```python
async def test_unique_email_template_constraint():
    """Test unique constraint on templates"""
    # Action: Try to create duplicate template
    # Assert: Should raise IntegrityError
```

#### Test: Fetch default template via API
```python
async def test_get_default_email_template():
    """Test fetching default email template"""
    # Action: GET /api/v1/voucher-email-templates/default/purchase_order/vendor
    # Assert: Returns correct default template
```

#### Test: Variable substitution in templates
```python
async def test_email_template_variable_substitution():
    """Test variable substitution in email templates"""
    # Action: Apply template with variables
    # Assert: Variables replaced with actual values
```

### 3. Email Privacy Tests

#### Test: No system email fallback
```python
async def test_send_voucher_email_requires_user_account():
    """Test that voucher email requires user email account"""
    # Action: Try to send voucher email without user account
    # Assert: Should fail with clear error message
```

#### Test: Send with user account
```python
async def test_send_voucher_email_with_user_account():
    """Test successful email send with user account"""
    # Setup: User with connected email account
    # Action: Send voucher email
    # Assert: Success, email sent from user's account
```

### 4. Voucher Format Template Tests

#### Test: Create format template
```python
async def test_create_voucher_format_template():
    """Test creating a voucher format template"""
    # Action: Create VoucherFormatTemplate with config
    # Assert: Template saved with correct JSON config
```

#### Test: System templates cannot be modified
```python
async def test_cannot_modify_system_template():
    """Test that system templates are read-only"""
    # Action: Try to update is_system_template=True template
    # Assert: Should fail with 403 Forbidden
```

#### Test: Org settings reference template
```python
async def test_org_settings_template_reference():
    """Test org settings can reference a template"""
    # Action: Set voucher_format_template_id in org settings
    # Assert: Reference is saved and retrievable
```

### 5. Organization Settings Tests

#### Test: Get organization settings
```python
async def test_get_organization_settings():
    """Test fetching organization settings"""
    # Action: GET /api/v1/organizations/settings
    # Assert: Returns settings with new fields
```

#### Test: Update voucher prefix
```python
async def test_update_voucher_prefix():
    """Test updating voucher prefix"""
    # Action: PUT with voucher_prefix="TEST"
    # Assert: Setting updated, max 5 chars enforced
```

#### Test: Update counter reset period
```python
async def test_update_counter_reset_period():
    """Test updating counter reset period"""
    # Action: PUT with voucher_counter_reset_period="quarterly"
    # Assert: Setting updated
```

#### Test: Select format template
```python
async def test_select_format_template():
    """Test selecting a format template"""
    # Action: PUT with voucher_format_template_id
    # Assert: Template selection saved
```

### 6. API Endpoint Tests

#### Test: List email templates
```python
async def test_list_email_templates():
    """Test listing voucher email templates"""
    # Action: GET /api/v1/voucher-email-templates/
    # Assert: Returns list of templates for organization
```

#### Test: List format templates
```python
async def test_list_format_templates():
    """Test listing voucher format templates"""
    # Action: GET /api/v1/voucher-format-templates/
    # Assert: Returns system and custom templates
```

#### Test: Get system default templates
```python
async def test_get_system_default_templates():
    """Test getting system default templates"""
    # Action: GET /api/v1/voucher-format-templates/system/defaults
    # Assert: Returns only system templates
```

### 7. Integration Tests

#### Test: Complete voucher creation flow
```python
async def test_complete_voucher_creation_with_email():
    """Test full flow: create voucher, generate PDF, send email"""
    # Setup: User with email, org with settings
    # Action: Create voucher, generate PDF, send email
    # Assert: Voucher number uses org settings, email sent with template
```

#### Test: Voucher number sequence
```python
async def test_voucher_number_sequence():
    """Test voucher numbers increment correctly"""
    # Action: Create 3 vouchers in same period
    # Assert: Numbers are 00001, 00002, 00003
```

#### Test: Period reset behavior
```python
async def test_period_reset_behavior():
    """Test counter resets at period boundary"""
    # Setup: Create voucher at end of period
    # Action: Create voucher in next period
    # Assert: Counter reset to 00001
```

## Manual Testing Checklist

### Email Privacy
- [ ] Try sending voucher email without connected email account
- [ ] Verify error message appears clearly
- [ ] Connect email account (Gmail/Outlook)
- [ ] Send voucher email successfully
- [ ] Verify email arrives from user's address (not system)

### Email Templates
- [ ] Navigate to voucher email templates
- [ ] Create custom template for Purchase Order + Vendor
- [ ] Use variables in subject and body
- [ ] Create voucher and download PDF
- [ ] Verify email dialog shows custom template
- [ ] Edit and send email

### Chatbot
- [ ] Verify chatbot appears in bottom-right corner
- [ ] Click to open chatbot
- [ ] Test commands: "open vendors", "add customer", "low stock"
- [ ] Verify navigation works
- [ ] Test multiple commands in succession
- [ ] Verify chatbot persists across page navigation

### Attachment UI
- [ ] Open email with multiple attachments
- [ ] Verify exact count shown (e.g., "3 attachments")
- [ ] Click to expand attachment list
- [ ] Verify file icons match file types
- [ ] Click to download each attachment
- [ ] Test with different attachment counts (0, 1, 5+)

### Voucher Prefix
- [ ] Navigate to Settings → Voucher Settings
- [ ] Enable prefix, enter "TEST"
- [ ] Verify preview updates to "TEST-PO/2526/00001"
- [ ] Create new voucher
- [ ] Verify voucher number includes prefix
- [ ] Change prefix to "ACME" (5 chars)
- [ ] Create another voucher
- [ ] Verify new prefix used

### Counter Reset
- [ ] Navigate to Settings → Voucher Settings
- [ ] Select "Monthly" reset
- [ ] Verify preview shows month (e.g., "PO/2526/JAN/00001")
- [ ] Create voucher
- [ ] Verify number includes month
- [ ] Change to "Quarterly"
- [ ] Create voucher
- [ ] Verify number includes quarter (Q1, Q2, Q3, or Q4)

### Format Templates
- [ ] Navigate to Settings → Voucher Settings
- [ ] View available templates
- [ ] Select different template
- [ ] Click "Preview Template" (if implemented)
- [ ] Generate voucher PDF
- [ ] Verify PDF uses selected template

### Cross-Feature Testing
- [ ] Enable prefix AND quarterly reset
- [ ] Verify format: "PREFIX-PO/2526/Q1/00001"
- [ ] Create 2 vouchers
- [ ] Verify sequence increments
- [ ] Switch to next quarter (simulated)
- [ ] Verify counter resets

## Performance Testing

### Voucher Number Generation
- Test with 1000+ existing vouchers
- Measure generation time
- Verify no race conditions in concurrent creation

### Email Template Loading
- Test with 50+ templates
- Measure API response time
- Test template caching

### Chatbot Responsiveness
- Test chatbot with 100+ messages in history
- Measure UI responsiveness
- Test memory usage

## Security Testing

### Email Templates
- Test SQL injection in template fields
- Test XSS in template body
- Verify organization isolation (can't access other org templates)

### Voucher Settings
- Verify only org admins can modify settings
- Test authorization for non-admin users
- Verify organization isolation

### API Endpoints
- Test authentication required
- Test authorization per endpoint
- Test rate limiting

## Error Handling

### Email Sending
- Test with invalid email address
- Test with disconnected email account
- Test with expired OAuth token
- Verify error messages are clear

### Voucher Creation
- Test with invalid prefix (>5 chars)
- Test with invalid counter reset period
- Test with non-existent template ID
- Verify validation errors

### Chatbot
- Test with malformed commands
- Test with very long messages
- Test rapid successive commands
- Verify graceful error handling

## Browser Compatibility

Test chatbot and UI components in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility Testing

- [ ] Test chatbot with keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Test attachment UI with keyboard
- [ ] Verify ARIA labels
- [ ] Test color contrast

## Documentation Verification

- [ ] All API endpoints documented
- [ ] Examples work as described
- [ ] Troubleshooting section accurate
- [ ] Screenshots up to date (if any)

## Rollback Plan

If issues occur in production:
1. Disable chatbot by removing from _app.tsx
2. Revert email template API if causing errors
3. Disable prefix/counter reset via organization settings
4. Revert to system email fallback if needed (emergency only)

## Future Test Additions

As features expand:
- E2E tests with Playwright/Cypress
- Load testing with K6
- Chaos testing for resilience
- Multi-tenant isolation tests
- Compliance testing (GDPR, etc.)
