# Enhanced Features Documentation

## Overview

This document describes the enhanced features implemented in the TRITIQ ERP system, focusing on improved file management, PDF extraction, and user experience enhancements.

## 1. Products Module Enhancement

### File Upload Functionality

The Products module now supports uploading up to 5 files per product, replacing the previous text-based "drawings path" field.

#### Features:
- **Multiple File Support**: Upload up to 5 files of any type per product
- **Drag-and-Drop Interface**: User-friendly file upload with visual feedback
- **File Management**: Preview, download, and remove files easily
- **File Type Support**: All file types supported (PDF, images, CAD files, documents, etc.)
- **Size Validation**: Maximum 10MB per file

#### API Endpoints:
- `POST /api/v1/products/{product_id}/files` - Upload a file
- `GET /api/v1/products/{product_id}/files` - List all files for a product
- `GET /api/v1/products/{product_id}/files/{file_id}/download` - Download a file
- `DELETE /api/v1/products/{product_id}/files/{file_id}` - Delete a file

#### Database Changes:
- Removed `drawings_path` column from `products` table
- Added new `product_files` table with proper relationships
- Migration script: `add_product_files.py`

## 2. PDF Extraction Service

### Intelligent Data Extraction

A new PDF extraction service automatically extracts structured data from uploaded PDF documents.

#### Supported Document Types:
- **Purchase Vouchers**: Extract vendor information, invoice details, line items
- **Sales Orders**: Extract customer information, order details, products
- **Vendor Documents**: Extract business information from GST certificates
- **Customer Documents**: Extract customer details from business documents

#### Features:
- **Real-time Processing**: Processes PDFs in real-time using PyMuPDF
- **Pattern Recognition**: Uses regex patterns to identify key information
- **Auto-population**: Automatically fills form fields with extracted data
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **File Validation**: Validates PDF format and file size

#### API Endpoint:
- `POST /api/v1/pdf-extraction/extract/{voucher_type}` - Extract data from PDF

#### Supported Voucher Types:
- `purchase_voucher`
- `sales_order` 
- `vendor`
- `customer`

## 3. Sales Order PDF Upload

### Enhanced Sales Order Creation

Sales Order creation now includes PDF upload functionality similar to Purchase Vouchers.

#### Features:
- **PDF Upload Interface**: Drag-and-drop PDF upload in create mode
- **Data Extraction**: Automatically extracts customer and order information
- **Form Auto-population**: Pre-fills form fields with extracted data
- **Line Items**: Automatically adds extracted product line items
- **Progress Indicators**: Visual feedback during processing
- **Error Recovery**: Graceful error handling with clear messages

#### Usage:
1. Navigate to Sales Order creation
2. Upload a customer order PDF using the upload area
3. Wait for processing to complete
4. Review and verify extracted data
5. Make adjustments if needed
6. Save the sales order

## 4. Centralized UI Configuration

### Unified User Experience

Implemented centralized configuration for tooltips, help text, and user messages.

#### Configuration File:
- Location: `frontend/src/config/ui-config.json`
- Sections: tooltips, help_text, error_messages, success_messages

#### Features:
- **Tooltips**: Context-sensitive help for form fields
- **Help Text**: Detailed guidance for complex features
- **Error Messages**: Consistent error messaging across the application
- **Success Messages**: Positive feedback for completed actions

#### Usage Hook:
```typescript
import { useUIConfig } from '../hooks/useUIConfig';

const { getTooltip, getHelpText, getErrorMessage } = useUIConfig();

// Get tooltip for a form field
const tooltip = getTooltip('masters.products.name');

// Get help text for a feature
const helpText = getHelpText('vouchers.pdf_extraction');
```

## 5. Updated Modules

### Purchase Voucher
- **Enhanced PDF Processing**: Now uses the real PDF extraction API
- **Better Error Handling**: Improved error messages and recovery
- **Consistent UI**: Updated to match new design patterns

### Vendor and Customer Management
- **PDF Support**: Ready for PDF extraction integration
- **Improved Forms**: Enhanced with tooltips and help text
- **Better Validation**: Client-side and server-side validation improvements

## 6. Technical Implementation

### Backend Changes:
- **New Service**: `PDFExtractionService` for document processing
- **Enhanced Models**: Updated Product model and added ProductFile model
- **API Extensions**: New endpoints for file management and PDF extraction
- **Database Migration**: Alembic migration for schema updates

### Frontend Changes:
- **New Components**: 
  - `ProductFileUpload`: File management component
  - `useUIConfig`: Configuration hook
- **Enhanced Forms**: Updated Sales Order and Purchase Voucher forms
- **Real API Integration**: Replaced mock implementations with real API calls
- **Improved UX**: Better loading states, error handling, and user feedback

### Dependencies:
- **Backend**: PyMuPDF (fitz) for PDF processing
- **Frontend**: Existing React/Material-UI stack
- **No Breaking Changes**: All changes are backward compatible

## 7. Testing

### Test Coverage:
- **Unit Tests**: PDF extraction service functionality
- **Integration Tests**: File upload and form validation
- **Mock Tests**: API endpoint testing with proper error scenarios

### Test Files:
- `tests/test_enhancements.py`: Main test suite for new features

## 8. Future Enhancements

### Planned Improvements:
- **OCR Support**: Add optical character recognition for scanned PDFs
- **Template Learning**: Learn from user corrections to improve extraction accuracy
- **Bulk Processing**: Support for processing multiple PDFs at once
- **Advanced Validation**: Cross-reference extracted data with existing records
- **Audit Trail**: Track all file operations and PDF extractions

### Scalability Considerations:
- **File Storage**: Consider cloud storage for production environments
- **Processing Queue**: Implement background processing for large files
- **Caching**: Cache extracted data to improve performance
- **Rate Limiting**: Implement rate limiting for PDF processing endpoints

## 9. Deployment Notes

### Prerequisites:
1. Install PyMuPDF: `pip install PyMuPDF`
2. Run database migration: `alembic upgrade head`
3. Ensure upload directories exist with proper permissions
4. Update environment variables if needed

### Configuration:
- **Upload Directory**: Default `uploads/products` (configurable)
- **File Size Limits**: 10MB per file (configurable)
- **Max Files per Product**: 5 files (configurable)

### Security Considerations:
- File uploads are validated for type and size
- PDF processing is sandboxed to prevent malicious code execution
- All file operations require proper authentication and organization context
- Temporary files are cleaned up automatically

## 10. Support and Troubleshooting

### Common Issues:
1. **PDF Not Processing**: Ensure PDF contains extractable text (not scanned images)
2. **File Upload Fails**: Check file size and network connection
3. **Extraction Inaccurate**: PDF may have non-standard format; manual entry required

### Logging:
- PDF extraction operations are logged for debugging
- File upload operations include detailed error logging
- API endpoint usage is tracked for monitoring

### Contact:
For technical support or feature requests, contact the development team.