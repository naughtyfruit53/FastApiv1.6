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
    CompletionRecord, CustomerFeedback, ServiceClosure,
    ChatbotConversation, ChatbotMessage, SurveyTemplate, CustomerSurvey, ChannelConfiguration
)
# Import CRM models
from .crm_models import (
    Lead, Opportunity, OpportunityProduct, LeadActivity, OpportunityActivity,
    SalesPipeline, SalesForecast
)
# Import Marketing models  
from .marketing_models import (
    Campaign, Promotion, PromotionRedemption, CampaignAnalytics,
    MarketingList, MarketingListContact
)
# Import ERP core models
from .erp_models import (
    ChartOfAccounts, GSTConfiguration, TaxCode, JournalEntry,
    AccountsPayable, AccountsReceivable, PaymentRecord
)
# Import procurement models
from .procurement_models import (
    RequestForQuotation, RFQItem, VendorRFQ, VendorQuotation, QuotationItem,
    VendorEvaluation, PurchaseRequisition, PurchaseRequisitionItem
)
# Import Tally integration models
from .tally_models import (
    TallyConfiguration, TallyLedgerMapping, TallyVoucherMapping, TallySyncLog,
    TallySyncItem, TallyDataCache, TallyErrorLog
)
# Import enhanced inventory models
from .enhanced_inventory_models import (
    Warehouse, StockLocation, ProductTracking, WarehouseStock, ProductBatch,
    ProductSerial, BatchLocation, StockMovement, StockAdjustment, StockAdjustmentItem
)
# Import asset management models
from .asset_models import (
    Asset, AssetStatus, AssetCondition, MaintenanceSchedule, MaintenanceRecord,
    MaintenanceType, MaintenanceStatus, DepreciationRecord, MaintenancePartUsed,
    DepreciationMethod
)
# Import transport and freight models
from .transport_models import (
    Carrier, CarrierType, Route, RouteStatus, FreightRate, FreightMode,
    Shipment, ShipmentStatus, ShipmentItem, ShipmentTracking, FreightCostAnalysis,
    VehicleType
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
    "ChatbotConversation", "ChatbotMessage", "SurveyTemplate", "CustomerSurvey", "ChannelConfiguration",
    
    # CRM models (new)
    "Lead", "Opportunity", "OpportunityProduct", "LeadActivity", "OpportunityActivity",
    "SalesPipeline", "SalesForecast",
    
    # Marketing models (new)
    "Campaign", "Promotion", "PromotionRedemption", "CampaignAnalytics",
    "MarketingList", "MarketingListContact",
    
    # Voucher models
    "BaseVoucher", "PurchaseVoucher", "PurchaseVoucherItem",
    "SalesVoucher", "SalesVoucherItem", "PurchaseOrder", "PurchaseOrderItem",
    "SalesOrder", "SalesOrderItem", "GoodsReceiptNote", "GoodsReceiptNoteItem",
    "DeliveryChallan", "DeliveryChallanItem", "ProformaInvoice", "ProformaInvoiceItem",
    "Quotation", "QuotationItem", "CreditNote", "CreditNoteItem",
    "DebitNote", "DebitNoteItem",
    
    # Asset management models
    "Asset", "AssetStatus", "AssetCondition", "MaintenanceSchedule", "MaintenanceRecord",
    "MaintenanceType", "MaintenanceStatus", "DepreciationRecord", "MaintenancePartUsed",
    "DepreciationMethod",
    
    # Transport and freight models
    "Carrier", "CarrierType", "Route", "RouteStatus", "FreightRate", "FreightMode",
    "Shipment", "ShipmentStatus", "ShipmentItem", "ShipmentTracking", "FreightCostAnalysis",
    "VehicleType"
]