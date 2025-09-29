# app/models/__init__.py

# Import all models from the new modular structure for backward compatibility
from .user_models import (
    PlatformUser, Organization, User, ServiceRole, ServicePermission, 
    ServiceRolePermission, UserServiceRole, OrganizationRole, RoleModuleAssignment,
    UserOrganizationRole, OrganizationApprovalSettings, VoucherApproval
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
    NotificationPreference, PaymentTerm, OTPVerification, EmailSend, EmailProvider, 
    EmailStatus, EmailType
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
    ChartOfAccounts, GSTConfiguration, ERPTaxCode, JournalEntry,
    AccountsPayable, AccountsReceivable, PaymentRecord,
    GeneralLedger, CostCenter, BankAccount, BankReconciliation,
    FinancialStatement, FinancialKPI
)
# Import financial modeling models
from .financial_modeling_models import (
    FinancialModel, DCFModel, ScenarioAnalysis, TradingComparables,
    TransactionComparables, FinancialModelTemplate, ModelAuditTrail,
    ValuationMethodType, ScenarioType
)
# Import forecasting models
from .forecasting_models import (
    FinancialForecast, ForecastVersion, BusinessDriverModel, MLForecastModel,
    MLPrediction, RiskAnalysis, RiskEvent, AutomatedInsight,
    ForecastMethodType, ForecastFrequency, ForecastStatus
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
# Import migration models
from .migration_models import (
    MigrationJob, MigrationDataMapping, MigrationLog, MigrationTemplate,
    MigrationConflict, MigrationSourceType, MigrationDataType, MigrationJobStatus
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
# Import HR, Payroll, Recruitment and Talent models
from .hr_models import (
    EmployeeProfile, AttendanceRecord, LeaveType, LeaveApplication, PerformanceReview
)
from .payroll_models import (
    SalaryStructure, PayrollPeriod, Payslip, TaxSlab, EmployeeLoan, PayrollSettings
)
from .recruitment_models import (
    JobPosting, Candidate, JobApplication, Interview, JobOffer, RecruitmentPipeline
)
from .talent_models import (
    SkillCategory, Skill, EmployeeSkill, TrainingProgram, TrainingSession, 
    TrainingEnrollment, LearningPath, LearningPathProgram, EmployeeLearningPath
)
from .vouchers import (
    BaseVoucher, PurchaseVoucher, PurchaseVoucherItem,
    SalesVoucher, SalesVoucherItem, PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem,
    DeliveryChallan, DeliveryChallanItem, ProformaInvoice, ProformaInvoiceItem,
    Quotation, QuotationItem, CreditNote, CreditNoteItem,
    DebitNote, DebitNoteItem
)
# Import exhibition models
from .exhibition_models import (
    ExhibitionEvent, BusinessCardScan, ExhibitionProspect
)
# Import task management models
from .task_management import (
    Task, TaskProject, TaskProjectMember, TaskComment, TaskAttachment,
    TaskTimeLog, TaskReminder, TaskStatus, TaskPriority
)
# Import calendar management models
from .calendar_management import (
    CalendarEvent, EventAttendee, EventReminder, Calendar, CalendarShare,
    GoogleCalendarIntegration, EventType, RecurrenceType, EventStatus
)
# Import OAuth2 models
from .oauth_models import (
    UserEmailToken, OAuthState, OAuthProvider, TokenStatus
)
# Import AI analytics models
from .ai_analytics_models import (
    AIModel, PredictionResult, AnomalyDetection, AIInsight, 
    ModelPerformanceMetric, AutomationWorkflow, ModelStatus, PredictionType
)
# Import Workflow Automation models
from .workflow_automation_models import (
    BusinessRule, WorkflowTemplateAdvanced, AutomationWorkflowStep, AutomationWorkflowInstance,
    AutomationWorkflowStepExecution, BusinessRuleExecution, WorkflowSchedule
)
# Import project models
from .project_models import (
    Project, ProjectMilestone, ProjectResource, ProjectDocument, ProjectTimeLog,
    ProjectStatus, ProjectPriority, ProjectType, MilestoneStatus, ResourceType
)
# Import workflow models
from .workflow_models import (
    WorkflowTemplate, WorkflowStep, WorkflowInstance, WorkflowStepInstance,
    ApprovalRequest, ApprovalHistory, ApprovalAttachment,
    WorkflowStatus, WorkflowTriggerType, ApprovalStatus, StepType, InstanceStatus, EscalationAction
)
# Import api gateway models
from .api_gateway_models import (
    APIKey, APIUsageLog, APIEndpoint, Webhook, WebhookDelivery, RateLimitRule, APIError,
    APIKeyStatus, RateLimitType, AccessLevel, LogLevel, WebhookStatus
)
# Import integration models
from .integration_models import (
    ExternalIntegration, IntegrationMapping, IntegrationSyncJob, IntegrationSyncRecord,
    IntegrationLog, DataTransformationRule, IntegrationSchedule,
    IntegrationType, IntegrationStatus, AuthType, SyncDirection, SyncStatus, MappingType
)
# Import master data models
from .master_data_models import (
    Category, Unit, TaxCode, PaymentTermsExtended,
    CategoryType, UnitType, TaxType
)
# Import email models
from .email import (
    MailAccount, Email, EmailThread, EmailAttachment, EmailSyncLog,
    EmailAccountType, EmailSyncStatus, EmailStatus as EmailMessageStatus, EmailPriority
)

# No imports from .base as all models have been moved

__all__ = [
    # User and organization models
    "PlatformUser", "Organization", "User", "ServiceRole", "ServicePermission",
    "ServiceRolePermission", "UserServiceRole", "OrganizationRole", "RoleModuleAssignment",
    "UserOrganizationRole", "OrganizationApprovalSettings", "VoucherApproval",
    
    # Customer and business entity models
    "Company", "Vendor", "Customer", "CustomerFile", "CustomerInteraction",
    "CustomerSegment", "VendorFile",
    
    # Product and inventory models
    "Product", "ProductFile", "Stock", "InventoryTransaction", "JobParts", "InventoryAlert",
    
    # System and notification models
    "Company", "AuditLog", "EmailNotification", "NotificationTemplate", "NotificationLog",
    "NotificationPreference", "PaymentTerm", "OTPVerification", "EmailSend", "EmailProvider",
    "EmailStatus", "EmailType",
    
    # Email module models
    "MailAccount", "Email", "EmailThread", "EmailAttachment", "EmailSyncLog",
    "EmailAccountType", "EmailSyncStatus", "EmailMessageStatus", "EmailPriority",
    
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
    
    # ERP and financial models
    "ChartOfAccounts", "GSTConfiguration", "ERPTaxCode", "JournalEntry",
    "AccountsPayable", "AccountsReceivable", "PaymentRecord",
    "GeneralLedger", "CostCenter", "BankAccount", "BankReconciliation",
    "FinancialStatement", "FinancialKPI",
    
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
    "VehicleType",
    
    # HR models
    "EmployeeProfile", "AttendanceRecord", "LeaveType", "LeaveApplication", "PerformanceReview",
    
    # Payroll models
    "SalaryStructure", "PayrollPeriod", "Payslip", "TaxSlab", "EmployeeLoan", "PayrollSettings",
    
    # Recruitment models
    "JobPosting", "Candidate", "JobApplication", "Interview", "JobOffer", "RecruitmentPipeline",
    
    # Talent models
    "SkillCategory", "Skill", "EmployeeSkill", "TrainingProgram", "TrainingSession", 
    "TrainingEnrollment", "LearningPath", "LearningPathProgram", "EmployeeLearningPath",
    
    # Exhibition models
    "ExhibitionEvent", "BusinessCardScan", "ExhibitionProspect",
    
    # Task management models
    "Task", "TaskProject", "TaskProjectMember", "TaskComment", "TaskAttachment",
    "TaskTimeLog", "TaskReminder", "TaskStatus", "TaskPriority",
    
    # Calendar management models
    "CalendarEvent", "EventAttendee", "EventReminder", "Calendar", "CalendarShare",
    "GoogleCalendarIntegration", "EventType", "RecurrenceType", "EventStatus",
    
    # OAuth2 models
    "UserEmailToken", "OAuthState", "OAuthProvider", "TokenStatus",
    
    # AI analytics models
    "AIModel", "PredictionResult", "AnomalyDetection", "AIInsight", 
    "ModelPerformanceMetric", "AutomationWorkflow", "ModelStatus", "PredictionType",
    
    # Migration models
    "MigrationJob", "MigrationDataMapping", "MigrationLog", "MigrationTemplate",
    "MigrationConflict", "MigrationSourceType", "MigrationDataType", "MigrationJobStatus",
    
    # Workflow automation models
    "BusinessRule", "WorkflowTemplateAdvanced", "AutomationWorkflowStep", "AutomationWorkflowInstance",
    "AutomationWorkflowStepExecution", "BusinessRuleExecution", "WorkflowSchedule",

    # Project models
    "Project", "ProjectMilestone", "ProjectResource", "ProjectDocument", "ProjectTimeLog",
    "ProjectStatus", "ProjectPriority", "ProjectType", "MilestoneStatus", "ResourceType",

    # Workflow models
    "WorkflowTemplate", "WorkflowStep", "WorkflowInstance", "WorkflowStepInstance",
    "ApprovalRequest", "ApprovalHistory", "ApprovalAttachment",
    "WorkflowStatus", "WorkflowTriggerType", "ApprovalStatus", "StepType", "InstanceStatus", "EscalationAction",

    # API gateway models
    "APIKey", "APIUsageLog", "APIEndpoint", "Webhook", "WebhookDelivery", "RateLimitRule", "APIError",
    "APIKeyStatus", "RateLimitType", "AccessLevel", "LogLevel", "WebhookStatus",

    # Integration models
    "ExternalIntegration", "IntegrationMapping", "IntegrationSyncJob", "IntegrationSyncRecord",
    "IntegrationLog", "DataTransformationRule", "IntegrationSchedule",
    "IntegrationType", "IntegrationStatus", "AuthType", "SyncDirection", "SyncStatus", "MappingType",

    # Master data models
    "Category", "Unit", "TaxCode", "PaymentTermsExtended",
    "CategoryType", "UnitType", "TaxType"
]

# No imports from .base as all models have been moved