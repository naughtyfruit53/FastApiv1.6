# Data Encryption Implementation Guide

## Overview

This document describes the field-level encryption implementation for sensitive data in the FastAPI application. The encryption is transparent to the application logic and provides strong protection for PII, financial data, and other sensitive information.

## Architecture

### Encryption Framework

The encryption framework consists of three main components:

1. **Encryption Utilities** (`app/utils/encryption.py`)
   - Fernet symmetric encryption using cryptography library
   - Environment-based key management
   - Multiple key support for different data types

2. **Encrypted Field Types** (`app/models/encrypted_fields.py`) 
   - Custom SQLAlchemy types for transparent encryption/decryption
   - Specialized types for different data categories
   - Backward compatibility with existing unencrypted data

3. **Model Implementation** (`app/models/encrypted_customer_example.py`)
   - Example model showing encryption best practices
   - Properties for transparent data access
   - Privacy compliance methods

## Key Management

### Environment Variables

Set the following environment variables for encryption keys:

```bash
# Default encryption key
ENCRYPTION_KEY_DEFAULT=<base64-encoded-key>

# Specialized keys for different data types
ENCRYPTION_KEY_PII=<base64-encoded-key>
ENCRYPTION_KEY_FINANCIAL=<base64-encoded-key> 
ENCRYPTION_KEY_CUSTOMER=<base64-encoded-key>
ENCRYPTION_KEY_EMPLOYEE=<base64-encoded-key>
```

### Key Generation

Generate encryption keys using Python:

```python
from cryptography.fernet import Fernet
import base64

# Generate a new key
key = Fernet.generate_key()
key_b64 = base64.b64encode(key).decode()
print(f"ENCRYPTION_KEY_DEFAULT={key_b64}")
```

### Key Rotation

1. Generate new key with different environment variable name
2. Update models to use new key
3. Create migration script to re-encrypt data with new key
4. Remove old key after migration complete

## Usage Examples

### Basic Encrypted Field

```python
from app.models.encrypted_fields import EncryptedPII

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email_encrypted = Column(EncryptedPII(), nullable=False)
    
    # Transparent property access
    @property
    def email(self):
        return self.email_encrypted
    
    @email.setter
    def email(self, value):
        self.email_encrypted = value
```

### Multiple Key Types

```python
from app.models.encrypted_fields import EncryptedPII, EncryptedFinancial

class Customer(Base):
    __tablename__ = "customers"
    
    # PII data (names, emails, phones)
    name_encrypted = Column(EncryptedPII())
    
    # Financial data (bank details, tax IDs)
    bank_details_encrypted = Column(EncryptedFinancial())
```

### Service Layer Usage

```python
def create_customer(db: Session, customer_data: dict):
    customer = Customer(
        name=customer_data["name"],  # Automatically encrypted
        email=customer_data["email"], # Automatically encrypted
        bank_details=customer_data["bank_details"]  # Automatically encrypted
    )
    db.add(customer)
    db.commit()
    return customer

def get_customer(db: Session, customer_id: int):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    # Data is automatically decrypted when accessed
    return {
        "name": customer.name,  # Decrypted automatically
        "email": customer.email,  # Decrypted automatically
    }
```

## Security Best Practices

### Key Management

1. **Never store keys in code** - Always use environment variables or secret management systems
2. **Use different keys for different data types** - Limits blast radius if key is compromised
3. **Rotate keys regularly** - Implement key rotation procedures
4. **Secure key storage** - Use HashiCorp Vault, AWS KMS, or similar in production

### Data Handling

1. **Encrypt at application level** - Not at database level for better control
2. **Use property decorators** - For transparent encryption/decryption
3. **Audit access** - Log when sensitive data is accessed
4. **Implement data retention** - Automatically delete or anonymize old data

### Migration Strategy

1. **Add encrypted columns alongside existing ones**
2. **Copy data to encrypted columns in batches**
3. **Update application to use encrypted columns**
4. **Drop unencrypted columns after verification**

## Compliance Features

### GDPR Compliance

```python
# Data anonymization
customer.anonymize_data()

# Data retention checking
if customer.can_be_deleted():
    db.delete(customer)

# Consent tracking
customer.gdpr_consent = True
customer.consent_date = datetime.utcnow()
```

### Audit Trail

```python
# Track data access
customer.update_last_accessed()

# Data retention policy
customer.data_retention_until = datetime.utcnow() + timedelta(days=2555)  # 7 years
```

## Performance Considerations

1. **Encryption overhead** - ~1-2ms per field for encryption/decryption
2. **Indexing** - Cannot index encrypted fields, use business identifiers
3. **Searching** - Cannot search encrypted fields directly, use hash indexes for exact matches
4. **Caching** - Consider caching decrypted data with TTL in Redis

## Monitoring and Alerts

1. **Key rotation alerts** - Alert when keys are about to expire
2. **Encryption failures** - Log and alert on encryption/decryption errors
3. **Access patterns** - Monitor unusual access to encrypted data
4. **Compliance reporting** - Generate reports on data access and retention

## Migration Guide

### For Existing Models

1. **Create new encrypted columns**:
   ```python
   # Add to existing model
   email_encrypted = Column(EncryptedPII(), nullable=True)
   ```

2. **Create migration script**:
   ```python
   def migrate_to_encrypted():
       customers = db.query(Customer).all()
       for customer in customers:
           if customer.email and not customer.email_encrypted:
               customer.email_encrypted = customer.email
       db.commit()
   ```

3. **Update application code**:
   ```python
   # Replace direct field access with property
   @property
   def email(self):
       return self.email_encrypted or self.email_legacy
   ```

4. **Drop legacy columns** after migration complete

## Testing

```python
def test_customer_encryption():
    customer = Customer(name="John Doe", email="john@example.com")
    
    # Data should be encrypted in database
    assert customer.name_encrypted != "John Doe"
    assert customer.email_encrypted != "john@example.com"
    
    # But accessible via properties  
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
```

## Troubleshooting

### Common Issues

1. **Key not found error** - Check environment variables are set
2. **Decryption failed** - Data may not be encrypted or key is wrong
3. **Performance issues** - Consider caching strategy for frequently accessed data

### Debug Mode

Set `ENCRYPTION_DEBUG=true` to enable detailed logging of encryption operations.