# app/schemas/vouchers/__init__.py

# Import from base
from .base import (
    VoucherBase, VoucherInDBBase, VoucherItemBase, VoucherItemWithTax, SimpleVoucherItem,
    ChartOfAccountMinimal, ProductMinimal, VendorMinimal, PurchaseOrderMinimal,
    EmailNotificationBase, EmailNotificationCreate, EmailNotificationInDB,
    PaymentTermBase, PaymentTermCreate, PaymentTermUpdate, PaymentTermInDB,
    BulkImportResponse, BulkImportError, BulkImportWarning, DetailedBulkImportResponse,
    ExcelImportValidationResponse
)

# Import from purchase
from .purchase import (
    PurchaseVoucherItemCreate, PurchaseVoucherItemInDB, PurchaseVoucherCreate,
    PurchaseVoucherUpdate, PurchaseVoucherInDB, PurchaseOrderItemCreate,
    PurchaseOrderItemInDB, PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderInDB,
    PurchaseOrderAutoPopulateResponse, GRNItemCreate, GRNItemInDB, GRNCreate,
    GRNUpdate, GRNInDB, GRNAutoPopulateResponse, PurchaseReturnItemCreate,
    PurchaseReturnItemInDB, PurchaseReturnCreate, PurchaseReturnUpdate, PurchaseReturnInDB
)

# Import from sales
from .sales import (
    SalesVoucherItemCreate, SalesVoucherItemInDB, SalesVoucherCreate,
    SalesVoucherUpdate, SalesVoucherInDB, SalesOrderItemCreate,
    SalesOrderItemInDB, SalesOrderCreate, SalesOrderUpdate, SalesOrderInDB,
    SalesOrderAutoPopulateResponse, DeliveryChallanItemCreate, DeliveryChallanItemInDB,
    DeliveryChallanCreate, DeliveryChallanUpdate, DeliveryChallanInDB,
    DeliveryChallanAutoPopulateResponse, SalesReturnItemCreate, SalesReturnItemInDB,
    SalesReturnCreate, SalesReturnUpdate, SalesReturnInDB
)

# Import from presales
from .presales import (
    ProformaInvoiceItemCreate, ProformaInvoiceItemInDB, ProformaInvoiceCreate,
    ProformaInvoiceUpdate, ProformaInvoiceInDB, QuotationItemCreate,
    QuotationItemInDB, QuotationCreate, QuotationUpdate, QuotationInDB
)

# Import from financial
from .financial import (
    CreditNoteItemCreate, CreditNoteItemInDB, CreditNoteCreate,
    CreditNoteUpdate, CreditNoteInDB, DebitNoteItemCreate,
    DebitNoteItemInDB, DebitNoteCreate, DebitNoteUpdate, DebitNoteInDB,
    PaymentVoucherCreate, PaymentVoucherUpdate, PaymentVoucherInDB,
    ReceiptVoucherCreate, ReceiptVoucherUpdate, ReceiptVoucherInDB,
    ContraVoucherCreate, ContraVoucherUpdate, ContraVoucherInDB,
    JournalVoucherCreate, JournalVoucherUpdate, JournalVoucherInDB,
    InterDepartmentVoucherItemCreate, InterDepartmentVoucherItemInDB,
    InterDepartmentVoucherCreate, InterDepartmentVoucherUpdate, InterDepartmentVoucherInDB
)

# Re-export all for backward compatibility in vouchers submodule
__all__ = [
    # base
    'VoucherBase', 'VoucherInDBBase', 'VoucherItemBase', 'VoucherItemWithTax', 'SimpleVoucherItem',
    'ChartOfAccountMinimal', 'ProductMinimal', 'VendorMinimal', 'PurchaseOrderMinimal',
    'EmailNotificationBase', 'EmailNotificationCreate', 'EmailNotificationInDB',
    'PaymentTermBase', 'PaymentTermCreate', 'PaymentTermUpdate', 'PaymentTermInDB',
    'BulkImportResponse', 'BulkImportError', 'BulkImportWarning', 'DetailedBulkImportResponse',
    'ExcelImportValidationResponse',
    
    # purchase
    'PurchaseVoucherItemCreate', 'PurchaseVoucherItemInDB', 'PurchaseVoucherCreate',
    'PurchaseVoucherUpdate', 'PurchaseVoucherInDB', 'PurchaseOrderItemCreate',
    'PurchaseOrderItemInDB', 'PurchaseOrderCreate', 'PurchaseOrderUpdate', 'PurchaseOrderInDB',
    'PurchaseOrderAutoPopulateResponse', 'GRNItemCreate', 'GRNItemInDB', 'GRNCreate',
    'GRNUpdate', 'GRNInDB', 'GRNAutoPopulateResponse', 'PurchaseReturnItemCreate',
    'PurchaseReturnItemInDB', 'PurchaseReturnCreate', 'PurchaseReturnUpdate', 'PurchaseReturnInDB',
    
    # sales
    'SalesVoucherItemCreate', 'SalesVoucherItemInDB', 'SalesVoucherCreate',
    'SalesVoucherUpdate', 'SalesVoucherInDB', 'SalesOrderItemCreate',
    'SalesOrderItemInDB', 'SalesOrderCreate', 'SalesOrderUpdate', 'SalesOrderInDB',
    'SalesOrderAutoPopulateResponse', 'DeliveryChallanItemCreate', 'DeliveryChallanItemInDB',
    'DeliveryChallanCreate', 'DeliveryChallanUpdate', 'DeliveryChallanInDB',
    'DeliveryChallanAutoPopulateResponse', 'SalesReturnItemCreate', 'SalesReturnItemInDB',
    'SalesReturnCreate', 'SalesReturnUpdate', 'SalesReturnInDB',
    
    # presales
    'ProformaInvoiceItemCreate', 'ProformaInvoiceItemInDB', 'ProformaInvoiceCreate',
    'ProformaInvoiceUpdate', 'ProformaInvoiceInDB', 'QuotationItemCreate',
    'QuotationItemInDB', 'QuotationCreate', 'QuotationUpdate', 'QuotationInDB',
    
    # financial
    'CreditNoteItemCreate', 'CreditNoteItemInDB', 'CreditNoteCreate',
    'CreditNoteUpdate', 'CreditNoteInDB', 'DebitNoteItemCreate',
    'DebitNoteItemInDB', 'DebitNoteCreate', 'DebitNoteUpdate', 'DebitNoteInDB',
    'PaymentVoucherCreate', 'PaymentVoucherUpdate', 'PaymentVoucherInDB',
    'ReceiptVoucherCreate', 'ReceiptVoucherUpdate', 'ReceiptVoucherInDB',
    'ContraVoucherCreate', 'ContraVoucherUpdate', 'ContraVoucherInDB',
    'JournalVoucherCreate', 'JournalVoucherUpdate', 'JournalVoucherInDB',
    'InterDepartmentVoucherItemCreate', 'InterDepartmentVoucherItemInDB',
    'InterDepartmentVoucherCreate', 'InterDepartmentVoucherUpdate', 'InterDepartmentVoucherInDB'
]