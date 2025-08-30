# WhatsApp OTP Authentication Configuration Guide

This document provides comprehensive instructions for configuring WhatsApp OTP authentication in the TRITIQ ERP system.

## Overview

The system supports multiple OTP delivery methods:
- **WhatsApp** (preferred) - Via Brevo (SendinBlue) API
- **Email** (fallback) - Via Brevo or SMTP
- **Auto** - Attempts WhatsApp first, falls back to email

## Prerequisites

1. **Brevo Account**: Sign up at [brevo.com](https://brevo.com) (formerly SendinBlue)
2. **WhatsApp Business Account**: Required for WhatsApp messaging
3. **WhatsApp Template Approval**: Templates must be approved by WhatsApp

## Configuration Steps

### 1. Brevo API Setup

1. Create a Brevo account and verify your identity
2. Go to API Keys section in your Brevo dashboard
3. Generate a new API key
4. Note your sender phone number (must be WhatsApp Business verified)

### 2. WhatsApp Template Creation

WhatsApp requires pre-approved templates for business messaging:

1. In Brevo dashboard, navigate to WhatsApp > Templates
2. Create a new template for OTP messages
3. Use a format like:
   ```
   🔐 {{company_name}} Security Code
   
   Your OTP: {{otp_code}}
   
   Valid for 10 minutes. Do not share this code.
   ```
4. Submit for WhatsApp approval (can take 24-48 hours)
5. Note the template ID once approved

### 3. Environment Variables

Add the following to your `.env` file:

```bash
# Brevo API Configuration
BREVO_API_KEY=your-brevo-api-key
BREVO_FROM_EMAIL=your-verified-email@domain.com

# WhatsApp Configuration
WHATSAPP_PROVIDER=brevo
WHATSAPP_SENDER_NUMBER=+1234567890
WHATSAPP_OTP_TEMPLATE_ID=123

# Optional: Force specific delivery method
# WHATSAPP_DELIVERY_METHOD=auto  # auto, whatsapp, email
```

### 4. Free Tier Limits

Brevo offers generous free tiers:

#### Email
- **300 emails/day** on free plan
- Unlimited contacts
- No setup fees

#### WhatsApp
- **Free tier varies by region**
- Typically includes:
  - 1,000 service messages/month
  - Conversation-based pricing after free tier
  - Template messages are usually free up to limits

#### Cost-Effective Scaling
- Email remains free up to 300/day
- WhatsApp pricing starts around $0.005-0.05 per message
- Consider hybrid approach: WhatsApp for critical OTPs, email for others

## Alternative Providers

The system is designed to be provider-agnostic. You can easily switch to other providers:

### Twilio
```bash
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

### Gupshup
```bash
WHATSAPP_PROVIDER=gupshup
GUPSHUP_API_KEY=your-api-key
GUPSHUP_APP_NAME=your-app-name
```

### MessageBird
```bash
WHATSAPP_PROVIDER=messagebird
MESSAGEBIRD_API_KEY=your-api-key
MESSAGEBIRD_WHATSAPP_NUMBER=+1234567890
```

## Implementation Details

### Backend Integration

The system uses a provider pattern for easy switching:

```python
# Extend for new providers
class CustomWhatsAppProvider(WhatsAppProvider):
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login"):
        # Your implementation
        pass
```

### Frontend Integration

The login form automatically detects WhatsApp capability:

```typescript
// Auto-detection based on phone number
const deliveryMethod = phoneNumber ? 'auto' : 'email';
await authService.requestOTP(email, phoneNumber, deliveryMethod);
```

## Testing Configuration

### 1. Test WhatsApp Capability

```bash
# Test if WhatsApp service is configured
curl -X POST http://localhost:8000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "phone_number": "+919876543210",
    "delivery_method": "whatsapp"
  }'
```

### 2. Test Email Fallback

```bash
# Test email-only delivery
curl -X POST http://localhost:8000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "delivery_method": "email"
  }'
