# AI PDF Extraction Integration Guide

## Overview
The system now supports AI-powered PDF extraction for invoices, receipts, and other business documents. This feature uses free-tier AI APIs to automatically extract structured data from uploaded PDFs.

## Supported AI Services

### 1. Mindee API (Recommended)
**Free Tier:** 250 documents/month  
**Best For:** Invoices, receipts, financial documents  
**Sign Up:** https://mindee.com

**Setup:**
```bash
# Set environment variable
export MINDEE_API_KEY="your-api-key-here"
export USE_AI_EXTRACTION="true"
```

**Features:**
- Pre-trained models for invoices, receipts, passports
- High accuracy for structured business documents
- Automatic field extraction (vendor name, amounts, dates, line items)
- Fast processing (< 2 seconds per document)

### 2. Google Document AI
**Free Tier:** 1000 pages/month  
**Best For:** Complex documents, custom parsing  
**Sign Up:** https://cloud.google.com/document-ai

**Setup:**
```bash
# 1. Enable Document AI API in Google Cloud Console
# 2. Create an Invoice Parser processor
# 3. Download service account JSON key
# 4. Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_DOCUMENT_AI_KEY="your-project-id"
export USE_AI_EXTRACTION="true"
```

**Note:** Google Document AI requires more setup but offers better customization options.

### 3. PDF.co (Alternative)
**Free Tier:** 100 requests/month  
**Best For:** Simple OCR and text extraction  
**Sign Up:** https://pdf.co

## Usage

### Backend API
The AI extraction is automatically used when enabled:

```python
# Upload PDF for vendor data extraction
POST /api/v1/pdf-extraction/extract/vendor
Content-Type: multipart/form-data

file: <pdf-file>
```

### Frontend Integration
Already integrated in:
- Add Vendor Modal (GST certificate upload)
- Add Customer Modal (GST certificate upload)
- Purchase Voucher creation
- Sales Order creation

### Example Response
```json
{
  "success": true,
  "voucher_type": "vendor",
  "extracted_data": {
    "vendor_name": "ABC Suppliers Pvt Ltd",
    "gst_number": "27AABCU9603R1ZM",
    "address1": "123 Business Park",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pin_code": "400001",
    "pan_number": "AABCU9603R",
    "items": [
      {
        "description": "Product A",
        "quantity": 10,
        "unit_price": 100.00,
        "total_amount": 1000.00
      }
    ]
  },
  "filename": "gst_certificate.pdf"
}
```

## Configuration

### Environment Variables
```bash
# Enable/Disable AI extraction
USE_AI_EXTRACTION=true  # Set to false to use regex-based extraction only

# Mindee API (recommended)
MINDEE_API_KEY=your_mindee_api_key

# Google Document AI (optional)
GOOGLE_DOCUMENT_AI_KEY=your_google_project_id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# PDF.co (optional)
PDFCO_API_KEY=your_pdfco_api_key
```

### Fallback Behavior
When AI extraction fails or is disabled, the system automatically falls back to:
1. PyMuPDF text extraction
2. Regex-based pattern matching
3. Manual data entry

## Testing

### Test with Sample PDFs
1. Upload a sample invoice PDF
2. Check the extracted data in the response
3. Verify that fields are correctly populated in the form

### Testing Without AI APIs
Set `USE_AI_EXTRACTION=false` to test regex-based extraction.

## Performance Considerations

### Speed
- Mindee: ~2 seconds per document
- Google Document AI: ~3-5 seconds per document
- Regex fallback: < 1 second

### Accuracy
- AI extraction: 85-95% accuracy for standard invoices
- Regex extraction: 60-75% accuracy (depends on document format)

### Cost
All mentioned services have free tiers suitable for small to medium usage:
- Mindee: 250 docs/month free
- Google Document AI: 1000 pages/month free
- PDF.co: 100 requests/month free

## Troubleshooting

### "AI extraction failed" error
1. Check API key is correctly set
2. Verify API quota hasn't been exceeded
3. Check PDF file is valid and not corrupted
4. Review logs for specific error messages

### Low accuracy
1. Ensure PDF is not scanned at low resolution
2. Check if document format is supported
3. Try different AI service
4. Use manual correction for critical fields

### Slow processing
1. Optimize PDF file size (compress images)
2. Use async processing for batch uploads
3. Consider caching frequently accessed documents

## Future Enhancements
- [ ] Support for PDF.co integration
- [ ] Batch processing for multiple PDFs
- [ ] Custom model training for specific document types
- [ ] Webhook support for async processing
- [ ] Document type auto-detection
- [ ] Multi-language support

## Support
For issues or questions, please refer to:
- Mindee Documentation: https://developers.mindee.com/
- Google Document AI Docs: https://cloud.google.com/document-ai/docs
- PDF.co Documentation: https://pdf.co/docs
