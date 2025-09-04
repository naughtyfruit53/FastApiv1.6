# PDF Generation System Documentation

## Overview

The FastAPI v1.6 PDF Generation System provides comprehensive voucher PDF generation with Indian formatting standards, multi-tenant support, and professional styling.

## Features

### ✅ Comprehensive PDF Generation
- **Voucher Types**: Purchase, Sales, Pre-Sales (Quotations, Sales Orders, Proforma)
- **A4 Format**: Professional business-ready layout
- **Indian Standards**: Currency formatting (₹1,23,456.78), number-to-words conversion
- **Tax Calculations**: Automatic GST (CGST/SGST/IGST) calculations
- **Multi-page Support**: Automatic page breaks and numbering

### ✅ Company Branding Integration
- **Logo Support**: Company logos appear in top-left corner of PDFs
- **Upload API**: `POST /api/v1/companies/{id}/logo` for JPG/PNG uploads
- **Automatic Integration**: Logos automatically included in all voucher PDFs
- **Fallback Support**: Professional layout even without logo

### ✅ Product File Attachments
- **Multi-file Support**: Up to 5 files per product
- **All Formats**: Support for all file types
- **Upload API**: `POST /api/v1/products/{id}/files`
- **Database Storage**: Complete metadata tracking

### ✅ Security & RBAC
- **Multi-tenant Safe**: Organization-scoped PDF generation
- **RBAC Integration**: Permission-based access control
- **Audit Logging**: Complete operation tracking
- **Secure Storage**: Tenant-isolated file storage

## API Endpoints

### PDF Generation
```
POST /api/v1/pdf-generation/voucher/{type}/{id}
- Generate and preview PDF in browser
- Supported types: purchase, sales, quotation, sales_order, proforma

POST /api/v1/pdf-generation/voucher/{type}/{id}/download  
- Force download PDF file

GET /api/v1/pdf-generation/templates
- List available PDF templates
```

### Company Logo Management
```
POST /api/v1/companies/{id}/logo
- Upload company logo (JPG/PNG)

GET /api/v1/companies/{id}/logo
- Retrieve company logo

DELETE /api/v1/companies/{id}/logo  
- Delete company logo
```

### Product File Management
```
POST /api/v1/products/{id}/files
- Upload product attachment files

GET /api/v1/products/{id}/files
- List product files

DELETE /api/v1/products/{id}/files/{file_id}
- Delete product file
```

## Frontend Integration

### React Components

#### VoucherPDFButton
```tsx
import VoucherPDFButton from './components/VoucherPDFButton';

<VoucherPDFButton
  voucherType="sales"
  voucherId={123}
  voucherNumber="SV/2526/00001"
  variant="menu"  // 'button' | 'icon' | 'menu'
  size="medium"
/>
```

#### usePDFGeneration Hook
```tsx
import { usePDFGeneration } from './hooks/usePDFGeneration';

const { isGenerating, error, previewPDF, downloadPDF } = usePDFGeneration();

// Preview PDF
await previewPDF('sales', 123);

// Download PDF
await downloadPDF('sales', 123, 'invoice_123.pdf');
```

#### Enhanced VoucherHeaderActions
```tsx
import VoucherHeaderActions from './components/VoucherHeaderActions';

<VoucherHeaderActions
  mode="view"
  voucherType="Sales Voucher"
  voucherRoute="/vouchers/sales"
  currentId={123}
  voucherNumber="SV/2526/00001"
  showPDFButton={true}  // Enables PDF generation buttons
/>
```

### Integration Examples

#### Company Setup with Logo
```tsx
import CompanyLogoUpload from './components/CompanyLogoUpload';
import PDFSystemStatus from './components/PDFSystemStatus';

// In your company settings page
<CompanyLogoUpload 
  companyId={companyId}
  onLogoChange={(logoPath) => setCompanyLogo(logoPath)}
/>

<PDFSystemStatus
  companyLogo={companyLogo}
  hasProductFiles={true}
  voucherCount={150}
  rbacEnabled={true}
/>
```

## Technical Implementation

### Backend Architecture

#### PDF Generation Service
```python
from app.services.pdf_generation_service import pdf_generator

# Generate any voucher type PDF
pdf_path = pdf_generator.generate_voucher_pdf(
    voucher_type='sales',
    voucher_data=voucher_data,
    db=db,
    organization_id=org_id,
    current_user=user
)
```

#### Indian Number Formatting
```python
from app.services.pdf_generation_service import IndianNumberFormatter

# Amount to words
words = IndianNumberFormatter.amount_to_words(12345.67)
# Result: "Twelve Thousand Three Hundred Forty Five Rupees and Sixty Seven Paise Only"

# Currency formatting
formatted = IndianNumberFormatter.format_indian_currency(123456.78)
# Result: "₹1,23,456.78"
```