```

### 3. Monitor Logs

Check application logs for delivery status:

```bash
# Look for delivery confirmations
grep "OTP delivery completed" app.log

# Check for WhatsApp failures
grep "WhatsApp delivery failed" app.log
```

## Troubleshooting

### Common Issues

1. **WhatsApp Template Not Approved**
   - Error: "Template not found"
   - Solution: Wait for WhatsApp approval or use text-based messages

2. **Invalid Phone Number Format**
   - Error: "Invalid contact number"
   - Solution: Ensure number includes country code (+91XXXXXXXXXX)

3. **Brevo Rate Limits**
   - Error: "Rate limit exceeded"
   - Solution: Implement request queuing or upgrade plan

4. **WhatsApp Business Account Issues**
   - Error: "Sender number not verified"
   - Solution: Complete WhatsApp Business verification

### Debugging Steps

1. **Check Configuration**
   ```python
   from app.services.whatsapp_service import whatsapp_service
   print(f"Available: {whatsapp_service.is_available()}")
   ```

2. **Test Phone Number Formatting**
   ```python
   # Should format correctly
   provider.send_otp("+919876543210", "123456")  # ✓
   provider.send_otp("9876543210", "123456")     # ✓ (adds +91)
   provider.send_otp("invalid", "123456")        # ✗
   ```

3. **Monitor API Responses**
   - Enable debug logging for detailed API responses
   - Check Brevo dashboard for delivery status

## Security Considerations

### Phone Number Privacy
- Phone numbers are used only for OTP delivery
- Not stored in database permanently
- Logged for audit purposes only

### OTP Security
- 6-digit codes with 10-minute expiration
- Rate limiting prevents brute force attacks
- Hashed storage in database

### Provider Security
- API keys stored securely in environment variables
- TLS encryption for all API communications
- Audit logging for all OTP operations

## Monitoring and Analytics

### Key Metrics to Track

1. **Delivery Success Rates**
   - WhatsApp delivery rate
   - Email fallback usage
   - Overall OTP success rate

2. **Performance Metrics**
   - OTP delivery time
   - Verification completion rate
   - User preference patterns

3. **Cost Analysis**
   - WhatsApp message costs
   - Email volume
   - Provider efficiency

### Recommended Alerts

- WhatsApp service downtime
- High email fallback rate
- OTP delivery failures > 5%
- Rate limit warnings

## Migration Strategy

### Gradual Rollout

1. **Phase 1**: Configure WhatsApp for select users
2. **Phase 2**: Enable auto-detection for all users
3. **Phase 3**: Monitor and optimize delivery methods
4. **Phase 4**: Consider making WhatsApp default for mobile users

### A/B Testing

Test user preference and delivery success:

```python
# Route users based on criteria
delivery_method = "whatsapp" if user.mobile_preferred else "email"
```

## Support and Maintenance

### Regular Tasks

1. **Monthly**: Review delivery metrics and costs
2. **Quarterly**: Update WhatsApp templates if needed
3. **Annually**: Evaluate provider performance and alternatives

### Emergency Procedures

1. **WhatsApp Service Down**: System automatically falls back to email
2. **Brevo Outage**: Configure secondary SMTP provider
3. **Rate Limit Hit**: Implement request queuing

## Cost Optimization

### Best Practices

1. **Smart Routing**: Use email for non-critical OTPs
2. **Template Optimization**: Minimize WhatsApp template variations
3. **User Preferences**: Let users choose preferred method
4. **Batch Operations**: Group operations to minimize API calls

### Budget Planning

- Start with Brevo free tier: $0/month
- Scale to paid plans: ~$25-100/month for most organizations
- WhatsApp costs: ~$0.01-0.05 per OTP message
- ROI: Improved security and user experience

## Conclusion

WhatsApp OTP authentication provides enhanced security and user experience. The system's flexible architecture ensures easy provider switching and graceful fallback to email when needed.

For additional support or custom provider integration, refer to the developer documentation or contact the development team.