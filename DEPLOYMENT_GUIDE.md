# Organization Role Restructuring - Deployment Guide

## Prerequisites
- FastAPI application running
- PostgreSQL database configured
- Redis (optional, for caching)
- SMTP server credentials

## Deployment Steps

### 1. Database Migration
```bash
# Run Alembic migrations
alembic upgrade head

# Verify role tables created
python -c "from app.models.user_models import OrganizationRole; print('✅ Role models available')"
```

### 2. Email Service Configuration
```bash
# Configure email service
python scripts/setup_email_service.py

# Update .env file with SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. User Migration
```bash
# Validate and migrate existing users
python scripts/validate_user_migration.py

# Review migration report
cat migration_report.json
```

### 4. Frontend Deployment
```bash
cd frontend
npm run build
npm start
```

### 5. Validation
```bash
# Validate complete implementation
python scripts/organization_role_validation_demo.py
```

## Post-Deployment
- Train administrators on new role management interface
- Monitor dashboard performance and user adoption
- Collect feedback on role structure and approval workflows
- Schedule regular backup of role and permission data

## Support
- Check ORGANIZATION_ROLE_RESTRUCTURING_COMPLETE.md for detailed implementation info
- Review IMPLEMENTATION_AUDIT_CHECKLIST.md for feature completeness
- Refer to API documentation for endpoint details