#### Tax Calculations
```python
from app.services.pdf_generation_service import TaxCalculator

# Calculate GST
gst_calc = TaxCalculator.calculate_gst(
    taxable_amount=10000.0,
    gst_rate=18.0,
    is_interstate=False
)
# Result: {'cgst_amount': 900.0, 'sgst_amount': 900.0, 'total_gst': 1800.0}
```

### Database Schema

#### Company Table (Existing)
```sql
ALTER TABLE companies ADD COLUMN logo_path VARCHAR;  -- Already exists
```

#### Product Files Table (Existing)
```sql
CREATE TABLE product_files (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES products(id),
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### File Structure
```
app/
├── services/
│   └── pdf_generation_service.py     # Main PDF generation logic
├── api/v1/
│   └── pdf_generation.py             # FastAPI endpoints
├── templates/pdf/
│   ├── base_voucher.html             # Master template
│   ├── purchase_voucher.html         # Purchase voucher
│   ├── sales_voucher.html            # Sales invoice
│   └── presales_voucher.html         # Quotation template
└── static/css/
    └── voucher_print.css             # Professional styling

frontend/src/
├── components/
│   ├── VoucherPDFButton.tsx          # PDF generation button
│   ├── PDFSystemStatus.tsx           # Status indicator
│   ├── VoucherHeaderActions.tsx      # Enhanced header with PDF
│   └── VoucherPageWithPDF.tsx        # Example integration
└── hooks/
    └── usePDFGeneration.ts           # PDF generation hook
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install weasyprint jinja2 reportlab num2words
```

### 2. Run Verification Script
```bash
python scripts/verify_pdf_system_setup.py
```

### 3. Test PDF Generation
```bash
# Test via API
curl -X POST "http://localhost:8000/api/v1/pdf-generation/voucher/sales/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/pdf"
```

### 4. Frontend Integration
```bash
# Install required components
npm install @mui/material @mui/icons-material
```

## Configuration

### Environment Variables
```env
# Optional - for advanced PDF features
WEASYPRINT_DPI=96
WEASYPRINT_TIMEOUT=60
```

### CSS Customization
Edit `app/static/css/voucher_print.css` to customize PDF styling:
- A4 page size and margins
- Company branding colors
- Font sizes and spacing
- Print optimizations

### Template Customization
Modify templates in `app/templates/pdf/` to customize PDF layout:
- Company header layout
- Item table structure
- Footer information
- Signature areas

## Testing

### Unit Tests
```bash
python -m pytest tests/test_pdf_voucher_generation.py -v
```

### Integration Tests
```bash
# Test with real voucher data
python -c "
from app.services.pdf_generation_service import pdf_generator
# Test PDF generation with sample data
"
```

## Troubleshooting

### Common Issues

1. **PDF Generation Fails**
   - Check WeasyPrint installation: `pip install weasyprint`
   - Verify template files exist in `app/templates/pdf/`
   - Check CSS file exists: `app/static/css/voucher_print.css`

2. **Logo Not Appearing**
   - Verify logo upload: `POST /api/v1/companies/{id}/logo`
   - Check file permissions on uploads directory
   - Ensure logo_path field exists in companies table

3. **Permission Denied**
   - Check RBAC permissions for current user
   - Verify organization_id matches voucher ownership
   - Ensure user has `voucher_read` or `presales_read` permission

4. **Templates Not Found**
   - Run verification script: `python scripts/verify_pdf_system_setup.py`
   - Check Jinja2 template loader configuration
   - Verify template directory structure

### Performance Optimization

1. **Large PDFs**
   - Enable pagination for multi-page vouchers
   - Optimize image sizes (logo should be < 500KB)
   - Use CSS print optimizations

2. **High Volume**
   - Implement PDF caching
   - Use background task queues for bulk generation
   - Optimize database queries with eager loading

## Future Enhancements

### Planned Features
- [ ] Multiple PDF template themes
- [ ] Bulk PDF generation
- [ ] Email integration with PDF attachments
- [ ] Digital signature support
- [ ] Advanced reporting with charts
- [ ] Custom fields in templates

### Performance Improvements
- [ ] PDF caching layer
- [ ] Background PDF generation
- [ ] Template compilation optimization
- [ ] CDN integration for static assets

## Support

For issues and questions:
1. Check this documentation
2. Run verification script
3. Review logs in `/var/log/fastapi/`
4. Test with sample data

The PDF generation system is designed to be robust, scalable, and production-ready for Indian business requirements.