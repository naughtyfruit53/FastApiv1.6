# Import all models from the new modular structure for backward compatibility
from .user_models import (
    PlatformUser, Organization, User, ServiceRole, ServicePermission, 
    ServiceRolePermission, UserServiceRole
)
from .customer_models import (
    Vendor, Customer, CustomerFile, CustomerInteraction, 
    CustomerSegment, VendorFile
)
from .product_models import (
    Product, ProductFile, Stock, InventoryTransaction, JobParts, InventoryAlert
)
from .system_models import (
    Company, AuditLog, EmailNotification, NotificationTemplate, NotificationLog, 
    NotificationPreference, PaymentTerm, OTPVerification
)
from .analytics_models import (
    ServiceAnalyticsEvent, ReportConfiguration, AnalyticsSummary
)
# Import service models from service_models.py
from .service_models import (
    Ticket, TicketHistory, TicketAttachment, SLAPolicy, SLATracking,
    DispatchOrder, DispatchItem, InstallationJob, InstallationTask,
    CompletionRecord, CustomerFeedback, ServiceClosure
)
from .vouchers import (
    BaseVoucher, PurchaseVoucher, PurchaseVoucherItem,
    SalesVoucher, SalesVoucherItem, PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem,
    DeliveryChallan, DeliveryChallanItem, ProformaInvoice, ProformaInvoiceItem,
    Quotation, QuotationItem, CreditNote, CreditNoteItem,
    DebitNote, DebitNoteItem
)

# No imports from .base as all models have been moved

__all__ = [
    # User and organization models
    "PlatformUser", "Organization", "User", "ServiceRole", "ServicePermission",
    "ServiceRolePermission", "UserServiceRole",
    
    # Customer and business entity models
    "Company", "Vendor", "Customer", "CustomerFile", "CustomerInteraction",
    "CustomerSegment", "VendorFile",
    
    # Product and inventory models
    "Product", "ProductFile", "Stock", "InventoryTransaction", "JobParts", "InventoryAlert",
    
    # System and notification models
    "Company", "AuditLog", "EmailNotification", "NotificationTemplate", "NotificationLog",
    "NotificationPreference", "PaymentTerm", "OTPVerification",
    
    # Analytics models
    "ServiceAnalyticsEvent", "ReportConfiguration", "AnalyticsSummary",
    
    # Service and ticket models
    "Ticket", "TicketHistory", "TicketAttachment", "SLAPolicy", "SLATracking",
    "DispatchOrder", "DispatchItem", "InstallationJob", "InstallationTask",
    "CompletionRecord", "CustomerFeedback", "ServiceClosure",
    
    # Voucher models
    "BaseVoucher", "PurchaseVoucher", "PurchaseVoucherItem",
    "SalesVoucher", "SalesVoucherItem", "PurchaseOrder", "PurchaseOrderItem",
    "SalesOrder", "SalesOrderItem", "GoodsReceiptNote", "GoodsReceiptNoteItem",
    "DeliveryChallan", "DeliveryChallanItem", "ProformaInvoice", "ProformaInvoiceItem",
    "Quotation", "QuotationItem", "CreditNote", "CreditNoteItem",
    "DebitNote", "DebitNoteItem"
]